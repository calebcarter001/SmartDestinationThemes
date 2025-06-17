#!/usr/bin/env python3
"""
Quick launcher for the Enhanced Intelligence Dashboard
"""

import os
import webbrowser
from pathlib import Path

def open_enhanced_dashboard():
    """Open the enhanced dashboard in the default browser."""
    
    # Get the absolute path to the enhanced dashboard
    current_dir = Path(__file__).parent
    dashboard_path = current_dir / "enhanced_dashboard" / "index.html"
    
    if dashboard_path.exists():
        # Convert to file URL
        file_url = f"file://{dashboard_path.resolve()}"
        
        print("🚀 Opening Enhanced Intelligence Dashboard...")
        print(f"📍 URL: {file_url}")
        
        # Open in default browser
        webbrowser.open(file_url)
        
        print("✨ Enhanced dashboard opened!")
        print("\n🧠 Features showcased:")
        print("   • Individual destination pages with full intelligence analysis")
        print("   • Theme depth analysis (Macro → Micro → Nano)")
        print("   • Authenticity scoring and hidden gem discovery")
        print("   • Emotional resonance profiling")
        print("   • Experience intensity calibration")
        print("   • Contextual intelligence and micro-climate analysis")
        print("   • Composition intelligence and quality assessment")
        print("   • Beautiful, responsive design")
        
    else:
        print("❌ Enhanced dashboard not found!")
        print("💡 Run the demo first: python demo_enhanced_intelligence.py")
        print("💡 Then generate dashboard: python -c \"from src.enhanced_viewer_generator import EnhancedViewerGenerator; generator = EnhancedViewerGenerator(); generator.generate_multi_destination_viewer(['outputs/las_vegas_nevada_enhanced_demo.json', 'outputs/new_york_new_york_enhanced_demo.json'])\"")

if __name__ == "__main__":
    open_enhanced_dashboard() 