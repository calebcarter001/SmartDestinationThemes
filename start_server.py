#!/usr/bin/env python3
"""
Standalone Development Server for SmartDestinationThemes Dashboard
Provides a dedicated HTTP server for viewing generated dashboards with graceful shutdown.
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
import requests
from pathlib import Path

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from tools.config_loader import load_app_config
except ImportError:
    # Fallback if config loader is not available
    def load_app_config():
        return {}

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
    
    def _is_server_running_with_content(self, port):
        """Check if server is running on port and serving the right content."""
        try:
            response = requests.get(f"http://{self.host}:{port}/index.html", timeout=2)
            return response.status_code == 200
        except:
            return False
    
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
    
    def _check_dashboard_files(self):
        """Check if dashboard files exist and provide helpful feedback."""
        dashboard_path = Path(self.directory)
        
        if not dashboard_path.exists():
            print(f"❌ Dashboard directory not found: {dashboard_path.absolute()}")
            print(f"💡 To generate dashboard files:")
            print(f"   python main.py")
            return False
        
        index_file = dashboard_path / "index.html"
        if not index_file.exists():
            print(f"❌ Dashboard index file not found: {index_file}")
            print(f"💡 To generate dashboard files:")
            print(f"   python main.py")
            return False
        
        # Count available destination files
        html_files = list(dashboard_path.glob("*.html"))
        destination_files = [f for f in html_files if f.name != "index.html"]
        
        print(f"✅ Found dashboard with {len(destination_files)} destination(s)")
        if destination_files:
            print(f"📊 Available destinations:")
            for dest_file in sorted(destination_files):
                dest_name = dest_file.stem.replace('__', ', ').replace('_', ' ').title()
                print(f"   • {dest_name}: /{dest_file.name}")
        
        return True
    
    def start(self, port=None, open_browser=True):
        """Start the dashboard server."""
        port = port or self.port
        
        print("🚀 Destination Insights Discovery Server")
        print("="*50)
        
        # Check if dashboard files exist
        if not self._check_dashboard_files():
            return False
        
        # Check if server is already running with the right content
        if self._is_server_running_with_content(port):
            print(f"✅ Server already running and serving dashboard content on port {port}")
            dashboard_url = f"http://{self.host}:{port}/index.html"
            print(f"🔗 Dashboard URL: {dashboard_url}")
            if open_browser:
                print(f"🌐 Opening dashboard in browser...")
                webbrowser.open(dashboard_url)
            return True
        
        # Handle port conflicts
        original_port = port
        if self._is_port_in_use(port):
            print(f"⚠️  Port {port} is in use by another service")
            try:
                port = self._find_available_port(port)
                print(f"🔄 Using port {port} instead")
            except RuntimeError as e:
                print(f"❌ {e}")
                return False
        
        try:
            print(f"🌐 Starting dashboard server on port {port}")
            print(f"📁 Serving from: {Path(self.directory).absolute()}")
            
            handler_directory = self.directory

            # Custom handler to serve from specific directory and suppress logs
            class CustomHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=handler_directory, **kwargs)
                
                def log_message(self, format, *args):
                    # Suppress request logging for cleaner output
                    pass
                
                def handle_one_request(self):
                    """Handle a single HTTP request with proper error handling."""
                    try:
                        super().handle_one_request()
                    except (BrokenPipeError, ConnectionResetError):
                        # Client disconnected abruptly - this is normal, don't log as error
                        pass
                    except Exception as e:
                        # Log other unexpected errors
                        logger.debug(f"Request handling error: {e}")
                
                def finish(self):
                    """Finish the request with proper error handling."""
                    try:
                        super().finish()
                    except (BrokenPipeError, ConnectionResetError):
                        # Client disconnected - this is normal
                        pass
            
            # Custom TCP server with better error handling
            class RobustTCPServer(socketserver.TCPServer):
                def handle_error(self, request, client_address):
                    """Handle errors during request processing."""
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    
                    # Don't log common network errors
                    if isinstance(exc_value, (BrokenPipeError, ConnectionResetError)):
                        return
                    
                    # Log other errors at debug level
                    logger.debug(f"Request error from {client_address}: {exc_value}")
            
            # Create server
            self.server = RobustTCPServer((self.host, port), CustomHandler)
            self.server.allow_reuse_address = True
            
            # Start server in separate thread
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            # Wait a moment for server to start
            time.sleep(0.5)
            
            print("✅ Server started successfully!")
            print(f"🌐 Dashboard available at: http://{self.host}:{port}")
            print(f"📊 Main dashboard: http://{self.host}:{port}/index.html")
            print(f"")
            print(f"🎯 Usage tips:")
            print(f"   • Click 📎 paperclip icons to view evidence")
            print(f"   • Navigate between destinations using the main dashboard")
            print(f"   • Evidence links to real travel websites")
            print(f"")
            print(f"Press Ctrl+C to stop the server")
            
            # Open browser if requested
            if open_browser:
                dashboard_url = f"http://{self.host}:{port}/index.html"
                try:
                    webbrowser.open(dashboard_url)
                    print(f"🌐 Opened dashboard in browser")
                except Exception as e:
                    print(f"⚠️  Could not open browser: {e}")
                    print(f"   Please manually open: {dashboard_url}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def stop(self):
        """Stop the dashboard server."""
        print(f"\n🛑 Stopping dashboard server...")
        
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)
        
        self.shutdown_event.set()
        print("✅ Server stopped gracefully")
    
    def wait_for_shutdown(self):
        """Wait for shutdown signal."""
        try:
            while not self.shutdown_event.is_set():
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()

def list_available_sessions():
    """List available dashboard sessions."""
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        return []
    
    sessions = []
    for session_dir in outputs_dir.iterdir():
        if session_dir.is_dir() and session_dir.name.startswith("session_"):
            dashboard_dir = session_dir / "dashboard"
            if dashboard_dir.exists() and (dashboard_dir / "index.html").exists():
                sessions.append({
                    'session_id': session_dir.name,
                    'dashboard_path': str(dashboard_dir),
                    'created': session_dir.stat().st_ctime
                })
    
    # Sort by creation time (newest first)
    sessions.sort(key=lambda x: x['created'], reverse=True)
    return sessions

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Destination Insights Discovery Server')
    parser.add_argument('--port', type=int, help='Port to run server on (default: 8000)')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    parser.add_argument('--list-sessions', action='store_true', help='List available dashboard sessions')
    parser.add_argument('--session', type=str, help='Serve a specific session (use session ID)')
    
    args = parser.parse_args()
    
    if args.list_sessions:
        sessions = list_available_sessions()
        if not sessions:
            print("No dashboard sessions found.")
            print("Run 'python main.py' to generate dashboard data.")
        else:
            print("Available Dashboard Sessions:")
            print("="*50)
            for i, session in enumerate(sessions, 1):
                print(f"{i}. {session['session_id']}")
                print(f"   Path: {session['dashboard_path']}")
                print(f"   Created: {time.ctime(session['created'])}")
                print()
        return
    
    # Load configuration
    try:
        config = load_app_config()
    except Exception as e:
        logger.warning(f"Could not load config: {e}, using defaults")
        config = {}
    
    # Create server instance
    server = DashboardServer(config)
    
    # Handle specific session serving
    if args.session:
        session_path = Path("outputs") / args.session / "dashboard"
        if not session_path.exists():
            print(f"❌ Session not found: {args.session}")
            print("Use --list-sessions to see available sessions")
            sys.exit(1)
        server.directory = str(session_path)
    
    # Start server
    if server.start(port=args.port, open_browser=not args.no_browser):
        server.wait_for_shutdown()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
