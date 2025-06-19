"""
Focused LLM Generator
Enhanced wrapper for LLM calls with connection pooling and persistent caching.
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional
from src.core.llm_factory import LLMFactory
from src.utils.grpc_cleanup import register_grpc_cleanup

# Import new performance optimizations
try:
    from src.core.persistent_llm_cache import PersistentLLMCache
    PERSISTENT_CACHE_AVAILABLE = True
except ImportError:
    PERSISTENT_CACHE_AVAILABLE = False

try:
    from src.core.llm_connection_pool import LLMConnectionPool
    CONNECTION_POOL_AVAILABLE = True
except ImportError:
    CONNECTION_POOL_AVAILABLE = False

logger = logging.getLogger(__name__)

class FocusedLLMGenerator:
    """Enhanced LLM generator with connection pooling and persistent caching"""
    
    def __init__(self, provider: str, config: Dict[str, Any]):
        self.provider = provider
        self.config = config
        
        # Performance optimization configuration
        perf_config = config.get('performance_optimization', {})
        use_connection_pool = perf_config.get('llm_connection_pool_size', 0) > 0
        use_persistent_cache = perf_config.get('enable_persistent_cache', False)
        
        # Initialize connection pool if available and enabled
        if CONNECTION_POOL_AVAILABLE and use_connection_pool:
            self.connection_pool = LLMConnectionPool(provider, config)
            self.use_connection_pool = True
            logger.info(f"Initialized LLM connection pool for {provider}")
        else:
            self.llm = LLMFactory.create_llm(provider, config)
            self.connection_pool = None
            self.use_connection_pool = False
            logger.info(f"Using direct LLM connection for {provider}")
        
        # Initialize persistent cache if available and enabled
        if PERSISTENT_CACHE_AVAILABLE and use_persistent_cache:
            self.persistent_cache = PersistentLLMCache(config)
            self.use_persistent_cache = True
            logger.info("Initialized persistent LLM cache")
        else:
            self.persistent_cache = None
            self.use_persistent_cache = False
        
        # Fallback to existing configuration
        legacy_config = config.get('performance', {})
        self.max_retries = (
            perf_config.get('max_llm_retries') or 
            legacy_config.get('max_llm_retries', 3)
        )
        self.base_delay = (
            perf_config.get('retry_base_delay') or 
            legacy_config.get('retry_base_delay', 1.0)
        )
        self.max_delay = (
            perf_config.get('retry_max_delay') or 
            legacy_config.get('retry_max_delay', 30.0)
        )
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_response_time': 0.0,
            'connection_pool_usage': 0,
            'error_count': 0
        }
        
        # Register cleanup for gRPC resources
        register_grpc_cleanup(self.cleanup)
        
    async def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate a response from the LLM with enhanced caching and pooling"""
        start_time = time.time()
        self.metrics['total_requests'] += 1
        
        try:
            # Check persistent cache first
            if self.use_persistent_cache:
                cached_response = await self.persistent_cache.get_cached_response(prompt, max_tokens)
                if cached_response:
                    self.metrics['cache_hits'] += 1
                    logger.debug("Persistent cache hit for LLM request")
                    return cached_response
                else:
                    self.metrics['cache_misses'] += 1
            
            # Generate response with retry logic
            response = await self._generate_with_retries(prompt, max_tokens)
            
            # Cache the response
            if self.use_persistent_cache and response:
                await self.persistent_cache.cache_response(prompt, response, max_tokens)
            
            # Update performance metrics
            response_time = time.time() - start_time
            self.metrics['avg_response_time'] = (
                (self.metrics['avg_response_time'] * (self.metrics['total_requests'] - 1) + response_time) /
                self.metrics['total_requests']
            )
            
            return response
            
        except Exception as e:
            self.metrics['error_count'] += 1
            logger.error(f"LLM generation failed: {e}")
            return ""
    
    async def _generate_with_retries(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate response with intelligent retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if self.use_connection_pool:
                    # Use connection pool
                    response = await self.connection_pool.execute_request(prompt, max_tokens)
                    self.metrics['connection_pool_usage'] += 1
                else:
                    # Use direct connection
                    response = await self.llm.ainvoke(prompt)
                    if hasattr(response, 'content'):
                        response = response.content
                    else:
                        response = str(response)
                
                return response
                    
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    # Calculate exponential backoff delay
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    
                    logger.warning(f"LLM call failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"LLM generation failed after {self.max_retries + 1} attempts: {e}")
        
        # If all retries failed, return empty string
        return ""
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        stats = {
            'llm_metrics': self.metrics.copy(),
            'cache_hit_rate': (
                self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses'])
                if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
            ),
            'error_rate': (
                self.metrics['error_count'] / self.metrics['total_requests']
                if self.metrics['total_requests'] > 0 else 0
            ),
            'features_enabled': {
                'connection_pool': self.use_connection_pool,
                'persistent_cache': self.use_persistent_cache
            }
        }
        
        # Add connection pool stats if available
        if self.use_connection_pool and self.connection_pool:
            try:
                pool_stats = await self.connection_pool.get_pool_stats()
                stats['connection_pool_stats'] = pool_stats
            except Exception as e:
                logger.warning(f"Failed to get connection pool stats: {e}")
        
        # Add cache stats if available
        if self.use_persistent_cache and self.persistent_cache:
            try:
                cache_stats = await self.persistent_cache.get_cache_stats()
                stats['persistent_cache_stats'] = cache_stats
            except Exception as e:
                logger.warning(f"Failed to get persistent cache stats: {e}")
        
        return stats
    
    async def cleanup(self):
        """Enhanced cleanup with connection pool and cache management"""
        try:
            # Give time for any pending requests to complete
            await asyncio.sleep(0.1)
            
            # Close connection pool
            if self.use_connection_pool and self.connection_pool:
                await self.connection_pool.close()
                logger.debug("Connection pool closed")
            
            # Close persistent cache
            if self.use_persistent_cache and self.persistent_cache:
                await self.persistent_cache.close()
                logger.debug("Persistent cache closed")
            
            # Cleanup direct LLM connection if used
            if not self.use_connection_pool and hasattr(self, 'llm'):
                if hasattr(self.llm, 'cleanup'):
                    await self.llm.cleanup()
                elif hasattr(self.llm, 'close'):
                    await self.llm.close()
                    
        except Exception as e:
            logger.debug(f"Cleanup warning (non-critical): {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            # Don't attempt async cleanup in destructor as it can cause warnings
            # The cleanup should be called explicitly before object destruction
                    pass
        except Exception:
            # Ignore cleanup errors in destructor
            pass 