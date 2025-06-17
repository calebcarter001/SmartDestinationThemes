#!/usr/bin/env python3
"""
Simple script to open the SmartDestinationThemes dashboard in the browser.
"""

import os
import webbrowser
import sys

def open_dashboard():
    """Open the HTML dashboard in the default browser."""
    # Check for modular dashboard first
    modular_dashboard = "dashboard/index.html"
    legacy_dashboard = "themes_dashboard.html"
    
    dashboard_file = None
    if os.path.exists(modular_dashboard):
        dashboard_file = modular_dashboard
        print("🎯 Found modular dashboard - opening main index page")
    elif os.path.exists(legacy_dashboard):
        dashboard_file = legacy_dashboard
        print("📄 Found legacy dashboard - opening single page")
    else:
        print("❌ No dashboard files found!")
        print("💡 Run 'python main.py' first to generate the dashboard.")
        return False
    
    # Get absolute path
    dashboard_path = os.path.abspath(dashboard_file)
    file_url = f"file://{dashboard_path}"
    
    print("🌐 Opening SmartDestinationThemes Dashboard...")
    print(f"📍 Location: {dashboard_path}")
    
    try:
        # Open in default browser
        webbrowser.open(file_url)
        print("✅ Dashboard opened in your default browser!")
        
        # If modular dashboard, show available individual pages
        if dashboard_file == modular_dashboard:
            dashboard_dir = "dashboard"
            html_files = [f for f in os.listdir(dashboard_dir) if f.endswith('.html') and f != 'index.html']
            if html_files:
                print(f"\n📍 Individual destination pages available:")
                for html_file in sorted(html_files):
                    dest_name = html_file.replace('.html', '').replace('_', ' ').title()
                    print(f"   • {dest_name}: file://{os.path.abspath(os.path.join(dashboard_dir, html_file))}")
        
        return True
    except Exception as e:
        print(f"❌ Error opening dashboard: {e}")
        print(f"🔗 You can manually open: {file_url}")
        return False

if __name__ == "__main__":
    open_dashboard() 