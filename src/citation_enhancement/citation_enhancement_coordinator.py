"""
Citation Enhancement Coordinator

Orchestrates the complete citation enhancement pipeline:
1. Extract citations from LLM responses
2. Validate citation URLs
3. Mine content from valid citations
4. Fuse citation evidence with discovered evidence

Provides a simple interface for integration with the agent system.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .citation_extractor import CitationExtractor, CitationExtractionResult
from .url_validator import URLValidator
from .citation_content_miner import CitationContentMiner
from .evidence_fusion_manager import EvidenceFusionManager

logger = logging.getLogger(__name__)

@dataclass
class CitationEnhancementResult:
    """Complete result of citation enhancement process"""
    theme_name: str
    enhanced_evidence: List[Dict[str, Any]]
    citation_statistics: Dict[str, Any]
    processing_time: float
    enhancement_success: bool
    error_messages: List[str]

@dataclass
class CitationPipelineMetrics:
    """Comprehensive metrics for the citation enhancement pipeline"""
    total_citations_extracted: int
    valid_citations: int
    successful_content_extractions: int
    evidence_pieces_added: int
    deduplication_count: int
    total_processing_time: float
    success_rate: float

class CitationEnhancementCoordinator:
    """
    Coordinates the complete citation enhancement pipeline with error handling,
    fallback mechanisms, and performance monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Extract feature flags
        citation_config = config.get('llm_citation_enhancement', {})
        feature_flags = citation_config.get('feature_flags', {})
        
        self.enabled = citation_config.get('enabled', True)
        self.enable_extraction = feature_flags.get('enable_citation_extraction', True)
        self.enable_validation = feature_flags.get('enable_url_validation', True)
        self.enable_content_mining = feature_flags.get('enable_content_mining', True)
        self.enable_fusion = feature_flags.get('enable_evidence_fusion', True)
        self.fallback_enabled = feature_flags.get('enable_fallback_to_discovered_only', True)
        
        # Performance monitoring
        monitoring_config = citation_config.get('monitoring', {})
        self.enable_metrics = monitoring_config.get('enable_detailed_metrics', True)
        self.log_failures = monitoring_config.get('log_failed_citations', True)
        
        # Initialize components if enabled
        self.citation_extractor = None
        self.url_validator = None
        self.content_miner = None
        self.fusion_manager = None
        
        if self.enabled:
            try:
                if self.enable_extraction:
                    self.citation_extractor = CitationExtractor(config)
                
                if self.enable_validation:
                    self.url_validator = URLValidator(config)
                
                if self.enable_content_mining:
                    self.content_miner = CitationContentMiner(config)
                
                if self.enable_fusion:
                    self.fusion_manager = EvidenceFusionManager(config)
                
                logger.info("Citation Enhancement Coordinator initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize Citation Enhancement Coordinator: {e}")
                self.enabled = False
        
        # Performance metrics
        self.metrics = {
            'total_enhancements': 0,
            'successful_enhancements': 0,
            'fallback_activations': 0,
            'average_processing_time': 0.0,
            'total_citations_processed': 0,
            'total_evidence_enhanced': 0
        }
    
    async def enhance_theme_evidence(self, theme_text: str, theme_name: str, 
                                    discovered_evidence: List[Dict] = None,
                                    structured_citations: List[str] = None) -> CitationEnhancementResult:
        """
        Enhanced theme evidence processing with support for structured citations
        
        Args:
            theme_text: Theme description text for text-based extraction
            theme_name: Name of the theme
            discovered_evidence: Existing web-discovered evidence
            structured_citations: Pre-parsed URLs from structured theme data
        """
        
        if not self.enabled:
            return self._create_fallback_result(theme_name, discovered_evidence, 0.0)
        
        start_time = time.time()
        errors = []
        
        try:
            logger.info(f"Starting citation enhancement for theme '{theme_name}'")
            
            # Phase 1: Citation Extraction (Enhanced)
            citation_result = await self._extract_citations_enhanced(
                theme_text, theme_name, structured_citations
            )
            
            if not citation_result.citations:
                logger.info(f"No citations found for '{theme_name}', using discovered evidence only")
                return self._create_fallback_result(theme_name, discovered_evidence, start_time)
            
            # Phase 2: URL Validation
            validated_urls = []
            if self.url_validator:
                try:
                    validation_results = await self.url_validator.validate_urls_batch(
                        [c.url for c in citation_result.citations]
                    )
                    validated_urls = [result.url for result in validation_results.results if result.is_valid]
                    logger.info(f"URL validation: {len(validated_urls)}/{len(citation_result.citations)} URLs validated")
                except Exception as e:
                    logger.error(f"URL validation failed for '{theme_name}': {e}")
                    errors.append(f"URL validation error: {str(e)}")
                    validated_urls = [c.url for c in citation_result.citations]  # Fallback to unvalidated
            else:
                validated_urls = [c.url for c in citation_result.citations]
            
            # Phase 3: Content Mining
            mined_content = None
            if validated_urls and self.content_miner:
                try:
                    mined_content = await self.content_miner.mine_citation_content(
                        validated_urls, context_theme=theme_name
                    )
                    logger.info(f"Content mining: {len(mined_content.citation_contents)} pieces extracted")
                except Exception as e:
                    logger.error(f"Content mining failed for '{theme_name}': {e}")
                    errors.append(f"Content mining error: {str(e)}")
            
            # Phase 4: Evidence Fusion
            fused_evidence = []
            if self.fusion_manager:
                try:
                    # Convert mined content to evidence format
                    citation_evidence = self._convert_mined_content_to_evidence(
                        mined_content, citation_result.citations
                    )
                    
                    # Fuse with discovered evidence
                    fusion_result = await self.fusion_manager.fuse_evidence_streams(
                        discovered_evidence or [],
                        citation_evidence,
                        theme_context=theme_name
                    )
                    fused_evidence = fusion_result.fused_evidence
                    logger.info(f"Evidence fusion: {len(fused_evidence)} final evidence pieces")
                except Exception as e:
                    logger.error(f"Evidence fusion failed for '{theme_name}': {e}")
                    errors.append(f"Evidence fusion error: {str(e)}")
                    fused_evidence = discovered_evidence or []
            else:
                fused_evidence = discovered_evidence or []
            
            # Calculate metrics
            processing_time = time.time() - start_time
            
            success_metrics = {
                'citations_extracted': len(citation_result.citations),
                'urls_validated': len(validated_urls),
                'content_pieces_mined': len(mined_content.citation_contents) if mined_content else 0,
                'final_evidence_count': len(fused_evidence),
                'processing_time': processing_time,
                'extraction_method': citation_result.extraction_method,
                'structured_citations_used': len(structured_citations) if structured_citations else 0
            }
            
            return CitationEnhancementResult(
                theme_name=theme_name,
                enhanced_evidence=fused_evidence,
                citation_statistics=success_metrics,
                processing_time=processing_time,
                enhancement_success=True,
                error_messages=errors
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Citation enhancement failed for '{theme_name}': {e}")
            
            # Return fallback result
            return CitationEnhancementResult(
                theme_name=theme_name,
                enhanced_evidence=discovered_evidence or [],
                citation_statistics={
                    'processing_time': processing_time,
                    'failure_reason': str(e)
                },
                processing_time=processing_time,
                enhancement_success=False,
                error_messages=[str(e)] + errors
            )
    
    async def _extract_citations_enhanced(self, theme_text: str, theme_name: str, 
                                        structured_citations: List[str] = None) -> CitationExtractionResult:
        """Enhanced citation extraction with support for structured citations"""
        
        if not self.citation_extractor:
            logger.warning("Citation extractor not available")
            return CitationExtractionResult(
                citations=[],
                total_urls_found=0,
                valid_urls_count=0,
                extraction_time=0.0,
                source_response_id=theme_name,
                extraction_method="no_extractor",
                errors=["Citation extractor not initialized"]
            )
        
        # If we have structured citations, use them preferentially
        if structured_citations and len(structured_citations) > 0:
            logger.info(f"Processing {len(structured_citations)} structured citations for '{theme_name}'")
            
            # Create a theme object for structured extraction
            theme_data = [{
                'theme': theme_name,
                'description': theme_text,
                'citations': structured_citations
            }]
            
            return await self.citation_extractor.extract_citations_from_structured_themes(
                theme_data, context_id=theme_name
            )
        else:
            # Fallback to text-based extraction
            logger.info(f"No structured citations, using text extraction for '{theme_name}'")
            return await self.citation_extractor.extract_citations_from_response(
                theme_text, response_id=theme_name
            )
    
    def _convert_mined_content_to_evidence(self, mined_content, citations) -> List[Dict[str, Any]]:
        """Convert mined citation content to standard evidence format"""
        
        if not mined_content or not mined_content.citation_contents:
            return []
        
        citation_evidence = []
        
        for citation_content in mined_content.citation_contents:
            evidence_item = {
                'text_content': citation_content.content,
                'source_url': citation_content.url,
                'source_title': citation_content.title,
                'authority_score': citation_content.authority_score,
                'quality_rating': self._map_quality_score_to_rating(citation_content.quality_score),
                'source_type': 'citation_mined',
                'confidence_score': citation_content.relevance_score,
                'relevance_score': citation_content.relevance_score,
                'evidence_source': 'cited',
                'extraction_method': citation_content.extraction_method,
                'metadata': citation_content.metadata or {}
            }
            citation_evidence.append(evidence_item)
        
        return citation_evidence
    
    def _map_quality_score_to_rating(self, quality_score: float) -> str:
        """Map numerical quality score to rating string"""
        if quality_score >= 0.8:
            return "excellent"
        elif quality_score >= 0.6:
            return "good"
        elif quality_score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def _convert_fused_to_standard_format(self, fused_evidence: List) -> List[Dict[str, Any]]:
        """Convert fused evidence back to standard evidence format"""
        standard_evidence = []
        
        for evidence in fused_evidence:
            evidence_item = {
                'text_content': evidence.text_content,
                'source_url': evidence.source_url,
                'source_title': evidence.source_title,
                'authority_score': evidence.authority_score,
                'quality_rating': evidence.quality_rating,
                'source_type': evidence.source_type,
                'confidence_score': evidence.confidence_score,
                'relevance_score': evidence.relevance_score,
                'evidence_source': evidence.evidence_source,  # 'discovered', 'cited', or 'fused'
                'fusion_metadata': evidence.fusion_metadata
            }
            standard_evidence.append(evidence_item)
        
        return standard_evidence
    
    def _create_fallback_result(self, 
                              theme_name: str, 
                              discovered_evidence: List[Dict[str, Any]], 
                              start_time: float,
                              error_messages: List[str] = None) -> CitationEnhancementResult:
        """Create fallback result using only discovered evidence"""
        
        return CitationEnhancementResult(
            theme_name=theme_name,
            enhanced_evidence=discovered_evidence,
            citation_statistics={
                'citations_extracted': 0,
                'citations_validated': 0,
                'citations_mined': 0,
                'evidence_pieces_added': 0,
                'fallback_used': True
            },
            processing_time=time.time() - start_time,
            enhancement_success=bool(discovered_evidence),
            error_messages=error_messages or []
        )
    
    def _generate_statistics(self, fused_result, citation_evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive statistics for the enhancement process"""
        
        return {
            'citations_extracted': len(citation_evidence),
            'citations_validated': len([c for c in citation_evidence if c.get('authority_score', 0) > 0.5]),
            'citations_mined': len(citation_evidence),
            'evidence_pieces_added': fused_result.final_evidence_count - fused_result.original_discovered_count,
            'deduplication_count': fused_result.deduplication_count,
            'fusion_strategy': fused_result.fusion_strategy,
            'quality_improvement': fused_result.quality_improvement,
            'fusion_time': fused_result.fusion_time,
            'fallback_used': False
        }
    
    def _update_metrics(self, result: CitationEnhancementResult, fused_result):
        """Update coordinator performance metrics"""
        
        # Update running averages
        total = self.metrics['total_enhancements']
        
        current_avg_time = self.metrics['average_processing_time']
        self.metrics['average_processing_time'] = (
            (current_avg_time * (total - 1) + result.processing_time) / total
        )
        
        # Update citation and evidence counts
        stats = result.citation_statistics
        self.metrics['total_citations_processed'] += stats.get('citations_extracted', 0)
        self.metrics['total_evidence_enhanced'] += stats.get('evidence_pieces_added', 0)
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics from all components"""
        
        metrics = {
            'coordinator_metrics': self.metrics.copy(),
            'components_enabled': {
                'citation_extraction': self.enable_extraction,
                'url_validation': self.enable_validation,
                'content_mining': self.enable_content_mining,
                'evidence_fusion': self.enable_fusion
            }
        }
        
        # Add component-specific metrics if available
        if self.citation_extractor:
            metrics['extraction_metrics'] = self.citation_extractor.get_metrics()
        
        if self.url_validator:
            metrics['validation_metrics'] = self.url_validator.get_metrics()
        
        if self.content_miner:
            metrics['mining_metrics'] = self.content_miner.get_metrics()
        
        if self.fusion_manager:
            metrics['fusion_metrics'] = self.fusion_manager.get_metrics()
        
        # Calculate derived coordinator metrics
        if metrics['coordinator_metrics']['total_enhancements'] > 0:
            total = metrics['coordinator_metrics']['total_enhancements']
            metrics['coordinator_metrics']['success_rate'] = (
                metrics['coordinator_metrics']['successful_enhancements'] / total
            )
            metrics['coordinator_metrics']['fallback_rate'] = (
                metrics['coordinator_metrics']['fallback_activations'] / total
            )
        
        return metrics
    
    async def cleanup(self):
        """Cleanup all components"""
        try:
            cleanup_tasks = []
            
            if self.citation_extractor:
                cleanup_tasks.append(self.citation_extractor.cleanup())
            
            if self.url_validator:
                cleanup_tasks.append(self.url_validator.cleanup())
            
            if self.content_miner:
                cleanup_tasks.append(self.content_miner.cleanup())
            
            if self.fusion_manager:
                cleanup_tasks.append(self.fusion_manager.cleanup())
            
            if cleanup_tasks:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
            
            logger.debug("Citation Enhancement Coordinator cleanup complete")
            
        except Exception as e:
            logger.warning(f"Citation Enhancement Coordinator cleanup warning: {e}") 