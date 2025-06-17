"""
Focused LLM Generator
Simple wrapper for LLM calls in the focused prompt processor.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from src.core.llm_factory import LLMFactory
from src.utils.grpc_cleanup import register_grpc_cleanup

logger = logging.getLogger(__name__)

class FocusedLLMGenerator:
    """Simple LLM generator for focused prompts"""
    
    def __init__(self, provider: str, config: Dict[str, Any]):
        self.provider = provider
        self.config = config
        self.llm = LLMFactory.create_llm(provider, config)
        self._session = None
        
        # Register cleanup for gRPC resources
        register_grpc_cleanup(self.cleanup)
        
    async def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate a response from the LLM"""
        try:
            # Use the LLM to generate response
            response = await self.llm.ainvoke(prompt)
            
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return ""
    
    async def cleanup(self):
        """Cleanup resources to prevent gRPC warnings"""
        try:
            # Give time for any pending requests to complete
            await asyncio.sleep(0.1)
            
            # If the LLM has cleanup methods, call them
            if hasattr(self.llm, 'cleanup'):
                await self.llm.cleanup()
            elif hasattr(self.llm, 'close'):
                await self.llm.close()
                
        except Exception as e:
            logger.debug(f"Cleanup warning (non-critical): {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            # Try to cleanup synchronously if possible
            if hasattr(self.llm, 'cleanup'):
                try:
                    asyncio.create_task(self.cleanup())
                except RuntimeError:
                    # Event loop might be closed, ignore
                    pass
        except Exception:
            # Ignore cleanup errors in destructor
            pass 