"""
Development Staging Manager
Automatically stages the latest processed data in a consistent development folder
for easy dashboard access during development.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional

class DevStagingManager:
    """Manages development staging of processed data."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = logging.getLogger("app.dev_staging")
        
        # Development staging paths
        self.dev_staging_dir = Path("dev_staging")
        self.dev_dashboard_dir = self.dev_staging_dir / "dashboard"
        self.dev_json_dir = self.dev_staging_dir / "json"
        
        # Ensure staging directories exist
        self.dev_staging_dir.mkdir(exist_ok=True)
        self.dev_dashboard_dir.mkdir(exist_ok=True)
        self.dev_json_dir.mkdir(exist_ok=True)
        
    def stage_latest_session(self, session_dir: str) -> bool:
        """
        Stage the latest session data to development folder.
        
        Args:
            session_dir: Path to the session directory to stage
            
        Returns:
            bool: True if staging successful, False otherwise
        """
        try:
            session_path = Path(session_dir)
            if not session_path.exists():
                self.logger.error(f"Session directory does not exist: {session_dir}")
                return False
            
            # Clear existing staging data
            self._clear_staging_area()
            
            # Copy dashboard files
            session_dashboard = session_path / "dashboard"
            if session_dashboard.exists():
                self._copy_dashboard_files(session_dashboard)
                self.logger.info(f"Staged dashboard files from {session_dashboard}")
            
            # Copy JSON files
            session_json = session_path / "json"
            if session_json.exists():
                self._copy_json_files(session_json)
                self.logger.info(f"Staged JSON files from {session_json}")
            
            # Copy session summary
            session_summary = session_path / "session_summary.json"
            if session_summary.exists():
                shutil.copy2(session_summary, self.dev_staging_dir / "session_summary.json")
                self.logger.info("Staged session summary")
            
            # Create staging metadata
            self._create_staging_metadata(session_dir)
            
            self.logger.info(f"✅ Successfully staged session: {session_dir}")
            self.logger.info(f"📁 Development dashboard available at: {self.dev_dashboard_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stage session {session_dir}: {e}")
            return False
    
    def _clear_staging_area(self):
        """Clear existing staging data."""
        for item in self.dev_dashboard_dir.iterdir():
            if item.is_file():
                item.unlink()
        
        for item in self.dev_json_dir.iterdir():
            if item.is_file():
                item.unlink()
        
        # Remove staging metadata if exists
        staging_meta = self.dev_staging_dir / "staging_metadata.json"
        if staging_meta.exists():
            staging_meta.unlink()
    
    def _copy_dashboard_files(self, source_dashboard: Path):
        """Copy dashboard files to staging area."""
        for file in source_dashboard.glob("*.html"):
            shutil.copy2(file, self.dev_dashboard_dir / file.name)
    
    def _copy_json_files(self, source_json: Path):
        """Copy JSON files to staging area."""
        for file in source_json.glob("*.json"):
            shutil.copy2(file, self.dev_json_dir / file.name)
    
    def _create_staging_metadata(self, session_dir: str):
        """Create metadata about the staged session."""
        import json
        from datetime import datetime
        
        metadata = {
            "staged_at": datetime.now().isoformat(),
            "source_session": session_dir,
            "staging_dir": str(self.dev_staging_dir),
            "dashboard_url": f"http://localhost:8002/",
            "files_staged": {
                "dashboard": len(list(self.dev_dashboard_dir.glob("*.html"))),
                "json": len(list(self.dev_json_dir.glob("*.json")))
            }
        }
        
        with open(self.dev_staging_dir / "staging_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_staging_info(self) -> Optional[dict]:
        """Get information about the currently staged session."""
        try:
            metadata_file = self.dev_staging_dir / "staging_metadata.json"
            if metadata_file.exists():
                import json
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.error(f"Failed to read staging metadata: {e}")
            return None
    
    def start_dev_server(self, port: int = 8002) -> bool:
        """Start development server serving the staged dashboard."""
        try:
            import subprocess
            import webbrowser
            import time
            
            # Check if dashboard files exist
            dashboard_files = list(self.dev_dashboard_dir.glob("*.html"))
            if not dashboard_files:
                self.logger.error("No dashboard files found in staging area. Run processing first.")
                return False
            
            # Start server in background
            self.logger.info(f"🌐 Starting development server on port {port}")
            self.logger.info(f"📁 Serving: {self.dev_dashboard_dir}")
            
            # Change to dashboard directory and start server
            os.chdir(self.dev_dashboard_dir)
            
            # Start server process
            server_process = subprocess.Popen(
                ["python3", "-m", "http.server", str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give server time to start
            time.sleep(2)
            
            # Open browser
            dashboard_url = f"http://localhost:{port}/"
            self.logger.info(f"🌍 Opening dashboard: {dashboard_url}")
            webbrowser.open(dashboard_url)
            
            self.logger.info("🎉 Development server started successfully!")
            self.logger.info("Press Ctrl+C to stop the server")
            
            # Wait for server to finish
            server_process.wait()
            
            return True
            
        except KeyboardInterrupt:
            self.logger.info("🛑 Development server stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start development server: {e}")
            return False
    
    def auto_stage_and_serve(self, session_dir: str, port: int = 8002) -> bool:
        """Automatically stage the latest session and start development server."""
        if self.stage_latest_session(session_dir):
            return self.start_dev_server(port)
        return False 