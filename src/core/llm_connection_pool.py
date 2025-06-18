"""
LLM Connection Pool System
Implements connection pooling for LLM providers to improve performance and resource management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import time
from dataclasses import dataclass
from src.core.llm_factory import LLMFactory

logger = logging.getLogger(__name__)

@dataclass
class ConnectionMetrics:
    """Metrics for connection pool performance"""
    total_requests: int = 0
    active_connections: int = 0
    pool_hits: int = 0
    pool_misses: int = 0
    avg_response_time: float = 0.0
    error_count: int = 0
    last_reset: datetime = None

class LLMConnection:
    """Wrapper for individual LLM connections with health tracking"""
    
    def __init__(self, connection_id: str, llm_instance, max_requests: int = 1000):
        self.connection_id = connection_id
        self.llm = llm_instance
        self.max_requests = max_requests
        self.request_count = 0
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        self.is_healthy = True
        self.error_count = 0
        self.total_response_time = 0.0
        
    async def execute_request(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Execute a request through this connection"""
        start_time = time.time()
        
        try:
            self.last_used = datetime.now()
            response = await self.llm.ainvoke(prompt)
            
            # Track performance
            response_time = time.time() - start_time
            self.total_response_time += response_time
            self.request_count += 1
            
            # Check if connection should be recycled
            if self.request_count >= self.max_requests:
                self.is_healthy = False
                logger.debug(f"Connection {self.connection_id} marked for recycling (max requests reached)")
            
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            self.error_count += 1
            if self.error_count > 5:  # Mark unhealthy after 5 errors
                self.is_healthy = False
                logger.warning(f"Connection {self.connection_id} marked unhealthy due to errors")
            raise e
    
    @property
    def avg_response_time(self) -> float:
        """Calculate average response time for this connection"""
        if self.request_count == 0:
            return 0.0
        return self.total_response_time / self.request_count
    
    @property
    def age_minutes(self) -> float:
        """Get connection age in minutes"""
        return (datetime.now() - self.created_at).total_seconds() / 60
    
    async def close(self):
        """Close the connection"""
        try:
            if hasattr(self.llm, 'cleanup'):
                await self.llm.cleanup()
            elif hasattr(self.llm, 'close'):
                await self.llm.close()
        except Exception as e:
            logger.debug(f"Connection cleanup warning: {e}")

class LLMConnectionPool:
    """Connection pool for LLM instances with health monitoring and auto-scaling"""
    
    def __init__(self, provider: str, config: Dict[str, Any]):
        self.provider = provider
        self.config = config
        
        # Pool configuration
        perf_config = config.get('performance_optimization', {})
        self.min_connections = max(1, perf_config.get('llm_connection_pool_size', 15) // 3)
        self.max_connections = perf_config.get('llm_connection_pool_size', 15)
        self.max_requests_per_connection = perf_config.get('max_requests_per_connection', 1000)
        self.connection_timeout = perf_config.get('connection_timeout_seconds', 30)
        self.health_check_interval = perf_config.get('health_check_interval_seconds', 60)
        
        # Pool state
        self.available_connections: asyncio.Queue = asyncio.Queue(maxsize=self.max_connections)
        self.all_connections: Dict[str, LLMConnection] = {}
        self.metrics = ConnectionMetrics(last_reset=datetime.now())
        self.is_initialized = False
        self._lock = asyncio.Lock()
        
        # Health monitoring
        self._health_check_task = None
        
    async def initialize(self):
        """Initialize the connection pool with minimum connections"""
        if self.is_initialized:
            return
            
        async with self._lock:
            if self.is_initialized:
                return
                
            logger.info(f"Initializing LLM connection pool for {self.provider}")
            
            # Create minimum connections
            for i in range(self.min_connections):
                try:
                    connection = await self._create_connection(f"init_{i}")
                    await self.available_connections.put(connection)
                    logger.debug(f"Created initial connection {connection.connection_id}")
                except Exception as e:
                    logger.error(f"Failed to create initial connection {i}: {e}")
            
            # Start health monitoring
            self._health_check_task = asyncio.create_task(self._health_monitor())
            self.is_initialized = True
            
            logger.info(f"Connection pool initialized with {len(self.all_connections)} connections")
    
    async def _create_connection(self, connection_id: str) -> LLMConnection:
        """Create a new LLM connection"""
        try:
            llm_instance = LLMFactory.create_llm(self.provider, self.config)
            connection = LLMConnection(
                connection_id=connection_id,
                llm_instance=llm_instance,
                max_requests=self.max_requests_per_connection
            )
            self.all_connections[connection_id] = connection
            return connection
        except Exception as e:
            logger.error(f"Failed to create connection {connection_id}: {e}")
            raise
    
    async def get_connection(self) -> LLMConnection:
        """Get a connection from the pool"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Try to get from available pool with timeout
            connection = await asyncio.wait_for(
                self.available_connections.get(),
                timeout=self.connection_timeout
            )
            
            # Check if connection is still healthy
            if not connection.is_healthy:
                # Remove unhealthy connection and create new one
                await self._remove_connection(connection)
                return await self._get_or_create_connection()
            
            self.metrics.pool_hits += 1
            self.metrics.active_connections += 1
            return connection
            
        except asyncio.TimeoutError:
            # Pool is empty, try to create new connection if under limit
            self.metrics.pool_misses += 1
            return await self._get_or_create_connection()
    
    async def _get_or_create_connection(self) -> LLMConnection:
        """Get connection or create new one if under limit"""
        if len(self.all_connections) < self.max_connections:
            # Create new connection
            connection_id = f"dynamic_{len(self.all_connections)}_{int(time.time())}"
            connection = await self._create_connection(connection_id)
            self.metrics.active_connections += 1
            logger.debug(f"Created new connection {connection_id} (pool size: {len(self.all_connections)})")
            return connection
        else:
            # Wait for connection to become available
            logger.warning("Connection pool at maximum capacity, waiting for available connection")
            connection = await self.available_connections.get()
            self.metrics.active_connections += 1
            return connection
    
    async def return_connection(self, connection: LLMConnection):
        """Return a connection to the pool"""
        try:
            self.metrics.active_connections = max(0, self.metrics.active_connections - 1)
            
            if connection.is_healthy and connection.connection_id in self.all_connections:
                # Return healthy connection to pool
                await self.available_connections.put(connection)
            else:
                # Remove unhealthy connection
                await self._remove_connection(connection)
                
                # Maintain minimum pool size
                if len(self.all_connections) < self.min_connections:
                    try:
                        new_connection = await self._create_connection(
                            f"replacement_{int(time.time())}"
                        )
                        await self.available_connections.put(new_connection)
                    except Exception as e:
                        logger.error(f"Failed to create replacement connection: {e}")
                        
        except Exception as e:
            logger.error(f"Error returning connection to pool: {e}")
    
    async def _remove_connection(self, connection: LLMConnection):
        """Remove a connection from the pool"""
        try:
            if connection.connection_id in self.all_connections:
                del self.all_connections[connection.connection_id]
            await connection.close()
            logger.debug(f"Removed connection {connection.connection_id}")
        except Exception as e:
            logger.error(f"Error removing connection {connection.connection_id}: {e}")
    
    async def execute_request(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Execute a request using a pooled connection"""
        start_time = time.time()
        connection = None
        
        try:
            connection = await self.get_connection()
            response = await connection.execute_request(prompt, max_tokens)
            
            # Update metrics
            response_time = time.time() - start_time
            self.metrics.total_requests += 1
            self.metrics.avg_response_time = (
                (self.metrics.avg_response_time * (self.metrics.total_requests - 1) + response_time) /
                self.metrics.total_requests
            )
            
            return response
            
        except Exception as e:
            self.metrics.error_count += 1
            logger.error(f"Request execution failed: {e}")
            raise
        finally:
            if connection:
                await self.return_connection(connection)
    
    async def _health_monitor(self):
        """Background task to monitor connection health"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                # Check for stale connections
                now = datetime.now()
                stale_connections = []
                
                for conn_id, connection in self.all_connections.items():
                    # Mark connections as stale if unused for too long
                    if (now - connection.last_used).total_seconds() > 300:  # 5 minutes
                        stale_connections.append(connection)
                
                # Remove stale connections
                for connection in stale_connections:
                    if len(self.all_connections) > self.min_connections:
                        await self._remove_connection(connection)
                
                # Log pool status
                logger.debug(f"Pool health check - Active: {self.metrics.active_connections}, "
                           f"Total: {len(self.all_connections)}, Available: {self.available_connections.qsize()}")
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            'total_connections': len(self.all_connections),
            'available_connections': self.available_connections.qsize(),
            'active_connections': self.metrics.active_connections,
            'total_requests': self.metrics.total_requests,
            'pool_hit_rate': (
                self.metrics.pool_hits / (self.metrics.pool_hits + self.metrics.pool_misses)
                if (self.metrics.pool_hits + self.metrics.pool_misses) > 0 else 0
            ),
            'avg_response_time': self.metrics.avg_response_time,
            'error_rate': (
                self.metrics.error_count / self.metrics.total_requests
                if self.metrics.total_requests > 0 else 0
            ),
            'uptime_minutes': (datetime.now() - self.metrics.last_reset).total_seconds() / 60
        }
    
    async def close(self):
        """Close all connections and cleanup"""
        logger.info("Closing LLM connection pool")
        
        # Stop health monitoring
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        close_tasks = []
        for connection in self.all_connections.values():
            close_tasks.append(connection.close())
        
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
        
        self.all_connections.clear()
        
        # Clear the queue
        while not self.available_connections.empty():
            try:
                self.available_connections.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        logger.info("Connection pool closed") 