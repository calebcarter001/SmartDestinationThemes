#!/usr/bin/env python3
"""
SmartDestinationThemes Main Processing Script

Processing Modes:
- Full Mode: Complete pipeline with web discovery and focused prompt processing
- Server Mode: Start development server for viewing existing results
"""

import asyncio
import argparse
import logging
import os
import sys
from typing import List, Dict, Any

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools.config_loader import load_app_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='SmartDestinationThemes Processing System')
    parser.add_argument('--mode', choices=['full', 'server'], default='full',
                       help='Processing mode: full pipeline or development server')
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
    """Run full pipeline with enhanced performance optimizations."""
    
    print(f"\n🚀 FULL PIPELINE MODE (Enhanced Performance)")
    print(f"Processing {len(destinations)} destinations with complete workflow")
    
    # Check if performance optimizations are enabled
    perf_config = config.get('performance_optimization', {})
    if perf_config.get('enable_performance_profiling', False):
        print(f"🔧 Performance optimizations enabled:")
        if perf_config.get('enable_persistent_cache', False):
            print(f"  ✅ Persistent LLM caching")
        if perf_config.get('llm_connection_pool_size', 0) > 0:
            print(f"  ✅ LLM connection pooling ({perf_config['llm_connection_pool_size']} connections)")
        if perf_config.get('enable_work_stealing', False):
            print(f"  ✅ Work-stealing parallel processing")
        if perf_config.get('enable_streaming_results', False):
            print(f"  ✅ Streaming results")
    
    print("="*70)
    
    # Use the enhanced data processor with focused prompts
    from src.enhanced_data_processor import EnhancedDataProcessor
    from src.focused_prompt_processor import FocusedPromptProcessor
    
    processor = EnhancedDataProcessor(config)
    
    # Initialize enhanced LLM and focused prompt processor
    from src.focused_llm_generator import FocusedLLMGenerator
    provider = config.get("llm_settings", {}).get("provider", "gemini")
    llm_generator = FocusedLLMGenerator(provider, config)
    focused_processor = FocusedPromptProcessor(llm_generator, config)
    
    # Performance monitoring setup
    import time
    pipeline_start_time = time.time()
    performance_stats = {
        'destinations_processed': 0,
        'total_themes_generated': 0,
        'avg_processing_time_per_destination': 0.0,
        'web_discovery_time': 0.0,
        'llm_processing_time': 0.0,
        'enhancement_time': 0.0
    }
    
    # Step 1: Web Discovery for each destination (Enhanced with parallel processing)
    print(f"\n🌐 Step 1: Enhanced Web Discovery")
    web_data = {}
    
    from tools.web_discovery_tools import WebDiscoveryTool
    web_tool = WebDiscoveryTool(config)
    
    # Enhanced parallel web discovery
    web_start_time = time.time()
    max_concurrent_web = perf_config.get('max_concurrent_web_requests', 10)
    
    async def discover_destination(dest):
        try:
            discovery_result = await web_tool.discover_destination_content(dest)
            return dest, discovery_result
        except Exception as e:
            logger.error(f"Web discovery failed for {dest}: {e}")
            return dest, {"urls": [], "content": []}
    
    # Process web discovery in parallel batches
    semaphore = asyncio.Semaphore(max_concurrent_web)
    
    async def bounded_discover(dest):
        async with semaphore:
            return await discover_destination(dest)
    
    web_tasks = [bounded_discover(dest) for dest in destinations]
    web_results = await asyncio.gather(*web_tasks, return_exceptions=True)
    
    for result in web_results:
        if isinstance(result, Exception):
            logger.error(f"Web discovery error: {result}")
            continue
        dest, discovery_result = result
        web_data[dest] = discovery_result
        print(f"    ✅ Found {len(discovery_result.get('urls', []))} sources for {dest}")
    
    performance_stats['web_discovery_time'] = time.time() - web_start_time
    
    # Step 2: Enhanced Focused Prompt Processing
    print(f"\n🎯 Step 2: Enhanced Focused Prompt Processing")
    destination_profiles = {}
    
    llm_start_time = time.time()
    
    # Enhanced parallel processing with work stealing if enabled
    if perf_config.get('enable_work_stealing', False):
        print(f"  🔄 Using work-stealing parallel processing")
        # Process destinations with work stealing
        # For now, we'll use the existing approach but with enhanced monitoring
    
    for dest in destinations:
        dest_start_time = time.time()
        print(f"  🧠 Processing {dest} with enhanced focused prompts...")
        try:
            # Process with focused prompts (includes web context if available)
            dest_web_data = web_data.get(dest, {})
            profile = await focused_processor.process_destination(dest, dest_web_data)
            destination_profiles[dest] = profile
            
            theme_count = len(profile.get('affinities', []))
            avg_confidence = profile.get('processing_metadata', {}).get('average_confidence', 0)
            processing_time = time.time() - dest_start_time
            
            print(f"    ✅ Generated {theme_count} themes for {dest} (avg confidence: {avg_confidence:.2f}, {processing_time:.1f}s)")
            
            # Update performance stats
            performance_stats['destinations_processed'] += 1
            performance_stats['total_themes_generated'] += theme_count
            
        except Exception as e:
            logger.error(f"Focused processing failed for {dest}: {e}")
            print(f"    ❌ Failed to process {dest}")
            continue
    
    performance_stats['llm_processing_time'] = time.time() - llm_start_time
    
    # Step 3: Enhanced Intelligence Processing
    print(f"\n✨ Step 3: Enhanced Intelligence Processing")
    
    enhancement_start_time = time.time()
    
    if destination_profiles:
        # Process with enhanced intelligence - pass web_data for evidence collection
        processed_files = processor.process_destinations_with_progress(
            destination_profiles, 
            generate_dashboard=True,
            web_data=web_data  # Pass web data for evidence collection
        )
        
        performance_stats['enhancement_time'] = time.time() - enhancement_start_time
        total_pipeline_time = time.time() - pipeline_start_time
        
        # Enhanced performance reporting
        print(f"\n🎉 Enhanced Pipeline Complete!")
        print(f"📊 Performance Summary:")
        print(f"  📈 Total destinations: {performance_stats['destinations_processed']}")
        print(f"  🎯 Total themes generated: {performance_stats['total_themes_generated']}")
        print(f"  ⏱️  Total time: {total_pipeline_time:.2f}s")
        print(f"  🌐 Web discovery: {performance_stats['web_discovery_time']:.2f}s")
        print(f"  🧠 LLM processing: {performance_stats['llm_processing_time']:.2f}s")
        print(f"  ✨ Enhancement: {performance_stats['enhancement_time']:.2f}s")
        
        if performance_stats['destinations_processed'] > 0:
            avg_time = total_pipeline_time / performance_stats['destinations_processed']
            avg_themes = performance_stats['total_themes_generated'] / performance_stats['destinations_processed']
            print(f"  📊 Avg per destination: {avg_time:.2f}s, {avg_themes:.1f} themes")
        
        # Get enhanced performance stats from LLM generator
        try:
            llm_stats = await llm_generator.get_performance_stats()
            if llm_stats.get('cache_hit_rate', 0) > 0:
                print(f"  💾 Cache hit rate: {llm_stats['cache_hit_rate']:.1%}")
            if llm_stats.get('features_enabled', {}).get('connection_pool', False):
                pool_stats = llm_stats.get('connection_pool_stats', {})
                print(f"  🔗 Connection pool efficiency: {pool_stats.get('pool_hit_rate', 0):.1%}")
        except Exception as e:
            logger.debug(f"Failed to get enhanced performance stats: {e}")
        
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

def start_development_server(port: int = 8000, open_browser: bool = True):
    """Start development server for viewing results."""
    import http.server
    import socketserver
    import threading
    import webbrowser
    import socket
    import time
    import requests
    from pathlib import Path
    
    # Check if dev_staging/dashboard exists
    dashboard_dir = Path("dev_staging/dashboard")
    if not dashboard_dir.exists():
        print(f"💡 Run with --mode full first to generate data")
        return
    
    def is_server_running_with_content(port: int) -> bool:
        """Check if server is running on port and serving the right content."""
        try:
            response = requests.get(f"http://localhost:{port}/index.html", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def is_port_in_use(port: int) -> bool:
        """Check if a port is in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    # Check if server is already running with the right content
    if is_server_running_with_content(port):
        print(f"✅ Server already running on port {port}")
        if open_browser:
            dashboard_url = f"http://localhost:{port}/index.html"
            print(f"🌐 Opening dashboard in browser...")
            webbrowser.open(dashboard_url)
        else:
            print(f"🔗 Dashboard available at: http://localhost:{port}/index.html")
        return

    # If port is in use but not serving our content, find alternative
    if is_port_in_use(port):
        print(f"⚠️  Port {port} is in use by another service")
        # Try to find an available port
        for i in range(1, 11):  # Try ports 8001-8010
            test_port = port + i
            if not is_port_in_use(test_port):
                port = test_port
                print(f"🔄 Using port {port} instead")
                break
        else:
            print(f"❌ Could not find available port")
            return
    
    # Change to dashboard directory
    original_dir = os.getcwd()
    os.chdir(dashboard_dir)
    
    try:
        # Custom handler to suppress request logging
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(dashboard_dir), **kwargs)
            
            def log_message(self, format, *args):
                # Suppress request logging for cleaner output
                pass
        
        def run_server():
            with socketserver.TCPServer(("", port), Handler) as httpd:
                print(f"🌐 Server running at: http://localhost:{port}")
                print(f"📁 Serving from: {dashboard_dir.absolute()}")
                print(f"🔗 Dashboard URL: http://localhost:{port}/index.html")
                print(f"Press Ctrl+C to stop the server")
                
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print(f"\n🛑 Server stopped")
                    httpd.shutdown()
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(1)
        
        # Open browser if requested
        if open_browser:
            dashboard_url = f"http://localhost:{port}/index.html"
            print(f"🌐 Opening dashboard in browser...")
            webbrowser.open(dashboard_url)
        
        # Keep main thread alive
        try:
            while server_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n🛑 Shutting down server...")
            
    finally:
        # Return to original directory
        os.chdir(original_dir)

async def main():
    """Main entry point."""
    args = parse_arguments()
    
    print("🚀 SmartDestinationThemes Processing System")
    print("="*60)
    
    # Load configuration
    print("🔧 Loading configuration...")
    config = load_config()
    if not config:
        print("❌ Failed to load configuration")
        return
    
    # Get destinations to process
    print("📊 Loading destinations...")
    try:
        destinations = get_destinations_to_process(args.destinations)
        print(f"✅ Loaded {len(destinations)} destinations: {', '.join(destinations)}")
    except Exception as e:
        print(f"❌ Error loading destinations: {e}")
        return
    
    try:
        if args.mode == 'full':
            # Full pipeline mode
            processed_files = await run_full_pipeline(destinations, config)
            
            if processed_files:
                print(f"\n🎉 Processing Complete!")
                print(f"📊 Successfully processed: {len(processed_files)} destinations")
                
                # Stage latest data for development server
                print(f"\n📁 Staging latest data for development server...")
                from src.dev_staging_manager import DevStagingManager
                staging_manager = DevStagingManager()
                staging_manager.stage_latest_session()
                
                # Start development server
                print(f"\n🌐 Starting development server...")
                start_development_server(args.port, not args.no_browser)
            else:
                print(f"\n❌ No data was processed successfully")
                
        elif args.mode == 'server':
            # Development server mode
            print(f"\n🌐 DEVELOPMENT SERVER MODE")
            print("="*50)
            start_development_server(args.port, not args.no_browser)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Operation cancelled by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 