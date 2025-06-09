import os
from typing import List, Dict, Optional
from uuid import UUID
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class DocumentStore:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(url, key)
    
    def set_user_context(self, user_id: str):
        """Set the user context for RLS policies"""
        # This would typically be done with a service role key and custom headers
        # For MVP, we'll use a simplified approach
        self.current_user_id = user_id
    
    async def create_document(self, owner_id: str, title: str, doc_type: str, metadata: Optional[Dict] = None) -> Dict:
        """Create a new document"""
        data = {
            "owner_id": owner_id,
            "title": title,
            "type": doc_type,
            "metadata": metadata or {}
        }
        
        response = self.supabase.table("documents").insert(data).execute()
        return response.data[0] if response.data else None
    
    async def get_document(self, document_id: str, owner_id: str) -> Optional[Dict]:
        """Get a document by ID"""
        response = (
            self.supabase.table("documents")
            .select("*")
            .eq("id", document_id)
            .eq("owner_id", owner_id)
            .single()
            .execute()
        )
        return response.data
    
    async def list_documents(self, owner_id: str) -> List[Dict]:
        """List all documents for a user"""
        response = (
            self.supabase.table("documents")
            .select("*")
            .eq("owner_id", owner_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    
    async def delete_document(self, document_id: str, owner_id: str) -> bool:
        """Delete a document and all its sections"""
        response = (
            self.supabase.table("documents")
            .delete()
            .eq("id", document_id)
            .eq("owner_id", owner_id)
            .execute()
        )
        return len(response.data) > 0 if response.data else False
    
    async def add_document_section(
        self, 
        document_id: str, 
        content: str, 
        embedding: Optional[List[float]] = None,
        chunk_index: int = 0,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Add a section to a document"""
        data = {
            "document_id": document_id,
            "content": content,
            "chunk_index": chunk_index,
            "metadata": metadata or {}
        }
        
        if embedding:
            data["embedding"] = embedding
        
        response = self.supabase.table("document_sections").insert(data).execute()
        return response.data[0] if response.data else None
    
    async def search_similar_sections(
        self, 
        embedding: List[float], 
        owner_id: str,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict]:
        """Search for similar document sections using vector similarity"""
        # Using RPC function for vector similarity search
        # This assumes you've created a Postgres function for similarity search
        response = self.supabase.rpc(
            "search_document_sections",
            {
                "query_embedding": embedding,
                "owner_id": owner_id,
                "match_threshold": threshold,
                "match_count": limit
            }
        ).execute()
        
        return response.data if response.data else []
    
    async def get_document_sections(self, document_id: str) -> List[Dict]:
        """Get all sections for a document"""
        response = (
            self.supabase.table("document_sections")
            .select("*")
            .eq("document_id", document_id)
            .order("chunk_index")
            .execute()
        )
        return response.data