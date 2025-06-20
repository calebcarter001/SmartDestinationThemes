#!/usr/bin/env python3
"""
Selective cleanup script for Destination Intelligence system.
Supports debugging modes that preserve working theme data while cleaning problematic nuance data.
"""

import os
import shutil
import glob
import yaml
from pathlib import Path

def load_config():
    """Load configuration to determine cleanup behavior"""
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"⚠️  Could not load config.yaml: {e}")
        print("Using default cleanup behavior (clean everything)")
        return {}

def get_processing_mode(config):
    """Extract processing mode settings"""
    processing_mode = config.get('processing_mode', {})
    
    # Default values for safety
    defaults = {
        'preserve_existing_themes': True,
        'clean_nuance_all_sessions': True,
        'preserve_all_theme_sessions': True,
        'patterns_to_preserve': ['*_enhanced.json', '*_evidence.json'],
        'patterns_to_clean': ['*_nuances.json', '*_nuances_evidence.json']
    }
    
    cleanup_controls = processing_mode.get('cleanup_controls', {})
    
    return {
        'preserve_themes': processing_mode.get('preserve_existing_themes', defaults['preserve_existing_themes']),
        'clean_nuances': processing_mode.get('nuance_controls', {}).get('clean_nuance_files', defaults['clean_nuance_all_sessions']),
        'preserve_all_sessions': cleanup_controls.get('preserve_all_theme_sessions', defaults['preserve_all_theme_sessions']),
        'patterns_to_preserve': cleanup_controls.get('patterns_to_preserve', defaults['patterns_to_preserve']),
        'patterns_to_clean': cleanup_controls.get('patterns_to_clean', defaults['patterns_to_clean']),
        'debug_info': processing_mode.get('debug_info', {})
    }

def selective_session_cleanup(session_dir, patterns_to_preserve, patterns_to_clean):
    """Clean specific patterns from a session directory while preserving others"""
    preserved_count = 0
    cleaned_count = 0
    
    if not os.path.exists(session_dir):
        return preserved_count, cleaned_count
    
    # Get all JSON files in session
    json_dir = os.path.join(session_dir, 'json')
    if not os.path.exists(json_dir):
        return preserved_count, cleaned_count
    
    all_files = glob.glob(os.path.join(json_dir, '*.json'))
    
    for file_path in all_files:
        filename = os.path.basename(file_path)
        should_preserve = False
        should_clean = False
        
        # Check if file matches preservation patterns
        for pattern in patterns_to_preserve:
            if filename.endswith(pattern.replace('*', '')):
                should_preserve = True
                break
        
        # Check if file matches cleaning patterns  
        for pattern in patterns_to_clean:
            if filename.endswith(pattern.replace('*', '')):
                should_clean = True
                break
        
        # Decision logic: preserve takes priority over clean
        if should_preserve and not should_clean:
            preserved_count += 1
            # Don't delete - just count as preserved
        elif should_clean and not should_preserve:
            try:
                os.remove(file_path)
                cleaned_count += 1
            except Exception as e:
                print(f"⚠️  Error removing {file_path}: {e}")
        elif should_preserve and should_clean:
            # Conflict - preserve wins (themes are working, nuances are not)
            preserved_count += 1
        # If neither pattern matches, leave the file alone
    
    return preserved_count, cleaned_count

def clean_directory_selective(dir_path, description, skip_if_preserve=False):
    """Clean a directory with optional preservation logic"""
    if skip_if_preserve:
        print(f"🛡️  Preserving {description} (themes working correctly)")
        return
        
    if os.path.exists(dir_path):
        try:
            if os.path.isfile(dir_path):
                os.remove(dir_path)
                print(f"✅ Removed file: {description}")
            else:
                files_removed = 0
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        files_removed += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        files_removed += 1
                
                if files_removed > 0:
                    print(f"✅ Cleaned {description}: removed {files_removed} items")
                else:
                    print(f"✅ {description}: already clean")
        except Exception as e:
            print(f"⚠️  Error cleaning {description}: {e}")
    else:
        print(f"✅ {description}: directory doesn't exist (clean)")

def main():
    """Run selective cleanup based on configuration"""
    print("🧹 Starting selective cleanup for debugging...")
    print("=" * 60)
    
    # Load configuration and processing mode
    config = load_config()
    mode = get_processing_mode(config)
    
    # Display current processing mode
    debug_info = mode.get('debug_info', {})
    if debug_info:
        print("🔧 Processing Mode Information:")
        print(f"   Reason: {debug_info.get('reason', 'Not specified')}")
        print(f"   Themes: {debug_info.get('themes_status', 'Unknown')}")
        print(f"   Nuances: {debug_info.get('nuances_status', 'Unknown')}")
        print(f"   Images: {debug_info.get('images_status', 'Unknown')}")
        print()
    
    print("🎯 Cleanup Strategy:")
    print(f"   Preserve themes: {'✅ YES' if mode['preserve_themes'] else '❌ NO'}")
    print(f"   Clean nuances: {'✅ YES' if mode['clean_nuances'] else '❌ NO'}")
    print(f"   Preserve all sessions: {'✅ YES' if mode['preserve_all_sessions'] else '❌ NO'}")
    print()
    
    # Session-based selective cleanup
    if mode['preserve_themes'] and mode['clean_nuances']:
        print("🎯 Selective Session Cleanup (Preserve Themes, Clean Nuances)")
        print("-" * 50)
        
        # Find all session directories
        session_dirs = glob.glob("outputs/session_*")
        
        if session_dirs:
            total_preserved = 0
            total_cleaned = 0
            
            for session_dir in session_dirs:
                session_name = os.path.basename(session_dir)
                preserved, cleaned = selective_session_cleanup(
                    session_dir, 
                    mode['patterns_to_preserve'], 
                    mode['patterns_to_clean']
                )
                total_preserved += preserved
                total_cleaned += cleaned
                
                if preserved > 0 or cleaned > 0:
                    print(f"   📁 {session_name}: preserved {preserved}, cleaned {cleaned}")
            
            print(f"\n📊 Session cleanup summary:")
            print(f"   🛡️  Total files preserved: {total_preserved}")
            print(f"   🧹 Total files cleaned: {total_cleaned}")
            print(f"   📁 Sessions processed: {len(session_dirs)}")
        else:
            print("   No session directories found")
    
    # Clean development staging (but preserve themes if configured)
    print("\n🔧 Development Staging Cleanup")
    print("-" * 50)
    
    if mode['preserve_themes']:
        # Selective cleaning of dev staging
        dev_staging_cleaned = 0
        
        # Clean nuance files from dev_staging
        if os.path.exists("dev_staging/json"):
            json_files = glob.glob("dev_staging/json/*.json")
            for json_file in json_files:
                filename = os.path.basename(json_file)
                should_clean = any(filename.endswith(pattern.replace('*', '')) 
                                 for pattern in mode['patterns_to_clean'])
                
                if should_clean:
                    try:
                        os.remove(json_file)
                        dev_staging_cleaned += 1
                    except Exception as e:
                        print(f"⚠️  Error removing {json_file}: {e}")
        
        # Clean dashboard files (they'll be regenerated)
        if os.path.exists("dev_staging/dashboard"):
            dashboard_files = glob.glob("dev_staging/dashboard/*")
            for dash_file in dashboard_files:
                try:
                    if os.path.isfile(dash_file):
                        os.remove(dash_file)
                        dev_staging_cleaned += 1
                    elif os.path.isdir(dash_file):
                        shutil.rmtree(dash_file)
                        dev_staging_cleaned += 1
                except Exception as e:
                    print(f"⚠️  Error removing {dash_file}: {e}")
        
        if dev_staging_cleaned > 0:
            print(f"✅ Development staging: cleaned {dev_staging_cleaned} items (preserved theme data)")
        else:
            print("✅ Development staging: no cleanup needed")
    else:
        # Full development staging cleanup
        clean_directory_selective("dev_staging", "Development staging")
    
    # Standard system cleanup (always safe to clean)
    print("\n🧹 Standard System Cleanup")
    print("-" * 50)
    
    # Always safe to clean these
    safe_cleanup_targets = [
        ("logs", "Application logs"),
        ("cache", "File-based cache"), 
        ("chroma_db", "ChromaDB vector database"),
        (".pytest_cache", "Pytest cache directory"),
    ]
    
    for dir_path, description in safe_cleanup_targets:
        clean_directory_selective(dir_path, description)
    
    # Database files - only clean if not preserving themes
    db_files = [
        "enhanced_destination_intelligence.db",
        "test_enhanced_destination_intelligence.db", 
        "comprehensive_database_report.json",
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            if mode['preserve_themes']:
                print(f"🛡️  Preserving database: {db_file} (may contain theme data)")
            else:
                try:
                    file_size = os.path.getsize(db_file) / (1024*1024)  # Size in MB
                    os.remove(db_file)
                    print(f"✅ Removed database: {db_file} ({file_size:.1f}MB)")
                except Exception as e:
                    print(f"⚠️  Error removing {db_file}: {e}")
    
    # Clean Python cache files (always safe)
    print("\n🐍 Python Cache Cleanup")
    print("-" * 50)
    
    cache_cleaned = 0
    
    # Remove __pycache__ directories recursively
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                cache_cleaned += 1
            except Exception as e:
                print(f"⚠️  Error removing {pycache_path}: {e}")
    
    # Remove .pyc and .pyo files
    pyc_files = glob.glob('**/*.pyc', recursive=True) + glob.glob('**/*.pyo', recursive=True)
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            cache_cleaned += 1
        except Exception as e:
            print(f"⚠️  Error removing {pyc_file}: {e}")
    
    if cache_cleaned > 0:
        print(f"✅ Python cache: removed {cache_cleaned} items")
    else:
        print("✅ Python cache: already clean")
    
    # Clean system files (always safe)
    system_files = glob.glob('.DS_Store') + glob.glob('**/.DS_Store', recursive=True)
    system_files += glob.glob('.coverage') + glob.glob('**/*.prof', recursive=True)
    system_files += glob.glob('dynamic_viewer_*.html')
    
    if system_files:
        for sys_file in system_files:
            try:
                if 'venv/' not in sys_file:  # Skip venv files
                    os.remove(sys_file)
                    print(f"✅ Removed system file: {sys_file}")
            except Exception as e:
                print(f"⚠️  Error removing {sys_file}: {e}")
    
    # Final status report
    print("\n" + "=" * 60)
    print("🎉 Selective cleanup completed!")
    print("\n📊 Cleanup Summary:")
    
    if mode['preserve_themes']:
        print("   🛡️  THEMES: Preserved across all sessions (working correctly)")
        remaining_enhanced = len(glob.glob("outputs/*/json/*_enhanced.json"))
        remaining_evidence = len(glob.glob("outputs/*/json/*_evidence.json"))
        print(f"      - Enhanced files preserved: {remaining_enhanced}")
        print(f"      - Evidence files preserved: {remaining_evidence}")
    
    if mode['clean_nuances']:
        print("   🧹 NUANCES: Cleaned from all sessions (debugging fresh)")
        remaining_nuances = len(glob.glob("outputs/*/json/*_nuances.json"))
        remaining_nuance_evidence = len(glob.glob("outputs/*/json/*_nuances_evidence.json"))
        print(f"      - Nuance files remaining: {remaining_nuances}")
        print(f"      - Nuance evidence remaining: {remaining_nuance_evidence}")
        
        if remaining_nuances > 0 or remaining_nuance_evidence > 0:
            print(f"      ⚠️  Some nuance files remain - manual cleanup may be needed")
    
    # Show preserved sessions
    remaining_sessions = glob.glob("outputs/session_*")
    if remaining_sessions:
        print(f"   📁 Sessions preserved: {len(remaining_sessions)}")
        for session_dir in remaining_sessions[-3:]:  # Show last 3
            session_name = os.path.basename(session_dir)
            json_count = len(glob.glob(f"{session_dir}/json/*.json"))
            print(f"      - {session_name}: {json_count} files")
    
    print(f"\n🚀 Ready for nuance debugging!")
    if mode['clean_nuances']:
        print("   Run: python main.py  (will process nuances only)")
    print("   Server: python start_server.py  (themes will still display)")

if __name__ == "__main__":
    main() 