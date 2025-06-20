#!/usr/bin/env python3
"""
Test Script for Incremental Processing and Export Systems
Test the new theme lifecycle, session consolidation, caching, and export systems.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from src.agent_integration_layer import AgentCompatibilityLayer
from tools.config_loader import ConfigLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_theme_incremental_processing():
    """Test theme incremental processing"""
    print("\n🎯 Testing Theme Incremental Processing")
    print("=" * 50)
    
    try:
        config = ConfigLoader.load_config()
        integration_layer = AgentCompatibilityLayer(config)
        await integration_layer.initialize()
        
        # Test theme statistics
        destinations = ["Tokyo, Japan", "Paris, France"]
        
        for destination in destinations:
            stats = integration_layer.theme_lifecycle_manager.get_theme_statistics(destination)
            print(f"\n📊 Theme Statistics for {destination}:")
            print(f"   • Has existing data: {stats['has_existing_data']}")
            print(f"   • Theme count: {stats['theme_count']}")
            print(f"   • Quality score: {stats['quality_score']:.3f}")
            print(f"   • Last updated: {stats['last_updated']}")
            
            # Test incremental decision
            should_update = integration_layer.theme_lifecycle_manager.should_update_themes(destination)
            print(f"   • Should update: {should_update}")
        
        print("\n✅ Theme incremental processing tests completed")
        
    except Exception as e:
        print(f"❌ Theme incremental processing test failed: {e}")

async def test_session_consolidation():
    """Test session consolidation"""
    print("\n🔄 Testing Session Consolidation")
    print("=" * 50)
    
    try:
        config = ConfigLoader.load_config()
        integration_layer = AgentCompatibilityLayer(config)
        await integration_layer.initialize()
        
        # Test consolidation statistics
        destination = "Tokyo, Japan"
        
        print(f"\n📊 Consolidation Statistics for {destination}:")
        stats = await integration_layer.session_consolidator.get_consolidation_statistics(destination)
        
        print(f"   • Total sessions: {stats['total_sessions']}")
        print(f"   • Data availability:")
        for data_type, count in stats['data_type_availability'].items():
            print(f"     - {data_type}: {count} sessions")
        
        if stats['date_range']['oldest']:
            print(f"   • Date range: {stats['date_range']['oldest']} to {stats['date_range']['newest']}")
        
        if stats['quality_ranges']:
            print(f"   • Quality ranges:")
            for data_type, quality_info in stats['quality_ranges'].items():
                print(f"     - {data_type}: {quality_info['min']:.3f} - {quality_info['max']:.3f} (avg: {quality_info['avg']:.3f})")
        
        # Test actual consolidation if data exists
        if stats['total_sessions'] > 0:
            print(f"\n🔄 Attempting consolidation for {destination}...")
            try:
                consolidated = await integration_layer.session_consolidator.consolidate_destination_data(destination)
                print(f"✅ Consolidation successful!")
                print(f"   • Source sessions: {len(consolidated.source_sessions)}")
                print(f"   • Consolidation strategy: {consolidated.metadata.get('consolidation_strategy')}")
                if consolidated.themes:
                    print(f"   • Themes: {len(consolidated.themes.get('affinities', []))}")
                if consolidated.nuances:
                    total_nuances = sum(len(consolidated.nuances.get(cat, [])) for cat in ['destination_nuances', 'hotel_expectations', 'vacation_rental_expectations'])
                    print(f"   • Nuances: {total_nuances}")
                if consolidated.evidence:
                    print(f"   • Evidence: {len(consolidated.evidence.get('evidence', []))}")
            except Exception as e:
                print(f"⚠️ Consolidation failed: {e}")
        
        print("\n✅ Session consolidation tests completed")
        
    except Exception as e:
        print(f"❌ Session consolidation test failed: {e}")

async def test_caching_system():
    """Test enhanced caching system"""
    print("\n📦 Testing Enhanced Caching System")
    print("=" * 50)
    
    try:
        config = ConfigLoader.load_config()
        integration_layer = AgentCompatibilityLayer(config)
        await integration_layer.initialize()
        
        # Test cache statistics
        cache_stats = await integration_layer.consolidated_cache.get_cache_statistics()
        
        print(f"\n📊 Cache Statistics:")
        cache_info = cache_stats.get('cache_statistics', {})
        print(f"   • Cached destinations: {cache_info.get('cached_destinations', 0)}")
        print(f"   • Versioned entries: {cache_info.get('versioned_entries', 0)}")
        print(f"   • Export cache entries: {cache_info.get('export_cache_entries', 0)}")
        print(f"   • Total cache size: {cache_info.get('total_cache_size_mb', 0):.2f} MB")
        print(f"   • Cache TTL: {cache_info.get('cache_ttl_hours', 0)} hours")
        
        config_info = cache_stats.get('configuration', {})
        print(f"\n⚙️ Cache Configuration:")
        print(f"   • Versioning enabled: {config_info.get('versioning_enabled', False)}")
        print(f"   • Max versions per destination: {config_info.get('max_versions_per_destination', 0)}")
        print(f"   • Auto-invalidate on new data: {config_info.get('auto_invalidate_on_new_data', False)}")
        
        # Test cache operations
        destination = "Tokyo, Japan"
        print(f"\n🔍 Testing cache operations for {destination}:")
        
        # Try to get cached data
        cached_data = await integration_layer.consolidated_cache.get_consolidated_data(destination)
        if cached_data:
            print(f"   ✅ Found cached data (version: {cached_data.get('cache_metadata', {}).get('data_version', 'unknown')[:8]})")
        else:
            print(f"   ℹ️ No cached data found")
        
        print("\n✅ Caching system tests completed")
        
    except Exception as e:
        print(f"❌ Caching system test failed: {e}")

async def test_export_system():
    """Test export system"""
    print("\n🚀 Testing Export System")
    print("=" * 50)
    
    try:
        config = ConfigLoader.load_config()
        integration_layer = AgentCompatibilityLayer(config)
        await integration_layer.initialize()
        
        # Test export statistics
        export_stats = await integration_layer.data_exporter.get_export_statistics()
        
        print(f"\n📊 Export Statistics:")
        print(f"   • Total exports: {export_stats.get('total_exports', 0)}")
        print(f"   • Export directory: {export_stats.get('export_directory')}")
        print(f"   • Total export size: {export_stats.get('total_export_size_mb', 0)} MB")
        
        if export_stats.get('destinations_exported'):
            print(f"   • Destinations exported: {len(export_stats['destinations_exported'])}")
            for dest in export_stats['destinations_exported'][:5]:  # Show first 5
                print(f"     - {dest}")
            if len(export_stats['destinations_exported']) > 5:
                print(f"     ... and {len(export_stats['destinations_exported']) - 5} more")
        
        # Discover available destinations
        print(f"\n🔍 Discovering available destinations for export:")
        available_destinations = await integration_layer._discover_all_destinations()
        
        if available_destinations:
            print(f"   • Found {len(available_destinations)} destinations with data:")
            for dest in available_destinations[:5]:  # Show first 5
                print(f"     - {dest}")
            if len(available_destinations) > 5:
                print(f"     ... and {len(available_destinations) - 5} more")
            
            # Test export for first destination
            test_destination = available_destinations[0]
            print(f"\n🚀 Testing export for {test_destination}:")
            
            try:
                export_result = await integration_layer.export_destination_data(test_destination, "structured")
                print(f"   ✅ Export successful!")
                print(f"   • Export path: {export_result['export_path']}")
                print(f"   • Export format: {export_result['export_format']}")
                print(f"   • Files created: {len(export_result['export_result']['files_created'])}")
                
                # Show data summary
                data_summary = export_result['export_result']['data_summary']
                if data_summary:
                    print(f"   • Data summary:")
                    for data_type, info in data_summary.items():
                        if isinstance(info, dict):
                            for key, value in info.items():
                                print(f"     - {data_type}.{key}: {value}")
                        else:
                            print(f"     - {data_type}: {info}")
                
            except Exception as e:
                print(f"   ⚠️ Export test failed: {e}")
        else:
            print(f"   ℹ️ No destinations found with data")
        
        print("\n✅ Export system tests completed")
        
    except Exception as e:
        print(f"❌ Export system test failed: {e}")

async def test_full_integration():
    """Test full integration workflow"""
    print("\n🔄 Testing Full Integration Workflow")
    print("=" * 50)
    
    try:
        config = ConfigLoader.load_config()
        integration_layer = AgentCompatibilityLayer(config)
        await integration_layer.initialize()
        
        # Get comprehensive statistics
        print(f"\n📊 System-wide Statistics:")
        
        stats = await integration_layer.get_consolidation_statistics()
        
        # Display system statistics
        if 'system_statistics' in stats:
            system_stats = stats['system_statistics']
            
            if 'cache_stats' in system_stats:
                cache_info = system_stats['cache_stats'].get('cache_statistics', {})
                print(f"\n📦 Cache System:")
                print(f"   • Cached destinations: {cache_info.get('cached_destinations', 0)}")
                print(f"   • Total cache size: {cache_info.get('total_cache_size_mb', 0):.2f} MB")
            
            if 'export_stats' in system_stats:
                export_info = system_stats['export_stats']
                print(f"\n🚀 Export System:")
                print(f"   • Total exports: {export_info.get('total_exports', 0)}")
                print(f"   • Export size: {export_info.get('total_export_size_mb', 0)} MB")
        
        # Test destination-specific statistics
        available_destinations = await integration_layer._discover_all_destinations()
        if available_destinations:
            test_destination = available_destinations[0]
            print(f"\n🎯 Destination-specific statistics for {test_destination}:")
            
            dest_stats = await integration_layer.get_consolidation_statistics(test_destination)
            
            if 'destination_statistics' in dest_stats:
                dest_info = dest_stats['destination_statistics']
                
                if 'consolidation_stats' in dest_info:
                    consolidation_info = dest_info['consolidation_stats']
                    print(f"   📊 Consolidation:")
                    print(f"     • Sessions: {consolidation_info.get('total_sessions', 0)}")
                    data_availability = consolidation_info.get('data_type_availability', {})
                    for data_type, count in data_availability.items():
                        print(f"     • {data_type}: {count} sessions")
                
                if 'theme_stats' in dest_info:
                    theme_info = dest_info['theme_stats']
                    print(f"   🎨 Themes:")
                    print(f"     • Has data: {theme_info.get('has_existing_data', False)}")
                    print(f"     • Theme count: {theme_info.get('theme_count', 0)}")
                    print(f"     • Quality: {theme_info.get('quality_score', 0):.3f}")
        
        print("\n✅ Full integration tests completed")
        
    except Exception as e:
        print(f"❌ Full integration test failed: {e}")

async def main():
    """Run all tests"""
    print("🧪 Smart Destination Themes - Incremental Processing & Export Systems Test")
    print("=" * 80)
    
    start_time = time.time()
    
    # Run all tests
    await test_theme_incremental_processing()
    await test_session_consolidation()
    await test_caching_system()
    await test_export_system()
    await test_full_integration()
    
    total_time = time.time() - start_time
    
    print(f"\n🎉 All tests completed in {total_time:.2f} seconds")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
