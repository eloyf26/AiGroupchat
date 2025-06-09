from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from livekit import api
import os
import json
import asyncio
import logging
from dotenv import load_dotenv
from typing import Optional, List
from uuid import UUID
from agent_templates import get_agent_template, get_available_templates
from document_store import DocumentStore

# Configure logging
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


class TokenRequest(BaseModel):
    room_name: str
    participant_name: str
    enable_ai_agent: bool = True  # Enable AI agent by default for Stage 3
    agent_type: str = "study_partner"  # Default agent type for Stage 5


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
            
            # Add metadata to participant to indicate agent should join
            # Include the selected agent type in metadata
            metadata = {
                "wants_agent": True,
                "agent_type": request.agent_type
            }
            token.with_metadata(json.dumps(metadata))
            
            # Create room with metadata to pass agent type
            try:
                livekit_api = api.LiveKitAPI(
                    url=os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
                    api_key=api_key,
                    api_secret=api_secret
                )
                room_metadata = {
                    "agent_type": request.agent_type
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


# Initialize document store
document_store = DocumentStore()


@app.post("/api/documents")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    owner_id: str = Form(...),
    doc_type: str = Form("text")
):
    """Upload a new document"""
    try:
        # Create document record
        document = await document_store.create_document(
            owner_id=owner_id,
            title=title,
            doc_type=doc_type,
            metadata={
                "filename": file.filename,
                "content_type": file.content_type,
                "size": file.size
            }
        )
        
        # For now, just store the raw content
        # In Stage 7, we'll add chunking and embedding generation
        content = await file.read()
        content_text = content.decode('utf-8') if doc_type == "text" else str(content)
        
        # Add as a single section for now
        await document_store.add_document_section(
            document_id=document["id"],
            content=content_text,
            chunk_index=0,
            metadata={"type": "full_document"}
        )
        
        return {
            "document_id": document["id"],
            "title": document["title"],
            "type": document["type"],
            "created_at": document["created_at"]
        }
        
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
        documents = await document_store.list_documents(owner_id)
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