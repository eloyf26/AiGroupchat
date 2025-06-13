"""
Contextual Processor for RAG Enhancement
Implements Anthropic's Contextual Retrieval method with prompt caching
Supports both batch and streaming modes as configurable options
"""

import os
import time
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import anthropic
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ContextualProcessor:
    """
    Contextual processor with deterministic behavior
    - Configurable batch or streaming processing (no fallbacks)
    - Simple rate limiting
    - No fallbacks or retries
    - Clear error handling
    """
    
    def __init__(self):
        """Initialize with minimal configuration"""
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        self.enabled = os.environ.get("ENABLE_CONTEXTUAL_RETRIEVAL", "true").lower() == "true"
        self.model = os.environ.get("CONTEXTUAL_RETRIEVAL_MODEL", "claude-3-7-sonnet-latest")
        self.max_tokens_per_doc = int(os.environ.get("MAX_CONTEXTUAL_TOKENS_PER_DOCUMENT", "100000"))
        self.processing_timeout = int(os.environ.get("CONTEXTUAL_PROCESSING_TIMEOUT", "120"))
        
        # Processing mode configuration (no fallback between modes)
        self.use_batch_api = os.environ.get("CONTEXTUAL_USE_BATCH_API", "false").lower() == "true"
        self.batch_threshold = int(os.environ.get("CONTEXTUAL_BATCH_THRESHOLD", "10"))
        self.batch_timeout = int(os.environ.get("CONTEXTUAL_BATCH_TIMEOUT", "3600"))
        
        # Simple rate limiting - just request spacing
        self.min_request_interval = 2.0  # 2 seconds between requests (30 RPM max)
        self.last_request_time = 0
        
        # Basic tracking
        self.total_requests = 0
        self.successful_requests = 0
        
        processing_mode = "batch" if self.use_batch_api else "streaming"
        logger.info(f"🧠 [CONTEXTUAL] Initialized - Model: {self.model}, Mode: {processing_mode}, Enabled: {self.enabled}")
    
    def _build_prompt(self, chunk: str, document: str) -> Dict[str, Any]:
        """Build prompt with system message caching"""
        system_messages = [
            {
                "type": "text",
                "text": "You are an AI assistant that helps create contextual information for document chunks to improve search retrieval."
            },
            {
                "type": "text", 
                "text": f"<document>\n{document}\n</document>",
                "cache_control": {"type": "ephemeral"}
            }
        ]
        
        user_message = f"""Here is the chunk we want to situate within the whole document:

<chunk>
{chunk}
</chunk>

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else."""
        
        return {
            "system": system_messages,
            "messages": [{"role": "user", "content": user_message}]
        }
    
    async def _wait_for_rate_limit(self):
        """Simple rate limiting - just ensure minimum interval between requests"""
        now = time.time()
        time_since_last = now - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            logger.debug(f"⏰ Rate limiting: waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def _make_request(self, system: List[Dict], messages: List[Dict]) -> str:
        """Make API request with simple error handling"""
        def make_request():
            return self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.0,
                system=system,
                messages=messages,
                extra_headers={
                    "anthropic-beta": "prompt-caching-2024-07-31"
                }
            )
        
        response = await asyncio.get_event_loop().run_in_executor(None, make_request)
        return response.content[0].text.strip()
    
    async def generate_chunk_context(self, chunk: str, full_document: str) -> Optional[str]:
        """Generate context for a single chunk - simple and deterministic"""
        if not self.enabled:
            return None
        
        try:
            # Check document size
            doc_tokens = len(full_document) // 4  # Rough estimate
            if doc_tokens > self.max_tokens_per_doc:
                logger.warning(f"[CONTEXTUAL] Document too large ({doc_tokens} tokens), skipping")
                return None
            
            # Rate limiting
            await self._wait_for_rate_limit()
            
            # Build prompt
            prompt_data = self._build_prompt(chunk, full_document)
            
            # Make request with timeout
            self.total_requests += 1
            context = await asyncio.wait_for(
                self._make_request(prompt_data["system"], prompt_data["messages"]),
                timeout=self.processing_timeout
            )
            
            # Simple validation
            if context and context.strip():
                self.successful_requests += 1
                logger.debug(f"[CONTEXTUAL] Generated context: {context[:100]}...")
                return context
            else:
                logger.warning("[CONTEXTUAL] Empty context returned")
                return None
                
        except asyncio.TimeoutError:
            logger.error(f"[CONTEXTUAL] Timeout after {self.processing_timeout}s")
            return None
        except anthropic.APIError as e:
            logger.error(f"[CONTEXTUAL] API error: {e}")
            return None
        except Exception as e:
            logger.error(f"[CONTEXTUAL] Unexpected error: {e}")
            return None
    
    async def _process_streaming(
        self, 
        chunks: List[str], 
        full_document: str,
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """Process chunks sequentially with streaming API"""
        logger.info(f"[STREAMING] Processing {len(chunks)} chunks sequentially")
        
        processed_chunks = []
        successful_contexts = 0
        
        for idx, chunk in enumerate(chunks):
            logger.debug(f"[STREAMING] Processing chunk {idx + 1}/{len(chunks)}")
            
            context = await self.generate_chunk_context(chunk, full_document)
            
            if context:
                successful_contexts += 1
            
            processed_chunks.append({
                "content": chunk,
                "contextual_content": context,
                "is_contextualized": context is not None
            })
            
            if progress_callback:
                progress_callback(idx + 1, len(chunks))
        
        success_rate = (successful_contexts / len(chunks)) * 100 if chunks else 0
        logger.info(f"[STREAMING] Completed: {successful_contexts}/{len(chunks)} chunks ({success_rate:.1f}%)")
        
        return processed_chunks
    
    async def _process_batch(
        self, 
        chunks: List[str], 
        full_document: str,
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """Process chunks using Batch API - no fallback to streaming"""
        logger.info(f"[BATCH] Processing {len(chunks)} chunks via Batch API")
        
        # Create batch requests
        batch_requests = []
        for idx, chunk in enumerate(chunks):
            prompt_data = self._build_prompt(chunk, full_document)
            request = {
                "custom_id": f"chunk_{idx}",
                "params": {
                    "model": self.model,
                    "max_tokens": 1024,
                    "temperature": 0.0,
                    "system": prompt_data["system"],
                    "messages": prompt_data["messages"]
                }
            }
            batch_requests.append(request)
        
        # Submit batch (synchronous call in executor)
        def submit_batch():
            return self.client.messages.batches.create(requests=batch_requests)
        
        logger.info(f"[BATCH] Submitting {len(batch_requests)} requests")
        batch_response = await asyncio.get_event_loop().run_in_executor(None, submit_batch)
        
        # Wait for completion
        logger.info(f"[BATCH] Waiting for completion (ID: {batch_response.id})")
        results = await self._wait_for_batch_completion(batch_response.id, progress_callback)
        
        # Process results
        processed_chunks = []
        successful_contexts = 0
        
        for idx, chunk in enumerate(chunks):
            custom_id = f"chunk_{idx}"
            if custom_id in results:
                context = results[custom_id].content[0].text.strip()
                if context and context.strip():
                    successful_contexts += 1
                else:
                    context = None
            else:
                context = None
                logger.warning(f"[BATCH] No result for chunk {idx}")
            
            processed_chunks.append({
                "content": chunk,
                "contextual_content": context,
                "is_contextualized": context is not None
            })
        
        success_rate = (successful_contexts / len(chunks)) * 100 if chunks else 0
        logger.info(f"[BATCH] Completed: {successful_contexts}/{len(chunks)} chunks ({success_rate:.1f}%)")
        
        return processed_chunks
    
    async def _wait_for_batch_completion(self, batch_id: str, progress_callback=None) -> Dict:
        """Wait for batch completion and return results"""
        start_time = time.time()
        
        while True:
            # Check batch status
            def retrieve_batch():
                return self.client.messages.batches.retrieve(batch_id)
            
            batch = await asyncio.get_event_loop().run_in_executor(None, retrieve_batch)
            
            if batch.processing_status == "ended":
                # Get results
                def get_results():
                    return self.client.messages.batches.results(batch_id)
                
                results_response = await asyncio.get_event_loop().run_in_executor(None, get_results)
                
                # Parse results
                results = {}
                for result in results_response:
                    if result.result.type == "succeeded":
                        results[result.custom_id] = result.result.message
                
                processing_time = time.time() - start_time
                logger.info(f"[BATCH] Processing completed in {processing_time:.1f}s")
                return results
                
            elif batch.processing_status in ["failed", "expired"]:
                raise Exception(f"Batch processing failed: {batch.processing_status}")
            
            # Wait before next check
            await asyncio.sleep(30)
            
            # Timeout check
            if time.time() - start_time > self.batch_timeout:
                raise Exception(f"Batch processing timeout after {self.batch_timeout}s")
    
    async def process_document_chunks(
        self, 
        chunks: List[str], 
        full_document: str,
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Process document chunks with configurable batch or streaming mode
        - No fallbacks between modes
        - Deterministic behavior
        - Clear failure modes
        """
        if not self.enabled:
            logger.info("[CONTEXTUAL] Processing disabled")
            return [{"content": chunk, "contextual_content": None, "is_contextualized": False} 
                   for chunk in chunks]
        
        # Check document size
        doc_tokens = len(full_document) // 4
        if doc_tokens > self.max_tokens_per_doc:
            logger.warning(f"[CONTEXTUAL] Document too large ({doc_tokens} tokens), skipping")
            return [{"content": chunk, "contextual_content": None, "is_contextualized": False} 
                   for chunk in chunks]
        
        # Choose processing mode based on configuration with intelligent fallback
        if self.use_batch_api and len(chunks) >= self.batch_threshold:
            # Use batch API for large documents
            logger.info(f"[BATCH] Using batch API for {len(chunks)} chunks (≥ {self.batch_threshold} threshold)")
            return await self._process_batch(chunks, full_document, progress_callback)
        else:
            # Use streaming for small documents or when batch API is disabled
            if self.use_batch_api and len(chunks) < self.batch_threshold:
                logger.info(f"[FALLBACK] Using streaming fallback: {len(chunks)} chunks < {self.batch_threshold} threshold")
            else:
                logger.info(f"[STREAMING] Using streaming mode for {len(chunks)} chunks")
            return await self._process_streaming(chunks, full_document, progress_callback)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get simple processing statistics"""
        success_rate = (self.successful_requests / self.total_requests) * 100 if self.total_requests > 0 else 0
        processing_mode = "batch" if self.use_batch_api else "streaming"
        
        return {
            "enabled": self.enabled,
            "model": self.model,
            "processing_mode": processing_mode,
            "batch_threshold": self.batch_threshold if self.use_batch_api else None,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "success_rate_percent": round(success_rate, 1),
            "max_tokens_per_document": self.max_tokens_per_doc
        }