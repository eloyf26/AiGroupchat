"""
Document Store for RAG (Retrieval-Augmented Generation)
Handles document processing, embedding generation, and vector search using Supabase
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import tempfile
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class DocumentStore:
    def __init__(self):
        """Initialize DocumentStore with Supabase client and OpenAI embeddings"""
        # Initialize Supabase client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
        
        self.supabase: Client = create_client(url, key)
        
        # Initialize OpenAI embeddings (text-embedding-3-small)
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=openai_api_key
        )
        
        # Initialize text splitter (512 tokens per chunk as per plan)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    async def process_file(self, file_path: str, file_type: str, owner_id: str, title: str) -> str:
        """
        Process a file and store it in the database
        
        Args:
            file_path: Path to the file to process
            file_type: Type of file (pdf, txt)
            owner_id: ID of the document owner
            title: Title of the document
            
        Returns:
            document_id: ID of the created document
        """
        # Load document based on file type
        if file_type == "pdf":
            loader = PyPDFLoader(file_path)
        elif file_type in ["txt", "text"]:
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        documents = loader.load()
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Create document record
        doc_data = {
            "owner_id": owner_id,
            "title": title,
            "type": file_type,
            "metadata": {
                "chunk_count": len(chunks),
                "source_file": os.path.basename(file_path)
            }
        }
        
        # Insert document
        doc_response = self.supabase.table("documents").insert(doc_data).execute()
        document_id = doc_response.data[0]["id"]
        
        # Process and store chunks with embeddings
        for idx, chunk in enumerate(chunks):
            # Generate embedding
            embedding = self.embeddings.embed_query(chunk.page_content)
            
            # Prepare chunk data
            chunk_data = {
                "document_id": document_id,
                "content": chunk.page_content,
                "embedding": embedding,
                "chunk_index": idx,
                "metadata": {
                    "page": chunk.metadata.get("page", None),
                    "source": chunk.metadata.get("source", None)
                }
            }
            
            # Insert chunk
            self.supabase.table("document_sections").insert(chunk_data).execute()
        
        return document_id
    
    async def search_documents(
        self, 
        query: str, 
        owner_id: str, 
        match_count: int = 5,
        match_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant document sections using semantic similarity
        
        Args:
            query: Search query
            owner_id: ID of the document owner
            match_count: Number of results to return
            match_threshold: Minimum similarity threshold
            
        Returns:
            List of matching document sections with metadata
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Call the search function
        response = self.supabase.rpc(
            "search_document_sections",
            {
                "query_embedding": query_embedding,
                "owner_id": owner_id,
                "match_count": match_count,
                "match_threshold": match_threshold
            }
        ).execute()
        
        # Format results
        results = []
        for row in response.data:
            # Get document info
            doc_response = self.supabase.table("documents").select("*").eq("id", row["document_id"]).execute()
            doc_info = doc_response.data[0] if doc_response.data else {}
            
            results.append({
                "content": row["content"],
                "similarity": row["similarity"],
                "document_title": doc_info.get("title", "Unknown"),
                "document_type": doc_info.get("type", "Unknown"),
                "metadata": row.get("metadata", {})
            })
        
        return results
    
    async def get_user_documents(self, owner_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a user"""
        response = self.supabase.table("documents").select("*").eq("owner_id", owner_id).order("created_at", desc=True).execute()
        return response.data
    
    async def get_document(self, document_id: str, owner_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        response = self.supabase.table("documents").select("*").eq("id", document_id).eq("owner_id", owner_id).execute()
        return response.data[0] if response.data else None
    
    async def get_document_sections(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all sections for a document"""
        response = self.supabase.table("document_sections").select("*").eq("document_id", document_id).order("chunk_index").execute()
        return response.data
    
    async def delete_document(self, document_id: str, owner_id: str) -> bool:
        """Delete a document and all its sections"""
        try:
            self.supabase.table("documents").delete().eq("id", document_id).eq("owner_id", owner_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    async def get_context_for_query(self, query: str, owner_id: str, max_tokens: int = 1500) -> str:
        """
        Get relevant context for a query to use in LLM prompts
        
        Args:
            query: The user's question
            owner_id: ID of the document owner
            max_tokens: Maximum tokens to include in context
            
        Returns:
            Formatted context string
        """
        # Search for relevant documents
        results = await self.search_documents(query, owner_id, match_count=5)
        
        if not results:
            return ""
        
        # Build context string
        context_parts = []
        total_length = 0
        
        for result in results:
            # Format each result
            part = f"[From: {result['document_title']}]\n{result['content']}\n"
            part_length = len(part)
            
            # Check if adding this would exceed max tokens
            if total_length + part_length > max_tokens:
                break
            
            context_parts.append(part)
            total_length += part_length
        
        return "\n---\n".join(context_parts)