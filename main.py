#!/usr/bin/env python3
"""
SmartDestinationThemes Main Processing Script

Processing Mode:
- Full Mode: Complete pipeline with web discovery and focused prompt processing
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
    parser.add_argument('--destinations', nargs='+', 
                       help='Specific destinations to process (overrides default list)')
    parser.add_argument('--no-browser', action='store_true',
                       help='Do not show server instructions after processing')
    return parser.parse_args()

def load_config():
    """Load application configuration."""
    try:
        config = load_app_config()
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return None

def get_destinations_to_process(custom_destinations: List[str] = None) -> List[str]:
    """Get list of destinations to process."""
    
    if custom_destinations:
        logger.info(f"Using custom destinations: {custom_destinations}")
        return custom_destinations
    
    # Load destinations from config
    logger.info("Loading destinations from config.yaml")
    config = load_app_config()
    destinations = config.get('destinations', [])
    
    if not destinations:
        raise ValueError("No destinations found in configuration. Please add destinations to config.yaml or use --destinations argument.")
    
    return destinations

async def run_full_pipeline(destinations: List[str], config: Dict[str, Any]) -> Dict[str, str]:
    """Run the complete processing pipeline for all destinations."""
    
    # Import here to avoid circular imports and reduce startup time
    from src.enhanced_data_processor import EnhancedDataProcessor
    from src.focused_llm_generator import FocusedLLMGenerator
    from src.focused_prompt_processor import FocusedPromptProcessor
    from tools.web_discovery_tools import WebDiscoveryTool
    from src.monitoring import AffinityMonitoring
    
    # Initialize components
    print(f"\n⚙️  Initializing processing components...")
    
    # Initialize LLM generator
    # Use the primary LLM provider from config
    primary_provider = config.get('llm_settings', {}).get('provider', 'gemini')  # Default to gemini
    llm_generator = FocusedLLMGenerator(primary_provider, config)
    
    # Initialize focused prompt processor
    prompt_processor = FocusedPromptProcessor(llm_generator, config)
    
    # Initialize web discovery tool
    web_discovery = WebDiscoveryTool(config)
    
    # Initialize enhanced data processor
    processor = EnhancedDataProcessor(config)
    
    # Initialize monitoring
    monitor = AffinityMonitoring(config)
    
    print(f"🌐 Starting web discovery for {len(destinations)} destinations...")
    
    # Phase 1: Web Discovery (parallel for all destinations)
    import asyncio
    from tqdm import tqdm
    
    # Create semaphore to limit concurrent web discovery
    max_concurrent_discovery = min(3, len(destinations))  # Limit to 3 concurrent
    discovery_semaphore = asyncio.Semaphore(max_concurrent_discovery)
    
    async def discover_destination(dest):
        async with discovery_semaphore:
            return await web_discovery.discover_destination_content(dest)
    
    # Bounded discovery function to prevent too many concurrent requests
    async def bounded_discover(dest):
        try:
            return dest, await discover_destination(dest)
        except Exception as e:
            logger.error(f"Web discovery failed for {dest}: {e}")
            return dest, []
    
    # Run web discovery for all destinations in parallel
    discovery_tasks = [bounded_discover(dest) for dest in destinations]
    
    # Use tqdm for progress tracking
    discovery_results = {}
    with tqdm(total=len(destinations), desc="Web discovery", unit="dest") as pbar:
        for coro in asyncio.as_completed(discovery_tasks):
            dest, pages = await coro
            discovery_results[dest] = pages
            pbar.update(1)
            pbar.set_description(f"Discovered {dest}")
    
    print(f"✅ Web discovery completed for {len(discovery_results)} destinations")
    
    # Phase 2: Affinity Generation from Web Data
    print(f"\n🎯 Generating affinities from web discovery data...")
    
    # Generate affinities for each destination using focused prompt processor
    destinations_data = {}
    affinity_progress = tqdm(discovery_results.items(), 
                           desc="Generating affinities",
                           unit="dest",
                           colour="green")
    
    for destination_name, web_data in affinity_progress:
        affinity_progress.set_description(f"Processing {destination_name}")
        
        try:
            # Convert web_data to the format expected by focused prompt processor
            web_data_formatted = {
                'content': web_data if isinstance(web_data, list) else []
            }
            
            # Generate affinities using focused prompt processor
            destination_profile = await prompt_processor.process_destination(
                destination_name, 
                web_data_formatted
            )
            
            # Store the destination profile with affinities
            destinations_data[destination_name] = destination_profile
            
            logger.info(f"Generated {len(destination_profile.get('affinities', []))} affinities for {destination_name}")
            
        except Exception as e:
            logger.error(f"Error generating affinities for {destination_name}: {e}")
            # Create empty profile as fallback
            destinations_data[destination_name] = {
                'destination': destination_name,
                'affinities': [],
                'processing_metadata': {
                    'error': str(e),
                    'processing_method': 'focused_prompts'
                }
            }
    
    affinity_progress.close()
    print(f"✅ Affinity generation completed for {len(destinations_data)} destinations")
    
    # Phase 3: Enhanced Processing
    print(f"\n🧠 Starting enhanced processing pipeline...")
    
    # Process each destination with the enhanced processor
    processed_files = processor.process_destinations_with_progress(
        destinations_data, 
        web_data=discovery_results,
        generate_dashboard=True
    )
    
    # Phase 4: Performance Summary
    print(f"\n🎉 Enhanced Pipeline Complete!")
    print(f"📊 Performance Summary:")
    
    # Get performance stats (simplified since monitor methods may differ)
    try:
        print(f"  📈 Total destinations: {len(destinations)}")
        if processed_files:
            print(f"  🎯 Successfully processed: {len(processed_files)} destinations")
        
        # Enhanced LLM stats - handle async method properly
        try:
            llm_stats = await llm_generator.get_performance_stats()
            if llm_stats.get('cache_hit_rate', 0) > 0:
                print(f"  💾 Cache hit rate: {llm_stats['cache_hit_rate']:.1%}")
            if llm_stats.get('features_enabled', {}).get('connection_pool', False):
                pool_stats = llm_stats.get('connection_pool_stats', {})
                print(f"  🔗 Connection pool efficiency: {pool_stats.get('pool_hit_rate', 0):.1%}")
        except Exception as e:
            logger.debug(f"LLM stats unavailable: {e}")
    except Exception as e:
        logger.debug(f"Failed to get enhanced performance stats: {e}")
    
    # Cleanup LLM resources
    try:
        await llm_generator.cleanup()
    except Exception as e:
        logger.debug(f"LLM cleanup warning: {e}")
    
    return processed_files

# Server functionality moved to start_server.py for standalone operation

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
        # Full pipeline mode (only mode now)
        processed_files = await run_full_pipeline(destinations, config)
        
        if processed_files:
            print(f"\n🎉 Processing Complete!")
            print(f"📊 Successfully processed: {len(processed_files)} destinations")
            
            # Stage latest data for development server
            print(f"\n📁 Staging latest data for development server...")
            from src.dev_staging_manager import DevStagingManager
            staging_manager = DevStagingManager()
            staging_manager.stage_latest_session()
            
            # Provide server instructions
            if not args.no_browser:
                print(f"\n🌐 To view your results:")
                print(f"📋 Run the standalone server:")
                print(f"   python start_server.py")
                print(f"")
                print(f"🔗 Or manually serve the dashboard:")
                print(f"   cd dev_staging/dashboard")
                print(f"   python -m http.server 8000")
                print(f"")
                print(f"📊 Available destinations:")
                for dest in destinations:
                    dest_filename = dest.lower().replace(', ', '__').replace(' ', '_')
                    print(f"   • {dest}: http://localhost:8000/{dest_filename}.html")
        else:
            print(f"\n❌ No data was processed successfully")
            
    except KeyboardInterrupt:
        print(f"\n🛑 Operation cancelled by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 