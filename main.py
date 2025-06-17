#!/usr/bin/env python3
"""
SmartDestinationThemes - Main Entry Point
Unified processing system with multiple modes:
- Full Pipeline: LLM Generation + Web Discovery + Evidence Collection + Intelligence Enhancement
- Demo Mode: Quick processing with sample data
- Development Server: Serve existing data with evidence validation
"""

import asyncio
import json
import logging
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import gRPC cleanup utility first to suppress warnings
from src.utils.grpc_cleanup import suppress_grpc_warnings
suppress_grpc_warnings()

# from src.affinity_pipeline import AffinityPipeline  # Not needed for focused prompt approach
from src.dev_staging_manager import DevStagingManager
from tools.config_loader import load_app_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main_processing.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='SmartDestinationThemes Processing System')
    parser.add_argument('--mode', choices=['full', 'demo', 'server'], default='full',
                       help='Processing mode: full pipeline, demo with sample data, or development server')
    parser.add_argument('--destinations', nargs='+', 
                       help='Specific destinations to process (overrides default list)')
    parser.add_argument('--port', type=int, default=8000,
                       help='Port for development server (default: 8000)')
    parser.add_argument('--no-browser', action='store_true',
                       help='Do not automatically open browser')
    return parser.parse_args()

def load_config():
    """Load application configuration."""
    try:
        return load_app_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

def get_destinations_to_process(custom_destinations: List[str] = None) -> List[str]:
    """Get list of destinations to process."""
    
    if custom_destinations:
        return custom_destinations
    
    # Always load from config.yaml first
    logger.info("Loading destinations from config.yaml")
    config = load_config()
    destinations = config.get('destinations', [])
    
    if not destinations:
        logger.error("No destinations found in config.yaml")
        raise ValueError("No destinations configured. Please add destinations to config.yaml")
    
    # Respect the max_destinations_to_process setting
    max_destinations = config.get('processing_settings', {}).get('max_destinations_to_process', 0)
    
    if max_destinations > 0 and len(destinations) > max_destinations:
        logger.info(f"Limiting to {max_destinations} destinations (from {len(destinations)} total)")
        destinations = destinations[:max_destinations]
    
    return destinations

async def run_full_pipeline(destinations: List[str], config: Dict[str, Any]) -> Dict[str, str]:
    """Run full pipeline with web discovery and focused prompt processing."""
    
    print(f"\n🚀 FULL PIPELINE MODE")
    print(f"Processing {len(destinations)} destinations with complete workflow")
    print("="*70)
    
    # Use the enhanced data processor with focused prompts
    from src.enhanced_data_processor import EnhancedDataProcessor
    from src.focused_prompt_processor import FocusedPromptProcessor
    
    processor = EnhancedDataProcessor(config)
    
    # Initialize LLM and focused prompt processor
    from src.focused_llm_generator import FocusedLLMGenerator
    provider = config.get("llm_settings", {}).get("provider", "gemini")
    llm_generator = FocusedLLMGenerator(provider, config)
    focused_processor = FocusedPromptProcessor(llm_generator, config)
    
    # Step 1: Web Discovery for each destination
    print(f"\n🌐 Step 1: Web Discovery")
    web_data = {}
    
    from tools.web_discovery_tools import WebDiscoveryTool
    web_tool = WebDiscoveryTool(config)
    
    for dest in destinations:
        print(f"  🔍 Discovering web content for {dest}...")
        try:
            discovery_result = await web_tool.discover_destination_content(dest)
            web_data[dest] = discovery_result
            print(f"    ✅ Found {len(discovery_result.get('urls', []))} sources for {dest}")
        except Exception as e:
            logger.error(f"Web discovery failed for {dest}: {e}")
            web_data[dest] = {"urls": [], "content": []}
            print(f"    ⚠️  Web discovery failed for {dest}, continuing with focused prompts only")
    
    # Step 2: Focused Prompt Processing
    print(f"\n🎯 Step 2: Focused Prompt Processing")
    destination_profiles = {}
    
    for dest in destinations:
        print(f"  🧠 Processing {dest} with focused prompts...")
        try:
            # Process with focused prompts (includes web context if available)
            dest_web_data = web_data.get(dest, {})
            profile = await focused_processor.process_destination(dest, dest_web_data)
            destination_profiles[dest] = profile
            
            theme_count = len(profile.get('affinities', []))
            avg_confidence = profile.get('processing_metadata', {}).get('average_confidence', 0)
            print(f"    ✅ Generated {theme_count} themes for {dest} (avg confidence: {avg_confidence:.2f})")
            
        except Exception as e:
            logger.error(f"Focused processing failed for {dest}: {e}")
            print(f"    ❌ Failed to process {dest}")
            continue
    
    # Step 3: Enhanced Intelligence Processing
    print(f"\n✨ Step 3: Enhanced Intelligence Processing")
    
    if destination_profiles:
        # Process with enhanced intelligence
        processed_files = processor.process_destinations_with_progress(
            destination_profiles, 
            generate_dashboard=True
        )
        
        print(f"\n🎉 Full pipeline complete!")
        print(f"📊 Successfully processed: {len(processed_files)} destinations")
        
        # Cleanup LLM resources
        try:
            await llm_generator.cleanup()
        except Exception as e:
            logger.debug(f"LLM cleanup warning: {e}")
        
        return processed_files
    else:
        print(f"\n❌ No destinations were successfully processed")
        
        # Cleanup LLM resources even on failure
        try:
            await llm_generator.cleanup()
        except Exception as e:
            logger.debug(f"LLM cleanup warning: {e}")
            
        return {}

async def run_demo_mode(destinations: List[str], config: Dict[str, Any]) -> Dict[str, str]:
    """Run demo mode with sample data (no web discovery)."""
    
    print(f"\n🎭 DEMO MODE")
    print(f"Processing {len(destinations)} destinations with sample data (no web discovery)")
    print("="*70)
    
    # Use the enhanced data processor directly for demo
    from src.enhanced_data_processor import EnhancedDataProcessor
    
    processor = EnhancedDataProcessor(config)
    
    # Generate rich sample data for all destinations
    demo_data = {}
    
    # Sample theme templates for generating diverse data
    theme_templates = [
        {"category": "culture", "themes": ["Cultural Heritage", "Art and Museums", "Traditional Experiences", "Local Festivals", "Historic Sites"]},
        {"category": "food", "themes": ["Culinary Excellence", "Street Food Scene", "Fine Dining", "Local Specialties", "Food Markets"]},
        {"category": "adventure", "themes": ["Outdoor Adventures", "Thrill Seeking", "Extreme Sports", "Nature Exploration", "Active Tourism"]},
        {"category": "luxury", "themes": ["High-end Indulgence", "Premium Experiences", "Luxury Shopping", "Upscale Accommodations", "VIP Services"]},
        {"category": "entertainment", "themes": ["Nightlife Scene", "Live Entertainment", "Music and Arts", "Theater and Shows", "Entertainment Districts"]},
        {"category": "nature", "themes": ["Natural Beauty", "Scenic Landscapes", "Wildlife Encounters", "Outdoor Recreation", "Eco-Tourism"]},
        {"category": "family", "themes": ["Family Fun", "Kid-Friendly Activities", "Educational Experiences", "Theme Parks", "Family Attractions"]},
        {"category": "romance", "themes": ["Romantic Getaways", "Couple Activities", "Intimate Dining", "Sunset Views", "Romantic Walks"]},
        {"category": "wellness", "themes": ["Relaxation and Wellness", "Spa Retreats", "Health Tourism", "Mindfulness Experiences", "Fitness Activities"]},
        {"category": "urban", "themes": ["City Life", "Urban Exploration", "Modern Architecture", "Shopping Districts", "Metropolitan Vibes"]}
    ]
    
    for dest in destinations:
        # Generate 6-8 diverse themes per destination
        import random
        random.seed(hash(dest))  # Consistent randomization based on destination name
        
        num_themes = random.randint(6, 8)
        selected_categories = random.sample(theme_templates, min(num_themes, len(theme_templates)))
        
        affinities = []
        for i, cat_info in enumerate(selected_categories):
            theme_name = random.choice(cat_info["themes"])
            
            affinity = {
                "category": cat_info["category"],
                "theme": theme_name,
                "sub_themes": [f"{theme_name} aspect {j+1}" for j in range(3)],
                "confidence": round(random.uniform(0.65, 0.9), 3),
                "seasonality": {
                    "peak": random.sample(["March", "April", "May", "June", "September", "October", "November"], 3),
                    "avoid": random.sample(["July", "August", "December", "January", "February"], random.randint(0, 2))
                },
                "traveler_types": random.sample(["solo", "couple", "family", "group"], random.randint(2, 4)),
                "price_point": random.choice(["budget", "mid", "luxury"]),
                "rationale": f"{dest} offers excellent {theme_name.lower()} experiences with unique local character and attractions.",
                "unique_selling_points": [f"Authentic {theme_name.lower()}", f"High-quality {cat_info['category']} scene", "Memorable experiences"]
            }
            affinities.append(affinity)
        
        demo_data[dest] = {"affinities": affinities}
    
    if not demo_data:
        print("❌ No sample data available for demo mode")
        return {}
    
    # Process with enhanced intelligence (but no web discovery)
    processed_files = processor.process_destinations_with_progress(demo_data, generate_dashboard=True)
    
    return processed_files

def start_development_server(port: int = 8000, open_browser: bool = True):
    """Start the development server for existing data."""
    
    print(f"\n🌐 DEVELOPMENT SERVER MODE")
    print("="*50)
    
    try:
        import webbrowser
        import http.server
        import socketserver
        import threading
        import time
        import socket
        
        # Function to find an available port
        def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
            for test_port in range(start_port, start_port + max_attempts):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        s.bind(('', test_port))
                        return test_port
                    except OSError:
                        continue
            raise RuntimeError(f"Could not find available port in range {start_port}-{start_port + max_attempts}")
        
        # Find an available port
        available_port = find_available_port(port)
        if available_port != port:
            print(f"⚠️  Port {port} is in use, using port {available_port} instead")
        
        # Ensure staging is up to date
        staging_manager = DevStagingManager()
        
        # Find the latest session directory
        import glob
        session_dirs = glob.glob("outputs/session_*")
        if session_dirs:
            latest_session = max(session_dirs, key=os.path.getctime)
            success = staging_manager.stage_latest_session(latest_session)
            if not success:
                print(f"⚠️  Failed to stage session: {latest_session}")
        else:
            print("⚠️  No session directories found to stage")
        
        # Server configuration
        DIRECTORY = "dev_staging/dashboard"
        
        if not os.path.exists(DIRECTORY):
            print(f"❌ Dashboard directory not found: {DIRECTORY}")
            print(f"💡 Run with --mode full or --mode demo first to generate data")
        return

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=DIRECTORY, **kwargs)
            
            def log_message(self, format, *args):
                # Suppress request logging for cleaner output
                pass
        
        def run_server():
            with socketserver.TCPServer(("", available_port), Handler) as httpd:
                print(f"🌐 Server running at: http://localhost:{available_port}")
                print(f"📁 Serving directory: {DIRECTORY}")
                print(f"🔗 Dashboard URL: http://localhost:{available_port}/index.html")
                print(f"📋 Press Ctrl+C to stop server")
                
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print(f"\n🛑 Server stopped")
                    httpd.shutdown()
        
        # Start server in background thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Give server time to start
        time.sleep(1)
        
        # Open browser
        if open_browser:
            dashboard_url = f"http://localhost:{available_port}/index.html"
            print(f"🌐 Opening dashboard in browser: {dashboard_url}")
            webbrowser.open(dashboard_url)
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n🛑 Shutting down...")
            
    except Exception as e:
        logger.error(f"Failed to start development server: {e}")
        print(f"❌ Failed to start development server: {e}")

async def main():
    """Main entry point with multiple processing modes."""
    
    args = parse_arguments()
    
    print("🚀 SmartDestinationThemes Processing System")
    print("=" * 60)
    
    # Load configuration
    print("🔧 Loading configuration...")
    config = load_config()
    
    if args.mode == 'server':
        # Development server mode
        start_development_server(port=args.port, open_browser=not args.no_browser)
        return
    
    # Get destinations to process
    print("📊 Loading destinations...")
    destinations = get_destinations_to_process(args.destinations)
    print(f"✅ Loaded {len(destinations)} destinations: {', '.join(destinations)}")
    
    try:
        if args.mode == 'full':
            # Full pipeline with web discovery
            processed_files = await run_full_pipeline(destinations, config)
        elif args.mode == 'demo':
            # Demo mode with sample data
            processed_files = await run_demo_mode(destinations, config)
        else:
            print(f"❌ Unknown mode: {args.mode}")
            return
        
        if processed_files:
            print(f"\n🎉 Processing Complete!")
            print(f"📊 Successfully processed: {len(processed_files)} destinations")
            
            # Stage latest data for development server
            print(f"\n📁 Staging latest data for development server...")
            staging_manager = DevStagingManager()
            
            # Find the latest session directory
            import glob
            session_dirs = glob.glob("outputs/session_*")
            if session_dirs:
                latest_session = max(session_dirs, key=os.path.getctime)
                success = staging_manager.stage_latest_session(latest_session)
                if not success:
                    print(f"⚠️  Failed to stage session: {latest_session}")
            else:
                print("⚠️  No session directories found to stage")
            
            # Offer to start development server
            if not args.no_browser:
                print(f"\n🌐 Starting development server...")
                start_development_server(port=args.port, open_browser=True)
            else:
                print(f"\n💡 To view results, run: python main.py --mode server")
        else:
            print("❌ No destinations were processed successfully")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        print(f"❌ Processing failed: {e}")
        return

if __name__ == "__main__":
    asyncio.run(main()) 