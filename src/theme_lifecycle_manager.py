"""
Theme Lifecycle Manager
Manages theme data lifecycle and incremental updates across sessions.
"""

import logging
import json
import os
import glob
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class ThemeLifecycleManager:
    """Manages theme data lifecycle and incremental updates"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.theme_config = config.get('theme_processing', {})
        self.session_config = config.get('session_management', {})
        
    def should_update_themes(self, destination: str) -> bool:
        """Determine if themes need updating based on existing data and thresholds"""
        existing_themes = self._get_existing_themes(destination)
        
        if not existing_themes:
            logger.info(f"No existing themes found for {destination} - full processing needed")
            return True
            
        # Check if incremental updates are enabled
        if not self.theme_config.get('enable_incremental_updates', False):
            logger.info(f"Incremental updates disabled - full processing for {destination}")
            return True
            
        # Check age threshold
        threshold_days = self.theme_config.get('incremental_update_threshold_days', 7)
        if self._is_data_older_than_threshold(existing_themes, threshold_days):
            logger.info(f"Existing themes for {destination} older than {threshold_days} days - updating")
            return True
            
        # Check quality threshold
        existing_quality = existing_themes.get('processing_metadata', {}).get('quality_score', 0.0)
        min_quality = self.theme_config.get('min_quality_for_preservation', 0.7)
        
        if existing_quality < min_quality:
            logger.info(f"Existing themes for {destination} below quality threshold ({existing_quality:.3f} < {min_quality}) - updating")
            return True
            
        logger.info(f"Existing themes for {destination} are sufficient (quality: {existing_quality:.3f}) - preserving")
        return False
        
    def merge_theme_data(self, destination: str, new_themes: List[Dict], existing_themes: Dict) -> Dict:
        """Merge new theme data with existing using configured strategy"""
        merge_strategy = self.theme_config.get('merge_strategy', 'quality_based')
        
        logger.info(f"Merging themes for {destination} using strategy: {merge_strategy}")
        
        if merge_strategy == 'quality_based':
            return self._merge_themes_by_quality(destination, new_themes, existing_themes)
        elif merge_strategy == 'additive':
            return self._merge_themes_additive(destination, new_themes, existing_themes)
        elif merge_strategy == 'replace':
            return self._create_theme_data_structure(destination, new_themes)
        else:
            logger.warning(f"Unknown merge strategy: {merge_strategy}, using quality_based")
            return self._merge_themes_by_quality(destination, new_themes, existing_themes)
    
    def _get_existing_themes(self, destination: str) -> Optional[Dict[str, Any]]:
        """Get existing theme data for a destination from the most recent session"""
        try:
            dest_filename = destination.lower().replace(', ', '__').replace(' ', '_')
            
            # Look through session directories (most recent first)
            outputs_dir = Path("outputs")
            if not outputs_dir.exists():
                return None
            
            session_dirs = sorted([d for d in outputs_dir.iterdir() 
                                 if d.is_dir() and d.name.startswith("session_")], 
                                 key=lambda x: x.stat().st_mtime, reverse=True)
            
            for session_dir in session_dirs:
                json_dir = session_dir / "json"
                if not json_dir.exists():
                    continue
                
                enhanced_file = json_dir / f"{dest_filename}_enhanced.json"
                if enhanced_file.exists():
                    with open(enhanced_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                    
                    processing_date = existing_data.get('processing_metadata', {}).get('processing_date', '')
                    logger.debug(f"Found existing theme data for {destination} from {processing_date}")
                    return existing_data
            
            return None
            
        except Exception as e:
            logger.warning(f"Error checking existing theme data for {destination}: {e}")
            return None
    
    def _is_data_older_than_threshold(self, data: Dict, threshold_days: int) -> bool:
        """Check if data is older than the threshold"""
        try:
            processing_date = data.get('processing_metadata', {}).get('processing_date', '')
            if not processing_date:
                return True
            
            processed_at = datetime.fromisoformat(processing_date.replace('Z', '+00:00'))
            threshold = datetime.now() - timedelta(days=threshold_days)
            return processed_at < threshold
            
        except Exception as e:
            logger.warning(f"Error checking data age: {e}")
            return True
    
    def _merge_themes_by_quality(self, destination: str, new_themes: List[Dict], existing_data: Dict) -> Dict:
        """Merge themes based on quality and confidence scores"""
        existing_themes = existing_data.get('affinities', [])
        
        # Compare overall quality first
        new_avg_confidence = sum(theme.get('confidence', 0.0) for theme in new_themes) / len(new_themes) if new_themes else 0.0
        existing_avg_confidence = sum(theme.get('confidence', 0.0) for theme in existing_themes) / len(existing_themes) if existing_themes else 0.0
        
        quality_threshold = self.theme_config.get('quality_improvement_threshold', 0.05)
        
        # If new data is significantly better, replace entirely
        if new_avg_confidence > existing_avg_confidence + quality_threshold:
            logger.info(f"New themes significantly better for {destination}: {existing_avg_confidence:.3f} -> {new_avg_confidence:.3f}")
            return self._create_theme_data_structure(destination, new_themes)
        
        # Otherwise, do intelligent merging
        logger.info(f"Merging themes for {destination}: preserving existing quality {existing_avg_confidence:.3f}, adding unique from new {new_avg_confidence:.3f}")
        
        # Create theme comparison matrix
        merged_themes = []
        used_existing = set()
        
        for new_theme in new_themes:
            best_match = self._find_best_matching_theme(new_theme, existing_themes)
            
            if best_match:
                # Compare quality scores
                new_confidence = new_theme.get('confidence', 0.0)
                existing_confidence = best_match.get('confidence', 0.0)
                
                # Use better quality theme
                if new_confidence > existing_confidence + quality_threshold:
                    merged_themes.append(new_theme)
                    logger.debug(f"Replaced theme '{new_theme.get('theme', 'unknown')}': {existing_confidence:.3f} -> {new_confidence:.3f}")
                else:
                    merged_themes.append(best_match)
                    used_existing.add(id(best_match))
                    logger.debug(f"Kept existing theme '{best_match.get('theme', 'unknown')}': {existing_confidence:.3f}")
            else:
                # New unique theme
                merged_themes.append(new_theme)
                logger.debug(f"Added new unique theme: '{new_theme.get('theme', 'unknown')}'")
        
        # Add any existing themes not matched
        for existing_theme in existing_themes:
            if id(existing_theme) not in used_existing:
                if not self._theme_exists_in_list(existing_theme, merged_themes):
                    merged_themes.append(existing_theme)
                    logger.debug(f"Preserved unmatched existing theme: '{existing_theme.get('theme', 'unknown')}'")
        
        # Update existing data structure
        result = existing_data.copy()
        result['affinities'] = merged_themes
        result['processing_metadata']['last_merge'] = datetime.now().isoformat()
        result['processing_metadata']['merge_strategy'] = 'quality_based'
        result['processing_metadata']['merged_theme_count'] = len(merged_themes)
        
        return result
    
    def _merge_themes_additive(self, destination: str, new_themes: List[Dict], existing_data: Dict) -> Dict:
        """Add new unique themes to existing themes"""
        existing_themes = existing_data.get('affinities', [])
        similarity_threshold = self.theme_config.get('similarity_threshold', 0.85)
        
        merged_themes = existing_themes.copy()
        added_count = 0
        
        for new_theme in new_themes:
            if not self._is_theme_similar_to_existing(new_theme, existing_themes, similarity_threshold):
                merged_themes.append(new_theme)
                added_count += 1
                logger.debug(f"Added unique theme: '{new_theme.get('theme', 'unknown')}'")
        
        result = existing_data.copy()
        result['affinities'] = merged_themes
        result['processing_metadata']['last_merge'] = datetime.now().isoformat()
        result['processing_metadata']['merge_strategy'] = 'additive'
        result['processing_metadata']['themes_added'] = added_count
        
        logger.info(f"Added {added_count} unique themes to {len(existing_themes)} existing themes for {destination}")
        return result
    
    def _create_theme_data_structure(self, destination: str, themes: List[Dict]) -> Dict:
        """Create new theme data structure"""
        return {
            'destination': destination,
            'destination_id': destination.lower().replace(', ', '__').replace(' ', '_'),
            'destination_name': destination,
            'affinities': themes,
            'processing_metadata': {
                'processing_date': datetime.now().isoformat(),
                'source_system': 'theme_lifecycle_manager',
                'theme_count': len(themes),
                'processing_strategy': 'replace',
                'quality_score': sum(theme.get('confidence', 0.0) for theme in themes) / len(themes) if themes else 0.0
            }
        }
    
    def _find_best_matching_theme(self, new_theme: Dict, existing_themes: List[Dict]) -> Optional[Dict]:
        """Find the best matching theme from existing themes"""
        new_theme_name = new_theme.get('theme', '').lower()
        new_category = new_theme.get('category', '').lower()
        
        best_match = None
        best_score = 0.0
        
        for existing_theme in existing_themes:
            existing_name = existing_theme.get('theme', '').lower()
            existing_category = existing_theme.get('category', '').lower()
            
            # Calculate similarity score
            score = 0.0
            
            # Name similarity (most important)
            if new_theme_name == existing_name:
                score += 0.8
            elif new_theme_name in existing_name or existing_name in new_theme_name:
                score += 0.6
            elif self._calculate_string_similarity(new_theme_name, existing_name) > 0.7:
                score += 0.4
            
            # Category similarity
            if new_category == existing_category:
                score += 0.2
            
            if score > best_score and score > 0.5:  # Minimum similarity threshold
                best_score = score
                best_match = existing_theme
        
        return best_match
    
    def _theme_exists_in_list(self, theme: Dict, theme_list: List[Dict]) -> bool:
        """Check if a theme already exists in the list"""
        theme_name = theme.get('theme', '').lower()
        return any(existing.get('theme', '').lower() == theme_name for existing in theme_list)
    
    def _is_theme_similar_to_existing(self, new_theme: Dict, existing_themes: List[Dict], threshold: float) -> bool:
        """Check if new theme is similar to any existing theme"""
        new_theme_name = new_theme.get('theme', '').lower()
        
        for existing_theme in existing_themes:
            existing_name = existing_theme.get('theme', '').lower()
            
            if new_theme_name == existing_name:
                return True
            
            if self._calculate_string_similarity(new_theme_name, existing_name) > threshold:
                return True
        
        return False
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using simple algorithm"""
        if not str1 or not str2:
            return 0.0
        
        # Simple Jaccard similarity on words
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def get_theme_statistics(self, destination: str) -> Dict[str, Any]:
        """Get statistics about theme data for a destination"""
        existing_themes = self._get_existing_themes(destination)
        
        if not existing_themes:
            return {
                'has_existing_data': False,
                'theme_count': 0,
                'quality_score': 0.0,
                'last_updated': None
            }
        
        affinities = existing_themes.get('affinities', [])
        
        return {
            'has_existing_data': True,
            'theme_count': len(affinities),
            'quality_score': sum(theme.get('confidence', 0.0) for theme in affinities) / len(affinities) if affinities else 0.0,
            'last_updated': existing_themes.get('processing_metadata', {}).get('processing_date'),
            'categories': list(set(theme.get('category', 'unknown') for theme in affinities)),
            'processing_strategy': existing_themes.get('processing_metadata', {}).get('processing_strategy', 'unknown')
        } 