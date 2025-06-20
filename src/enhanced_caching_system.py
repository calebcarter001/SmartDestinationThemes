"""
Enhanced Caching System
Provides versioned caching for consolidated destination data and incremental processing.
"""

import logging
import json
import hashlib
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)

class ConsolidatedDataCache:
    """Cache manager for consolidated destination data"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache_config = config.get('enhanced_caching', {})
        self.cache_ttl = config.get('session_management', {}).get('consolidated_cache_ttl_hours', 24) * 3600
        
        # Cache directories
        self.cache_dir = Path("cache/consolidated")
        self.version_dir = Path("cache/versions")
        self.export_cache_dir = Path("cache/exports")
        
        # Create cache directories
        for dir_path in [self.cache_dir, self.version_dir, self.export_cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    async def get_consolidated_data(self, destination: str) -> Optional[Dict[str, Any]]:
        """Get cached consolidated data if valid"""
        cache_file = self._get_cache_file_path(destination)
        
        if not cache_file.exists():
            return None
            
        # Check if cache is still valid
        if time.time() - cache_file.stat().st_mtime > self.cache_ttl:
            cache_file.unlink()  # Remove expired cache
            logger.debug(f"Removed expired cache for {destination}")
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            logger.debug(f"Cache hit for consolidated data: {destination}")
            return cached_data
            
        except Exception as e:
            logger.warning(f"Failed to load cached data for {destination}: {e}")
            return None
    
    async def cache_consolidated_data(self, destination: str, data: Dict[str, Any]):
        """Cache consolidated data with versioning"""
        cache_file = self._get_cache_file_path(destination)
        
        try:
            # Generate version hash
            data_version = self._generate_data_version(data)
            
            # Add cache metadata
            cache_data = {
                'destination': destination,
                'data': data,
                'cache_metadata': {
                    'cached_at': datetime.now().isoformat(),
                    'data_version': data_version,
                    'ttl_hours': self.cache_ttl / 3600
                }
            }
            
            # Save main cache
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            # Save versioned copy if enabled
            if self.cache_config.get('data_versioning', True):
                await self._save_versioned_data(destination, data, data_version)
                
            logger.debug(f"Cached consolidated data for {destination} (version: {data_version[:8]})")
            
        except Exception as e:
            logger.error(f"Failed to cache data for {destination}: {e}")
    
    async def invalidate_destination_cache(self, destination: str):
        """Invalidate cache for a specific destination"""
        cache_file = self._get_cache_file_path(destination)
        if cache_file.exists():
            cache_file.unlink()
            logger.debug(f"Invalidated cache for {destination}")
    
    async def get_data_diff(self, destination: str, old_version: str, new_version: str) -> Optional[Dict]:
        """Get difference between two cached versions"""
        try:
            old_data = await self._get_versioned_data(destination, old_version)
            new_data = await self._get_versioned_data(destination, new_version)
            
            if not old_data or not new_data:
                return None
            
            # Calculate diff
            diff = {
                'destination': destination,
                'old_version': old_version,
                'new_version': new_version,
                'changes': self._calculate_data_diff(old_data, new_data),
                'diff_timestamp': datetime.now().isoformat()
            }
            
            return diff
            
        except Exception as e:
            logger.error(f"Failed to calculate diff for {destination}: {e}")
            return None
    
    def _get_cache_file_path(self, destination: str) -> Path:
        """Get cache file path for destination"""
        safe_name = destination.lower().replace(', ', '_').replace(' ', '_')
        return self.cache_dir / f"{safe_name}_consolidated.json"
    
    def _generate_data_version(self, data: Dict[str, Any]) -> str:
        """Generate version hash for data"""
        # Create deterministic string representation
        data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    async def _save_versioned_data(self, destination: str, data: Dict[str, Any], version: str):
        """Save versioned copy of data"""
        try:
            safe_name = destination.lower().replace(', ', '_').replace(' ', '_')
            version_file = self.version_dir / f"{safe_name}_{version[:8]}.json"
            
            version_data = {
                'destination': destination,
                'version': version,
                'data': data,
                'version_metadata': {
                    'created_at': datetime.now().isoformat(),
                    'data_size': len(json.dumps(data))
                }
            }
            
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2, ensure_ascii=False)
            
            # Clean up old versions
            await self._cleanup_old_versions(destination)
            
        except Exception as e:
            logger.error(f"Failed to save versioned data for {destination}: {e}")
    
    async def _get_versioned_data(self, destination: str, version: str) -> Optional[Dict]:
        """Get data for a specific version"""
        try:
            safe_name = destination.lower().replace(', ', '_').replace(' ', '_')
            version_file = self.version_dir / f"{safe_name}_{version[:8]}.json"
            
            if not version_file.exists():
                return None
            
            with open(version_file, 'r', encoding='utf-8') as f:
                version_data = json.load(f)
            
            return version_data.get('data')
            
        except Exception as e:
            logger.error(f"Failed to load versioned data for {destination} v{version}: {e}")
            return None
    
    async def _cleanup_old_versions(self, destination: str):
        """Clean up old versions beyond the limit"""
        try:
            max_versions = self.cache_config.get('max_versions_per_destination', 5)
            safe_name = destination.lower().replace(', ', '_').replace(' ', '_')
            
            # Find all version files for this destination
            version_files = list(self.version_dir.glob(f"{safe_name}_*.json"))
            
            if len(version_files) <= max_versions:
                return
            
            # Sort by modification time and remove oldest
            version_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            for old_file in version_files[max_versions:]:
                old_file.unlink()
                logger.debug(f"Removed old version file: {old_file.name}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old versions for {destination}: {e}")
    
    def _calculate_data_diff(self, old_data: Dict, new_data: Dict) -> Dict:
        """Calculate detailed diff between two data structures"""
        
        changes = {
            'themes': self._diff_themes(old_data.get('themes', {}), new_data.get('themes', {})),
            'nuances': self._diff_nuances(old_data.get('nuances', {}), new_data.get('nuances', {})),
            'images': self._diff_images(old_data.get('images', {}), new_data.get('images', {})),
            'evidence': self._diff_evidence(old_data.get('evidence', {}), new_data.get('evidence', {}))
        }
        
        return changes
    
    def _diff_themes(self, old_themes: Dict, new_themes: Dict) -> Dict:
        """Calculate diff for theme data"""
        
        old_affinities = {theme.get('theme', ''): theme for theme in old_themes.get('affinities', [])}
        new_affinities = {theme.get('theme', ''): theme for theme in new_themes.get('affinities', [])}
        
        added = []
        removed = []
        modified = []
        
        # Find added themes
        for theme_name, theme_data in new_affinities.items():
            if theme_name not in old_affinities:
                added.append(theme_data)
        
        # Find removed themes
        for theme_name, theme_data in old_affinities.items():
            if theme_name not in new_affinities:
                removed.append(theme_data)
        
        # Find modified themes
        for theme_name in set(old_affinities.keys()) & set(new_affinities.keys()):
            old_theme = old_affinities[theme_name]
            new_theme = new_affinities[theme_name]
            
            if old_theme != new_theme:
                modified.append({
                    'theme_name': theme_name,
                    'old': old_theme,
                    'new': new_theme
                })
        
        return {
            'added': added,
            'removed': removed,
            'modified': modified,
            'stats': {
                'total_added': len(added),
                'total_removed': len(removed),
                'total_modified': len(modified)
            }
        }
    
    def _diff_nuances(self, old_nuances: Dict, new_nuances: Dict) -> Dict:
        """Calculate diff for nuance data"""
        
        changes = {}
        categories = ['destination_nuances', 'hotel_expectations', 'vacation_rental_expectations']
        
        for category in categories:
            old_items = {item.get('phrase', ''): item for item in old_nuances.get(category, [])}
            new_items = {item.get('phrase', ''): item for item in new_nuances.get(category, [])}
            
            added = [item for phrase, item in new_items.items() if phrase not in old_items]
            removed = [item for phrase, item in old_items.items() if phrase not in new_items]
            
            changes[category] = {
                'added': added,
                'removed': removed,
                'stats': {
                    'total_added': len(added),
                    'total_removed': len(removed)
                }
            }
        
        return changes
    
    def _diff_images(self, old_images: Dict, new_images: Dict) -> Dict:
        """Calculate diff for image data"""
        
        added = {k: v for k, v in new_images.items() if k not in old_images}
        removed = {k: v for k, v in old_images.items() if k not in new_images}
        changed = {k: {'old': old_images[k], 'new': new_images[k]} 
                  for k in set(old_images.keys()) & set(new_images.keys()) 
                  if old_images[k] != new_images[k]}
        
        return {
            'added': added,
            'removed': removed,
            'changed': changed,
            'stats': {
                'total_added': len(added),
                'total_removed': len(removed),
                'total_changed': len(changed)
            }
        }
    
    def _diff_evidence(self, old_evidence: Dict, new_evidence: Dict) -> Dict:
        """Calculate diff for evidence data"""
        
        old_items = old_evidence.get('evidence', [])
        new_items = new_evidence.get('evidence', [])
        
        old_urls = {item.get('url', ''): item for item in old_items}
        new_urls = {item.get('url', ''): item for item in new_items}
        
        added = [item for url, item in new_urls.items() if url not in old_urls]
        removed = [item for url, item in old_urls.items() if url not in new_urls]
        
        return {
            'added': added,
            'removed': removed,
            'stats': {
                'total_added': len(added),
                'total_removed': len(removed)
            }
        }
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache usage statistics"""
        
        try:
            # Count cache files
            cache_files = list(self.cache_dir.glob("*.json"))
            version_files = list(self.version_dir.glob("*.json"))
            export_files = list(self.export_cache_dir.glob("*.json"))
            
            # Calculate sizes
            cache_size = sum(f.stat().st_size for f in cache_files)
            version_size = sum(f.stat().st_size for f in version_files)
            export_size = sum(f.stat().st_size for f in export_files)
            
            return {
                'cache_statistics': {
                    'cached_destinations': len(cache_files),
                    'versioned_entries': len(version_files),
                    'export_cache_entries': len(export_files),
                    'total_cache_size_mb': (cache_size + version_size + export_size) / (1024 * 1024),
                    'cache_directories': {
                        'consolidated': str(self.cache_dir),
                        'versions': str(self.version_dir),
                        'exports': str(self.export_cache_dir)
                    },
                    'cache_ttl_hours': self.cache_ttl / 3600
                },
                'configuration': {
                    'versioning_enabled': self.cache_config.get('data_versioning', True),
                    'max_versions_per_destination': self.cache_config.get('max_versions_per_destination', 5),
                    'auto_invalidate_on_new_data': self.cache_config.get('auto_invalidate_on_new_data', True)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            return {'error': str(e)}
    
    async def clear_all_cache(self):
        """Clear all cached data"""
        try:
            for cache_dir in [self.cache_dir, self.version_dir, self.export_cache_dir]:
                for file in cache_dir.glob("*.json"):
                    file.unlink()
            
            logger.info("Cleared all cached data")
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    async def cache_export_data(self, destination: str, export_data: Dict[str, Any], export_format: str):
        """Cache export data for faster retrieval"""
        try:
            safe_name = destination.lower().replace(', ', '_').replace(' ', '_')
            export_file = self.export_cache_dir / f"{safe_name}_{export_format}.json"
            
            cache_data = {
                'destination': destination,
                'export_format': export_format,
                'export_data': export_data,
                'cached_at': datetime.now().isoformat()
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Cached export data for {destination} ({export_format})")
            
        except Exception as e:
            logger.error(f"Failed to cache export data for {destination}: {e}")
    
    async def get_cached_export_data(self, destination: str, export_format: str) -> Optional[Dict[str, Any]]:
        """Get cached export data if available and valid"""
        try:
            safe_name = destination.lower().replace(', ', '_').replace(' ', '_')
            export_file = self.export_cache_dir / f"{safe_name}_{export_format}.json"
            
            if not export_file.exists():
                return None
            
            # Check if cache is still valid (shorter TTL for exports)
            export_ttl = 3600  # 1 hour for exports
            if time.time() - export_file.stat().st_mtime > export_ttl:
                export_file.unlink()
                return None
            
            with open(export_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            return cached_data.get('export_data')
            
        except Exception as e:
            logger.error(f"Failed to get cached export data for {destination}: {e}")
            return None 