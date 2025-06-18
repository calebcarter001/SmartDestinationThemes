#!/usr/bin/env python3
"""
Comprehensive Test for DevStagingManager
Tests the entire staging workflow to ensure it works correctly.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.dev_staging_manager import DevStagingManager


class TestDevStagingManager(unittest.TestCase):
    """Comprehensive test suite for DevStagingManager."""
    
    def setUp(self):
        """Set up test environment with temporary directories."""
        # Create temporary directory for testing
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        
        # Change to test directory
        os.chdir(self.test_dir)
        
        # Create mock outputs structure
        self.outputs_dir = self.test_dir / "outputs"
        self.session_dir = self.outputs_dir / "session_20250617_123456"
        self.dashboard_dir = self.session_dir / "dashboard"
        self.json_dir = self.session_dir / "json"
        
        # Create directories
        self.outputs_dir.mkdir()
        self.session_dir.mkdir()
        self.dashboard_dir.mkdir()
        self.json_dir.mkdir()
        
        # Create mock files
        self._create_mock_files()
        
        # Initialize DevStagingManager
        self.staging_manager = DevStagingManager()
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def _create_mock_files(self):
        """Create mock dashboard and JSON files for testing."""
        # Mock dashboard files
        dashboard_files = [
            "index.html",
            "paris__france.html",
            "tokyo__japan.html",
            "new_york__usa.html"
        ]
        
        for filename in dashboard_files:
            file_path = self.dashboard_dir / filename
            with open(file_path, 'w') as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head><title>{filename}</title></head>
                <body>
                    <h1>Mock Dashboard: {filename}</h1>
                    <p>This is a test dashboard file.</p>
                </body>
                </html>
                """)
        
        # Mock JSON files
        json_files = [
            "paris__france_enhanced.json",
            "tokyo__japan_enhanced.json", 
            "new_york__usa_enhanced.json"
        ]
        
        for filename in json_files:
            file_path = self.json_dir / filename
            mock_data = {
                "destination": filename.replace("_enhanced.json", "").replace("__", ", ").title(),
                "themes": [
                    {
                        "theme": "Mock Theme",
                        "category": "culture",
                        "confidence": 0.75,
                        "sub_themes": ["Mock Sub-theme 1", "Mock Sub-theme 2"]
                    }
                ],
                "processing_metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "total_themes": 1
                }
            }
            with open(file_path, 'w') as f:
                json.dump(mock_data, f, indent=2)
        
        # Mock session summary
        session_summary = {
            "session_id": "session_20250617_123456",
            "destinations_processed": 3,
            "total_themes": 75,
            "processing_time": "120.5 seconds",
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.session_dir / "session_summary.json", 'w') as f:
            json.dump(session_summary, f, indent=2)
    
    def test_staging_manager_initialization(self):
        """Test that DevStagingManager initializes correctly."""
        self.assertIsInstance(self.staging_manager, DevStagingManager)
        self.assertTrue(self.staging_manager.dev_staging_dir.exists())
        self.assertTrue(self.staging_manager.dev_dashboard_dir.exists())
        self.assertTrue(self.staging_manager.dev_json_dir.exists())
    
    def test_find_latest_session_dir(self):
        """Test finding the latest session directory."""
        # Test with existing session
        latest_session = self.staging_manager._find_latest_session_dir()
        self.assertIsNotNone(latest_session)
        self.assertIn("session_20250617_123456", latest_session)
        
        # Test with no outputs directory
        shutil.rmtree(self.outputs_dir)
        latest_session = self.staging_manager._find_latest_session_dir()
        self.assertIsNone(latest_session)
    
    def test_stage_latest_session_with_explicit_path(self):
        """Test staging with explicitly provided session directory."""
        success = self.staging_manager.stage_latest_session(str(self.session_dir))
        self.assertTrue(success)
        
        # Verify files were copied
        self._verify_staged_files()
    
    def test_stage_latest_session_auto_find(self):
        """Test staging with automatic session discovery."""
        success = self.staging_manager.stage_latest_session()
        self.assertTrue(success)
        
        # Verify files were copied
        self._verify_staged_files()
    
    def test_stage_nonexistent_session(self):
        """Test staging with nonexistent session directory."""
        success = self.staging_manager.stage_latest_session("/nonexistent/path")
        self.assertFalse(success)
    
    def test_clear_staging_area(self):
        """Test clearing the staging area."""
        # First stage some files
        self.staging_manager.stage_latest_session(str(self.session_dir))
        
        # Verify files exist
        self.assertTrue(len(list(self.staging_manager.dev_dashboard_dir.glob("*.html"))) > 0)
        
        # Clear staging area
        self.staging_manager._clear_staging_area()
        
        # Verify files are gone
        self.assertEqual(len(list(self.staging_manager.dev_dashboard_dir.glob("*.html"))), 0)
        self.assertEqual(len(list(self.staging_manager.dev_json_dir.glob("*.json"))), 0)
    
    def test_staging_metadata_creation(self):
        """Test creation of staging metadata."""
        success = self.staging_manager.stage_latest_session(str(self.session_dir))
        self.assertTrue(success)
        
        # Check metadata file exists
        metadata_file = self.staging_manager.dev_staging_dir / "staging_metadata.json"
        self.assertTrue(metadata_file.exists())
        
        # Verify metadata content
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        self.assertIn("staged_at", metadata)
        self.assertIn("source_session", metadata)
        self.assertIn("files_staged", metadata)
        self.assertEqual(metadata["files_staged"]["dashboard"], 4)  # 4 HTML files
        self.assertEqual(metadata["files_staged"]["json"], 3)      # 3 JSON files
    
    def test_get_staging_info(self):
        """Test retrieving staging information."""
        # Initially no staging info
        info = self.staging_manager.get_staging_info()
        self.assertIsNone(info)
        
        # Stage files
        self.staging_manager.stage_latest_session(str(self.session_dir))
        
        # Get staging info
        info = self.staging_manager.get_staging_info()
        self.assertIsNotNone(info)
        self.assertIn("staged_at", info)
        self.assertIn("source_session", info)
    
    def test_multiple_sessions_latest_selection(self):
        """Test that the latest session is selected when multiple exist."""
        # Create an older session
        older_session = self.outputs_dir / "session_20250616_123456"
        older_session.mkdir()
        (older_session / "dashboard").mkdir()
        (older_session / "json").mkdir()
        
        # Create a newer session  
        newer_session = self.outputs_dir / "session_20250618_123456"
        newer_session.mkdir()
        (newer_session / "dashboard").mkdir()
        (newer_session / "json").mkdir()
        
        # Add a test file to the newer session
        with open(newer_session / "dashboard" / "test.html", 'w') as f:
            f.write("<html><body>Newer session</body></html>")
        
        # Stage latest (should pick the newer one)
        success = self.staging_manager.stage_latest_session()
        self.assertTrue(success)
        
        # Verify the newer session was staged
        test_file = self.staging_manager.dev_dashboard_dir / "test.html"
        self.assertTrue(test_file.exists())
    
    def test_staging_with_missing_subdirectories(self):
        """Test staging when some subdirectories are missing."""
        # Remove JSON directory
        shutil.rmtree(self.json_dir)
        
        # Should still succeed with just dashboard files
        success = self.staging_manager.stage_latest_session(str(self.session_dir))
        self.assertTrue(success)
        
        # Verify dashboard files were staged
        dashboard_files = list(self.staging_manager.dev_dashboard_dir.glob("*.html"))
        self.assertEqual(len(dashboard_files), 4)
        
        # Verify no JSON files (since directory didn't exist)
        json_files = list(self.staging_manager.dev_json_dir.glob("*.json"))
        self.assertEqual(len(json_files), 0)
    
    def _verify_staged_files(self):
        """Helper method to verify that files were properly staged."""
        # Check dashboard files
        dashboard_files = list(self.staging_manager.dev_dashboard_dir.glob("*.html"))
        self.assertEqual(len(dashboard_files), 4)
        
        expected_dashboard_files = [
            "index.html", "paris__france.html", 
            "tokyo__japan.html", "new_york__usa.html"
        ]
        staged_filenames = [f.name for f in dashboard_files]
        for expected_file in expected_dashboard_files:
            self.assertIn(expected_file, staged_filenames)
        
        # Check JSON files
        json_files = list(self.staging_manager.dev_json_dir.glob("*.json"))
        self.assertEqual(len(json_files), 3)
        
        # Check session summary
        session_summary = self.staging_manager.dev_staging_dir / "session_summary.json"
        self.assertTrue(session_summary.exists())
        
        # Verify content of a staged file
        with open(self.staging_manager.dev_dashboard_dir / "index.html", 'r') as f:
            content = f.read()
            self.assertIn("Mock Dashboard: index.html", content)


def run_comprehensive_test():
    """Run the comprehensive test suite."""
    print("🧪 Running Comprehensive DevStagingManager Test Suite")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDevStagingManager)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED! DevStagingManager is working correctly.")
        print(f"📊 Ran {result.testsRun} tests successfully")
    else:
        print("❌ SOME TESTS FAILED!")
        print(f"📊 Ran {result.testsRun} tests")
        print(f"❌ Failures: {len(result.failures)}")
        print(f"⚠️  Errors: {len(result.errors)}")
        
        # Print failure details
        if result.failures:
            print("\n🔍 FAILURE DETAILS:")
            for test, traceback in result.failures:
                print(f"  • {test}: {traceback}")
        
        if result.errors:
            print("\n🔍 ERROR DETAILS:")
            for test, traceback in result.errors:
                print(f"  • {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 