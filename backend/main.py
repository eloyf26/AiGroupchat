from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from livekit import api
import os
import json
import asyncio
import logging
import tempfile
import shutil
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
    """Pre-load models and initialize resources on startup"""
    logger.info("🚀 Starting AiGroupchat Backend")
    
    # Pre-load the reranker model if enabled
    if document_store.use_rerank:
        logger.info("🧠 [RERANKER] Starting model pre-load...")
        asyncio.create_task(load_reranker_model())
    else:
        logger.info("❌ [RERANKER] Reranking disabled")
    
    logger.info("✅ Backend ready")


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


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AiGroupchat API"}


@app.get("/api/health/reranker")
async def reranker_status():
    """Check the status of the reranker model"""
    enabled = document_store.use_rerank
    loaded = document_store._reranker is not None
    model_name = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2") if enabled else None
    
    # Determine status
    if not enabled:
        status = "disabled"
    elif loaded:
        status = "ready"
    else:
        status = "loading"
    
    return {
        "enabled": enabled,
        "loaded": loaded,
        "status": status,
        "model": model_name,
        "message": {
            "disabled": "Reranking is disabled in configuration",
            "ready": "Reranker model is loaded and ready for use",
            "loading": "Reranker model is being pre-loaded at startup"
        }.get(status, "Unknown status")
    }


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
            
            # Add metadata to participant to indicate agent should join
            # Include the selected agent type in metadata
            metadata = {
                "wants_agent": True,
                "agent_type": request.agent_type
            }
            token.with_metadata(json.dumps(metadata))
            
            # Create room with metadata to pass agent type and owner_id
            try:
                livekit_api = api.LiveKitAPI(
                    url=os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
                    api_key=api_key,
                    api_secret=api_secret
                )
                room_metadata = {
                    "agent_type": request.agent_type,
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


# Document Management Endpoints for Stage 6

class DocumentMetadata(BaseModel):
    title: str
    type: str = "text"
    metadata: Optional[dict] = None




@app.post("/api/documents")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    owner_id: str = Form(...),
):
    """Upload and process a document with embeddings for Stage 7"""
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


@app.post("/api/documents/search")
async def search_documents(request: SearchRequest):
    """Search documents using semantic similarity for Stage 7"""
    try:
        results = await document_store.search_documents(
            query=request.query,
            owner_id=request.owner_id,
            match_count=request.max_results,
            match_threshold=request.similarity_threshold
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
            max_tokens=1500
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