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
import warnings
from typing import List, Dict, Any

# Suppress gRPC and coroutine warnings early
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*was never awaited.*")
warnings.filterwarnings("ignore", message=".*grpc.*")
warnings.filterwarnings("ignore", message=".*POLLER.*")

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
    
    # Seasonal image generation options
    parser.add_argument('--seasonal-images', action='store_true',
                       help='Enable seasonal image generation during processing')
    parser.add_argument('--no-seasonal-images', action='store_true',
                       help='Disable seasonal image generation (overrides config)')
    parser.add_argument('--force-seasonal-images', action='store_true',
                       help='Force regenerate existing seasonal images')
    parser.add_argument('--seasonal-images-only', action='store_true',
                       help='Only generate seasonal images (skip main processing)')
    
    return parser.parse_args()

def load_config():
    """Load application configuration."""
    try:
        config = load_app_config()
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return None

def apply_seasonal_image_config(config: Dict[str, Any], args) -> Dict[str, Any]:
    """Apply seasonal image command line arguments to configuration."""
    
    # Get current seasonal imagery config
    seasonal_config = config.get('seasonal_imagery', {})
    
    # Apply command line overrides
    if args.seasonal_images:
        seasonal_config['enabled'] = True
        print("🎨 Seasonal image generation enabled via --seasonal-images")
    elif args.no_seasonal_images:
        seasonal_config['enabled'] = False
        print("🚫 Seasonal image generation disabled via --no-seasonal-images")
    
    if args.force_seasonal_images:
        seasonal_config['force_regenerate'] = True
        print("🔄 Force regenerate seasonal images enabled")
    
    # Update config
    config['seasonal_imagery'] = seasonal_config
    return config

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

async def run_seasonal_images_only(destinations: List[str], config: Dict[str, Any], force_regenerate: bool = False) -> bool:
    """Run seasonal image generation only (skip main processing)."""
    
    print(f"\n🎨 Seasonal Images Only Mode")
    print(f"🎯 Generating seasonal images for {len(destinations)} destinations")
    print("="*60)
    
    # Import seasonal image generator
    from src.seasonal_image_generator import SeasonalImageGenerator
    from pathlib import Path
    import time
    
    # Initialize generator
    image_generator = SeasonalImageGenerator(config)
    
    # Check API status
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found")
        print("   Set OPENAI_API_KEY in your .env file")
        return False
    
    print(f"✅ OpenAI API key found")
    
    # Create output directory with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(f"seasonal_images_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output directory: {output_dir}")
    
    # Process destinations
    total_start_time = time.time()
    successful_destinations = 0
    failed_destinations = 0
    
    for i, destination in enumerate(destinations, 1):
        print(f"\n🎯 [{i}/{len(destinations)}] Processing: {destination}")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            # Check for existing images
            dest_name = destination.lower().replace(', ', '_').replace(' ', '_').replace(',', '')
            dest_images_dir = output_dir / "images" / dest_name
            
            existing_seasons = []
            if dest_images_dir.exists():
                seasons = ['spring', 'summer', 'autumn', 'winter']
                for season in seasons:
                    if (dest_images_dir / f"{season}.jpg").exists():
                        existing_seasons.append(season)
            
            if existing_seasons and not force_regenerate:
                print(f"⚠️  Images already exist: {', '.join(existing_seasons)}")
                print("   Use --force-seasonal-images to regenerate")
                successful_destinations += 1
                continue
            
            # Generate images
            images_generated = await asyncio.get_event_loop().run_in_executor(
                None,
                image_generator.generate_seasonal_images,
                destination,
                output_dir / "images"
            )
            
            processing_time = time.time() - start_time
            
            # Report results
            successful_seasons = [season for season, data in images_generated.items() 
                                if season != 'collage' and 'error' not in data]
            failed_seasons = [season for season, data in images_generated.items() 
                            if season != 'collage' and 'error' in data]
            
            print(f"✅ Generated {len(successful_seasons)} seasonal images in {processing_time:.1f}s")
            
            if successful_seasons:
                print(f"   🌸 Seasons: {', '.join(successful_seasons)}")
            
            if failed_seasons:
                print(f"   ❌ Failed: {', '.join(failed_seasons)}")
            
            # Check for collage
            if 'collage' in images_generated and 'error' not in images_generated['collage']:
                print("   🖼️  Seasonal collage created")
            
            if len(successful_seasons) > 0:
                successful_destinations += 1
            else:
                failed_destinations += 1
                
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"❌ Failed to generate images: {e}")
            print(f"   Processing time: {processing_time:.1f}s")
            failed_destinations += 1
    
    # Final summary
    total_time = time.time() - total_start_time
    
    print("\n" + "="*60)
    print("🎨 Seasonal Image Generation Complete")
    print(f"✅ Successful: {successful_destinations}/{len(destinations)}")
    print(f"❌ Failed: {failed_destinations}")
    print(f"⏱️  Total Time: {total_time:.1f}s")
    print(f"📈 Average: {total_time/len(destinations):.1f}s per destination")
    print(f"📁 Images saved to: {output_dir.absolute()}")
    
    return failed_destinations == 0

async def run_full_pipeline(destinations: List[str], config: Dict[str, Any]) -> Dict[str, str]:
    """Run the complete processing pipeline for all destinations using agent integration."""
    
    # Import agent integration layer
    from src.agent_integration_layer import AgentCompatibilityLayer
    
    print(f"\n⚙️  Initializing processing system...")
    
    # Initialize agent integration layer
    agent_layer = AgentCompatibilityLayer(config)
    await agent_layer.initialize()
    
    # Check if using agents or legacy system
    agents_enabled = config.get('agents', {}).get('enabled', False)
    migration_mode = config.get('agents', {}).get('migration_mode', 'legacy_only')
    
    if agents_enabled or migration_mode != 'legacy_only':
        print(f"🤖 Using Agent System - Mode: {migration_mode}")
    else:
        print(f"🔧 Using Legacy System")
    
    try:
        # Process destinations using the integration layer
        result = await agent_layer.process_destinations(destinations)
        
        # Extract processed files for compatibility (ProcessingResult object)
        processed_files = result.processed_files
        
        # Display results
        print(f"\n🎉 Processing Complete!")
        print(f"📊 System Used: {result.system_used}")
        print(f"📈 Destinations Processed: {result.destinations_processed}")
        print(f"🎯 Successful Destinations: {result.successful_destinations}")
        print(f"⏱️  Processing Time: {result.processing_time:.1f}s")
        
        # Display agent-specific metrics if available
        if result.agent_results:
            agent_results = result.agent_results
            quality_scores = [r.quality_score for r in agent_results.values() if hasattr(r, 'quality_score')]
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                print(f"🏆 Average Quality Score: {avg_quality:.3f}")
        
        # Display comparison data if available
        if result.comparison_data:
            comparison = result.comparison_data['comparison_metrics']
            print(f"\n🔀 System Comparison:")
            print(f"  Legacy Time: {comparison.get('performance_comparison', {}).get('legacy_time', 0):.1f}s")
            print(f"  Agent Time: {comparison.get('performance_comparison', {}).get('agent_time', 0):.1f}s")
            speedup = comparison.get('performance_comparison', {}).get('speedup_factor', 0)
            if speedup > 1:
                print(f"  🚀 Speedup: {speedup:.2f}x faster with agents")
            elif speedup > 0 and speedup < 1:
                print(f"  🐌 Slowdown: {1/speedup:.2f}x slower with agents")
        
        # Performance summary from integration layer
        performance_summary = agent_layer.get_performance_summary()
        if performance_summary.get('agent_performance'):
            agent_perf = performance_summary['agent_performance']
            print(f"\n🤖 Agent Performance Summary:")
            print(f"  Average Processing Time: {agent_perf.get('average_processing_time', 0):.1f}s")
            print(f"  Average Success Rate: {agent_perf.get('average_success_rate', 0):.1%}")
            print(f"  Average Quality Score: {agent_perf.get('average_quality_score', 0):.3f}")
        
        return processed_files
        
    except Exception as e:
        logger.error(f"Processing pipeline failed: {e}")
        print(f"❌ Processing failed: {e}")
        return {}
    
    finally:
        # Cleanup integration layer
        try:
            await agent_layer.cleanup()
        except Exception as e:
            logger.debug(f"Integration layer cleanup warning: {e}")

# Legacy pipeline function (kept for reference and fallback)
async def run_legacy_pipeline(destinations: List[str], config: Dict[str, Any]) -> Dict[str, str]:
    """Run the original legacy processing pipeline (for reference/fallback)."""
    
    # Import here to avoid circular imports and reduce startup time
    from src.enhanced_data_processor import EnhancedDataProcessor
    from src.focused_llm_generator import FocusedLLMGenerator
    from src.focused_prompt_processor import FocusedPromptProcessor
    from tools.web_discovery_tools import WebDiscoveryTool
    from src.monitoring import AffinityMonitoring
    
    # Initialize components
    print(f"\n⚙️  Initializing legacy processing components...")
    
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
    
    # Cleanup LLM resources properly
    try:
        await llm_generator.cleanup()
        logger.debug("LLM cleanup completed successfully")
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
    
    # Apply seasonal image configuration
    config = apply_seasonal_image_config(config, args)
    
    # Get destinations to process
    print("📊 Loading destinations...")
    try:
        destinations = get_destinations_to_process(args.destinations)
        print(f"✅ Loaded {len(destinations)} destinations: {', '.join(destinations)}")
    except Exception as e:
        print(f"❌ Error loading destinations: {e}")
        return
    
    try:
        # Handle seasonal images only mode
        if args.seasonal_images_only:
            success = await run_seasonal_images_only(
                destinations, 
                config, 
                force_regenerate=args.force_seasonal_images
            )
            
            if success:
                print(f"\n🎉 Seasonal image generation completed successfully!")
            else:
                print(f"\n❌ Some seasonal image generations failed")
            return
        
        # Full pipeline mode with optional seasonal images
        processed_files = await run_full_pipeline(destinations, config)
        
        if processed_files:
            print(f"\n🎉 Processing Complete!")
            print(f"📊 Successfully processed: {len(processed_files)} destinations")
            
            # Display seasonal image status if enabled
            seasonal_config = config.get('seasonal_imagery', {})
            if seasonal_config.get('enabled', False):
                print(f"🎨 Seasonal images: Enabled (Phase 3.5 integration)")
            else:
                print(f"🎨 Seasonal images: Disabled")
                print(f"   💡 Use --seasonal-images to enable")
            
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
                    
                # Seasonal images availability note
                seasonal_config = config.get('seasonal_imagery', {})
                if seasonal_config.get('enabled', False):
                    print(f"\n🎨 Seasonal Images:")
                    print(f"   • Images integrated into destination viewers")
                    print(f"   • 4 seasons per destination + collages")
                    print(f"   • Generated via DALL-E 3 during processing")
        else:
            print(f"\n❌ No data was processed successfully")
            
    except KeyboardInterrupt:
        print(f"\n🛑 Operation cancelled by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 