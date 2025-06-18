"""
Async Database Manager
Implements async database operations with connection pooling and batch operations.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiosqlite
from contextlib import asynccontextmanager
import json

logger = logging.getLogger(__name__)

class AsyncDatabaseManager:
    """Async database manager with connection pooling and batch operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.database_path = config.get('database', {}).get('path', 'enhanced_destination_intelligence.db')
        
        # Pool configuration
        perf_config = config.get('performance_optimization', {})
        self.max_connections = perf_config.get('database_connection_pool_size', 20)
        self.connection_timeout = perf_config.get('database_timeout_seconds', 30)
        self.batch_size = perf_config.get('database_batch_size', 100)
        
        # Connection pool
        self.connection_pool = asyncio.Queue(maxsize=self.max_connections)
        self.pool_initialized = False
        self._lock = asyncio.Lock()
        
        # Performance metrics
        self.metrics = {
            'total_queries': 0,
            'batch_operations': 0,
            'avg_query_time': 0.0,
            'connection_pool_hits': 0,
            'connection_pool_misses': 0
        }
    
    async def initialize_pool(self):
        """Initialize the connection pool"""
        if self.pool_initialized:
            return
            
        async with self._lock:
            if self.pool_initialized:
                return
                
            logger.info(f"Initializing database connection pool with {self.max_connections} connections")
            
            # Create initial connections
            for i in range(self.max_connections):
                try:
                    connection = await aiosqlite.connect(
                        self.database_path,
                        timeout=self.connection_timeout
                    )
                    # Configure connection for better performance
                    await connection.execute("PRAGMA journal_mode=WAL")
                    await connection.execute("PRAGMA synchronous=NORMAL") 
                    await connection.execute("PRAGMA cache_size=10000")
                    await connection.execute("PRAGMA temp_store=MEMORY")
                    
                    await self.connection_pool.put(connection)
                except Exception as e:
                    logger.error(f"Failed to create database connection {i}: {e}")
            
            self.pool_initialized = True
            logger.info(f"Database connection pool initialized")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool"""
        if not self.pool_initialized:
            await self.initialize_pool()
        
        connection = None
        try:
            # Get connection from pool
            connection = await asyncio.wait_for(
                self.connection_pool.get(),
                timeout=self.connection_timeout
            )
            self.metrics['connection_pool_hits'] += 1
            yield connection
        except asyncio.TimeoutError:
            self.metrics['connection_pool_misses'] += 1
            # Create temporary connection if pool is exhausted
            connection = await aiosqlite.connect(self.database_path)
            logger.warning("Connection pool exhausted, created temporary connection")
            yield connection
        finally:
            if connection:
                try:
                    # Return connection to pool if it's from the pool
                    if self.connection_pool.qsize() < self.max_connections:
                        await self.connection_pool.put(connection)
                    else:
                        await connection.close()
                except Exception as e:
                    logger.error(f"Error returning connection to pool: {e}")
                    try:
                        await connection.close()
                    except:
                        pass
    
    async def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        import time
        start_time = time.time()
        
        try:
            async with self.get_connection() as conn:
                async with conn.execute(query, params or ()) as cursor:
                    columns = [description[0] for description in cursor.description] if cursor.description else []
                    rows = await cursor.fetchall()
                    
                    # Convert to list of dictionaries
                    results = [dict(zip(columns, row)) for row in rows]
                    
                    # Update metrics
                    query_time = time.time() - start_time
                    self.metrics['total_queries'] += 1
                    self.metrics['avg_query_time'] = (
                        (self.metrics['avg_query_time'] * (self.metrics['total_queries'] - 1) + query_time) /
                        self.metrics['total_queries']
                    )
                    
                    return results
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def batch_insert_affinities(self, affinities: List[Dict[str, Any]], destination: str):
        """Batch insert affinities with optimized performance"""
        if not affinities:
            return
        
        import time
        start_time = time.time()
        
        try:
            async with self.get_connection() as conn:
                # Prepare batch insert query
                insert_query = """
                    INSERT OR REPLACE INTO destination_affinities 
                    (destination_id, destination_name, category, theme, sub_themes, confidence, 
                     seasonality, traveler_types, price_point, rationale, unique_selling_points, 
                     authenticity_score, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                # Prepare data for batch insert
                batch_data = []
                now = datetime.now().isoformat()
                
                for affinity in affinities:
                    batch_data.append((
                        destination.lower().replace(' ', '_').replace(',', ''),
                        destination,
                        affinity.get('category', ''),
                        affinity.get('theme', ''),
                        json.dumps(affinity.get('sub_themes', [])),
                        affinity.get('confidence', 0.0),
                        json.dumps(affinity.get('seasonality', {})),
                        json.dumps(affinity.get('traveler_types', [])),
                        affinity.get('price_point', 'mid'),
                        affinity.get('rationale', ''),
                        json.dumps(affinity.get('unique_selling_points', [])),
                        affinity.get('authenticity_score', 0.8),
                        now,
                        now
                    ))
                
                # Execute batch insert
                await conn.executemany(insert_query, batch_data)
                await conn.commit()
                
                # Update metrics
                operation_time = time.time() - start_time
                self.metrics['batch_operations'] += 1
                
                logger.info(f"Batch inserted {len(affinities)} affinities for {destination} in {operation_time:.2f}s")
                
        except Exception as e:
            logger.error(f"Batch insert failed for {destination}: {e}")
            raise
    
    async def create_tables_if_not_exist(self):
        """Create database tables if they don't exist"""
        try:
            async with self.get_connection() as conn:
                # Create destination_affinities table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS destination_affinities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        destination_id TEXT NOT NULL,
                        destination_name TEXT NOT NULL,
                        category TEXT,
                        theme TEXT,
                        sub_themes TEXT,
                        confidence REAL,
                        seasonality TEXT,
                        traveler_types TEXT,
                        price_point TEXT,
                        rationale TEXT,
                        unique_selling_points TEXT,
                        authenticity_score REAL,
                        created_at TEXT,
                        updated_at TEXT,
                        UNIQUE(destination_id, category, theme)
                    )
                """)
                
                # Create indexes for better performance
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_destination_id 
                    ON destination_affinities(destination_id)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_category 
                    ON destination_affinities(category)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_confidence 
                    ON destination_affinities(confidence)
                """)
                
                await conn.commit()
                logger.info("Database tables created/verified successfully")
                
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise

    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database performance statistics"""
        stats_query = """
            SELECT 
                COUNT(*) as total_affinities,
                COUNT(DISTINCT destination_id) as unique_destinations,
                AVG(confidence) as avg_confidence,
                MAX(updated_at) as last_update
            FROM destination_affinities
        """
        
        try:
            results = await self.execute_query(stats_query)
            db_stats = results[0] if results else {}
            
            # Add performance metrics
            db_stats.update({
                'connection_pool_size': self.connection_pool.qsize(),
                'total_queries': self.metrics['total_queries'],
                'batch_operations': self.metrics['batch_operations'],
                'avg_query_time': self.metrics['avg_query_time'],
                'pool_hit_rate': (
                    self.metrics['connection_pool_hits'] / 
                    (self.metrics['connection_pool_hits'] + self.metrics['connection_pool_misses'])
                    if (self.metrics['connection_pool_hits'] + self.metrics['connection_pool_misses']) > 0 else 0
                )
            })
            
            return db_stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    async def close_pool(self):
        """Close all connections in the pool"""
        logger.info("Closing database connection pool")
        
        while not self.connection_pool.empty():
            try:
                connection = self.connection_pool.get_nowait()
                await connection.close()
            except asyncio.QueueEmpty:
                break
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
        
        logger.info("Database connection pool closed")
