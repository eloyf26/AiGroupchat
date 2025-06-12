#!/usr/bin/env python3
"""
Test script for Official Anthropic Contextual Retrieval implementation
Validates alignment with official Anthropic documentation and methodology
"""

import os
import sys
import asyncio
import logging
import tempfile
from typing import Dict, Any
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from document_store import DocumentStore
from contextual_processor import ContextualProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("official_contextual_test")

load_dotenv()


class OfficialContextualRetrievalTester:
    """Test suite for official Anthropic contextual retrieval implementation"""
    
    def __init__(self):
        self.document_store = DocumentStore()
        self.contextual_processor = ContextualProcessor()
        self.test_owner_id = "test_user_official_contextual"
    
    async def test_official_api_implementation(self) -> bool:
        """Test that we're using the official Anthropic API correctly"""
        logger.info("🧪 Testing Official Anthropic API Implementation...")
        
        # Check model configuration
        if "haiku" not in self.contextual_processor.model.lower():
            logger.warning(f"⚠️  Expected Haiku model, got: {self.contextual_processor.model}")
            logger.warning("   Haiku is recommended for cost optimization")
        else:
            logger.info(f"✅ Using recommended model: {self.contextual_processor.model}")
        
        # Check beta API configuration
        if hasattr(self.contextual_processor, 'beta_version'):
            logger.info(f"✅ Beta API version configured: {self.contextual_processor.beta_version}")
        else:
            logger.error("❌ Beta API version not configured")
            return False
        
        # Test prompt format with official example
        test_document = """The Chronicles of Luminara is a fantasy epic set in a mystical realm where magic flows through starlight and ancient prophecies guide the fate of kingdoms. The story follows young heroes as they discover their destinies and face an encroaching darkness that threatens to consume their world."""
        
        test_chunk = "Young Aldric discovered he possessed the rare gift of wielding starlight magic during the Festival of Celestial Alignment."
        
        try:
            # Test prompt building (should match official format)
            messages = self.contextual_processor._build_contextual_prompt(test_chunk, test_document)
            
            # Validate prompt structure
            if len(messages) != 1:
                logger.error(f"❌ Expected 1 message, got {len(messages)}")
                return False
            
            message = messages[0]
            if message["role"] != "user":
                logger.error(f"❌ Expected user role, got {message['role']}")
                return False
            
            content = message["content"]
            if len(content) != 2:
                logger.error(f"❌ Expected 2 content parts, got {len(content)}")
                return False
            
            # Check document part has cache control
            doc_part = content[0]
            if "cache_control" not in doc_part:
                logger.error("❌ Document part missing cache_control")
                return False
            
            # Check prompt format matches official
            chunk_part = content[1]
            chunk_text = chunk_part["text"]
            
            if "Here is the chunk we want to situate within the whole document" not in chunk_text:
                logger.error("❌ Prompt doesn't match official Anthropic format")
                logger.error(f"   Got: {chunk_text[:100]}...")
                return False
            
            logger.info("✅ Prompt format matches official Anthropic specification")
            
            # Test actual API call
            context = await self.contextual_processor.generate_chunk_context(
                test_chunk, test_document, "The Chronicles of Luminara"
            )
            
            if context:
                logger.info(f"✅ API call successful. Context: {context}")
                
                # Validate context quality (should be succinct)
                if len(context) > 200:
                    logger.warning(f"⚠️  Context may be too verbose ({len(context)} chars)")
                    logger.warning("   Anthropic recommends 'short succinct context'")
                
                return True
            else:
                logger.error("❌ API call failed to generate context")
                return False
                
        except Exception as e:
            logger.error(f"❌ Official API test failed: {e}")
            return False
    
    async def test_token_tracking_and_caching(self) -> bool:
        """Test token usage tracking and cache effectiveness"""
        logger.info("🧪 Testing Token Tracking and Cache Metrics...")
        
        # Reset token counts
        self.contextual_processor.token_counts = {
            'input': 0, 'output': 0, 'cache_read': 0, 'cache_creation': 0
        }
        
        test_document = """The Chronicles of Luminara: A Fantasy Adventure
        
        In the mystical realm of Luminara, magic flows through starlight and ancient prophecies guide destiny. The kingdom faces an unprecedented threat as dark forces gather, seeking to corrupt the Crystal of Eternal Light and plunge the world into everlasting shadow.
        
        Young heroes must rise to fulfill ancient prophecies, wielding powers they never knew they possessed. The fate of all Luminara hangs in the balance as the final battle between light and darkness approaches."""
        
        test_chunks = [
            "In the mystical realm of Luminara, magic flows through starlight and ancient prophecies guide destiny.",
            "The kingdom faces an unprecedented threat as dark forces gather, seeking to corrupt the Crystal of Eternal Light.",
            "Young heroes must rise to fulfill ancient prophecies, wielding powers they never knew they possessed."
        ]
        
        try:
            # Process multiple chunks to test caching
            for i, chunk in enumerate(test_chunks):
                logger.info(f"Processing chunk {i+1}/3...")
                context = await self.contextual_processor.generate_chunk_context(
                    chunk, test_document, "The Chronicles of Luminara"
                )
                
                if context:
                    logger.info(f"✅ Chunk {i+1} processed: {context[:50]}...")
                else:
                    logger.warning(f"⚠️  Chunk {i+1} failed")
            
            # Check token usage
            stats = self.contextual_processor.get_processing_stats()
            token_usage = stats["token_usage"]
            cache_metrics = stats["cache_metrics"]
            
            logger.info("📊 Token Usage:")
            logger.info(f"   Input tokens: {token_usage['input']}")
            logger.info(f"   Output tokens: {token_usage['output']}")
            logger.info(f"   Cache reads: {token_usage['cache_read']}")
            logger.info(f"   Cache creations: {token_usage['cache_creation']}")
            
            logger.info("💰 Cache Metrics:")
            logger.info(f"   Hit rate: {cache_metrics['hit_rate']:.2%}")
            logger.info(f"   Cost savings: {cache_metrics['estimated_cost_savings_percent']:.1f}%")
            
            # Validate cache effectiveness
            if cache_metrics['hit_rate'] > 0:
                logger.info("✅ Prompt caching is working effectively!")
                return True
            elif token_usage['cache_creation'] > 0:
                logger.info("✅ Cache creation detected - caching should work on subsequent calls")
                return True
            else:
                logger.warning("⚠️  No cache activity detected - check beta API configuration")
                return False
                
        except Exception as e:
            logger.error(f"❌ Token tracking test failed: {e}")
            return False
    
    async def test_chunk_size_optimization(self) -> bool:
        """Test that we're using the recommended 800-token chunks"""
        logger.info("🧪 Testing Chunk Size Configuration...")
        
        # Check text splitter configuration
        chunk_size = self.document_store.text_splitter.chunk_size
        chunk_overlap = self.document_store.text_splitter.chunk_overlap
        
        if chunk_size == 800:
            logger.info(f"✅ Using recommended chunk size: {chunk_size} tokens")
        else:
            logger.warning(f"⚠️  Expected 800 tokens, got {chunk_size}")
            logger.warning("   Anthropic recommends 800-token chunks for optimal results")
        
        if chunk_overlap == 80:
            logger.info(f"✅ Using optimal chunk overlap: {chunk_overlap} tokens (10%)")
        else:
            logger.info(f"ℹ️  Chunk overlap: {chunk_overlap} tokens")
        
        return chunk_size == 800
    
    async def test_cost_efficiency(self) -> bool:
        """Test cost efficiency compared to non-cached implementation"""
        logger.info("🧪 Testing Cost Efficiency...")
        
        # Create a moderate-sized document for testing
        test_content = """
        Luminara Chronicles: The Complete Guide
        
        """ + "The mystical realm of Luminara stands as one of the most fascinating fantasy worlds ever created. " * 100
        
        try:
            # Process with contextual enhancement
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write(test_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Reset metrics
                self.contextual_processor.token_counts = {
                    'input': 0, 'output': 0, 'cache_read': 0, 'cache_creation': 0
                }
                
                # Process the document
                document_id = await self.document_store.process_file(
                    file_path=tmp_file_path,
                    file_type="text",
                    owner_id=self.test_owner_id,
                    title="Cost Efficiency Test Document"
                )
                
                # Get final metrics
                stats = self.contextual_processor.get_processing_stats()
                cache_metrics = stats["cache_metrics"]
                
                logger.info("💰 Cost Analysis:")
                logger.info(f"   Estimated cost savings: {cache_metrics['estimated_cost_savings_percent']:.1f}%")
                logger.info(f"   Cache hit rate: {cache_metrics['hit_rate']:.2%}")
                
                expected_savings = 70  # Expected with Haiku + caching
                if cache_metrics['estimated_cost_savings_percent'] >= expected_savings:
                    logger.info(f"✅ Achieving excellent cost efficiency (≥{expected_savings}%)")
                    result = True
                else:
                    logger.warning(f"⚠️  Cost savings below target ({expected_savings}%)")
                    result = False
                
                # Clean up
                await self.document_store.delete_document(document_id, self.test_owner_id)
                return result
                
            finally:
                os.unlink(tmp_file_path)
                
        except Exception as e:
            logger.error(f"❌ Cost efficiency test failed: {e}")
            return False
    
    async def test_retrieval_accuracy(self) -> bool:
        """Test that contextual retrieval improves search accuracy"""
        logger.info("🧪 Testing Retrieval Accuracy Improvement...")
        
        # Create test document with clear contextual relationships
        test_content = """
        The Luminara Magic System
        
        Chapter 1: Starlight Magic
        Starlight magic is the primary magical system in Luminara. Practitioners channel energy from celestial bodies to cast spells. The power varies based on moon phases and stellar alignments.
        
        Chapter 2: Shadow Magic  
        Shadow magic represents the dark counterpart to starlight magic. Used by the Shadow Lord and his followers, it corrupts natural magic and feeds on negative emotions.
        
        Chapter 3: Crystal Magic
        Crystal magic involves the use of magical crystals found throughout Luminara. The Crystal of Eternal Light is the most powerful, serving as the source of all magic in the realm.
        """
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write(test_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Process document
                document_id = await self.document_store.process_file(
                    file_path=tmp_file_path,
                    file_type="text",
                    owner_id=self.test_owner_id,
                    title="Magic System Guide"
                )
                
                # Test contextual search queries
                test_queries = [
                    "What is starlight magic?",
                    "Tell me about shadow magic",
                    "How do crystals work in magic?"
                ]
                
                all_relevant = True
                for query in test_queries:
                    results = await self.document_store.search_documents(
                        query=query,
                        owner_id=self.test_owner_id,
                        match_count=2
                    )
                    
                    if results:
                        top_result = results[0]
                        logger.info(f"Query: '{query}'")
                        logger.info(f"   Result: {top_result['content'][:100]}...")
                        logger.info(f"   Similarity: {top_result.get('similarity', 0):.3f}")
                        
                        # Check if result is contextually relevant
                        query_lower = query.lower()
                        result_lower = top_result['content'].lower()
                        
                        is_relevant = any(keyword in result_lower for keyword in 
                                        ['starlight', 'shadow', 'crystal'] if keyword in query_lower)
                        
                        if is_relevant:
                            logger.info("   ✅ Contextually relevant result")
                        else:
                            logger.warning("   ⚠️  Result may not be contextually optimal")
                            all_relevant = False
                    else:
                        logger.warning(f"   ⚠️  No results for query: {query}")
                        all_relevant = False
                
                # Clean up
                await self.document_store.delete_document(document_id, self.test_owner_id)
                
                if all_relevant:
                    logger.info("✅ Contextual retrieval showing good accuracy")
                    return True
                else:
                    logger.warning("⚠️  Some queries didn't return optimal results")
                    return False
                
            finally:
                os.unlink(tmp_file_path)
                
        except Exception as e:
            logger.error(f"❌ Retrieval accuracy test failed: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all official implementation tests"""
        logger.info("🚀 Starting Official Anthropic Contextual Retrieval Test Suite")
        logger.info("=" * 70)
        
        if not self.contextual_processor.enabled:
            logger.error("❌ Contextual processing is disabled")
            return {"all_tests": False, "error": "Contextual processing disabled"}
        
        tests = {
            "official_api_implementation": await self.test_official_api_implementation(),
            "token_tracking_and_caching": await self.test_token_tracking_and_caching(),
            "chunk_size_optimization": await self.test_chunk_size_optimization(),
            "cost_efficiency": await self.test_cost_efficiency(),
            "retrieval_accuracy": await self.test_retrieval_accuracy()
        }
        
        # Summary
        passed = sum(tests.values())
        total = len(tests)
        
        logger.info("=" * 70)
        logger.info(f"🏁 Official Implementation Test Results: {passed}/{total} tests passed")
        logger.info("=" * 70)
        
        for test_name, result in tests.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        # Final assessment
        if passed == total:
            logger.info("🎉 EXCELLENT: Full compliance with official Anthropic implementation!")
        elif passed >= total * 0.8:
            logger.info("✅ GOOD: Mostly compliant with official implementation")
        elif passed >= total * 0.6:
            logger.warning("⚠️  NEEDS IMPROVEMENT: Partial compliance with official implementation")
        else:
            logger.error("❌ POOR: Significant deviations from official implementation")
        
        tests["all_tests"] = passed >= total * 0.8  # 80% pass rate considered successful
        
        # Show final stats
        final_stats = self.contextual_processor.get_processing_stats()
        logger.info("\n📊 Final Processing Statistics:")
        logger.info(f"   Model: {final_stats['model']}")
        logger.info(f"   Cache hit rate: {final_stats['cache_metrics']['hit_rate']:.2%}")
        logger.info(f"   Estimated cost savings: {final_stats['cache_metrics']['estimated_cost_savings_percent']:.1f}%")
        
        return tests


async def main():
    """Main test function"""
    tester = OfficialContextualRetrievalTester()
    
    try:
        results = tester.run_all_tests()
        
        if results["all_tests"]:
            logger.info("🎉 Official Anthropic Contextual Retrieval implementation is working correctly!")
            sys.exit(0)
        else:
            logger.error("💥 Implementation needs fixes to match official Anthropic specification")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())