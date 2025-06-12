"""
Document Store for RAG (Retrieval-Augmented Generation)
Handles document processing, embedding generation, and vector search using Supabase
"""

import os
import uuid
import time
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import tempfile
import logging
from concurrent.futures import ThreadPoolExecutor

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document
from supabase import create_client, Client
from dotenv import load_dotenv

# Hybrid search and reranking imports
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

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
        
        # Configuration for hybrid search and reranking
        self.use_hybrid_search = os.environ.get("USE_HYBRID_SEARCH", "false").lower() == "true"
        self.use_rerank = os.environ.get("USE_RERANK", "false").lower() == "true"
        
        # Log configuration on startup
        logger.info(f"🔧 [RAG] Hybrid Search: {'ON' if self.use_hybrid_search else 'OFF'}, Reranking: {'ON' if self.use_rerank else 'OFF'}")
        
        # Performance optimization components
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._doc_metadata_cache = {}  # Document metadata cache with TTL
        self._bm25_indexes = {}  # Pre-built BM25 indexes per user
        self._reranker = None  # Will be loaded by startup event if enabled
    
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
        
        # Cache document metadata immediately
        self._cache_document_metadata(document_id, doc_response.data[0])
        
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
        
        # Build BM25 index immediately in background
        await self._rebuild_bm25_index(owner_id)
        
        return document_id
    
    async def search_documents(
        self, 
        query: str, 
        owner_id: str, 
        match_count: int = 5,
        match_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant document sections using configured search method
        
        Args:
            query: Search query
            owner_id: ID of the document owner
            match_count: Number of results to return
            match_threshold: Minimum similarity threshold
            
        Returns:
            List of matching document sections with metadata
        """
        # Choose search method based on configuration
        if self.use_hybrid_search:
            logger.info(f"🔍 [HYBRID] Query: '{query[:40]}...'")
            results = await self._hybrid_search(query, owner_id, match_count, match_threshold)
        else:
            logger.info(f"🔍 [SEMANTIC] Query: '{query[:40]}...'")
            results = await self._semantic_search(query, owner_id, match_count, match_threshold)
        
        # Apply reranking if enabled and model is loaded
        if self.use_rerank and len(results) > 1 and self._reranker is not None:
            logger.info(f"🎯 [RERANK] Processing {len(results)} results")
            results = self._rerank_results(query, results, match_count)
        
        logger.info(f"📊 [RESULT] {len(results)} documents found")
        return results
    
    async def _semantic_search(
        self, 
        query: str, 
        owner_id: str, 
        match_count: int = 5,
        match_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Original semantic search implementation"""
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
        
        # Format results using cached metadata
        results = []
        for row in response.data:
            # Try cached metadata first
            doc_info = self._get_cached_document_metadata(row["document_id"])
            if not doc_info:
                # Fetch and cache if not found
                try:
                    doc_response = self.supabase.table("documents").select("*").eq("id", row["document_id"]).execute()
                    doc_info = doc_response.data[0] if doc_response.data else {}
                    self._cache_document_metadata(row["document_id"], doc_info)
                except Exception as e:
                    logger.error(f"Failed to fetch document metadata: {e}")
                    doc_info = {}
            
            results.append({
                "content": row["content"],
                "similarity": row["similarity"],
                "document_title": doc_info.get("title", "Unknown"),
                "document_type": doc_info.get("type", "Unknown"),
                "metadata": row.get("metadata", {})
            })
        
        return results
    
    async def _hybrid_search(
        self, 
        query: str, 
        owner_id: str, 
        match_count: int = 5,
        match_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Concurrent hybrid search combining semantic and BM25 results"""
        # Removed verbose logging
        
        # Create concurrent tasks
        semantic_task = asyncio.create_task(
            self._semantic_search(query, owner_id, match_count * 2, match_threshold)
        )
        bm25_task = asyncio.create_task(
            self._bm25_search_async(query, owner_id, match_count * 2)
        )
        
        # Wait for both searches to complete
        semantic_results, bm25_results = await asyncio.gather(
            semantic_task, bm25_task, return_exceptions=True
        )
        
        # Handle exceptions from individual tasks
        if isinstance(semantic_results, Exception):
            logger.error(f"[HYBRID] Semantic search failed: {semantic_results}")
            semantic_results = []
        if isinstance(bm25_results, Exception):
            logger.error(f"[HYBRID] BM25 search failed: {bm25_results}")
            bm25_results = []
        
        # Removed verbose logging
        
        # Convert BM25 results using cached metadata
        formatted_bm25_results = self._format_bm25_results_with_cache(bm25_results)
        
        # Combine using RRF
        combined_results = self._reciprocal_rank_fusion(semantic_results, formatted_bm25_results)
        
        # Removed verbose logging
        return combined_results[:match_count]
    
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
            
            # Invalidate BM25 cache for this user
            if owner_id in self._bm25_indexes:
                del self._bm25_indexes[owner_id]
            
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
    
    async def get_context_for_query_progressive(self, query: str, owner_id: str, max_tokens: int = 1500):
        """
        Progressive context retrieval for voice applications
        Yields quick results first, then enhanced results if available
        """
        # Quick semantic search for immediate response
        quick_results = await self._semantic_search(query, owner_id, 3, 0.3)
        
        if quick_results:
            quick_context = self._format_context_results(quick_results, max_tokens // 2)
            yield quick_context
        
        # Enhanced search in background if hybrid enabled
        if self.use_hybrid_search:
            try:
                enhanced_results = await self._hybrid_search(query, owner_id, 5)
                if len(enhanced_results) > len(quick_results):
                    enhanced_context = self._format_context_results(enhanced_results, max_tokens)
                    yield enhanced_context
            except Exception as e:
                logger.error(f"Enhanced search failed: {e}")
    
    def _format_context_results(self, results: List[Dict], max_tokens: int) -> str:
        """Format search results into context string"""
        context_parts = []
        total_length = 0
        
        for result in results:
            part = f"[From: {result['document_title']}]\n{result['content']}\n"
            part_length = len(part)
            
            if total_length + part_length > max_tokens:
                break
            
            context_parts.append(part)
            total_length += part_length
        
        return "\n---\n".join(context_parts)
    
    def _get_bm25_index(self, owner_id: str):
        """Get or create BM25 index for a user"""
        if not self.use_hybrid_search:
            return None
            
        if owner_id not in self._bm25_indexes:
            self._build_bm25_index(owner_id)
        return self._bm25_indexes.get(owner_id)
    
    def _build_bm25_index(self, owner_id: str):
        """Build BM25 index for user's documents"""
        try:
            # Try to use the new function first, fallback to manual query
            try:
                response = self.supabase.rpc(
                    "get_user_document_sections",
                    {"user_id": owner_id}
                ).execute()
            except Exception:
                # Fallback: manual query if function doesn't exist
                response = self.supabase.table("document_sections").select(
                    "id, document_id, content, chunk_index, documents!inner(owner_id)"
                ).eq("documents.owner_id", owner_id).order("document_id, chunk_index").execute()
                
                # Reformat to match expected structure
                if response.data:
                    formatted_data = []
                    for item in response.data:
                        formatted_data.append({
                            'id': item['id'],
                            'content': item['content'],
                            'document_id': item['document_id'],
                            'chunk_index': item['chunk_index']
                        })
                    response.data = formatted_data
            
            if not response.data:
                return
            
            # Prepare tokenized corpus
            corpus = []
            doc_mapping = []
            
            for section in response.data:
                # Simple tokenization
                tokens = section['content'].lower().split()
                corpus.append(tokens)
                doc_mapping.append({
                    'id': section['id'],
                    'content': section['content'],
                    'document_id': section['document_id']
                })
            
            # Create BM25 index
            bm25 = BM25Okapi(corpus)
            self._bm25_indexes[owner_id] = {
                'index': bm25,
                'docs': doc_mapping
            }
            
        except Exception as e:
            logger.error(f"Error building BM25 index: {e}")
    
    def _bm25_search(self, query: str, owner_id: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform BM25 keyword search"""
        bm25_data = self._get_bm25_index(owner_id)
        if not bm25_data:
            return []
        
        # Tokenize query
        query_tokens = query.lower().split()
        
        # Get BM25 scores
        scores = bm25_data['index'].get_scores(query_tokens)
        
        # Convert to numpy array if not already, then ensure proper handling
        import numpy as np
        if not isinstance(scores, np.ndarray):
            scores = np.array(scores)
        
        # Get top results
        top_indices = sorted(range(len(scores)), key=lambda i: float(scores[i]), reverse=True)[:max_results]
        
        results = []
        for idx in top_indices:
            score_value = float(scores[idx])  # Convert to float to avoid numpy array issues
            if score_value > 0:  # Only include relevant results
                doc = bm25_data['docs'][idx]
                results.append({
                    'content': doc['content'],
                    'score': score_value,
                    'document_id': doc['document_id'],
                    'section_id': doc['id']
                })
        
        # Removed verbose logging
        return results
    
    def _reciprocal_rank_fusion(self, semantic_results: List, bm25_results: List, k: int = 60) -> List[Dict[str, Any]]:
        """Combine results using Reciprocal Rank Fusion"""
        rrf_scores = {}
        
        # Process semantic results
        for rank, result in enumerate(semantic_results, 1):
            key = result.get('content', '')[:100]  # Use content snippet as key
            rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (rank + k)
            rrf_scores[key + '_data'] = result
        
        # Process BM25 results
        for rank, result in enumerate(bm25_results, 1):
            key = result.get('content', '')[:100]
            rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (rank + k)
            if key + '_data' not in rrf_scores:
                rrf_scores[key + '_data'] = result
        
        # Sort by RRF score and format results
        scored_results = []
        for key, score in rrf_scores.items():
            if not key.endswith('_data'):
                data = rrf_scores.get(key + '_data', {})
                if data:
                    data['rrf_score'] = score
                    scored_results.append(data)
        
        return sorted(scored_results, key=lambda x: x.get('rrf_score', 0), reverse=True)
    
    def _get_reranker(self):
        """Get the pre-loaded reranker model"""
        if not self.use_rerank:
            return None
        return self._reranker
    
    def _rerank_results(self, query: str, results: List[Dict[str, Any]], max_results: int = 5) -> List[Dict[str, Any]]:
        """Rerank results using pre-loaded cross-encoder model"""
        reranker = self._get_reranker()
        
        # Skip reranking if model not loaded or insufficient results
        if not reranker or len(results) <= 1:
            if self.use_rerank and not reranker:
                logger.debug("[RERANKER] Model not ready, skipping reranking")
            return results[:max_results]
        
        try:
            # Prepare query-document pairs
            pairs = [(query, result['content']) for result in results]
            
            # Get reranking scores
            scores = reranker.predict(pairs)
            
            # Ensure scores is a proper numpy array and convert to list for safe handling
            import numpy as np
            if isinstance(scores, np.ndarray):
                scores_list = [float(score) for score in scores.flatten()]
            else:
                scores_list = [float(score) for score in scores]
            
            # Add scores to results and sort
            for i, result in enumerate(results):
                result['rerank_score'] = scores_list[i]
            return sorted(results, key=lambda x: x.get('rerank_score', 0), reverse=True)[:max_results]
            
        except Exception as e:
            logger.error(f"[RERANKER] Error during reranking: {e}")
            return results[:max_results]
    
    def _cache_document_metadata(self, document_id: str, doc_info: Dict):
        """Cache document metadata with TTL"""
        self._doc_metadata_cache[document_id] = {
            'data': doc_info,
            'timestamp': time.time()
        }
    
    def _get_cached_document_metadata(self, document_id: str) -> Optional[Dict]:
        """Get cached document metadata with TTL check (5 minute TTL)"""
        cached = self._doc_metadata_cache.get(document_id)
        if cached and (time.time() - cached['timestamp']) < 300:
            return cached['data']
        return None
    
    async def _rebuild_bm25_index(self, owner_id: str):
        """Rebuild BM25 index in background thread"""
        def build_index():
            self._build_bm25_index(owner_id)
        
        await asyncio.get_event_loop().run_in_executor(
            self._executor, build_index
        )
    
    async def _preload_reranker(self):
        """Pre-load reranker model on startup"""
        import time
        
        def load_model():
            model_name = os.environ.get("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
            return CrossEncoder(model_name)
        
        try:
            self._reranker = await asyncio.get_event_loop().run_in_executor(
                self._executor, load_model
            )
        except Exception as e:
            logger.error(f"💥 [RERANKER] Failed to load: {e}")
            raise
    
    async def _bm25_search_async(self, query: str, owner_id: str, max_results: int = 5):
        """Async wrapper for BM25 search"""
        def bm25_search():
            return self._bm25_search(query, owner_id, max_results)
        
        return await asyncio.get_event_loop().run_in_executor(
            self._executor, bm25_search
        )
    
    def _format_bm25_results_with_cache(self, bm25_results: List[Dict]) -> List[Dict[str, Any]]:
        """Format BM25 results using cached metadata"""
        formatted_results = []
        for result in bm25_results:
            # Try to get cached metadata first
            doc_info = self._get_cached_document_metadata(result["document_id"])
            if not doc_info:
                # Fetch and cache if not found
                try:
                    doc_response = self.supabase.table("documents").select("*").eq("id", result["document_id"]).execute()
                    doc_info = doc_response.data[0] if doc_response.data else {}
                    self._cache_document_metadata(result["document_id"], doc_info)
                except Exception as e:
                    logger.error(f"Failed to fetch document metadata: {e}")
                    doc_info = {}
            
            formatted_results.append({
                "content": result["content"],
                "similarity": result["score"],
                "document_title": doc_info.get("title", "Unknown"),
                "document_type": doc_info.get("type", "Unknown"),
                "metadata": {"bm25_score": result["score"]}
            })
        
        return formatted_results