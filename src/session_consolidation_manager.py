"""
Session Consolidation Manager
Manages consolidation of destination data across multiple sessions.
"""

import logging
import json
import os
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class SessionData:
    """Represents data from a single session"""
    session_id: str
    session_path: str
    creation_date: datetime
    destinations: List[str]
    data_types: List[str]  # ['themes', 'nuances', 'images']
    quality_scores: Dict[str, float]

@dataclass
class ConsolidatedData:
    """Consolidated data structure for a destination"""
    destination: str
    themes: Dict[str, Any]
    nuances: Dict[str, Any]
    images: Dict[str, str]  # season -> image_path
    evidence: Dict[str, Any]
    metadata: Dict[str, Any]
    source_sessions: List[str]

class SessionConsolidationManager:
    """Manages consolidation of destination data across sessions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.consolidation_config = config.get('session_management', {})
        self.outputs_dir = Path("outputs")
        
    async def consolidate_destination_data(self, destination: str) -> ConsolidatedData:
        """Main consolidation method for a destination"""
        
        logger.info(f"Starting consolidation for destination: {destination}")
        
        # 1. Discover all sessions with data for this destination
        relevant_sessions = await self._discover_sessions_for_destination(destination)
        
        if not relevant_sessions:
            raise ValueError(f"No session data found for destination: {destination}")
        
        # 2. Load data from all sessions
        session_data = await self._load_session_data(destination, relevant_sessions)
        
        # 3. Consolidate using configured strategy
        consolidation_strategy = self.consolidation_config.get('consolidation_strategy', 'quality_based')
        
        logger.info(f"Using consolidation strategy: {consolidation_strategy}")
        
        if consolidation_strategy == 'latest_wins':
            consolidated = await self._consolidate_latest_wins(destination, session_data)
        elif consolidation_strategy == 'quality_based':
            consolidated = await self._consolidate_quality_based(destination, session_data)
        elif consolidation_strategy == 'additive':
            consolidated = await self._consolidate_additive(destination, session_data)
        else:
            consolidated = await self._consolidate_quality_based(destination, session_data)
        
        # 4. Validate consolidated data
        await self._validate_consolidated_data(consolidated)
        
        logger.info(f"Consolidation complete for {destination}: {len(consolidated.source_sessions)} sessions combined")
        return consolidated
    
    async def _discover_sessions_for_destination(self, destination: str) -> List[SessionData]:
        """Discover all sessions containing data for destination"""
        sessions = []
        dest_filename = destination.lower().replace(', ', '__').replace(' ', '_')
        
        if not self.outputs_dir.exists():
            return sessions
        
        # Scan all session directories
        for session_dir in self.outputs_dir.glob("session_*"):
            if not session_dir.is_dir():
                continue
                
            json_dir = session_dir / "json"
            if not json_dir.exists():
                continue
            
            # Check what data types exist for this destination
            data_types = []
            quality_scores = {}
            
            # Check for themes
            enhanced_file = json_dir / f"{dest_filename}_enhanced.json"
            if enhanced_file.exists():
                data_types.append('themes')
                quality_scores['themes'] = await self._extract_quality_score(enhanced_file)
            
            # Check for nuances
            nuances_file = json_dir / f"{dest_filename}_nuances.json"
            if nuances_file.exists():
                data_types.append('nuances')
                quality_scores['nuances'] = await self._extract_quality_score(nuances_file)
            
            # Check for images
            images_dir = session_dir / "images" / dest_filename.replace('__', '_')
            if images_dir.exists() and any(images_dir.glob("*.jpg")):
                data_types.append('images')
                quality_scores['images'] = 1.0  # Images don't have quality scores
            
            if data_types:  # Found relevant data
                sessions.append(SessionData(
                    session_id=session_dir.name,
                    session_path=str(session_dir),
                    creation_date=datetime.fromtimestamp(session_dir.stat().st_ctime),
                    destinations=[destination],
                    data_types=data_types,
                    quality_scores=quality_scores
                ))
        
        # Sort by creation date (newest first)
        sessions.sort(key=lambda s: s.creation_date, reverse=True)
        
        # Limit number of sessions to consider
        max_sessions = self.consolidation_config.get('max_sessions_to_consider', 10)
        sessions = sessions[:max_sessions]
        
        logger.info(f"Found {len(sessions)} sessions with data for {destination}")
        return sessions
    
    async def _extract_quality_score(self, file_path: Path) -> float:
        """Extract quality score from a data file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Try different locations for quality score
            quality_score = (
                data.get('quality_score') or
                data.get('processing_metadata', {}).get('quality_score') or
                0.0
            )
            
            return float(quality_score)
            
        except Exception as e:
            logger.warning(f"Failed to extract quality score from {file_path}: {e}")
            return 0.0
    
    async def _load_session_data(self, destination: str, sessions: List[SessionData]) -> Dict[str, Dict]:
        """Load data from all relevant sessions"""
        session_data = {}
        dest_filename = destination.lower().replace(', ', '__').replace(' ', '_')
        
        for session in sessions:
            session_path = Path(session.session_path)
            json_dir = session_path / "json"
            
            session_info = {
                'session_id': session.session_id,
                'creation_date': session.creation_date,
                'quality_scores': session.quality_scores,
                'themes': None,
                'nuances': None,
                'images': None,
                'evidence': None
            }
            
            # Load themes
            if 'themes' in session.data_types:
                enhanced_file = json_dir / f"{dest_filename}_enhanced.json"
                if enhanced_file.exists():
                    try:
                        with open(enhanced_file, 'r', encoding='utf-8') as f:
                            session_info['themes'] = json.load(f)
                    except Exception as e:
                        logger.warning(f"Failed to load themes from {session.session_id}: {e}")
            
            # Load nuances
            if 'nuances' in session.data_types:
                nuances_file = json_dir / f"{dest_filename}_nuances.json"
                if nuances_file.exists():
                    try:
                        with open(nuances_file, 'r', encoding='utf-8') as f:
                            session_info['nuances'] = json.load(f)
                    except Exception as e:
                        logger.warning(f"Failed to load nuances from {session.session_id}: {e}")
            
            # Load evidence
            evidence_file = json_dir / f"{dest_filename}_evidence.json"
            if evidence_file.exists():
                try:
                    with open(evidence_file, 'r', encoding='utf-8') as f:
                        session_info['evidence'] = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load evidence from {session.session_id}: {e}")
            
            # Load images
            if 'images' in session.data_types:
                images_dir = session_path / "images" / dest_filename.replace('__', '_')
                if images_dir.exists():
                    session_info['images'] = await self._load_image_data(images_dir)
            
            session_data[session.session_id] = session_info
        
        return session_data
    
    async def _consolidate_quality_based(self, destination: str, session_data: Dict[str, Dict]) -> ConsolidatedData:
        """Consolidate based on quality scores"""
        
        # Find best quality data for each type
        best_themes = self._find_best_quality_data(session_data, 'themes')
        best_nuances = self._find_best_quality_data(session_data, 'nuances')
        best_images = self._find_latest_data(session_data, 'images')  # Images use latest
        
        # Consolidate evidence from all sources
        consolidated_evidence = await self._consolidate_evidence(destination, session_data)
        
        # Build consolidated data
        consolidated = ConsolidatedData(
            destination=destination,
            themes=best_themes['data'] if best_themes else {},
            nuances=best_nuances['data'] if best_nuances else {},
            images=best_images['data'] if best_images else {},
            evidence=consolidated_evidence,
            metadata={
                'consolidation_strategy': 'quality_based',
                'consolidation_timestamp': datetime.now().isoformat(),
                'quality_scores': {
                    'themes': best_themes['quality_score'] if best_themes else 0.0,
                    'nuances': best_nuances['quality_score'] if best_nuances else 0.0
                },
                'data_sources': {
                    'themes': best_themes['session_id'] if best_themes else None,
                    'nuances': best_nuances['session_id'] if best_nuances else None,
                    'images': best_images['session_id'] if best_images else None
                }
            },
            source_sessions=list(set(filter(None, [
                best_themes['session_id'] if best_themes else None,
                best_nuances['session_id'] if best_nuances else None,
                best_images['session_id'] if best_images else None
            ])))
        )
        
        return consolidated
    
    def _find_best_quality_data(self, session_data: Dict[str, Dict], data_type: str) -> Optional[Dict]:
        """Find the session with the best quality data for a given type"""
        best_data = None
        best_quality = 0.0
        
        for session_id, data in session_data.items():
            if data[data_type] is None:
                continue
                
            quality = data['quality_scores'].get(data_type, 0.0)
            
            if quality > best_quality:
                best_quality = quality
                best_data = {
                    'session_id': session_id,
                    'data': data[data_type],
                    'quality_score': quality,
                    'creation_date': data['creation_date']
                }
        
        return best_data
    
    def _find_latest_data(self, session_data: Dict[str, Dict], data_type: str) -> Optional[Dict]:
        """Find the latest data for a given type"""
        latest_data = None
        latest_date = None
        
        for session_id, data in session_data.items():
            if data[data_type] is None:
                continue
            
            creation_date = data['creation_date']
            
            if latest_date is None or creation_date > latest_date:
                latest_date = creation_date
                latest_data = {
                    'session_id': session_id,
                    'data': data[data_type],
                    'creation_date': creation_date
                }
        
        return latest_data
    
    async def _consolidate_evidence(self, destination: str, session_data: Dict[str, Dict]) -> Dict[str, Any]:
        """Consolidate evidence from all sessions"""
        all_evidence = []
        
        for session_id, data in session_data.items():
            if data['evidence'] and isinstance(data['evidence'], list):
                all_evidence.extend(data['evidence'])
        
        # Deduplicate evidence based on content similarity
        unique_evidence = self._deduplicate_evidence(all_evidence)
        
        return {
            'destination': destination,
            'evidence': unique_evidence,
            'metadata': {
                'consolidation_timestamp': datetime.now().isoformat(),
                'total_evidence_pieces': len(unique_evidence),
                'consolidated_from_sessions': len(session_data)
            }
        }
    
    def _deduplicate_evidence(self, evidence: List[Dict]) -> List[Dict]:
        """Remove duplicate evidence based on URL and content similarity"""
        unique_evidence = []
        seen_urls = set()
        
        for item in evidence:
            url = item.get('url', '').strip()
            if url and url not in seen_urls:
                unique_evidence.append(item)
                seen_urls.add(url)
        
        return unique_evidence
    
    async def _load_image_data(self, images_dir: Path) -> Dict[str, str]:
        """Load image paths from images directory"""
        image_data = {}
        
        if not images_dir.exists():
            return image_data
        
        # Look for seasonal images
        seasons = ['spring', 'summer', 'autumn', 'winter']
        for season in seasons:
            for ext in ['jpg', 'jpeg', 'png']:
                image_file = images_dir / f"{season}.{ext}"
                if image_file.exists():
                    image_data[season] = str(image_file)
                    break
        
        # Look for collage
        for ext in ['jpg', 'jpeg', 'png']:
            collage_file = images_dir / f"seasonal_collage.{ext}"
            if collage_file.exists():
                image_data['collage'] = str(collage_file)
                break
        
        return image_data
    
    async def _validate_consolidated_data(self, consolidated: ConsolidatedData):
        """Validate the consolidated data structure"""
        
        # Check minimum quality requirements
        min_quality = self.consolidation_config.get('min_quality_for_preservation', 0.6)
        
        themes_quality = consolidated.metadata.get('quality_scores', {}).get('themes', 0.0)
        nuances_quality = consolidated.metadata.get('quality_scores', {}).get('nuances', 0.0)
        
        if themes_quality > 0 and themes_quality < min_quality:
            logger.warning(f"Consolidated themes quality ({themes_quality:.3f}) below threshold ({min_quality})")
        
        if nuances_quality > 0 and nuances_quality < min_quality:
            logger.warning(f"Consolidated nuances quality ({nuances_quality:.3f}) below threshold ({min_quality})")
        
        # Validate data structure completeness
        if not consolidated.themes and not consolidated.nuances:
            logger.warning(f"Consolidated data for {consolidated.destination} has no themes or nuances")
        
        logger.debug(f"Consolidated data validation complete for {consolidated.destination}")
    
    async def get_consolidation_statistics(self, destination: str) -> Dict[str, Any]:
        """Get statistics about available session data for a destination"""
        
        sessions = await self._discover_sessions_for_destination(destination)
        
        stats = {
            'destination': destination,
            'total_sessions': len(sessions),
            'data_type_availability': {
                'themes': sum(1 for s in sessions if 'themes' in s.data_types),
                'nuances': sum(1 for s in sessions if 'nuances' in s.data_types),
                'images': sum(1 for s in sessions if 'images' in s.data_types)
            },
            'date_range': {
                'oldest': min(s.creation_date for s in sessions) if sessions else None,
                'newest': max(s.creation_date for s in sessions) if sessions else None
            },
            'quality_ranges': {}
        }
        
        # Calculate quality ranges
        for data_type in ['themes', 'nuances']:
            qualities = [s.quality_scores.get(data_type, 0.0) for s in sessions if data_type in s.data_types]
            if qualities:
                stats['quality_ranges'][data_type] = {
                    'min': min(qualities),
                    'max': max(qualities),
                    'avg': sum(qualities) / len(qualities)
                }
        
        return stats
