#!/usr/bin/env python3
"""
Enhanced Main Processor with Progress Tracking and Server Management
Integrates all enhanced intelligence features with production-ready output management.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.enhanced_data_processor_with_progress import EnhancedDataProcessorWithProgress
from src.server_manager import DashboardServerManager, list_available_dashboards

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_processing.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def load_sample_data() -> Dict[str, Any]:
    """Load sample destination data for processing."""
    
    # Sample data for demonstration
    sample_data = {
        "Las Vegas, Nevada": {
            "affinities": [
                {
                    "theme": "High-Energy Nightlife",
                    "score": 0.95,
                    "keywords": ["casino", "nightclub", "show", "entertainment", "party"],
                    "description": "World-class entertainment and vibrant nightlife scene"
                },
                {
                    "theme": "Luxury Gambling Experience",
                    "score": 0.92,
                    "keywords": ["casino", "poker", "blackjack", "high-stakes", "luxury"],
                    "description": "Premium gambling venues with high-end amenities"
                },
                {
                    "theme": "World-Class Shows",
                    "score": 0.88,
                    "keywords": ["cirque du soleil", "magic show", "concert", "theater"],
                    "description": "Broadway-style shows and exclusive performances"
                },
                {
                    "theme": "Gourmet Dining",
                    "score": 0.85,
                    "keywords": ["michelin star", "celebrity chef", "fine dining", "buffet"],
                    "description": "Celebrity chef restaurants and diverse culinary experiences"
                },
                {
                    "theme": "Desert Adventure",
                    "score": 0.72,
                    "keywords": ["red rocks", "hiking", "desert", "valley of fire"],
                    "description": "Natural desert landscapes and outdoor activities"
                }
            ],
            "destination_info": {
                "location": "Nevada, USA",
                "climate": "Desert",
                "season": "Year-round",
                "demographics": "Entertainment seekers, luxury travelers"
            }
        },
        
        "New York, New York": {
            "affinities": [
                {
                    "theme": "Urban Cultural Immersion",
                    "score": 0.93,
                    "keywords": ["museum", "art gallery", "broadway", "culture", "history"],
                    "description": "Rich cultural institutions and artistic experiences"
                },
                {
                    "theme": "Iconic Architecture",
                    "score": 0.91,
                    "keywords": ["skyscraper", "empire state", "one world trade", "brooklyn bridge"],
                    "description": "World-famous architectural landmarks and skylines"
                },
                {
                    "theme": "Diverse Food Scene",
                    "score": 0.89,
                    "keywords": ["pizza", "deli", "michelin", "food truck", "ethnic cuisine"],
                    "description": "Global cuisine and innovative dining experiences"
                },
                {
                    "theme": "Financial District Energy",
                    "score": 0.84,
                    "keywords": ["wall street", "stock exchange", "business", "finance"],
                    "description": "Business hub with economic significance"
                },
                {
                    "theme": "Central Park Escape",
                    "score": 0.78,
                    "keywords": ["park", "nature", "recreation", "green space", "relaxation"],
                    "description": "Urban oasis for recreation and relaxation"
                }
            ],
            "destination_info": {
                "location": "New York, USA",
                "climate": "Continental",
                "season": "Year-round with seasonal variations",
                "demographics": "Culture enthusiasts, business travelers, urban explorers"
            }
        },
        
        "Kyoto, Japan": {
            "affinities": [
                {
                    "theme": "Traditional Temple Culture",
                    "score": 0.96,
                    "keywords": ["temple", "shrine", "zen", "meditation", "traditional"],
                    "description": "Ancient temples and spiritual experiences"
                },
                {
                    "theme": "Cherry Blossom Beauty",
                    "score": 0.89,
                    "keywords": ["sakura", "cherry blossom", "hanami", "spring", "flowers"],
                    "description": "Seasonal beauty and traditional celebrations"
                },
                {
                    "theme": "Authentic Japanese Cuisine",
                    "score": 0.94,
                    "keywords": ["kaiseki", "sushi", "tea ceremony", "traditional", "authentic"],
                    "description": "Traditional culinary experiences and tea culture"
                },
                {
                    "theme": "Geisha District Mystique",
                    "score": 0.87,
                    "keywords": ["geisha", "gion", "traditional", "culture", "historic"],
                    "description": "Historic geisha districts and cultural traditions"
                },
                {
                    "theme": "Bamboo Forest Serenity",
                    "score": 0.83,
                    "keywords": ["bamboo", "arashiyama", "nature", "peaceful", "forest"],
                    "description": "Natural bamboo groves and tranquil environments"
                }
            ],
            "destination_info": {
                "location": "Kyoto, Japan",
                "climate": "Humid subtropical",
                "season": "Spring and autumn preferred",
                "demographics": "Culture seekers, spiritual travelers, nature lovers"
            }
        }
    }
    
    return sample_data

def main():
    """Main enhanced processing workflow."""
    
    print("🚀 Enhanced Intelligence Processing System")
    print("=" * 60)
    
    # Initialize processor
    print("🔧 Initializing Enhanced Data Processor...")
    processor = EnhancedDataProcessorWithProgress()
    
    # Load destination data
    print("📊 Loading destination data...")
    
    # Try to load from existing file first
    data_file = "destination_affinities_mvp.json"
    if os.path.exists(data_file):
        print(f"📁 Loading data from {data_file}")
        with open(data_file, 'r') as f:
            destinations_data = json.load(f)
    else:
        print("📝 Using sample data for demonstration")
        destinations_data = load_sample_data()
    
    print(f"✅ Loaded {len(destinations_data)} destinations for processing")
    
    # Process destinations with progress tracking
    try:
        processed_files = processor.process_destinations_with_progress(
            destinations_data, 
            generate_dashboard=True
        )
        
        # Get session output directory
        session_dir = processor.get_session_output_dir()
        
        print(f"\n🎉 Processing Complete!")
        print(f"📁 Session directory: {session_dir}")
        print(f"📊 Processed files: {len(processed_files)}")
        
        # Offer to start server
        dashboard_dir = os.path.join(session_dir, "dashboard")
        if os.path.exists(os.path.join(dashboard_dir, "index.html")):
            print(f"\n🌐 Dashboard Generation Complete!")
            
            # Ask user if they want to start the server
            response = input("\n❓ Start dashboard server? (y/n): ").strip().lower()
            
            if response in ['y', 'yes']:
                start_dashboard_server(session_dir)
            else:
                print(f"💡 To view dashboard later, run:")
                print(f"   python enhanced_main_processor.py --serve-session session_{processor.session_timestamp}")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        print(f"❌ Processing failed: {e}")
        return 1
    
    return 0

def start_dashboard_server(session_dir: str):
    """Start the dashboard server for the given session."""
    
    dashboard_dir = os.path.join(session_dir, "dashboard")
    
    print(f"\n🌐 Starting Dashboard Server...")
    
    try:
        # Initialize server manager
        server_manager = DashboardServerManager()
        
        # Start server
        server_info = server_manager.start_server(
            dashboard_dir=dashboard_dir,
            open_browser=True
        )
        
        print(f"\n💡 Server Controls:")
        print(f"   • Press Ctrl+C to stop the server")
        print(f"   • Server URL: {server_info['url']}")
        print(f"   • Status: {server_info['status']}")
        
        # Wait for shutdown
        try:
            server_manager.wait_for_shutdown()
        except KeyboardInterrupt:
            print(f"\n⚡ Received shutdown signal...")
            server_manager.stop_server()
            print(f"✅ Server stopped gracefully")
        
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Intelligence Processing System")
    parser.add_argument('--list-sessions', action='store_true', 
                       help='List all available processing sessions')
    parser.add_argument('--serve-session', 
                       help='Serve a specific session dashboard')
    
    args = parser.parse_args()
    
    if args.list_sessions:
        dashboards = list_available_dashboards()
        print("📋 Available Processing Sessions:")
        print("=" * 50)
        if not dashboards:
            print("No processing sessions found.")
        else:
            for i, dash in enumerate(dashboards, 1):
                print(f"{i}. {dash['session_id']}")
                if 'destination_count' in dash:
                    print(f"   • Destinations: {dash['destination_count']}")
                if 'summary' in dash:
                    print(f"   • Created: {dash['summary']['processing_date'][:19]}")
                print(f"   • Dashboard: {dash['dashboard_path']}")
                print()
    elif args.serve_session:
        dashboard_dir = os.path.join("outputs", args.serve_session, "dashboard")
        if not os.path.exists(dashboard_dir):
            print(f"Session not found: {args.serve_session}")
        else:
            server_manager = DashboardServerManager()
            server_info = server_manager.start_server(
                dashboard_dir=dashboard_dir,
                open_browser=True
            )
            print(f"💡 Server started: {server_info['url']}")
            print(f"Press Ctrl+C to stop the server")
            try:
                server_manager.wait_for_shutdown()
            except KeyboardInterrupt:
                server_manager.stop_server()
    else:
        # Run main processing
        sys.exit(main()) 