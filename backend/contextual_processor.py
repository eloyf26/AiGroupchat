"""
Contextual Processor for RAG Enhancement
Implements Anthropic's Contextual Retrieval method with prompt caching optimization
"""

import os
import time
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

import anthropic
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ContextualProcessor:
    """
    Handles contextual enhancement of document chunks using Claude with prompt caching
    """
    
    def __init__(self):
        """Initialize the contextual processor with Anthropic client"""
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        
        # Configuration from environment
        self.enabled = os.environ.get("ENABLE_CONTEXTUAL_RETRIEVAL", "true").lower() == "true"
        self.model = os.environ.get("CONTEXTUAL_RETRIEVAL_MODEL", "claude-3-haiku-20240307")
        self.max_tokens_per_doc = int(os.environ.get("MAX_CONTEXTUAL_TOKENS_PER_DOCUMENT", "100000"))
        self.processing_timeout = int(os.environ.get("CONTEXTUAL_PROCESSING_TIMEOUT", "120"))
        self.max_daily_requests = int(os.environ.get("MAX_DAILY_CONTEXTUAL_REQUESTS", "1000"))
        
        # Token usage tracking (official Anthropic approach)
        self.token_counts = {
            'input': 0,
            'output': 0,
            'cache_read': 0,
            'cache_creation': 0
        }
        self._daily_request_count = 0
        self._last_reset_date = datetime.now().date()
        
        # Prompt caching configuration
        self.use_cache = True
        self.cache_ttl = int(os.environ.get("CONTEXTUAL_CACHE_TTL", "3600"))
        
        logger.info(f"🧠 [CONTEXTUAL] Initialized - Model: {self.model}, Enabled: {self.enabled}, Cache: {self.use_cache}")
    
    def _build_contextual_prompt(self, chunk: str, document: str) -> List[Dict[str, Any]]:
        """
        Build a prompt using the exact official Anthropic format with proper caching
        
        Args:
            chunk: The specific chunk to contextualize
            document: The full document content
            
        Returns:
            List of message objects with cache control (no system prompt needed)
        """
        # Document content (cacheable - this is the expensive part)
        document_message = {
            "type": "text", 
            "text": f"<document>\n{document}\n</document>",
            "cache_control": {"type": "ephemeral"}
        }
        
        # Chunk and request (exact Anthropic format - not cached)
        chunk_message = {
            "type": "text",
            "text": f"""Here is the chunk we want to situate within the whole document
<chunk>
{chunk}
</chunk>
Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else."""
        }
        
        return [
            {"role": "user", "content": [document_message, chunk_message]}
        ]
    
    async def generate_chunk_context(
        self, 
        chunk: str, 
        full_document: str,
        document_title: str = ""
    ) -> Optional[str]:
        """
        Generate contextual information for a single chunk
        
        Args:
            chunk: The chunk content to contextualize
            full_document: The complete document content
            document_title: Optional document title for better context
            
        Returns:
            Contextual description or None if failed
        """
        if not self.enabled:
            return None
        
        try:
            # Check daily limits
            if not self._check_rate_limits():
                logger.warning("[CONTEXTUAL] Daily rate limit exceeded")
                return None
            
            # Build prompt with caching (official Anthropic format)
            messages = self._build_contextual_prompt(chunk, full_document)
            
            # Make API call with timeout
            start_time = time.time()
            
            response = await asyncio.wait_for(
                self._make_claude_request(messages),
                timeout=self.processing_timeout
            )
            
            processing_time = time.time() - start_time
            
            # Extract context from response
            context = response.content[0].text.strip()
            
            # Validate context
            if self._validate_context(context, chunk):
                logger.debug(f"[CONTEXTUAL] Generated context in {processing_time:.2f}s: {context[:100]}...")
                self._daily_request_count += 1
                return context
            else:
                logger.warning(f"[CONTEXTUAL] Invalid context generated: {context[:100]}...")
                return None
                
        except asyncio.TimeoutError:
            logger.error(f"[CONTEXTUAL] Timeout after {self.processing_timeout}s")
            return None
        except anthropic.APIError as e:
            logger.error(f"[CONTEXTUAL] Anthropic API error: {e}")
            return None
        except Exception as e:
            logger.error(f"[CONTEXTUAL] Unexpected error: {e}")
            return None
    
    async def _make_claude_request(self, messages: List[Dict]) -> anthropic.types.Message:
        """Make the actual Claude API request using GA prompt caching"""
        def make_request():
            try:
                # Use the GA prompt caching API with token-efficient tools header
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,  # Official recommendation
                    temperature=0.0,  # Official recommendation for deterministic results
                    messages=messages,
                    extra_headers={
                        "anthropic-beta": "token-efficient-tools-2025-02-19"
                    }
                )
                
                # Track token usage (official Anthropic approach)
                if hasattr(response, 'usage'):
                    usage = response.usage
                    self.token_counts['input'] += getattr(usage, 'input_tokens', 0)
                    self.token_counts['output'] += getattr(usage, 'output_tokens', 0)
                    
                    # Track cache metrics if available
                    if hasattr(usage, 'cache_read_input_tokens'):
                        self.token_counts['cache_read'] += getattr(usage, 'cache_read_input_tokens', 0)
                    if hasattr(usage, 'cache_creation_input_tokens'):
                        self.token_counts['cache_creation'] += getattr(usage, 'cache_creation_input_tokens', 0)
                    
                    # Log cache effectiveness with more detail
                    cache_read = self.token_counts['cache_read']
                    cache_creation = self.token_counts['cache_creation']
                    total_input = self.token_counts['input']
                    current_input = getattr(usage, 'input_tokens', 0)
                    current_cache_read = getattr(usage, 'cache_read_input_tokens', 0)
                    
                    if total_input > 0:
                        cache_hit_rate = cache_read / (cache_read + cache_creation) if (cache_read + cache_creation) > 0 else 0
                        logger.info(f"[CACHE] Request tokens - Input: {current_input}, Cache Read: {current_cache_read}, Hit rate: {cache_hit_rate:.2%}")
                        
                        # Verify cache is working properly after first request
                        if self.token_counts['cache_creation'] > 0 and current_cache_read == 0:
                            logger.warning("[CACHE] Expected cache hit but got none - cache may not be working properly")
                
                return response
                
            except Exception as e:
                logger.error(f"[CONTEXTUAL] API error: {e}")
                raise
        
        return await asyncio.get_event_loop().run_in_executor(None, make_request)
    
    def _validate_context(self, context: str, chunk: str) -> bool:
        """
        Validate the generated context
        
        Args:
            context: Generated contextual description
            chunk: Original chunk content
            
        Returns:
            True if context is valid
        """
        if not context or len(context.strip()) < 10:
            return False
        
        # Check if context is too long (should be brief)
        if len(context) > 500:
            return False
        
        # Check if context is just repeating the chunk
        chunk_words = set(chunk.lower().split())
        context_words = set(context.lower().split())
        overlap_ratio = len(chunk_words.intersection(context_words)) / len(context_words) if context_words else 0
        
        if overlap_ratio > 0.8:  # Too much overlap
            return False
        
        return True
    
    def _check_rate_limits(self) -> bool:
        """Check if we're within daily rate limits"""
        current_date = datetime.now().date()
        
        # Reset counter if it's a new day
        if current_date != self._last_reset_date:
            self._daily_request_count = 0
            self._last_reset_date = current_date
        
        return self._daily_request_count < self.max_daily_requests
    
    async def process_document_chunks(
        self, 
        chunks: List[str], 
        full_document: str,
        document_title: str = "",
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Process multiple chunks for a document with contextual enhancement
        
        Args:
            chunks: List of document chunks
            full_document: Complete document content
            document_title: Document title for context
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of processed chunks with contextual information
        """
        if not self.enabled:
            logger.info("[CONTEXTUAL] Processing disabled, returning original chunks")
            return [{"content": chunk, "contextual_content": None, "is_contextualized": False} 
                   for chunk in chunks]
        
        # Check document size limits
        doc_tokens = self._estimate_tokens(full_document)
        if doc_tokens > self.max_tokens_per_doc:
            logger.warning(f"[CONTEXTUAL] Document too large ({doc_tokens} tokens), skipping contextualization")
            return [{"content": chunk, "contextual_content": None, "is_contextualized": False} 
                   for chunk in chunks]
        
        logger.info(f"[CONTEXTUAL] Processing {len(chunks)} chunks for document: {document_title[:50]}...")
        logger.info(f"[CONTEXTUAL] Using sequential processing with 1s delays to respect rate limits")
        
        processed_chunks = []
        successful_contexts = 0
        
        # Process chunks with concurrency control
        # Using semaphore=1 for sequential processing to respect Anthropic's concurrent request limits
        # and ensure proper cache creation on first request
        semaphore = asyncio.Semaphore(1)  # Sequential processing for rate limit compliance
        
        async def process_single_chunk(idx: int, chunk: str) -> Dict[str, Any]:
            async with semaphore:
                # Add delay between requests to avoid burst issues (except for first chunk)
                if idx > 0:
                    await asyncio.sleep(1.0)  # 1 second delay to stay well under rate limits
                
                context = await self.generate_chunk_context(chunk, full_document, document_title)
                
                if progress_callback:
                    progress_callback(idx + 1, len(chunks))
                
                return {
                    "content": chunk,
                    "contextual_content": context,
                    "is_contextualized": context is not None
                }
        
        # Process all chunks concurrently
        tasks = [process_single_chunk(idx, chunk) for idx, chunk in enumerate(chunks)]
        processed_chunks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        final_results = []
        for idx, result in enumerate(processed_chunks):
            if isinstance(result, Exception):
                logger.error(f"[CONTEXTUAL] Error processing chunk {idx}: {result}")
                final_results.append({
                    "content": chunks[idx],
                    "contextual_content": None,
                    "is_contextualized": False
                })
            else:
                final_results.append(result)
                if result["is_contextualized"]:
                    successful_contexts += 1
        
        success_rate = (successful_contexts / len(chunks)) * 100 if chunks else 0
        logger.info(f"[CONTEXTUAL] Completed: {successful_contexts}/{len(chunks)} chunks contextualized ({success_rate:.1f}%)")
        
        return final_results
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count"""
        # Anthropic uses ~4 characters per token on average
        return len(text) // 4
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics including cache metrics"""
        # Calculate cache efficiency
        cache_read = self.token_counts['cache_read']
        cache_creation = self.token_counts['cache_creation']
        total_cached = cache_read + cache_creation
        cache_hit_rate = cache_read / total_cached if total_cached > 0 else 0
        
        # Calculate cost savings (approximate)
        total_input = self.token_counts['input']
        if total_input > 0:
            # Cache reads are 90% cheaper than regular tokens
            cost_without_cache = total_input * 1.0  # Baseline cost
            cost_with_cache = (cache_creation * 1.25) + (cache_read * 0.1) + ((total_input - total_cached) * 1.0)
            cost_savings_percent = ((cost_without_cache - cost_with_cache) / cost_without_cache) * 100 if cost_without_cache > 0 else 0
        else:
            cost_savings_percent = 0
        
        return {
            "enabled": self.enabled,
            "model": self.model,
            "daily_requests_used": self._daily_request_count,
            "daily_requests_limit": self.max_daily_requests,
            "last_reset_date": self._last_reset_date.isoformat(),
            "max_tokens_per_document": self.max_tokens_per_doc,
            "token_usage": self.token_counts.copy(),
            "cache_metrics": {
                "hit_rate": round(cache_hit_rate, 4),
                "total_cached_tokens": total_cached,
                "cache_reads": cache_read,
                "cache_creations": cache_creation,
                "estimated_cost_savings_percent": round(cost_savings_percent, 2)
            }
        }