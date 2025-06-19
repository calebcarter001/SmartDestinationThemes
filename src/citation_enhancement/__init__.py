"""
LLM Citation Enhancement Package

Provides citation-based evidence discovery and fusion capabilities
for the Destination Insights Discovery system.
"""

from .citation_extractor import CitationExtractor, ExtractedCitation, CitationExtractionResult
from .url_validator import URLValidator, URLValidationResult, ValidationStatus
from .citation_content_miner import CitationContentMiner, CitationContent, ContentMiningResult
from .evidence_fusion_manager import EvidenceFusionManager, FusedEvidence, EvidenceFusionResult
from .citation_enhancement_coordinator import CitationEnhancementCoordinator, CitationEnhancementResult

__all__ = [
    'CitationExtractor',
    'ExtractedCitation',
    'CitationExtractionResult',
    'URLValidator',
    'URLValidationResult',
    'ValidationStatus',
    'CitationContentMiner',
    'CitationContent',
    'ContentMiningResult',
    'EvidenceFusionManager',
    'FusedEvidence',
    'EvidenceFusionResult',
    'CitationEnhancementCoordinator',
    'CitationEnhancementResult'
]
