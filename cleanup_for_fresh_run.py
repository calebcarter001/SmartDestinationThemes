#!/usr/bin/env python3
"""
Comprehensive cleanup script for fresh runs of the Enhanced Destination Intelligence system.
Removes all cached data, logs, databases, previous outputs, and enhanced intelligence artifacts.
Updated for Enhanced Intelligence v2.0 with progress tracking, evidence validation, and destination nuances.
"""

import os
import shutil
import glob
from pathlib import Path

def clean_directory(dir_path, description):
    """Clean a directory and report results"""
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

def clean_session_outputs():
    """Clean timestamped session outputs from enhanced processing"""
    print("🧹 Cleaning Enhanced Intelligence session outputs...")
    
    if not os.path.exists("outputs"):
        print("✅ outputs/ directory doesn't exist (clean)")
        return
    
    sessions_removed = 0
    files_removed = 0
    
    # Find session directories with pattern: session_YYYYMMDD_HHMMSS
    for item in os.listdir("outputs"):
        item_path = os.path.join("outputs", item)
        if os.path.isdir(item_path) and item.startswith("session_"):
            try:
                # Count files in session before removal
                for root, dirs, files in os.walk(item_path):
                    files_removed += len(files)
                
                shutil.rmtree(item_path)
                sessions_removed += 1
                print(f"✅ Removed session: {item}")
            except Exception as e:
                print(f"⚠️  Error removing session {item}: {e}")
    
    if sessions_removed > 0:
        print(f"✅ Enhanced Intelligence sessions: removed {sessions_removed} sessions ({files_removed} files)")
    else:
        print("✅ Enhanced Intelligence sessions: no sessions found")

def main():
    """Run comprehensive cleanup for Enhanced Intelligence system"""
    print("🧹 Starting Enhanced Intelligence v2.0 cleanup for fresh run...")
    print("🎯 Cleaning: Enhanced processing, evidence validation, destination nuances")
    print("=" * 80)
    
    # Define cleanup targets (enhanced for v2.0)
    cleanup_targets = [
        ("logs", "Application logs"),
        ("cache", "File-based cache"), 
        ("chroma_db", "ChromaDB vector database"),
        ("destination_insights", "Previous destination insights"),
        ("test_destination_insights", "Test destination insights"),
        (".pytest_cache", "Pytest cache directory"),
        ("enhanced_dashboard", "Enhanced dashboard outputs"),
    ]
    
    # Database files and large data files (enhanced)
    db_files = [
        "enhanced_destination_intelligence.db",
        "test_enhanced_destination_intelligence.db", 
        ":memory:",  # SQLite memory database file
        "comprehensive_database_report.json",  # Large 2GB+ report file
        "destination_evidence.db",  # Evidence validation database
        "theme_intelligence.db",  # Enhanced intelligence database
    ]
    
    # Generated output files that should be cleaned (enhanced)
    generated_files = [
        "dynamic_database_viewer.html",
        "results_viewer.html", 
        "run_enhanced_agent_app.py.lprof",  # Profiling output
        "destination_affinities_production.json",  # Basic production output
        "destination_affinities_enhanced.json",  # Enhanced output
        "processing_summary.json",  # Processing summary
        "session_summary.json",  # Session summary
        "enhanced_intelligence_summary.json",  # Intelligence summary
        "evidence_validation_report.json",  # Evidence validation
    ]
    
    # Enhanced LLM artifacts and demo files
    enhanced_artifacts = [
        "demo_enhanced_*.py",  # Demo files
        "*_enhanced.json",  # Enhanced JSON outputs  
        "*_with_evidence.json",  # Evidence-enhanced files
        "enhanced_viewer_*.html",  # Enhanced viewer files
        "intelligence_report_*.json",  # Intelligence reports
        "validation_report_*.json",  # Validation reports
    ]
    
    # Dashboard artifacts (both basic and enhanced)
    dashboard_files = [
        "dashboard/index.html",
        "dashboard/*.html",
        "enhanced_dashboard/*.html",
        "open_dashboard.py",
        "open_enhanced_dashboard.py",
    ]
    
    # IDE and editor artifacts (optional cleanup)
    ide_dirs = ['.vscode', '.idea', '.sublime-project', '.sublime-workspace']
    
    # Clean main directories
    for dir_path, description in cleanup_targets:
        clean_directory(dir_path, description)
    
    # Clean Enhanced Intelligence session outputs (new feature)
    clean_session_outputs()
    
    # Clean dashboard directory completely
    if os.path.exists("dashboard"):
        clean_directory("dashboard", "Basic dashboard outputs")
    
    # Clean IDE directories (if they exist)
    for ide_dir in ide_dirs:
        if os.path.exists(ide_dir):
            clean_directory(ide_dir, f"IDE artifacts ({ide_dir})")
    
    # Clean database files and large data files
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                file_size = os.path.getsize(db_file) / (1024*1024)  # Size in MB
                os.remove(db_file)
                if file_size > 100:  # Show size for large files
                    print(f"✅ Removed large file: {db_file} ({file_size:.1f}MB)")
                else:
                    print(f"✅ Removed file: {db_file}")
            except Exception as e:
                print(f"⚠️  Error removing {db_file}: {e}")
        else:
            print(f"✅ File {db_file}: doesn't exist (clean)")
    
    # Clean generated output files
    for gen_file in generated_files:
        if os.path.exists(gen_file):
            try:
                os.remove(gen_file)
                print(f"✅ Removed generated file: {gen_file}")
            except Exception as e:
                print(f"⚠️  Error removing {gen_file}: {e}")
    
    # Clean enhanced artifacts using glob patterns
    print("🧹 Cleaning Enhanced Intelligence artifacts...")
    enhanced_removed = 0
    for pattern in enhanced_artifacts:
        matching_files = glob.glob(pattern)
        for artifact_file in matching_files:
            try:
                # Skip files in venv
                if 'venv/' in artifact_file or artifact_file.startswith('venv/'):
                    continue
                os.remove(artifact_file)
                enhanced_removed += 1
                print(f"✅ Removed enhanced artifact: {artifact_file}")
            except Exception as e:
                print(f"⚠️  Error removing {artifact_file}: {e}")
    
    if enhanced_removed > 0:
        print(f"✅ Enhanced artifacts: removed {enhanced_removed} files")
    else:
        print("✅ Enhanced artifacts: no files found")
    
    # Clean dynamic viewer HTML files (pattern-based cleanup)
    print("🧹 Cleaning dynamic viewer HTML files...")
    dynamic_viewer_files = glob.glob("dynamic_viewer_*.html")
    if dynamic_viewer_files:
        for dv_file in dynamic_viewer_files:
            try:
                file_size = os.path.getsize(dv_file) / (1024*1024)  # Size in MB
                os.remove(dv_file)
                if file_size > 0.1:  # Show size for files > 100KB
                    print(f"✅ Removed dynamic viewer: {dv_file} ({file_size:.1f}MB)")
                else:
                    print(f"✅ Removed dynamic viewer: {dv_file}")
            except Exception as e:
                print(f"⚠️  Error removing {dv_file}: {e}")
    else:
        print("✅ No dynamic viewer HTML files found")
    
    # Clean Python cache files recursively
    print("🧹 Cleaning Python cache files...")
    cache_cleaned = 0
    
    # Remove __pycache__ directories recursively
    for root, dirs, files in os.walk('.'):
        # Skip venv directory
        if 'venv' in root or root.startswith('./venv'):
            continue
            
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                cache_cleaned += 1
            except Exception as e:
                print(f"⚠️  Error removing {pycache_path}: {e}")
    
    # Remove .pyc and .pyo files recursively
    pyc_files = [f for f in glob.glob('**/*.pyc', recursive=True) if 'venv/' not in f]
    pyo_files = [f for f in glob.glob('**/*.pyo', recursive=True) if 'venv/' not in f]
    
    for pyc_file in pyc_files + pyo_files:
        try:
            os.remove(pyc_file)
            cache_cleaned += 1
        except Exception as e:
            print(f"⚠️  Error removing {pyc_file}: {e}")
    
    if cache_cleaned > 0:
        print(f"✅ Cleaned Python cache: removed {cache_cleaned} items")
    else:
        print("✅ Python cache: already clean")
    
    # Clean system files and development artifacts
    system_files = glob.glob('.DS_Store') + glob.glob('**/.DS_Store', recursive=True)
    system_files += glob.glob('.coverage') + glob.glob('**/*.db-journal', recursive=True)
    system_files += glob.glob('**/*.sqlite', recursive=True) + glob.glob('**/*.sqlite3', recursive=True)
    
    # Additional development artifacts
    system_files += glob.glob('.env.local') + glob.glob('.env.*.local')  # Local env files
    system_files += glob.glob('**/*.prof', recursive=True)  # Profiling files
    system_files += glob.glob('**/*.pstats', recursive=True)  # Performance stats
    system_files += glob.glob('.coverage.*')  # Coverage data files
    
    if system_files:
        for sys_file in system_files:
            try:
                # Skip files in venv directory
                if 'venv/' in sys_file or sys_file.startswith('venv/'):
                    continue
                os.remove(sys_file)
                print(f"✅ Removed system file: {sys_file}")
            except Exception as e:
                print(f"⚠️  Error removing {sys_file}: {e}")
    
    # Clean coverage HTML reports
    if os.path.exists('htmlcov'):
        clean_directory('htmlcov', "Coverage HTML reports")
    
    # Clean any stray log files in root
    log_files = [f for f in glob.glob("*.log") if not f.startswith('venv/')]
    if log_files:
        for log_file in log_files:
            try:
                os.remove(log_file)
                print(f"✅ Removed stray log file: {log_file}")
            except Exception as e:
                print(f"⚠️  Error removing {log_file}: {e}")
    
    # Clean any temporary test files (but preserve legitimate ones)
    temp_files = glob.glob("debug_*.py") + glob.glob("temp_*.py")
    # Be more selective with test files - only remove obvious temporary ones
    temp_test_files = [f for f in glob.glob("test_*.py") if any(pattern in f for pattern in ["temp_", "debug_", "_tmp", "_test_run"])]
    temp_files.extend(temp_test_files)
    
    if temp_files:
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
                print(f"✅ Removed temporary file: {temp_file}")
            except Exception as e:
                print(f"⚠️  Error removing {temp_file}: {e}")
    
    print("\n" + "=" * 80)
    print("🎉 Enhanced Intelligence v2.0 cleanup completed! System ready for fresh run.")
    print("\n📊 Post-cleanup status:")
    
    # Verify cleanup of directories
    verification_dirs = ["logs", "cache", "chroma_db", "outputs", "destination_insights", ".pytest_cache", "htmlcov", "dashboard", "enhanced_dashboard"]
    for dir_name in verification_dirs:
        if os.path.exists(dir_name):
            item_count = len(os.listdir(dir_name))
            status = "✅ Empty" if item_count == 0 else f"⚠️  {item_count} items remaining"
            print(f"   {dir_name}/: {status}")
        else:
            print(f"   {dir_name}/: ✅ Directory doesn't exist")
    
    # Check database and large files
    for db_file in db_files:
        status = "✅ Removed" if not os.path.exists(db_file) else "⚠️  Still exists"
        print(f"   {db_file}: {status}")
    
    # Check generated files
    for gen_file in generated_files:
        status = "✅ Removed" if not os.path.exists(gen_file) else "⚠️  Still exists"
        print(f"   {gen_file}: {status}")
    
    # Check dynamic viewer files
    remaining_dynamic_viewers = glob.glob("dynamic_viewer_*.html")
    if remaining_dynamic_viewers:
        print(f"   Dynamic viewer HTMLs: ⚠️  {len(remaining_dynamic_viewers)} remaining")
    else:
        print("   Dynamic viewer HTMLs: ✅ All removed")
    
    # Check enhanced artifacts
    remaining_enhanced = 0
    for pattern in enhanced_artifacts:
        remaining_enhanced += len([f for f in glob.glob(pattern) if 'venv/' not in f])
    
    if remaining_enhanced > 0:
        print(f"   Enhanced artifacts: ⚠️  {remaining_enhanced} remaining")
    else:
        print("   Enhanced artifacts: ✅ All removed")
    
    # Check for remaining cache files
    remaining_pycache = len([d for d in glob.glob('**/__pycache__', recursive=True) if 'venv/' not in d])
    remaining_pyc = len([f for f in glob.glob('**/*.pyc', recursive=True) if 'venv/' not in f])
    remaining_ds_store = len([f for f in glob.glob('**/.DS_Store', recursive=True) if 'venv/' not in f])
    
    cache_status = "✅ Clean" if (remaining_pycache + remaining_pyc + remaining_ds_store) == 0 else f"⚠️  {remaining_pycache + remaining_pyc + remaining_ds_store} items remaining"
    print(f"   Python cache files: {cache_status}")
    
    # Check for development artifacts
    remaining_prof = len([f for f in glob.glob('**/*.prof', recursive=True) if 'venv/' not in f])
    remaining_coverage = len(glob.glob('.coverage*'))
    if remaining_prof > 0 or remaining_coverage > 0:
        print(f"   Development artifacts: ⚠️  {remaining_prof + remaining_coverage} files remaining")
    else:
        print("   Development artifacts: ✅ Clean")
    
    print("\n🚀 Ready for fresh Enhanced Intelligence v2.0 run:")
    print("   • python enhanced_main_processor.py (Enhanced Intelligence with progress tracking)")
    print("   • python main.py (Basic processing)")
    print("   • python demo_enhanced_intelligence.py (Enhanced LLM nuances demo)")
    print("\n🎯 Enhanced Intelligence v2.0 Features Ready:")
    print("   ✅ 10 Intelligence Layers")
    print("   ✅ Progress Tracking with tqdm") 
    print("   ✅ Evidence Validation System")
    print("   ✅ Destination Nuances & Traveler Specifics")
    print("   ✅ HTTP Server Management")
    print("   ✅ Timestamped Session Organization")

if __name__ == "__main__":
    main() 