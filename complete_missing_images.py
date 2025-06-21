#!/usr/bin/env python3
"""
Complete Missing Seasonal Images

Smart script to complete missing seasonal images with DALL-E 3 rate limiting.
Analyzes existing exports and generates only the missing images.
"""

import asyncio
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml
from dotenv import load_dotenv
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
import sys
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.seasonal_image_generator import SeasonalImageGenerator

class MissingImageCompletor:
    """Complete missing seasonal images with rate limiting"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the missing image completor"""
        
        # Load configuration
        load_dotenv()
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize image generator
        self.image_generator = SeasonalImageGenerator(self.config)
        
        # Rate limiting settings for DALL-E 3
        self.rate_limit_images_per_minute = 5  # Conservative limit for Tier 1
        self.rate_limit_delay = 60 / self.rate_limit_images_per_minute  # 12 seconds between images
        
        # Seasons and expected files
        self.seasons = ['spring', 'summer', 'autumn', 'winter']
        self.expected_files = self.seasons  # Only 4 seasonal images, no collage
        
        print("🔧 Missing Image Completor")
        print("=" * 50)
        print(f"✅ Configuration loaded")
        print(f"✅ Rate limit: {self.rate_limit_images_per_minute} images/minute")
        print(f"✅ Delay between images: {self.rate_limit_delay:.1f} seconds")
    
    def analyze_missing_images(self, exports_dir: Path = Path("exports")) -> Dict[str, Dict]:
        """Analyze all exports to find missing seasonal images"""
        
        print(f"\n🔍 Analyzing exports in: {exports_dir}")
        print("-" * 40)
        
        if not exports_dir.exists():
            print(f"❌ Exports directory not found: {exports_dir}")
            return {}
        
        missing_analysis = {}
        total_destinations = 0
        complete_destinations = 0
        
        # Scan all destination export directories
        for dest_dir in exports_dir.glob("*/"):
            if not dest_dir.is_dir():
                continue
                
            destination_name = dest_dir.name.replace('_', ' ').title()
            total_destinations += 1
            
            # Find the latest export subdirectory
            export_subdirs = [d for d in dest_dir.glob("export_*") if d.is_dir()]
            if not export_subdirs:
                missing_analysis[destination_name] = {
                    'status': 'no_exports',
                    'missing_images': self.expected_files.copy(),
                    'existing_images': [],
                    'export_path': None
                }
                continue
            
            # Use the most recent export
            latest_export = max(export_subdirs, key=lambda x: x.name)
            images_dir = latest_export / "images"
            
            # Check for existing images
            existing_images = []
            missing_images = []
            
            if images_dir.exists():
                # Check for seasonal images
                for season in self.seasons:
                    season_file = images_dir / f"{season}.jpg"
                    if season_file.exists():
                        existing_images.append(season)
                    else:
                        missing_images.append(season)
            else:
                missing_images = self.expected_files.copy()
            
            # Determine status
            if not missing_images:
                status = 'complete'
                complete_destinations += 1
            elif not existing_images:
                status = 'empty'
            else:
                status = 'partial'
            
            missing_analysis[destination_name] = {
                'status': status,
                'missing_images': missing_images,
                'existing_images': existing_images,
                'export_path': latest_export,
                'images_dir': images_dir
            }
            
            # Print status
            if status == 'complete':
                print(f"✅ {destination_name}: Complete ({len(existing_images)}/4)")
            elif status == 'empty':
                print(f"❌ {destination_name}: No images (0/4)")
            else:
                print(f"⚠️  {destination_name}: Partial ({len(existing_images)}/4) - Missing: {', '.join(missing_images)}")
        
        # Summary
        incomplete_destinations = total_destinations - complete_destinations
        total_missing_images = sum(len(data['missing_images']) for data in missing_analysis.values())
        
        print(f"\n📊 Analysis Summary:")
        print(f"   Total destinations: {total_destinations}")
        print(f"   Complete: {complete_destinations}")
        print(f"   Incomplete: {incomplete_destinations}")
        print(f"   Total missing images: {total_missing_images}")
        
        if total_missing_images > 0:
            estimated_time = (total_missing_images * self.rate_limit_delay) / 60
            print(f"   ⏱️  Estimated completion time: {estimated_time:.1f} minutes")
        
        return missing_analysis
    
    async def complete_missing_images(self, missing_analysis: Dict[str, Dict], 
                                    max_destinations: int = None, 
                                    batch_size: int = 3,
                                    batch_delay_minutes: int = 2,
                                    dry_run: bool = False) -> Dict[str, bool]:
        """Complete missing images with batch processing and rate limiting"""
        
        # Filter to only destinations that need work
        incomplete_destinations = {
            name: data for name, data in missing_analysis.items() 
            if data['missing_images'] and data['status'] != 'no_exports'
        }
        
        if not incomplete_destinations:
            print("✅ No missing images to complete!")
            return {}
        
        # Limit destinations if specified
        if max_destinations:
            incomplete_destinations = dict(list(incomplete_destinations.items())[:max_destinations])
        
        # Sort by priority (partial destinations first - easier wins)
        sorted_destinations = sorted(
            incomplete_destinations.items(),
            key=lambda x: (len(x[1]['missing_images']), x[0])  # Fewer missing images first
        )
        
        print(f"\n🚀 Completing missing images for {len(sorted_destinations)} destinations")
        print(f"📦 Batch size: {batch_size} destinations")
        print(f"⏱️  Batch delay: {batch_delay_minutes} minutes")
        print(f"🔄 Dry run: {'Yes' if dry_run else 'No'}")
        print("=" * 60)
        
        results = {}
        total_images_generated = 0
        start_time = time.time()
        
        # Process in batches
        batches = [sorted_destinations[i:i + batch_size] for i in range(0, len(sorted_destinations), batch_size)]
        
        for batch_idx, batch in enumerate(batches, 1):
            print(f"\n🎯 Batch {batch_idx}/{len(batches)} - Processing {len(batch)} destinations")
            print("-" * 50)
            
            # Process each destination in the batch
            batch_results = await self._process_batch(batch, dry_run)
            results.update(batch_results)
            
            # Count images generated in this batch
            batch_images = sum(len([img for img in data['missing_images'] if img in self.seasons]) 
                             for _, data in batch)
            total_images_generated += batch_images
            
            # Inter-batch delay (except for last batch)
            if batch_idx < len(batches) and not dry_run:
                delay_seconds = batch_delay_minutes * 60
                print(f"\n⏳ Inter-batch delay: {batch_delay_minutes} minutes...")
                
                # Show countdown progress bar
                with tqdm(total=delay_seconds, desc="Waiting", unit="s") as pbar:
                    for _ in range(delay_seconds):
                        await asyncio.sleep(1)
                        pbar.update(1)
        
        # Final summary
        total_time = time.time() - start_time
        successful = sum(1 for success in results.values() if success)
        
        print("\n" + "=" * 60)
        print("🎨 Missing Image Completion Summary")
        print(f"✅ Successful destinations: {successful}/{len(results)}")
        print(f"🖼️  Total images generated: {total_images_generated}")
        print(f"⏱️  Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        
        if total_images_generated > 0 and not dry_run:
            print(f"📈 Average: {total_time/total_images_generated:.1f}s per image")
            actual_rate = (total_images_generated / total_time) * 60
            print(f"🚀 Actual generation rate: {actual_rate:.1f} images/minute")
        
        return results
    
    async def _process_batch(self, batch: List[Tuple[str, Dict]], dry_run: bool) -> Dict[str, bool]:
        """Process a single batch of destinations"""
        
        batch_results = {}
        
        for destination_name, dest_data in batch:
            missing_seasons = [img for img in dest_data['missing_images'] if img in self.seasons]
            
            print(f"\n🎯 {destination_name}")
            print(f"   Missing: {', '.join(dest_data['missing_images'])}")
            
            if dry_run:
                print("   🔄 DRY RUN - Would generate images here")
                batch_results[destination_name] = True
                continue
            
            dest_success = True
            
            # Generate missing seasonal images with progress bar
            if missing_seasons:
                with tqdm(missing_seasons, desc=f"   Generating", unit="img") as pbar:
                    for season in pbar:
                        pbar.set_description(f"   Generating {season}")
                        
                        try:
                            # Rate limiting delay (except for first image)
                            if len([k for k in batch_results.keys()]) > 0 or season != missing_seasons[0]:
                                await asyncio.sleep(self.rate_limit_delay)
                            
                            # Create prompt for this season
                            season_details = self.image_generator.season_prompts.get(season, "")
                            prompt = self.image_generator.prompt_template.format(
                                destination=destination_name,
                                season=season,
                                details=season_details
                            )
                            
                            # Generate image
                            image_url = self.image_generator._generate_image_with_dalle(prompt)
                            
                            # Download and save directly to export directory
                            dest_data['images_dir'].mkdir(parents=True, exist_ok=True)
                            image_path = dest_data['images_dir'] / f"{season}.jpg"
                            self.image_generator._download_image(image_url, image_path)
                            
                            pbar.set_postfix(status="✅ Saved")
                            
                        except Exception as e:
                            pbar.set_postfix(status=f"❌ Failed: {str(e)[:30]}")
                            dest_success = False
            
            batch_results[destination_name] = dest_success
        
        return batch_results
    
    def _update_image_manifest(self, images_dir: Path, destination: str, seasonal_images: List[Path]):
        """Update the image manifest file with new images"""
        
        manifest_path = images_dir / "image_manifest.json"
        
        # Create or update manifest
        manifest_data = {
            "destination": destination,
            "images": {},
            "copied_images": [],
            "export_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%f")
        }
        
        # Add seasonal images to manifest
        for image_path in seasonal_images:
            season = image_path.stem
            manifest_data["images"][season] = {
                "original_path": str(image_path),
                "export_path": str(image_path),
                "exists": True
            }
            manifest_data["copied_images"].append(str(image_path))
        
        # Write manifest
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Complete missing seasonal images")
    parser.add_argument('--analyze-only', action='store_true',
                       help='Only analyze missing images, do not generate')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without actually generating images')
    parser.add_argument('--max-destinations', type=int,
                       help='Maximum number of destinations to process (for rate limiting)')
    parser.add_argument('--batch-size', type=int, default=3,
                       help='Number of destinations per batch (default: 3)')
    parser.add_argument('--batch-delay', type=int, default=2,
                       help='Minutes to wait between batches (default: 2)')
    parser.add_argument('--exports-dir', default='exports',
                       help='Path to exports directory (default: exports)')
    parser.add_argument('--show-rate-limits', action='store_true',
                       help='Show rate limit information and recommendations')
    
    args = parser.parse_args()
    
    try:
        completor = MissingImageCompletor()
        
        # Show rate limit recommendations if requested
        if args.show_rate_limits:
            print("\n💡 DALL-E 3 Rate Limit Solutions:")
            print("=" * 50)
            
            print("🏆 OPTION 1: Upgrade OpenAI Account Tier")
            print("   • Tier 1 (Current): 5 images/minute")
            print("   • Tier 2: 7 images/minute (Pay $50+, wait 7 days)")
            print("   • Higher tiers: Up to 500 images/minute")
            print("   • Check: https://platform.openai.com/account/limits")
            
            print("\n⏰ OPTION 2: Use This Batch Script")
            print("   • python complete_missing_images.py --batch-size 3 --batch-delay 2")
            print("   • Processes 3 destinations, waits 2 minutes, repeats")
            print("   • Respects rate limits automatically")
            
            print("\n💰 OPTION 3: Alternative API Services")
            print("   • Services like laozhang.ai offer higher rate limits")
            print("   • Same API compatibility, better pricing")
            return 0
        
        # Analyze missing images
        exports_dir = Path(args.exports_dir)
        missing_analysis = completor.analyze_missing_images(exports_dir)
        
        if not missing_analysis:
            print("❌ No destination exports found")
            return 1
        
        # Stop here if analyze-only
        if args.analyze_only:
            print("\n✅ Analysis complete. Remove --analyze-only to generate missing images.")
            return 0
        
        # Complete missing images
        results = await completor.complete_missing_images(
            missing_analysis, 
            max_destinations=args.max_destinations,
            batch_size=args.batch_size,
            batch_delay_minutes=args.batch_delay,
            dry_run=args.dry_run
        )
        
        if not results:
            print("✅ No images needed to be generated!")
            return 0
        
        # Check if all succeeded
        failed_destinations = [name for name, success in results.items() if not success]
        if failed_destinations:
            print(f"\n⚠️  Some destinations had failures: {', '.join(failed_destinations)}")
            return 1
        else:
            print(f"\n🎉 All missing images completed successfully!")
            return 0
            
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
