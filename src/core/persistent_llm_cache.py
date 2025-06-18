"""
Persistent LLM Cache System
Implements Redis-based caching for LLM responses with TTL and memory management.
"""

import asyncio
import json
import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import pickle
import os

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class PersistentLLMCache:
    """Redis-based persistent cache for LLM responses"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        perf_config = config.get('performance_optimization', {})
        
        # Cache configuration
        self.ttl_seconds = perf_config.get('cache_ttl_days', 7) * 86400
        self.max_memory_mb = perf_config.get('max_memory_cache_mb', 512)
        self.enable_compression = perf_config.get('enable_result_compression', True)
        
        # Redis configuration
        redis_url = perf_config.get('redis_url', 'redis://localhost:6379/1')
        self.redis_client = None
        self.fallback_cache = {}  # In-memory fallback
        
        # Initialize Redis if available
        if REDIS_AVAILABLE and perf_config.get('enable_persistent_cache', True):
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=False)
                logger.info(f"Initialized Redis cache at {redis_url}")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis: {e}. Using in-memory fallback.")
        else:
            logger.info("Redis not available or disabled. Using in-memory cache.")
    
    def _generate_cache_key(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate a consistent cache key for the prompt"""
        cache_content = f"{prompt}_{max_tokens or 'default'}"
        return f"llm_cache:{hashlib.sha256(cache_content.encode()).hexdigest()}"
    
    def _compress_data(self, data: str) -> bytes:
        """Compress data if compression is enabled"""
        if self.enable_compression:
            import gzip
            return gzip.compress(data.encode('utf-8'))
        return data.encode('utf-8')
    
    def _decompress_data(self, data: bytes) -> str:
        """Decompress data if compression was used"""
        if self.enable_compression:
            import gzip
            try:
                return gzip.decompress(data).decode('utf-8')
            except:
                # Fallback for uncompressed data
                return data.decode('utf-8')
        return data.decode('utf-8')
    
    async def get_cached_response(self, prompt: str, max_tokens: Optional[int] = None) -> Optional[str]:
        """Retrieve cached LLM response"""
        cache_key = self._generate_cache_key(prompt, max_tokens)
        
        try:
            # Try Redis first
            if self.redis_client:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    response = self._decompress_data(cached_data)
                    logger.debug(f"Redis cache hit for key: {cache_key[:16]}...")
                    return response
            
            # Fallback to in-memory cache
            if cache_key in self.fallback_cache:
                cache_entry = self.fallback_cache[cache_key]
                if cache_entry['expires'] > datetime.now():
                    logger.debug(f"Memory cache hit for key: {cache_key[:16]}...")
                    return cache_entry['data']
                else:
                    # Expired entry
                    del self.fallback_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
            return None
    
    async def cache_response(self, prompt: str, response: str, max_tokens: Optional[int] = None):
        """Cache LLM response with TTL"""
        cache_key = self._generate_cache_key(prompt, max_tokens)
        
        try:
            # Cache in Redis
            if self.redis_client:
                compressed_data = self._compress_data(response)
                await self.redis_client.setex(cache_key, self.ttl_seconds, compressed_data)
                logger.debug(f"Cached response in Redis: {cache_key[:16]}...")
            
            # Also cache in memory as fallback
            self.fallback_cache[cache_key] = {
                'data': response,
                'expires': datetime.now() + timedelta(seconds=self.ttl_seconds)
            }
            
            # Manage memory cache size
            await self._manage_memory_cache()
            
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
    
    async def _manage_memory_cache(self):
        """Manage in-memory cache size using LRU eviction"""
        import sys
        
        # Estimate memory usage (rough approximation)
        cache_size_mb = sys.getsizeof(self.fallback_cache) / (1024 * 1024)
        
        if cache_size_mb > self.max_memory_mb:
            # Remove expired entries first
            now = datetime.now()
            expired_keys = [
                key for key, entry in self.fallback_cache.items()
                if entry['expires'] <= now
            ]
            
            for key in expired_keys:
                del self.fallback_cache[key]
            
            # If still over limit, remove oldest entries
            if len(self.fallback_cache) > 1000:  # Arbitrary limit
                # Sort by expiration time and remove oldest
                sorted_items = sorted(
                    self.fallback_cache.items(),
                    key=lambda x: x[1]['expires']
                )
                
                # Remove oldest 20%
                remove_count = len(sorted_items) // 5
                for key, _ in sorted_items[:remove_count]:
                    del self.fallback_cache[key]
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        stats = {
            'memory_cache_size': len(self.fallback_cache),
            'redis_available': self.redis_client is not None,
            'compression_enabled': self.enable_compression,
            'ttl_days': self.ttl_seconds / 86400
        }
        
        if self.redis_client:
            try:
                info = await self.redis_client.info('memory')
                stats['redis_memory_usage'] = info.get('used_memory_human', 'unknown')
                stats['redis_keys'] = await self.redis_client.dbsize()
            except Exception as e:
                logger.warning(f"Failed to get Redis stats: {e}")
        
        return stats
    
    async def clear_cache(self, pattern: str = None):
        """Clear cache entries, optionally by pattern"""
        try:
            if self.redis_client:
                if pattern:
                    keys = await self.redis_client.keys(f"llm_cache:*{pattern}*")
                    if keys:
                        await self.redis_client.delete(*keys)
                else:
                    await self.redis_client.flushdb()
            
            # Clear memory cache
            if pattern:
                keys_to_remove = [
                    key for key in self.fallback_cache.keys()
                    if pattern in key
                ]
                for key in keys_to_remove:
                    del self.fallback_cache[key]
            else:
                self.fallback_cache.clear()
                
            logger.info(f"Cleared cache (pattern: {pattern or 'all'})")
            
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close() 