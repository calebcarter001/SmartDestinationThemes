#!/usr/bin/env python3
"""
Development Server for SmartDestinationThemes Dashboard
Provides a simple HTTP server for viewing generated dashboards with graceful shutdown.
"""

import os
import sys
import logging
import signal
import socket
import threading
import time
import webbrowser
import http.server
import socketserver
from pathlib import Path

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools.config_loader import load_app_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DashboardServer:
    def __init__(self, config=None):
        """Initialize server with configuration."""
        self.config = config or {}
        server_config = self.config.get('server', {})
        
        # Load configuration
        self.port = server_config.get('default_port', 8000)
        self.host = server_config.get('host', 'localhost')
        self.directory = "dev_staging/dashboard"
        self.server = None
        self.server_thread = None
        self.shutdown_event = threading.Event()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"\n🛑 Received signal {signum}")
        self.stop()
    
    def _is_port_in_use(self, port):
        """Check if a port is already in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((self.host, port)) == 0
    
    def _find_available_port(self, start_port, max_attempts=10):
        """Find an available port starting from start_port."""
        for i in range(max_attempts):
            port = start_port + i
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((self.host, port))
                    return port
            except OSError:
                continue
        raise RuntimeError(f"Could not find available port after {max_attempts} attempts")
    
    def start(self, port=None, open_browser=True):
        """Start the dashboard server."""
        port = port or self.port
        
        # Check if dashboard directory exists
        if not Path(self.directory).exists():
            logger.error(f"Dashboard directory not found: {self.directory}")
            logger.info("Run 'python main.py' first to generate dashboard data")
            return False
        
        # Handle port conflicts
        if self._is_port_in_use(port):
            logger.warning(f"Port {port} is already in use")
            logger.info("Attempting to stop existing server...")
            time.sleep(1)  # Give time for cleanup
            
            # Try to find alternative port
            try:
                port = self._find_available_port(port)
                logger.info(f"Using alternative port: {port}")
            except RuntimeError as e:
                logger.error(str(e))
                return False
        
        try:
            logger.info(f"🚀 Starting dashboard server on port {port}")
            logger.info(f"📁 Serving from: {Path(self.directory).absolute()}")
            
            # Custom handler to serve from specific directory
            class CustomHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=self.directory, **kwargs)
                
                def log_message(self, format, *args):
                    # Suppress request logging for cleaner output
                    pass
            
            # Create server
            self.server = socketserver.TCPServer((self.host, port), CustomHandler)
            self.server.allow_reuse_address = True
            
            # Start server in separate thread
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            logger.info("✅ Server started successfully!")
            logger.info(f"🌐 Dashboard available at: http://{self.host}:{port}")
            logger.info(f"📊 View results at: http://{self.host}:{port}/index.html")
            logger.info("Press Ctrl+C to stop the server")
            
            # Open browser if requested
            if open_browser:
                dashboard_url = f"http://{self.host}:{port}/index.html"
                try:
                    webbrowser.open(dashboard_url)
                    logger.info("🌐 Opened dashboard in browser")
                except Exception as e:
                    logger.warning(f"Could not open browser: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def stop(self):
        """Stop the dashboard server."""
        logger.info("🛑 Stopping dashboard server...")
        
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)
        
        self.shutdown_event.set()
        logger.info("✅ Server stopped gracefully")
    
    def wait_for_shutdown(self):
        """Wait for shutdown signal."""
        try:
            while not self.shutdown_event.is_set():
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='SmartDestinationThemes Dashboard Server')
    parser.add_argument('--port', type=int, help='Port to run server on')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    parser.add_argument('--config', type=str, help='Path to config file')
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = load_app_config()
    except Exception as e:
        logger.warning(f"Could not load config: {e}, using defaults")
        config = {}
    
    # Create and start server
    server = DashboardServer(config)
    
    if server.start(port=args.port, open_browser=not args.no_browser):
        server.wait_for_shutdown()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 