#!/usr/bin/env python3
"""
Standalone Seasonal Image Generator

Generate seasonal images for destinations without running the full destination discovery workflow.
Useful for:
- Adding images to existing destinations
- Testing image generation in isolation 
- Regenerating images with different settings
- Batch processing multiple destinations
"""

import asyncio
import argparse
import sys
import os
import time
from pathlib import Path
from typing import List, Optional
import yaml
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.seasonal_image_generator import SeasonalImageGenerator

class StandaloneSeasonalGenerator:
    """Standalone seasonal image generator with progress tracking and batch processing"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the generator"""
        
        # Load environment and configuration
        load_dotenv()
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize image generator
        self.image_generator = SeasonalImageGenerator(self.config)
        
        # Get seasonal config
        self.seasonal_config = self.config.get('seasonal_imagery', {})
        
        # Default destinations from config
        self.default_destinations = self.config.get('destinations', [])
        
        print("🎨 Standalone Seasonal Image Generator")
        print("=" * 50)
        print(f"✅ Configuration loaded from {config_path}")
        print(f"✅ DALL-E Model: {self.seasonal_config.get('model', 'dall-e-3')}")
        print(f"✅ Image Size: {self.seasonal_config.get('image_size', '1024x1024')}")
        print(f"✅ Available Destinations: {len(self.default_destinations)}")
    
    async def generate_for_destination(self, destination: str, output_dir: Path, 
                                     force_regenerate: bool = False) -> bool:
        """Generate seasonal images for a single destination"""
        
        print(f"\n🎯 Processing: {destination}")
        print("-" * 40)
        
        # Create destination-specific output directory
        dest_output_dir = output_dir / "images"
        
        # Check if images already exist
        existing_images = self._check_existing_images(destination, dest_output_dir)
        if existing_images and not force_regenerate:
            print(f"⚠️  Images already exist for {destination}")
            print(f"   Found: {', '.join(existing_images)}")
            print("   Use --force to regenerate")
            return True
        
        # Generate images
        start_time = time.time()
        
        try:
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                self.image_generator.generate_seasonal_images,
                destination,
                dest_output_dir
            )
            
            processing_time = time.time() - start_time
            
            # Report results
            successful_seasons = [season for season, data in results.items() 
                                if season != 'collage' and 'error' not in data]
            failed_seasons = [season for season, data in results.items() 
                            if season != 'collage' and 'error' in data]
            
            print(f"✅ Generated {len(successful_seasons)} seasonal images in {processing_time:.1f}s")
            
            if successful_seasons:
                print(f"   🌸 Seasons: {', '.join(successful_seasons)}")
            
            if failed_seasons:
                print(f"   ❌ Failed: {', '.join(failed_seasons)}")
            
            # Check for collage
            if 'collage' in results and 'error' not in results['collage']:
                print("   🖼️  Seasonal collage created")
            
            return len(successful_seasons) > 0
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"❌ Failed to generate images for {destination}: {e}")
            print(f"   Processing time: {processing_time:.1f}s")
            return False
    
    def _check_existing_images(self, destination: str, output_dir: Path) -> List[str]:
        """Check for existing seasonal images"""
        dest_name = destination.lower().replace(', ', '_').replace(' ', '_').replace(',', '')
        dest_dir = output_dir / dest_name
        
        if not dest_dir.exists():
            return []
        
        seasons = ['spring', 'summer', 'autumn', 'winter']
        existing = []
        
        for season in seasons:
            image_path = dest_dir / f"{season}.jpg"
            if image_path.exists():
                existing.append(season)
        
        return existing
    
    async def generate_batch(self, destinations: List[str], output_dir: Path,
                           force_regenerate: bool = False, max_concurrent: int = 3) -> dict:
        """Generate images for multiple destinations with controlled concurrency"""
        
        print(f"\n🚀 Batch Processing: {len(destinations)} destinations")
        print(f"📁 Output Directory: {output_dir}")
        print(f"⚡ Max Concurrent: {max_concurrent}")
        print("=" * 50)
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process destinations with semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(destination):
            async with semaphore:
                return await self.generate_for_destination(destination, output_dir, force_regenerate)
        
        # Execute batch processing
        start_time = time.time()
        tasks = [process_with_semaphore(dest) for dest in destinations]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Compile results
        success_count = sum(1 for result in results if result is True)
        failure_count = len(destinations) - success_count
        
        print("\n" + "=" * 50)
        print("📊 Batch Processing Complete")
        print(f"✅ Successful: {success_count}/{len(destinations)}")
        print(f"❌ Failed: {failure_count}")
        print(f"⏱️  Total Time: {total_time:.1f}s")
        print(f"📈 Average: {total_time/len(destinations):.1f}s per destination")
        
        return {
            'total': len(destinations),
            'successful': success_count,
            'failed': failure_count,
            'processing_time': total_time,
            'results': dict(zip(destinations, results))
        }
    
    def list_configured_destinations(self):
        """List all destinations configured in the system"""
        print("\n📋 Configured Destinations:")
        print("=" * 30)
        
        for i, dest in enumerate(self.default_destinations, 1):
            print(f"{i:2d}. {dest}")
        
        print(f"\nTotal: {len(self.default_destinations)} destinations")
    
    def check_api_status(self):
        """Check OpenAI API key and DALL-E availability"""
        print("\n🔍 API Status Check:")
        print("-" * 20)
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print("✅ OpenAI API key found")
            print(f"   Key: {api_key[:8]}...{api_key[-4:]}")
        else:
            print("❌ OpenAI API key not found")
            print("   Set OPENAI_API_KEY in your .env file")
            return False
        
        # Test DALL-E configuration
        enabled = self.seasonal_config.get('enabled', False)
        model = self.seasonal_config.get('model', 'dall-e-3')
        
        print(f"✅ Seasonal imagery enabled: {enabled}")
        print(f"✅ DALL-E model: {model}")
        
        return True

async def main():
    """Main function with command line interface"""
    
    parser = argparse.ArgumentParser(
        description="Generate seasonal images for travel destinations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate images for a single destination
  python generate_seasonal_images.py --destination "Tokyo, Japan"
  
  # Generate for multiple destinations
  python generate_seasonal_images.py --destination "Tokyo, Japan" "Paris, France"
  
  # Generate for all configured destinations
  python generate_seasonal_images.py --all
  
  # Force regenerate existing images
  python generate_seasonal_images.py --all --force
  
  # Custom output directory
  python generate_seasonal_images.py --all --output custom_images/
  
  # List configured destinations
  python generate_seasonal_images.py --list
  
  # Check API status
  python generate_seasonal_images.py --check-api
        """)
    
    parser.add_argument('--destination', '-d', nargs='+', 
                       help='Destination(s) to generate images for')
    parser.add_argument('--all', '-a', action='store_true',
                       help='Generate images for all configured destinations')
    parser.add_argument('--output', '-o', type=str, default='seasonal_images_output',
                       help='Output directory (default: seasonal_images_output)')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Force regenerate existing images')
    parser.add_argument('--concurrent', '-c', type=int, default=3,
                       help='Maximum concurrent generations (default: 3)')
    parser.add_argument('--config', type=str, default='config/config.yaml',
                       help='Configuration file path')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List all configured destinations')
    parser.add_argument('--check-api', action='store_true',
                       help='Check API status and configuration')
    
    args = parser.parse_args()
    
    try:
        # Initialize generator
        generator = StandaloneSeasonalGenerator(args.config)
        
        # Handle list command
        if args.list:
            generator.list_configured_destinations()
            return 0
        
        # Handle API check command
        if args.check_api:
            if generator.check_api_status():
                print("\n✅ API configuration looks good!")
                return 0
            else:
                print("\n❌ API configuration issues found")
                return 1
        
        # Determine destinations to process
        destinations = []
        
        if args.all:
            destinations = generator.default_destinations
            if not destinations:
                print("❌ No destinations configured in config.yaml")
                return 1
        elif args.destination:
            destinations = args.destination
        else:
            print("❌ Must specify --destination, --all, --list, or --check-api")
            parser.print_help()
            return 1
        
        # Set up output directory
        output_dir = Path(args.output)
        
        # Check API before proceeding
        if not generator.check_api_status():
            return 1
        
        # Generate images
        if len(destinations) == 1:
            # Single destination
            success = await generator.generate_for_destination(
                destinations[0], output_dir, args.force
            )
            return 0 if success else 1
        else:
            # Batch processing
            results = await generator.generate_batch(
                destinations, output_dir, args.force, args.concurrent
            )
            return 0 if results['failed'] == 0 else 1
            
    except KeyboardInterrupt:
        print("\n\n🛑 Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 