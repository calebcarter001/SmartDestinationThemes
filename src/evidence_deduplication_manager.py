import os
import json
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class EvidenceDeduplicationManager:
    """Manages evidence deduplication across sessions and destinations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        evidence_config = config.get('destination_nuances', {}).get('evidence_quality', {})
        
        self.enable_deduplication = evidence_config.get('enable_evidence_deduplication', True)
        self.similarity_threshold = evidence_config.get('evidence_similarity_threshold', 0.85)
        
        # Evidence registry file
        self.registry_file = Path("cache") / "evidence_registry.json"
        self.registry_file.parent.mkdir(exist_ok=True)
        
        # Load existing registry
        self.evidence_registry = self._load_evidence_registry()
    
    def _load_evidence_registry(self) -> Dict[str, Any]:
        """Load the evidence registry from cache"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load evidence registry: {e}")
        
        return {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'evidence_by_phrase': {},
            'evidence_by_url': {},
            'last_updated': datetime.now().isoformat()
        }
    
    def register_evidence_batch(self, destination: str, evidence_list: List[Any]):
        """Register a batch of evidence for deduplication"""
        if not self.enable_deduplication:
            return evidence_list
        
        # For now, just pass through evidence without deduplication
        # but ensure we don't break the evidence collection process
        logger.debug(f"Processing {len(evidence_list)} evidence items for {destination}")
        return evidence_list
 