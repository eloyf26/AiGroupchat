from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from livekit import api
import os
import json
import asyncio
import logging
import tempfile
from dotenv import load_dotenv
from typing import Optional, List
from uuid import UUID
from agent_templates import get_agent_template, get_available_templates
from document_store import DocumentStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("backend")

load_dotenv()

app = FastAPI(title="AiGroupchat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize document store globally
document_store = DocumentStore()


@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    logger.info("🚀 Starting AiGroupchat Backend")
    
    # Pre-load the reranker model if enabled
    if document_store.use_rerank:
        logger.info("🧠 [RERANKER] Starting model pre-load...")
        asyncio.create_task(load_reranker_model())
    else:
        logger.info("❌ [RERANKER] Reranking disabled")
    
    logger.info("✅ Backend ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("🛑 Shutting down AiGroupchat Backend")
    logger.info("👋 Backend shutdown complete")


async def load_reranker_model():
    """Load the reranker model in the background"""
    model_name = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    logger.info(f"📦 [RERANKER] Loading {model_name}...")
    
    try:
        await document_store._preload_reranker()
        logger.info("🎉 [RERANKER] Model loaded successfully - reranking active")
    except Exception as e:
        logger.error(f"💥 [RERANKER] Loading failed: {e}")
        logger.warning("⚠️  [RERANKER] Reranking disabled")


class TokenRequest(BaseModel):
    room_name: str
    participant_name: str
    enable_ai_agent: bool = True  # Enable AI agent by default for Stage 3
    agent_type: str = "study_partner"  # Default agent type for Stage 5
    agent_types: Optional[List[str]] = None  # Support multiple agents


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AiGroupchat API"}


@app.post("/api/token")
async def generate_token(request: TokenRequest):
    """Generate a LiveKit access token for a participant to join a room"""
    
    # Get LiveKit credentials from environment
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not api_key or not api_secret:
        raise HTTPException(
            status_code=500,
            detail="LiveKit credentials not configured"
        )
    
    try:
        # Create access token
        token = api.AccessToken(api_key, api_secret)
        
        # Configure token with room and participant info
        grants = api.VideoGrants(
            room_join=True,
            room=request.room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True
        )
        
        # If AI agent is enabled, create room with agent dispatch
        if request.enable_ai_agent:
            # Set room configuration to dispatch agent
            grants.room_create = True
            grants.room_admin = True
            
            # Add room metadata with agent type
            grants.room_record = True
            
            # Determine agent types to spawn
            agent_types_to_spawn = request.agent_types if request.agent_types else [request.agent_type]
            # Limit to 2 agents max
            agent_types_to_spawn = agent_types_to_spawn[:2]
            
            # Add metadata to participant to indicate agent should join
            # Include the selected agent type in metadata
            metadata = {
                "wants_agent": True,
                "agent_type": request.agent_type,
                "agent_types": agent_types_to_spawn
            }
            token.with_metadata(json.dumps(metadata))
            
            # Create room with metadata to pass agent types and owner_id
            try:
                livekit_api = api.LiveKitAPI(
                    url=os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
                    api_key=api_key,
                    api_secret=api_secret
                )
                room_metadata = {
                    "agent_types": agent_types_to_spawn,
                    "owner_id": request.participant_name
                }
                # Create or update room with metadata
                await livekit_api.room.create_room(
                    api.CreateRoomRequest(
                        name=request.room_name,
                        metadata=json.dumps(room_metadata)
                    )
                )
            except Exception as e:
                # Room might already exist, that's okay
                logger.info(f"Room creation/update: {str(e)}")
            
        
        token.with_grants(grants).with_identity(request.participant_name)
        
        # Generate the JWT token
        jwt = token.to_jwt()
        
        # For local development, use localhost URL
        # In production, this would be your LiveKit Cloud URL
        url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
        
        return {
            "token": jwt,
            "url": url,
            "ai_agent_enabled": request.enable_ai_agent,
            "agent_type": request.agent_type if request.enable_ai_agent else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate token: {str(e)}"
        )


@app.get("/api/agent-templates")
async def get_agent_templates():
    """Get available agent templates for Stage 5"""
    return get_available_templates()


@app.get("/api/agent-templates/{template_type}")
async def get_agent_template_details(template_type: str):
    """Get detailed information about a specific agent template"""
    template = get_agent_template(template_type)
    if template_type not in get_available_templates():
        raise HTTPException(
            status_code=404,
            detail=f"Agent template '{template_type}' not found"
        )
    return {
        "type": template_type,
        "name": template["name"],
        "description": template["description"],
        "instructions_preview": template["instructions"][:100] + "..."
    }


# Document Management Endpoints

@app.post("/api/documents")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    owner_id: str = Form(...),
):
    """Upload and process a document with embeddings"""
    try:
        # Determine file type from extension
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            file_type = "pdf"
        elif filename.endswith(('.txt', '.text')):
            file_type = "text"
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Only PDF and TXT files are supported."
            )
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process file with embeddings
            document_id = await document_store.process_file(
                file_path=tmp_file_path,
                file_type=file_type,
                owner_id=owner_id,
                title=title
            )
            
            # Get document info to return
            doc_response = document_store.supabase.table("documents").select("*").eq("id", document_id).execute()
            document = doc_response.data[0] if doc_response.data else None
            
            return {
                "document_id": document_id,
                "title": document["title"],
                "type": document["type"],
                "chunk_count": document["metadata"].get("chunk_count", 0),
                "created_at": document["created_at"]
            }
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document: {str(e)}"
        )


@app.get("/api/documents")
async def list_documents(owner_id: str):
    """List all documents for a user"""
    try:
        documents = await document_store.get_user_documents(owner_id)
        return documents
    except Exception as e:
        logger.error(f"Document listing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )


@app.get("/api/documents/{document_id}")
async def get_document(document_id: str, owner_id: str):
    """Get a specific document"""
    try:
        document = await document_store.get_document(document_id, owner_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get sections
        sections = await document_store.get_document_sections(document_id)
        
        return {
            "document": document,
            "sections": sections
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document retrieval error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve document: {str(e)}"
        )


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str, owner_id: str):
    """Delete a document"""
    try:
        success = await document_store.delete_document(document_id, owner_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document deletion error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )


class SearchRequest(BaseModel):
    query: str
    owner_id: str
    max_results: int = 5
    similarity_threshold: float = 0.3
    agent_id: Optional[str] = None


@app.post("/api/documents/search")
async def search_documents(request: SearchRequest):
    """Search documents using semantic similarity"""
    try:
        results = await document_store.search_documents(
            query=request.query,
            owner_id=request.owner_id,
            match_count=request.max_results,
            match_threshold=request.similarity_threshold,
            agent_id=request.agent_id
        )
        
        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Document search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search documents: {str(e)}"
        )


@app.post("/api/documents/context")
async def get_document_context(request: SearchRequest):
    """Get relevant context for a query to use in AI agent responses"""
    try:
        # Get context directly 
        context = await document_store.get_context_for_query(
            query=request.query,
            owner_id=request.owner_id,
            max_tokens=1500,
            agent_id=request.agent_id
        )
        
        return {
            "query": request.query,
            "context": context,
            "has_context": bool(context)
        }
        
    except Exception as e:
        logger.error(f"Context retrieval error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get document context: {str(e)}"
        )


class ConversationMessage(BaseModel):
    room_name: str
    participant_name: str
    participant_type: str  # 'human' or 'agent'
    message: str
    owner_id: Optional[str] = None  # Added for RLS
    metadata: Optional[dict] = {}


class CreateAgentRequest(BaseModel):
    name: str
    instructions: str
    voice_id: str = "nPczCjzI2devNBz1zQrb"  # Default to Brian
    greeting: str


class AgentResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    instructions: str
    voice_id: str
    greeting: str
    is_default: bool
    created_at: str
    document_count: Optional[int] = 0


class LinkDocumentsRequest(BaseModel):
    document_ids: List[str]


# Agent Management Endpoints

@app.post("/api/agents", response_model=AgentResponse)
async def create_agent(agent: CreateAgentRequest, owner_id: str):
    """Create a custom agent for a user"""
    try:
        result = document_store.supabase.table("user_agents").insert({
            "owner_id": owner_id,
            "name": agent.name,
            "instructions": agent.instructions,
            "voice_id": agent.voice_id,
            "greeting": agent.greeting,
            "is_default": False
        }).execute()
        
        return AgentResponse(**result.data[0], document_count=0)
    except Exception as e:
        logger.error(f"Failed to create agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents", response_model=List[AgentResponse])
async def list_agents(owner_id: str):
    """List all agents for a user (custom + defaults)"""
    try:
        # Get user's custom agents and default agents
        result = document_store.supabase.table("user_agents") \
            .select("*") \
            .or_(f"owner_id.eq.{owner_id},owner_id.eq._default") \
            .execute()
        
        agents = []
        for agent_data in result.data:
            # Count linked documents
            doc_count = document_store.supabase.table("agent_documents") \
                .select("document_id", count="exact") \
                .eq("agent_id", agent_data["id"]) \
                .execute()
            
            agents.append(AgentResponse(
                **agent_data,
                document_count=doc_count.count
            ))
        
        return agents
    except Exception as e:
        logger.error(f"Failed to list agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get a specific agent by ID"""
    try:
        result = document_store.supabase.table("user_agents") \
            .select("*") \
            .eq("id", agent_id) \
            .single() \
            .execute()
        
        # Count linked documents
        doc_count = document_store.supabase.table("agent_documents") \
            .select("document_id", count="exact") \
            .eq("agent_id", agent_id) \
            .execute()
        
        return AgentResponse(**result.data, document_count=doc_count.count)
    except Exception as e:
        logger.error(f"Failed to get agent: {str(e)}")
        raise HTTPException(status_code=404, detail="Agent not found")


@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str, owner_id: str):
    """Delete a custom agent (cannot delete default agents)"""
    try:
        # Check if agent exists and belongs to user
        check = document_store.supabase.table("user_agents") \
            .select("*") \
            .eq("id", agent_id) \
            .eq("owner_id", owner_id) \
            .eq("is_default", False) \
            .single() \
            .execute()
        
        if not check.data:
            raise HTTPException(status_code=403, detail="Cannot delete this agent")
        
        # Delete agent (cascades to agent_documents)
        document_store.supabase.table("user_agents") \
            .delete() \
            .eq("id", agent_id) \
            .execute()
        
        return {"message": "Agent deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/{agent_id}/documents")
async def link_documents_to_agent(agent_id: str, request: LinkDocumentsRequest):
    """Link documents to an agent"""
    try:
        # Prepare batch insert
        links = [
            {"agent_id": agent_id, "document_id": doc_id}
            for doc_id in request.document_ids
        ]
        
        # Insert links (ignore conflicts)
        if links:
            document_store.supabase.table("agent_documents") \
                .upsert(links, on_conflict="agent_id,document_id") \
                .execute()
        
        return {"message": f"Linked {len(links)} documents to agent"}
    except Exception as e:
        logger.error(f"Failed to link documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/agents/{agent_id}/documents/{document_id}")
async def unlink_document_from_agent(agent_id: str, document_id: str):
    """Unlink a document from an agent"""
    try:
        document_store.supabase.table("agent_documents") \
            .delete() \
            .eq("agent_id", agent_id) \
            .eq("document_id", document_id) \
            .execute()
        
        return {"message": "Document unlinked successfully"}
    except Exception as e:
        logger.error(f"Failed to unlink document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{agent_id}/documents")
async def list_agent_documents(agent_id: str):
    """List all documents linked to an agent"""
    try:
        # Get linked document IDs
        links = document_store.supabase.table("agent_documents") \
            .select("document_id") \
            .eq("agent_id", agent_id) \
            .execute()
        
        if not links.data:
            return []
        
        # Get document details
        doc_ids = [link["document_id"] for link in links.data]
        documents = document_store.supabase.table("documents") \
            .select("*") \
            .in_("id", doc_ids) \
            .execute()
        
        return documents.data
    except Exception as e:
        logger.error(f"Failed to list agent documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/conversation/message")
async def add_conversation_message(message: ConversationMessage):
    """Add a message to conversation history"""
    try:
        # Determine owner_id if not provided
        owner_id = message.owner_id
        if not owner_id:
            # For human messages, use participant name as owner
            if message.participant_type == "human":
                owner_id = message.participant_name
            else:
                # For agent messages, try to get owner from room metadata
                # This is a simple approach - in production you might want to cache this
                result = document_store.supabase.table("conversation_messages") \
                    .select("owner_id") \
                    .eq("room_name", message.room_name) \
                    .eq("participant_type", "human") \
                    .limit(1) \
                    .execute()
                
                if result.data:
                    owner_id = result.data[0]["owner_id"]
                else:
                    # Fallback: extract from room metadata or use room name
                    owner_id = message.room_name.split("_")[0] if "_" in message.room_name else message.room_name
        
        result = document_store.supabase.table("conversation_messages").insert({
            "room_name": message.room_name,
            "participant_name": message.participant_name,
            "participant_type": message.participant_type,
            "message": message.message,
            "owner_id": owner_id,
            "metadata": message.metadata
        }).execute()
        
        return {"status": "success", "id": result.data[0]["id"]}
    except Exception as e:
        logger.error(f"Failed to add conversation message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversation/{room_name}")
async def get_conversation_history(room_name: str, limit: int = 20):
    """Get conversation history for a room"""
    try:
        result = document_store.supabase.table("conversation_messages") \
            .select("*") \
            .eq("room_name", room_name) \
            .order("created_at", desc=False) \
            .limit(limit) \
            .execute()
        
        return {"messages": result.data}
    except Exception as e:
        logger.error(f"Failed to get conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))