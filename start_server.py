#!/usr/bin/env python3
"""
Dashboard Server Startup Script
Handles graceful startup and shutdown of the development server.
"""

import os
import sys
import signal
import subprocess
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DashboardServer:
    """Manages the dashboard HTTP server"""
    
    def __init__(self, port=8000, directory="dev_staging/dashboard"):
        self.port = port
        self.directory = directory
        self.process = None
        
    def start(self):
        """Start the HTTP server"""
        try:
            # Check if directory exists
            if not os.path.exists(self.directory):
                logger.error(f"Dashboard directory not found: {self.directory}")
                logger.info("Please run the processing pipeline first to generate dashboard files")
                return False
            
            # Check if port is available
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', self.port)) == 0:
                    logger.warning(f"Port {self.port} is already in use")
                    logger.info("Attempting to stop existing server...")
                    self.stop_existing_server()
                    time.sleep(1)
            
            # Start the server
            cmd = [
                sys.executable, "-m", "http.server", str(self.port),
                "--directory", self.directory
            ]
            
            logger.info(f"🚀 Starting dashboard server on port {self.port}")
            logger.info(f"📁 Serving from: {os.path.abspath(self.directory)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Give server time to start
            time.sleep(1)
            
            # Check if server started successfully
            if self.process.poll() is None:
                logger.info(f"✅ Server started successfully!")
                logger.info(f"🌐 Dashboard available at: http://localhost:{self.port}")
                logger.info(f"📊 View results at: http://localhost:{self.port}/index.html")
                return True
            else:
                stdout, stderr = self.process.communicate()
                logger.error(f"Server failed to start: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def stop_existing_server(self):
        """Stop any existing server on the port"""
        try:
            # Kill any existing http.server processes
            subprocess.run(
                ["pkill", "-f", f"http.server.*{self.port}"],
                capture_output=True
            )
        except Exception as e:
            logger.debug(f"Error stopping existing server: {e}")
    
    def stop(self):
        """Stop the server gracefully"""
        if self.process:
            try:
                logger.info("🛑 Stopping dashboard server...")
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("✅ Server stopped gracefully")
            except subprocess.TimeoutExpired:
                logger.warning("Server didn't stop gracefully, forcing...")
                self.process.kill()
                self.process.wait()
            except Exception as e:
                logger.error(f"Error stopping server: {e}")
            finally:
                self.process = None
    
    def run_interactive(self):
        """Run server interactively with keyboard interrupt handling"""
        if not self.start():
            return
        
        try:
            logger.info("Press Ctrl+C to stop the server")
            
            # Keep server running and show access logs
            while self.process and self.process.poll() is None:
                try:
                    # Read server output
                    line = self.process.stdout.readline()
                    if line:
                        print(line.strip())
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    break
                    
        except KeyboardInterrupt:
            logger.info("\n🛑 Keyboard interrupt received")
        finally:
            self.stop()

def main():
    """Main function"""
    server = DashboardServer()
    
    # Handle shutdown signals
    def signal_handler(signum, frame):
        logger.info(f"\n🛑 Received signal {signum}")
        server.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the server
    server.run_interactive()

if __name__ == "__main__":
    main() 