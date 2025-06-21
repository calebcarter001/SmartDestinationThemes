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
        self.dev_images_dir = self.dev_staging_dir / "images"
        
        # Ensure staging directories exist
        self.dev_staging_dir.mkdir(exist_ok=True)
        self.dev_dashboard_dir.mkdir(exist_ok=True)
        self.dev_json_dir.mkdir(exist_ok=True)
        self.dev_images_dir.mkdir(exist_ok=True)
        
        # Check if we're in development mode
        self.is_development_mode = self._is_development_mode()
        
    def stage_latest_session(self, session_dir: str = None) -> bool:
        """
        Stage the latest session data to development folder.
        
        Args:
            session_dir: Path to the session directory to stage. If None, finds the latest automatically.
            
        Returns:
            bool: True if staging successful, False otherwise
        """
        try:
            # If no session_dir provided, find the latest one
            if session_dir is None:
                session_dir = self._find_latest_session_dir()
                if not session_dir:
                    self.logger.error("No session directories found to stage")
                    return False
            
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
            
            # Copy images files
            images_staged = self._copy_images_files(session_path)
            if images_staged:
                self.logger.info(f"Staged seasonal images from session")
            
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
        
        # Clear images directory
        if self.dev_images_dir.exists():
            shutil.rmtree(self.dev_images_dir)
            self.dev_images_dir.mkdir(exist_ok=True)
        
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
    
    def _copy_images_files(self, session_path: Path) -> bool:
        """Copy seasonal images to staging area, searching current and recent sessions."""
        images_staged = 0
        
        # First try the current session
        session_images = session_path / "images"
        if session_images.exists():
            images_staged += self._copy_images_from_directory(session_images)
        
        # If no images found in current session, search other recent sessions
        if images_staged == 0:
            images_staged += self._copy_images_from_recent_sessions()
        
        return images_staged > 0
    
    def _copy_images_from_directory(self, images_dir: Path) -> int:
        """Copy images from a specific directory to staging."""
        images_copied = 0
        
        # Copy all destination image directories
        for dest_dir in images_dir.iterdir():
            if dest_dir.is_dir():
                # Create destination directory in staging
                staging_dest_dir = self.dev_images_dir / dest_dir.name
                staging_dest_dir.mkdir(exist_ok=True)
                
                # Copy all image files
                for image_file in dest_dir.glob("*.jpg"):
                    shutil.copy2(image_file, staging_dest_dir / image_file.name)
                    images_copied += 1
                
                # Also copy any PNG files
                for image_file in dest_dir.glob("*.png"):
                    shutil.copy2(image_file, staging_dest_dir / image_file.name)
                    images_copied += 1
        
        if images_copied > 0:
            self.logger.info(f"📸 Copied {images_copied} seasonal images from {images_dir}")
        
        return images_copied
    
    def _copy_images_from_recent_sessions(self) -> int:
        """Search recent sessions for images if not found in current session."""
        try:
            import glob
            
            # Find recent session directories
            session_patterns = [
                "outputs/session_agent_*",
                "outputs/session_*"
            ]
            
            all_sessions = []
            for pattern in session_patterns:
                all_sessions.extend(glob.glob(pattern))
            
            # Sort by most recent
            recent_sessions = sorted(all_sessions, key=lambda x: Path(x).stat().st_ctime, reverse=True)
            
            images_copied = 0
            for session_dir in recent_sessions[:5]:  # Check last 5 sessions
                session_images = Path(session_dir) / "images"
                if session_images.exists():
                    copied = self._copy_images_from_directory(session_images)
                    images_copied += copied
                    
                    if copied > 0:
                        self.logger.info(f"📸 Found images in {session_dir}")
                        break  # Found images, stop searching
            
            return images_copied
            
        except Exception as e:
            self.logger.warning(f"Could not search for images in recent sessions: {e}")
            return 0
    
    def _create_staging_metadata(self, session_dir: str, processed_destinations: list = None):
        """Create metadata about the staged session."""
        import json
        from datetime import datetime
        
        # Load staging configuration
        try:
            import yaml
            with open("config/config.yaml", 'r') as f:
                config = yaml.safe_load(f)
            staging_config = config.get('development', {}).get('staging_mode', {})
        except:
            staging_config = {}
        
        metadata = {
            "staged_at": datetime.now().isoformat(),
            "source_session": session_dir,
            "staging_dir": str(self.dev_staging_dir),
            "dashboard_url": f"http://localhost:8000/",  # Updated to match actual server port
            "files_staged": {
                "dashboard": len(list(self.dev_dashboard_dir.glob("*.html"))),
                "json": len(list(self.dev_json_dir.glob("*.json"))),
                "images": len(list(self.dev_images_dir.rglob("*.jpg"))) + len(list(self.dev_images_dir.rglob("*.png")))
            }
        }
        
        # Add mode information if configured
        if staging_config.get('include_mode_in_metadata', True):
            metadata["staging_mode"] = {
                "is_development_mode": self.is_development_mode,
                "mode_name": "development" if self.is_development_mode else "production",
                "processed_destinations": processed_destinations or [],
                "selective_staging": self.is_development_mode,
                "auto_detected": staging_config.get('auto_detect_mode', True)
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

    def _find_latest_session_dir(self) -> Optional[str]:
        """Find the latest session directory in outputs folder."""
        try:
            outputs_dir = Path("outputs")
            if not outputs_dir.exists():
                return None
            
            # Find all session directories
            session_dirs = [d for d in outputs_dir.iterdir() 
                          if d.is_dir() and d.name.startswith("session_")]
            
            if not session_dirs:
                return None
            
            # Return the most recent one (by creation time)
            latest_session = max(session_dirs, key=lambda d: d.stat().st_ctime)
            return str(latest_session)
            
        except Exception as e:
            self.logger.error(f"Failed to find latest session directory: {e}")
            return None
    
    def _is_development_mode(self) -> bool:
        """Check if we're in development mode based on configuration."""
        try:
            # Load config to check staging mode
            import yaml
            config_path = Path("config/config.yaml")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Get staging mode configuration
                dev_config = config.get('development', {})
                staging_config = dev_config.get('staging_mode', {})
                
                # Check if auto-detection is enabled
                if not staging_config.get('auto_detect_mode', True):
                    # Manual mode - return false (production) by default
                    self.logger.info("🚀 Manual staging mode - defaulting to production")
                    return False
                
                # Auto-detect based on configured indicators
                dev_indicators = staging_config.get('dev_mode_indicators', {})
                processing_mode = config.get('processing_mode', {})
                
                # Check limited destinations
                dest_limit = dev_indicators.get('limited_destinations', 3)
                limited_destinations = len(config.get('destinations', [])) <= dest_limit
                
                # Check nuance-only processing
                if dev_indicators.get('nuance_only_processing', True):
                    nuance_only = (
                        not processing_mode.get('enable_theme_processing', True) and
                        processing_mode.get('enable_nuance_processing', True)
                    )
                else:
                    nuance_only = False
                
                # Check debug keywords in config
                debug_keywords = dev_indicators.get('debug_keywords', ['debug', 'test', 'development'])
                config_text = str(config).lower()
                has_debug_keywords = any(keyword in config_text for keyword in debug_keywords)
                
                # Determine mode
                is_dev = limited_destinations or nuance_only or has_debug_keywords
                
                # Log decision with details
                if staging_config.get('log_staging_decisions', True):
                    self.logger.info(f"🎯 Staging mode auto-detection:")
                    self.logger.info(f"   Limited destinations ({dest_limit}): {limited_destinations}")
                    self.logger.info(f"   Nuance-only processing: {nuance_only}")
                    self.logger.info(f"   Debug keywords found: {has_debug_keywords}")
                    
                    if is_dev:
                        self.logger.info("🔧 Development mode detected - selective staging enabled")
                    else:
                        self.logger.info("🚀 Production mode detected - full staging enabled")
                
                return is_dev
            
            return False
        except Exception as e:
            self.logger.warning(f"Could not determine staging mode: {e}, defaulting to production")
            return False
    
    def stage_session_selective(self, session_dir: str, processed_destinations: list = None) -> bool:
        """
        Stage session data with development vs production mode awareness.
        
        Args:
            session_dir: Path to the session directory to stage
            processed_destinations: List of destinations that were actually processed
            
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
            
            if self.is_development_mode and processed_destinations:
                # Development mode: Only stage processed destinations
                self.logger.info(f"🔧 Development staging: {len(processed_destinations)} destination(s)")
                success = self._stage_selective_destinations(session_path, processed_destinations)
            else:
                # Production mode: Stage everything
                self.logger.info("🚀 Production staging: all destinations")
                success = self._stage_all_destinations(session_path)
            
            if success:
                # Create staging metadata
                self._create_staging_metadata(session_dir, processed_destinations)
                
                self.logger.info(f"✅ Successfully staged session: {session_dir}")
                self.logger.info(f"📁 Development dashboard available at: {self.dev_dashboard_dir}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to stage session {session_dir}: {e}")
            return False
    
    def _stage_selective_destinations(self, session_path: Path, destinations: list) -> bool:
        """Stage only specific destinations (development mode)."""
        try:
            session_dashboard = session_path / "dashboard"
            session_json = session_path / "json"
            
            staged_count = 0
            
            # Stage specific destination files
            for destination in destinations:
                dest_filename = destination.lower().replace(', ', '__').replace(' ', '_')
                
                # Stage dashboard file
                if session_dashboard.exists():
                    dest_html = session_dashboard / f"{dest_filename}.html"
                    if dest_html.exists():
                        shutil.copy2(dest_html, self.dev_dashboard_dir / dest_html.name)
                        staged_count += 1
                        self.logger.info(f"📄 Staged dashboard: {destination}")
                
                # Stage JSON files (themes AND nuances)
                if session_json.exists():
                    json_files = [
                        f"{dest_filename}_enhanced.json",      # Theme data
                        f"{dest_filename}_evidence.json",      # Theme evidence
                        f"{dest_filename}_nuances.json",       # Nuance data
                        f"{dest_filename}_nuances_evidence.json"  # Nuance evidence
                    ]
                    
                    for json_file in json_files:
                        json_path = session_json / json_file
                        if json_path.exists():
                            shutil.copy2(json_path, self.dev_json_dir / json_file)
                            self.logger.info(f"📊 Staged data: {json_file}")
            
            # Copy index.html if it exists (for navigation)
            index_html = session_dashboard / "index.html"
            if index_html.exists():
                shutil.copy2(index_html, self.dev_dashboard_dir / "index.html")
                self.logger.info("📋 Staged index page")
            
            # Copy images for these destinations
            images_staged = self._copy_images_files(session_path)
            if images_staged:
                self.logger.info("📸 Staged seasonal images for destinations")
            
            # Also look for and copy theme data from previous sessions if this is nuance-only
            if self.is_development_mode:
                self._copy_theme_data_from_previous_sessions(destinations)
            
            return staged_count > 0
            
        except Exception as e:
            self.logger.error(f"Selective staging failed: {e}")
            return False
    
    def _stage_all_destinations(self, session_path: Path) -> bool:
        """Stage all destinations (production mode)."""
        try:
            # Copy all dashboard files
            session_dashboard = session_path / "dashboard"
            if session_dashboard.exists():
                self._copy_dashboard_files(session_dashboard)
                self.logger.info(f"Staged all dashboard files from {session_dashboard}")
            
            # Copy all JSON files
            session_json = session_path / "json"
            if session_json.exists():
                self._copy_json_files(session_json)
                self.logger.info(f"Staged all JSON files from {session_json}")
            
            # Copy all images
            images_staged = self._copy_images_files(session_path)
            if images_staged:
                self.logger.info("📸 Staged all seasonal images")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Full staging failed: {e}")
            return False
    
    def _copy_theme_data_from_previous_sessions(self, destinations: list):
        """Copy theme data from previous sessions for development mode."""
        try:
            # Find the most recent session with theme data
            import glob
            existing_sessions = sorted(glob.glob("outputs/session_agent_*"), reverse=True)
            
            for existing_session in existing_sessions:
                existing_json_dir = Path(existing_session) / "json"
                if not existing_json_dir.exists():
                    continue
                    
                copied_count = 0
                for destination in destinations:
                    dest_filename = destination.lower().replace(', ', '__').replace(' ', '_')
                    
                    # Copy theme files if they don't already exist
                    theme_files = [
                        f"{dest_filename}_enhanced.json",
                        f"{dest_filename}_evidence.json"
                    ]
                    
                    for theme_file in theme_files:
                        source_file = existing_json_dir / theme_file
                        dest_file = self.dev_json_dir / theme_file
                        
                        if source_file.exists() and not dest_file.exists():
                            shutil.copy2(source_file, dest_file)
                            copied_count += 1
                
                if copied_count > 0:
                    self.logger.info(f"🛡️ Copied {copied_count} theme files from {existing_session}")
                    break
            
        except Exception as e:
            self.logger.warning(f"Could not copy theme data from previous sessions: {e}") 