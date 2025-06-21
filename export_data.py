#!/usr/bin/env python3
"""
Standalone Export Script for SmartDestinationThemes

This script can export destination data as a standalone process.
It supports both individual destination exports and bulk exports.

Usage:
    python export_data.py --destination "Rome, Italy" --format structured
    python export_data.py --destination "Rome, Italy" --format json
    python export_data.py --all --format structured
    python export_data.py --list-destinations
    python export_data.py --stats
"""

import asyncio
import argparse
import logging
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tools.config_loader import load_app_config
from src.agent_integration_layer import AgentCompatibilityLayer
from src.export_system import DestinationDataExporter
from src.session_consolidation_manager import SessionConsolidationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StandaloneExporter:
    """Standalone exporter that can run independently"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_app_config()
        self.export_system = DestinationDataExporter(self.config)
        self.consolidation_manager = SessionConsolidationManager(self.config)
        self.agent_layer = None
    
    async def initialize(self):
        """Initialize the exporter systems"""
        logger.info("Initializing standalone exporter...")
        
        try:
            # Initialize agent compatibility layer if needed
            self.agent_layer = AgentCompatibilityLayer(self.config)
            await self.agent_layer.initialize()
            logger.info("✅ Agent compatibility layer initialized")
        except Exception as e:
            logger.warning(f"⚠️ Agent layer initialization failed: {e}")
            logger.info("🔄 Continuing with data-only export capabilities")
    
    async def export_destination(self, destination: str, export_format: str = "structured") -> Dict[str, Any]:
        """Export a single destination"""
        logger.info(f"🔄 Exporting {destination} in {export_format} format")
        
        try:
            # Get consolidated data for the destination
            consolidated_data = await self.consolidation_manager.consolidate_destination_data(destination)
            
            if not consolidated_data:
                logger.error(f"❌ No data found for destination: {destination}")
                return {"error": f"No data found for {destination}"}
            
            # Convert ConsolidatedData dataclass to dictionary for export system
            consolidated_dict = {
                'themes': consolidated_data.themes,
                'nuances': consolidated_data.nuances,
                'images': consolidated_data.images,
                'evidence': consolidated_data.evidence,
                'metadata': consolidated_data.metadata
            }
            
            # Export the data
            export_result = await self.export_system.export_destination(
                destination, consolidated_dict, export_format
            )
            
            logger.info(f"✅ Export completed for {destination}")
            return export_result
            
        except Exception as e:
            logger.error(f"❌ Export failed for {destination}: {e}")
            return {"error": str(e)}
    
    async def export_all_destinations(self, export_format: str = "structured") -> Dict[str, Any]:
        """Export all available destinations"""
        logger.info(f"🔄 Exporting all destinations in {export_format} format")
        
        try:
            # Discover available destinations
            destinations = await self.discover_destinations()
            
            if not destinations:
                logger.error("❌ No destinations found")
                return {"error": "No destinations found"}
            
            logger.info(f"📊 Found {len(destinations)} destinations to export")
            
            export_results = {}
            successful_exports = 0
            
            for destination in destinations:
                try:
                    result = await self.export_destination(destination, export_format)
                    export_results[destination] = result
                    
                    if "error" not in result:
                        successful_exports += 1
                        
                except Exception as e:
                    logger.error(f"❌ Failed to export {destination}: {e}")
                    export_results[destination] = {"error": str(e)}
            
            summary = {
                "total_destinations": len(destinations),
                "successful_exports": successful_exports,
                "failed_exports": len(destinations) - successful_exports,
                "export_format": export_format,
                "export_results": export_results
            }
            
            logger.info(f"✅ Bulk export completed: {successful_exports}/{len(destinations)} successful")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Bulk export failed: {e}")
            return {"error": str(e)}
    
    async def discover_destinations(self) -> List[str]:
        """Discover available destinations from session data"""
        try:
            if self.agent_layer:
                return await self.agent_layer._discover_all_destinations()
            else:
                # Fallback: discover from session directories
                destinations = []
                outputs_dir = Path("outputs")
                
                if outputs_dir.exists():
                    for session_dir in outputs_dir.glob("session_*"):
                        json_dir = session_dir / "json"
                        if json_dir.exists():
                            for json_file in json_dir.glob("*_enhanced.json"):
                                dest_name = json_file.stem.replace("_enhanced", "").replace("__", ", ").replace("_", " ")
                                # Capitalize words
                                dest_name = " ".join(word.capitalize() for word in dest_name.split())
                                if dest_name not in destinations:
                                    destinations.append(dest_name)
                
                return destinations
                
        except Exception as e:
            logger.error(f"❌ Failed to discover destinations: {e}")
            return []
    
    async def list_destinations(self) -> List[str]:
        """List all available destinations"""
        destinations = await self.discover_destinations()
        
        if destinations:
            logger.info(f"📊 Available destinations ({len(destinations)}):")
            for i, dest in enumerate(destinations, 1):
                print(f"  {i:2d}. {dest}")
        else:
            logger.info("📊 No destinations found")
        
        return destinations
    
    async def get_export_statistics(self) -> Dict[str, Any]:
        """Get export system statistics"""
        try:
            stats = await self.export_system.get_export_statistics()
            
            logger.info("📊 Export System Statistics:")
            print(f"  Export Directory: {stats.get('export_directory', 'N/A')}")
            print(f"  Total Exports: {stats.get('total_exports', 0)}")
            print(f"  Total Size: {stats.get('total_export_size_mb', 0):.2f} MB")
            print(f"  Destinations Exported: {len(stats.get('destinations_exported', []))}")
            
            if stats.get('destinations_exported'):
                print("  Exported Destinations:")
                for dest in stats['destinations_exported']:
                    print(f"    • {dest}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get export statistics: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.agent_layer:
            await self.agent_layer.cleanup()

def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Standalone Export Script for SmartDestinationThemes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python export_data.py --destination "Rome, Italy" --format structured
  python export_data.py --destination "Tokyo, Japan" --format json
  python export_data.py --all --format structured
  python export_data.py --list-destinations
  python export_data.py --stats
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--destination", "-d",
        type=str,
        help="Export a specific destination (e.g., 'Rome, Italy')"
    )
    group.add_argument(
        "--all", "-a",
        action="store_true",
        help="Export all available destinations"
    )
    group.add_argument(
        "--list-destinations", "-l",
        action="store_true",
        help="List all available destinations"
    )
    group.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Show export system statistics"
    )
    
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["structured", "json"],
        default="structured",
        help="Export format (default: structured)"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config/config.yaml",
        help="Configuration file path (default: config/config.yaml)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    return parser

async def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize exporter
    exporter = StandaloneExporter(args.config)
    
    try:
        await exporter.initialize()
        
        # Execute requested action
        if args.destination:
            result = await exporter.export_destination(args.destination, args.format)
            
            if args.output_json:
                print(json.dumps(result, indent=2))
            else:
                if "error" in result:
                    logger.error(f"Export failed: {result['error']}")
                    sys.exit(1)
                else:
                    logger.info(f"✅ Export completed successfully")
                    logger.info(f"📁 Export location: {result.get('export_path', 'Unknown')}")
        
        elif args.all:
            result = await exporter.export_all_destinations(args.format)
            
            if args.output_json:
                print(json.dumps(result, indent=2))
            else:
                if "error" in result:
                    logger.error(f"Bulk export failed: {result['error']}")
                    sys.exit(1)
                else:
                    successful = result.get('successful_exports', 0)
                    total = result.get('total_destinations', 0)
                    logger.info(f"✅ Bulk export completed: {successful}/{total} successful")
        
        elif args.list_destinations:
            destinations = await exporter.list_destinations()
            
            if args.output_json:
                print(json.dumps({"destinations": destinations}, indent=2))
        
        elif args.stats:
            stats = await exporter.get_export_statistics()
            
            if args.output_json:
                print(json.dumps(stats, indent=2))
    
    except Exception as e:
        logger.error(f"❌ Export script failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    finally:
        await exporter.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 