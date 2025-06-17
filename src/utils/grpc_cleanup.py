"""
gRPC Cleanup Utility
Handles proper cleanup of gRPC resources to prevent shutdown warnings.
"""

import asyncio
import logging
import atexit
from typing import Optional

logger = logging.getLogger(__name__)

class GRPCCleanupManager:
    """Manages gRPC resource cleanup"""
    
    def __init__(self):
        self._cleanup_tasks = []
        self._registered = False
        
    def register_cleanup(self, cleanup_func):
        """Register a cleanup function"""
        self._cleanup_tasks.append(cleanup_func)
        
        if not self._registered:
            atexit.register(self.cleanup_all)
            self._registered = True
    
    def cleanup_all(self):
        """Execute all cleanup tasks"""
        for cleanup_func in self._cleanup_tasks:
            try:
                if asyncio.iscoroutinefunction(cleanup_func):
                    # Handle async cleanup
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # Create a task if loop is running
                            asyncio.create_task(cleanup_func())
                        else:
                            # Run the cleanup if loop is not running
                            loop.run_until_complete(cleanup_func())
                    except RuntimeError:
                        # Event loop might be closed, try creating new one
                        try:
                            asyncio.run(cleanup_func())
                        except Exception as e:
                            logger.debug(f"Async cleanup failed: {e}")
                else:
                    # Handle sync cleanup
                    cleanup_func()
            except Exception as e:
                logger.debug(f"Cleanup task failed: {e}")
    
    async def async_cleanup_all(self):
        """Execute all cleanup tasks asynchronously"""
        for cleanup_func in self._cleanup_tasks:
            try:
                if asyncio.iscoroutinefunction(cleanup_func):
                    await cleanup_func()
                else:
                    cleanup_func()
            except Exception as e:
                logger.debug(f"Async cleanup task failed: {e}")

# Global cleanup manager instance
cleanup_manager = GRPCCleanupManager()

def register_grpc_cleanup(cleanup_func):
    """Register a gRPC cleanup function"""
    cleanup_manager.register_cleanup(cleanup_func)

def suppress_grpc_warnings():
    """Suppress common gRPC warnings"""
    import warnings
    import os
    
    # Suppress gRPC warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="grpc")
    
    # Set environment variables to reduce gRPC verbosity
    os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
    os.environ.setdefault("GRPC_TRACE", "")

# Initialize warning suppression
suppress_grpc_warnings() 