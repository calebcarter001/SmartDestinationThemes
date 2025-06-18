"""
gRPC Cleanup Utility
Handles proper cleanup of gRPC resources to prevent shutdown warnings.
"""

import asyncio
import logging
import atexit
import sys
import warnings
import os
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
                    # Handle async cleanup more carefully
                    self._handle_async_cleanup(cleanup_func)
                else:
                    # Handle sync cleanup
                    cleanup_func()
            except Exception as e:
                # Silently ignore cleanup errors to prevent shutdown noise
                pass
    
    def _handle_async_cleanup(self, cleanup_func):
        """Handle async cleanup with better error handling"""
        try:
            # Try to get the current event loop
            try:
                loop = asyncio.get_running_loop()
                # If we have a running loop, create a task
                task = loop.create_task(cleanup_func())
                # Don't wait for completion to avoid blocking shutdown
            except RuntimeError:
                # No running loop, try to create and run
                try:
                    if sys.version_info >= (3, 7):
                        asyncio.run(cleanup_func())
                    else:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(cleanup_func())
                        finally:
                            loop.close()
                except Exception:
                    # Silently ignore - cleanup is best effort
                    pass
        except Exception:
            # Silently ignore all cleanup errors
            pass
    
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
    """Suppress common gRPC warnings and errors"""
    import warnings
    import os
    
    # Suppress all gRPC-related warnings and errors
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="grpc")
    warnings.filterwarnings("ignore", category=UserWarning, module="grpc")
    warnings.filterwarnings("ignore", message=".*grpc.*")
    warnings.filterwarnings("ignore", message=".*POLLER.*")
    warnings.filterwarnings("ignore", message=".*shutdown.*")
    
    # Set environment variables to reduce gRPC verbosity
    os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
    os.environ.setdefault("GRPC_TRACE", "")
    os.environ.setdefault("GRPC_ENABLE_FORK_SUPPORT", "1")

# Initialize warning suppression immediately
suppress_grpc_warnings()

# Additional sys.excepthook to catch and suppress gRPC errors
def suppress_grpc_excepthook(exctype, value, traceback):
    """Custom exception hook to suppress gRPC errors"""
    if 'grpc' in str(value).lower() or 'poller' in str(value).lower():
        # Silently ignore gRPC-related exceptions during shutdown
        return
    # Call the original exception hook for non-gRPC errors
    sys.__excepthook__(exctype, value, traceback)

# Install the custom exception hook
sys.excepthook = suppress_grpc_excepthook 