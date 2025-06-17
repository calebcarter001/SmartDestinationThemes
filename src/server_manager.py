#!/usr/bin/env python3
"""
Server Manager for Enhanced Intelligence Dashboard
Provides a simple HTTP server to properly serve HTML dashboard files.
"""

import os
import sys
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DashboardHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler with proper MIME types for dashboard files."""
    
    def __init__(self, *args, directory=None, **kwargs):
        if directory is None:
            directory = os.getcwd()
        self.directory = os.path.abspath(directory)
        super().__init__(*args, directory=directory, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def guess_type(self, path):
        """Guess MIME type with enhanced support for web files."""
        result = super().guess_type(path)
        if isinstance(result, tuple):
            mimetype, encoding = result
        else:
            mimetype, encoding = result, None
        
        # Enhanced MIME type mappings
        if path.endswith('.html'):
            return 'text/html', encoding
        elif path.endswith('.css'):
            return 'text/css', encoding
        elif path.endswith('.js'):
            return 'application/javascript', encoding
        elif path.endswith('.json'):
            return 'application/json', encoding
        elif path.endswith('.svg'):
            return 'image/svg+xml', encoding
        elif path.endswith('.woff2'):
            return 'font/woff2', encoding
        elif path.endswith('.woff'):
            return 'font/woff', encoding
        
        return mimetype, encoding
    
    def log_message(self, format, *args):
        """Override to provide cleaner logging."""
        logger.info(f"Dashboard Server: {format % args}")

class DashboardServerManager:
    """Manager for the dashboard HTTP server."""
    
    def __init__(self, base_output_dir: str = "outputs"):
        self.base_output_dir = base_output_dir
        self.server = None
        self.server_thread = None
        self.port = 8000
        self.host = 'localhost'
        
    def find_latest_dashboard(self) -> str:
        """Find the most recent dashboard directory."""
        if not os.path.exists(self.base_output_dir):
            raise FileNotFoundError(f"Output directory not found: {self.base_output_dir}")
        
        # Find all session directories
        session_dirs = []
        for item in os.listdir(self.base_output_dir):
            item_path = os.path.join(self.base_output_dir, item)
            if os.path.isdir(item_path) and item.startswith('session_'):
                dashboard_dir = os.path.join(item_path, 'dashboard')
                if os.path.exists(dashboard_dir) and os.path.exists(os.path.join(dashboard_dir, 'index.html')):
                    session_dirs.append((item, item_path))
        
        if not session_dirs:
            raise FileNotFoundError("No dashboard sessions found")
        
        # Sort by session timestamp (latest first)
        session_dirs.sort(reverse=True)
        latest_session = session_dirs[0][1]
        dashboard_path = os.path.join(latest_session, 'dashboard')
        
        logger.info(f"Found latest dashboard: {dashboard_path}")
        return dashboard_path
    
    def find_available_port(self, start_port: int = 8000, max_attempts: int = 10) -> int:
        """Find an available port starting from start_port."""
        import socket
        
        for port in range(start_port, start_port + max_attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind((self.host, port))
                    return port
                except OSError:
                    continue
        
        raise RuntimeError(f"Could not find available port in range {start_port}-{start_port + max_attempts}")
    
    def start_server(self, dashboard_dir: str = None, port: int = None, open_browser: bool = True) -> dict:
        """
        Start the dashboard HTTP server.
        
        Args:
            dashboard_dir: Directory containing dashboard files (auto-detect if None)
            port: Port to serve on (auto-detect if None)
            open_browser: Whether to automatically open browser
            
        Returns:
            Dictionary with server info
        """
        
        # Find dashboard directory if not provided
        if dashboard_dir is None:
            dashboard_dir = self.find_latest_dashboard()
        
        if not os.path.exists(dashboard_dir):
            raise FileNotFoundError(f"Dashboard directory not found: {dashboard_dir}")
        
        # Find available port if not provided
        if port is None:
            port = self.find_available_port()
        
        self.port = port
        
        # Change to dashboard directory for serving
        original_cwd = os.getcwd()
        os.chdir(dashboard_dir)
        
        try:
            # Create server
            handler = lambda *args, **kwargs: DashboardHTTPRequestHandler(*args, directory=dashboard_dir, **kwargs)
            self.server = HTTPServer((self.host, self.port), handler)
            
            # Start server in background thread
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            server_url = f"http://{self.host}:{self.port}"
            
            print(f"\n🌐 Enhanced Intelligence Dashboard Server Started!")
            print(f"📍 URL: {server_url}")
            print(f"📁 Serving: {dashboard_dir}")
            print(f"🔗 Press Ctrl+C to stop the server")
            print("="*60)
            
            # Open browser if requested
            if open_browser:
                print(f"🌍 Opening dashboard in browser...")
                webbrowser.open(server_url)
            
            return {
                'url': server_url,
                'host': self.host,
                'port': self.port,
                'dashboard_dir': dashboard_dir,
                'status': 'running'
            }
            
        except Exception as e:
            # Restore original directory
            os.chdir(original_cwd)
            raise e
    
    def stop_server(self):
        """Stop the dashboard server."""
        if self.server:
            print(f"\n🛑 Stopping dashboard server...")
            self.server.shutdown()
            self.server.server_close()
            if self.server_thread:
                self.server_thread.join(timeout=5)
            
            print(f"✅ Dashboard server stopped")
            
            self.server = None
            self.server_thread = None
    
    def is_running(self) -> bool:
        """Check if server is currently running."""
        return self.server is not None and self.server_thread is not None and self.server_thread.is_alive()
    
    def get_server_info(self) -> dict:
        """Get current server information."""
        if self.is_running():
            return {
                'url': f"http://{self.host}:{self.port}",
                'host': self.host,
                'port': self.port,
                'status': 'running'
            }
        else:
            return {'status': 'stopped'}
    
    def wait_for_shutdown(self):
        """Wait for server shutdown (blocking)."""
        if self.server_thread:
            try:
                while self.server_thread.is_alive():
                    self.server_thread.join(1)
            except KeyboardInterrupt:
                print(f"\n⚡ Received shutdown signal...")
                self.stop_server()

def serve_latest_dashboard(port: int = None, open_browser: bool = True) -> dict:
    """
    Convenience function to serve the latest dashboard.
    
    Args:
        port: Port to serve on (auto-detect if None)
        open_browser: Whether to open browser automatically
        
    Returns:
        Dictionary with server info
    """
    
    manager = DashboardServerManager()
    return manager.start_server(port=port, open_browser=open_browser)

def list_available_dashboards(base_output_dir: str = "outputs") -> list:
    """
    List all available dashboard sessions.
    
    Args:
        base_output_dir: Base output directory to search
        
    Returns:
        List of dashboard session info
    """
    
    if not os.path.exists(base_output_dir):
        return []
    
    dashboards = []
    
    for item in os.listdir(base_output_dir):
        item_path = os.path.join(base_output_dir, item)
        if os.path.isdir(item_path) and item.startswith('session_'):
            dashboard_dir = os.path.join(item_path, 'dashboard')
            summary_file = os.path.join(item_path, 'session_summary.json')
            
            if os.path.exists(dashboard_dir) and os.path.exists(os.path.join(dashboard_dir, 'index.html')):
                dashboard_info = {
                    'session_id': item,
                    'session_path': item_path,
                    'dashboard_path': dashboard_dir,
                    'has_summary': os.path.exists(summary_file)
                }
                
                # Try to load summary info
                if dashboard_info['has_summary']:
                    try:
                        import json
                        with open(summary_file, 'r') as f:
                            summary = json.load(f)
                        dashboard_info['summary'] = summary['session_info']
                        dashboard_info['destination_count'] = summary['session_info']['destinations_processed']
                    except Exception as e:
                        logger.error(f"Error loading summary for {item}: {e}")
                
                dashboards.append(dashboard_info)
    
    # Sort by session timestamp (latest first)
    dashboards.sort(key=lambda x: x['session_id'], reverse=True)
    
    return dashboards

if __name__ == "__main__":
    """Command line interface for the dashboard server."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Intelligence Dashboard Server")
    parser.add_argument('--port', type=int, help='Port to serve on (auto-detect if not specified)')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    parser.add_argument('--dashboard-dir', help='Specific dashboard directory to serve')
    parser.add_argument('--list', action='store_true', help='List available dashboard sessions')
    
    args = parser.parse_args()
    
    if args.list:
        print("Available Dashboard Sessions:")
        print("="*50)
        
        dashboards = list_available_dashboards()
        if not dashboards:
            print("No dashboard sessions found.")
        else:
            for i, dash in enumerate(dashboards, 1):
                print(f"{i}. {dash['session_id']}")
                if 'destination_count' in dash:
                    print(f"   Destinations: {dash['destination_count']}")
                if 'summary' in dash:
                    print(f"   Created: {dash['summary']['processing_date'][:19]}")
                print(f"   Path: {dash['dashboard_path']}")
                print()
    else:
        # Start server
        manager = DashboardServerManager()
        
        try:
            server_info = manager.start_server(
                dashboard_dir=args.dashboard_dir,
                port=args.port,
                open_browser=not args.no_browser
            )
            
            # Wait for shutdown
            manager.wait_for_shutdown()
            
        except KeyboardInterrupt:
            print("\n⚡ Shutting down...")
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            sys.exit(1) 