"""
Evidence Fusion Manager

Intelligently merges web-discovered evidence with citation evidence to create
enhanced, comprehensive evidence for destination themes.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

@dataclass
class FusedEvidence:
    """Evidence piece combining discovered and citation sources"""
    text_content: str
    source_url: str
    source_title: str
    authority_score: float
    quality_rating: str
    source_type: str
    evidence_source: str  # 'discovered', 'cited', or 'fused'
    confidence_score: float
    relevance_score: float
    fusion_metadata: Dict[str, Any]

@dataclass
class EvidenceFusionResult:
    """Result of evidence fusion operation"""
    theme_name: str
    fused_evidence: List[FusedEvidence]
    original_discovered_count: int
    original_cited_count: int
    final_evidence_count: int
    deduplication_count: int
    fusion_strategy: str
    fusion_time: float
    quality_improvement: float

class EvidenceFusionManager:
    """
    Intelligent evidence fusion manager that combines web-discovered evidence
    with LLM-cited evidence using quality-driven strategies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Extract configuration
        fusion_config = config.get('llm_citation_enhancement', {}).get('evidence_fusion', {})
        
        # Fusion strategy
        self.strategy = fusion_config.get('strategy', 'intelligent_merge')
        
        # Quality weighting
        self.discovered_weight = fusion_config.get('discovered_evidence_weight', 0.6)
        self.cited_weight = fusion_config.get('cited_evidence_weight', 0.4)
        
        # Deduplication settings
        self.enable_deduplication = fusion_config.get('enable_deduplication', True)
        self.similarity_threshold = fusion_config.get('similarity_threshold', 0.85)
        
        # Evidence limits
        self.max_evidence_per_theme = fusion_config.get('max_evidence_per_theme', 10)
        self.max_cited_evidence_ratio = fusion_config.get('max_cited_evidence_ratio', 0.3)
        
        # Quality thresholds
        self.min_fused_quality_score = fusion_config.get('min_fused_quality_score', 0.4)
        self.require_source_diversity = fusion_config.get('require_source_diversity', True)
        self.min_source_types = fusion_config.get('min_source_types', 2)
        
        # Authority boosting
        self.authority_boosts = {
            'government': fusion_config.get('boost_government_sources', 1.2),
            'academic': fusion_config.get('boost_academic_sources', 1.1),
            'tourism': fusion_config.get('boost_official_tourism', 1.3)
        }
        
        # Conflict resolution
        self.handle_contradictions = fusion_config.get('handle_contradictions', True)
        self.contradiction_resolution = fusion_config.get('contradiction_resolution', 'authority_based')
        
        # Performance metrics
        self.metrics = {
            'total_fusions': 0,
            'successful_fusions': 0,
            'evidence_deduplicated': 0,
            'average_fusion_time': 0.0,
            'average_quality_improvement': 0.0,
            'source_diversity_improvements': 0
        }
        
        logger.info(f"Evidence Fusion Manager initialized with {self.strategy} strategy")
    
    async def fuse_evidence_for_theme(self, theme_name: str, 
                                     discovered_evidence: List[Dict[str, Any]], 
                                     citation_evidence: List[Dict[str, Any]]) -> EvidenceFusionResult:
        """Fuse discovered and citation evidence for a specific theme"""
        start_time = time.time()
        
        logger.debug(f"Fusing evidence for theme '{theme_name}': {len(discovered_evidence)} discovered + {len(citation_evidence)} cited")
        
        try:
            # Convert to standardized format
            standardized_discovered = self._standardize_discovered_evidence(discovered_evidence)
            standardized_cited = self._standardize_citation_evidence(citation_evidence)
            
            # Apply authority boosting
            boosted_discovered = self._apply_authority_boosting(standardized_discovered)
            boosted_cited = self._apply_authority_boosting(standardized_cited)
            
            # Perform fusion based on strategy
            if self.strategy == 'intelligent_merge':
                fused_evidence = await self._intelligent_merge_evidence(
                    boosted_discovered, boosted_cited, theme_name
                )
            elif self.strategy == 'prioritize_discovered':
                fused_evidence = await self._prioritize_discovered_evidence(
                    boosted_discovered, boosted_cited, theme_name
                )
            elif self.strategy == 'prioritize_cited':
                fused_evidence = await self._prioritize_cited_evidence(
                    boosted_discovered, boosted_cited, theme_name
                )
            else:
                # Default to intelligent merge
                fused_evidence = await self._intelligent_merge_evidence(
                    boosted_discovered, boosted_cited, theme_name
                )
            
            # Apply deduplication if enabled
            if self.enable_deduplication:
                fused_evidence, dedup_count = self._deduplicate_evidence(fused_evidence)
            else:
                dedup_count = 0
            
            # Apply quality filters and limits
            final_evidence = self._apply_quality_filters_and_limits(fused_evidence)
            
            # Calculate quality improvement
            quality_improvement = self._calculate_quality_improvement(
                standardized_discovered + standardized_cited, final_evidence
            )
            
            fusion_time = time.time() - start_time
            
            result = EvidenceFusionResult(
                theme_name=theme_name,
                fused_evidence=final_evidence,
                original_discovered_count=len(discovered_evidence),
                original_cited_count=len(citation_evidence),
                final_evidence_count=len(final_evidence),
                deduplication_count=dedup_count,
                fusion_strategy=self.strategy,
                fusion_time=fusion_time,
                quality_improvement=quality_improvement
            )
            
            # Update metrics
            self._update_metrics(result)
            
            logger.info(f"Evidence fusion complete for '{theme_name}': {len(final_evidence)} final evidence pieces")
            return result
            
        except Exception as e:
            logger.error(f"Evidence fusion failed for theme '{theme_name}': {e}")
            return EvidenceFusionResult(
                theme_name=theme_name,
                fused_evidence=[],
                original_discovered_count=len(discovered_evidence),
                original_cited_count=len(citation_evidence),
                final_evidence_count=0,
                deduplication_count=0,
                fusion_strategy=self.strategy,
                fusion_time=time.time() - start_time,
                quality_improvement=0.0
            )
    
    def _standardize_discovered_evidence(self, evidence_list: List[Dict[str, Any]]) -> List[FusedEvidence]:
        """Convert discovered evidence to standardized format"""
        standardized = []
        
        for evidence in evidence_list:
            try:
                fused_evidence = FusedEvidence(
                    text_content=evidence.get('text_content', ''),
                    source_url=evidence.get('source_url', ''),
                    source_title=evidence.get('source_title', ''),
                    authority_score=evidence.get('authority_score', 0.5),
                    quality_rating=evidence.get('quality_rating', 'medium'),
                    source_type=evidence.get('source_type', 'web'),
                    evidence_source='discovered',
                    confidence_score=evidence.get('confidence_score', 0.5),
                    relevance_score=evidence.get('relevance_score', 0.5),
                    fusion_metadata={
                        'original_format': 'discovered',
                        'processing_method': 'web_discovery'
                    }
                )
                standardized.append(fused_evidence)
            except Exception as e:
                logger.warning(f"Failed to standardize discovered evidence: {e}")
        
        return standardized
    
    def _standardize_citation_evidence(self, citation_contents: List[Dict[str, Any]]) -> List[FusedEvidence]:
        """Convert citation evidence to standardized format"""
        standardized = []
        
        for content in citation_contents:
            try:
                # Convert CitationContent to FusedEvidence format
                fused_evidence = FusedEvidence(
                    text_content=content.get('content', '')[:1000],  # Limit length
                    source_url=content.get('url', ''),
                    source_title=content.get('title', ''),
                    authority_score=content.get('authority_score', 0.5),
                    quality_rating=self._quality_score_to_rating(content.get('quality_score', 0.5)),
                    source_type='citation',
                    evidence_source='cited',
                    confidence_score=content.get('quality_score', 0.5),
                    relevance_score=content.get('relevance_score', 0.5),
                    fusion_metadata={
                        'original_format': 'citation',
                        'extraction_method': content.get('extraction_method', 'unknown'),
                        'extraction_time': content.get('extraction_time', 0.0)
                    }
                )
                standardized.append(fused_evidence)
            except Exception as e:
                logger.warning(f"Failed to standardize citation evidence: {e}")
        
        return standardized
    
    def _quality_score_to_rating(self, score: float) -> str:
        """Convert numeric quality score to rating"""
        if score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium'
        elif score >= 0.4:
            return 'low'
        else:
            return 'very_low'
    
    def _apply_authority_boosting(self, evidence_list: List[FusedEvidence]) -> List[FusedEvidence]:
        """Apply authority score boosting based on source characteristics"""
        boosted_evidence = []
        
        for evidence in evidence_list:
            boosted = evidence
            url_lower = evidence.source_url.lower()
            
            # Apply authority boosts
            if any(domain in url_lower for domain in ['.gov', '.edu']):
                if '.gov' in url_lower:
                    boosted.authority_score *= self.authority_boosts['government']
                elif '.edu' in url_lower:
                    boosted.authority_score *= self.authority_boosts['academic']
            
            # Tourism authority boost
            tourism_indicators = ['tourism', 'travel', 'visitor', 'official']
            if any(indicator in url_lower for indicator in tourism_indicators):
                boosted.authority_score *= self.authority_boosts['tourism']
            
            # Ensure score doesn't exceed 1.0
            boosted.authority_score = min(1.0, boosted.authority_score)
            
            boosted_evidence.append(boosted)
        
        return boosted_evidence
    
    async def _intelligent_merge_evidence(self, discovered: List[FusedEvidence], 
                                        cited: List[FusedEvidence], 
                                        theme_name: str) -> List[FusedEvidence]:
        """Intelligently merge discovered and cited evidence"""
        
        # Combine all evidence
        all_evidence = discovered + cited
        
        # Score each piece of evidence
        scored_evidence = []
        for evidence in all_evidence:
            composite_score = self._calculate_composite_score(evidence)
            evidence.fusion_metadata['composite_score'] = composite_score
            scored_evidence.append(evidence)
        
        # Sort by composite score (highest first)
        scored_evidence.sort(key=lambda x: x.fusion_metadata['composite_score'], reverse=True)
        
        # Apply citation ratio limit
        max_cited = int(len(scored_evidence) * self.max_cited_evidence_ratio)
        cited_count = 0
        
        filtered_evidence = []
        for evidence in scored_evidence:
            if evidence.evidence_source == 'cited':
                if cited_count < max_cited:
                    filtered_evidence.append(evidence)
                    cited_count += 1
            else:
                filtered_evidence.append(evidence)
        
        return filtered_evidence
    
    async def _prioritize_discovered_evidence(self, discovered: List[FusedEvidence], 
                                            cited: List[FusedEvidence], 
                                            theme_name: str) -> List[FusedEvidence]:
        """Prioritize discovered evidence over cited evidence"""
        
        # Score all evidence but weight discovered evidence higher
        all_evidence = []
        
        for evidence in discovered:
            evidence.fusion_metadata['composite_score'] = self._calculate_composite_score(evidence) * 1.2
            all_evidence.append(evidence)
        
        for evidence in cited:
            evidence.fusion_metadata['composite_score'] = self._calculate_composite_score(evidence) * 0.8
            all_evidence.append(evidence)
        
        # Sort by score
        all_evidence.sort(key=lambda x: x.fusion_metadata['composite_score'], reverse=True)
        
        return all_evidence
    
    async def _prioritize_cited_evidence(self, discovered: List[FusedEvidence], 
                                       cited: List[FusedEvidence], 
                                       theme_name: str) -> List[FusedEvidence]:
        """Prioritize cited evidence over discovered evidence"""
        
        # Score all evidence but weight cited evidence higher
        all_evidence = []
        
        for evidence in discovered:
            evidence.fusion_metadata['composite_score'] = self._calculate_composite_score(evidence) * 0.8
            all_evidence.append(evidence)
        
        for evidence in cited:
            evidence.fusion_metadata['composite_score'] = self._calculate_composite_score(evidence) * 1.2
            all_evidence.append(evidence)
        
        # Sort by score
        all_evidence.sort(key=lambda x: x.fusion_metadata['composite_score'], reverse=True)
        
        return all_evidence
    
    def _calculate_composite_score(self, evidence: FusedEvidence) -> float:
        """Calculate composite score for evidence ranking"""
        
        # Base factors
        authority_factor = evidence.authority_score * 0.3
        confidence_factor = evidence.confidence_score * 0.2
        relevance_factor = evidence.relevance_score * 0.2
        
        # Quality factor
        quality_map = {'high': 1.0, 'medium': 0.7, 'low': 0.4, 'very_low': 0.2}
        quality_factor = quality_map.get(evidence.quality_rating, 0.5) * 0.2
        
        # Source type factor
        source_weight = self.discovered_weight if evidence.evidence_source == 'discovered' else self.cited_weight
        
        # Length factor (prefer substantial content)
        length_factor = min(1.0, len(evidence.text_content) / 500) * 0.1
        
        composite = (authority_factor + confidence_factor + relevance_factor + 
                    quality_factor + length_factor) * source_weight
        
        return min(1.0, composite)
    
    def _deduplicate_evidence(self, evidence_list: List[FusedEvidence]) -> Tuple[List[FusedEvidence], int]:
        """Remove duplicate evidence using similarity analysis"""
        
        if not evidence_list:
            return [], 0
        
        unique_evidence = []
        dedup_count = 0
        
        for evidence in evidence_list:
            is_duplicate = False
            
            for existing in unique_evidence:
                # Check URL similarity
                if evidence.source_url == existing.source_url:
                    is_duplicate = True
                    break
                
                # Check content similarity
                similarity = SequenceMatcher(None, 
                    evidence.text_content.lower(), 
                    existing.text_content.lower()
                ).ratio()
                
                if similarity > self.similarity_threshold:
                    # Keep the higher-scored evidence
                    existing_score = existing.fusion_metadata.get('composite_score', 0)
                    current_score = evidence.fusion_metadata.get('composite_score', 0)
                    
                    if current_score > existing_score:
                        # Replace existing with current
                        unique_evidence.remove(existing)
                        unique_evidence.append(evidence)
                    
                    is_duplicate = True
                    dedup_count += 1
                    break
            
            if not is_duplicate:
                unique_evidence.append(evidence)
        
        return unique_evidence, dedup_count
    
    def _apply_quality_filters_and_limits(self, evidence_list: List[FusedEvidence]) -> List[FusedEvidence]:
        """Apply quality filters and evidence count limits"""
        
        # Filter by minimum quality score
        quality_filtered = [
            evidence for evidence in evidence_list
            if evidence.fusion_metadata.get('composite_score', 0) >= self.min_fused_quality_score
        ]
        
        # Ensure source diversity if required
        if self.require_source_diversity:
            quality_filtered = self._ensure_source_diversity(quality_filtered)
        
        # Apply evidence count limit
        limited_evidence = quality_filtered[:self.max_evidence_per_theme]
        
        return limited_evidence
    
    def _ensure_source_diversity(self, evidence_list: List[FusedEvidence]) -> List[FusedEvidence]:
        """Ensure minimum source type diversity"""
        
        # Count source types
        source_types = set(evidence.source_type for evidence in evidence_list)
        
        if len(source_types) >= self.min_source_types:
            return evidence_list
        
        # Try to maintain diversity while keeping high-quality evidence
        diverse_evidence = []
        used_types = set()
        
        # First pass: ensure we have minimum source types
        for evidence in evidence_list:
            if len(used_types) < self.min_source_types:
                if evidence.source_type not in used_types:
                    diverse_evidence.append(evidence)
                    used_types.add(evidence.source_type)
        
        # Second pass: add remaining high-quality evidence
        for evidence in evidence_list:
            if evidence not in diverse_evidence:
                diverse_evidence.append(evidence)
        
        return diverse_evidence
    
    def _calculate_quality_improvement(self, original_evidence: List[FusedEvidence], 
                                     fused_evidence: List[FusedEvidence]) -> float:
        """Calculate quality improvement from fusion process"""
        
        if not original_evidence:
            return 0.0
        
        # Calculate average quality before fusion
        original_scores = [
            evidence.fusion_metadata.get('composite_score', evidence.authority_score)
            for evidence in original_evidence
        ]
        original_avg = sum(original_scores) / len(original_scores) if original_scores else 0
        
        # Calculate average quality after fusion
        fused_scores = [
            evidence.fusion_metadata.get('composite_score', evidence.authority_score)
            for evidence in fused_evidence
        ]
        fused_avg = sum(fused_scores) / len(fused_scores) if fused_scores else 0
        
        # Return improvement ratio
        if original_avg > 0:
            return (fused_avg - original_avg) / original_avg
        else:
            return 0.0
    
    def _update_metrics(self, result: EvidenceFusionResult):
        """Update fusion performance metrics"""
        self.metrics['total_fusions'] += 1
        
        if result.final_evidence_count > 0:
            self.metrics['successful_fusions'] += 1
        
        self.metrics['evidence_deduplicated'] += result.deduplication_count
        
        # Update running averages
        total = self.metrics['total_fusions']
        
        current_avg_time = self.metrics['average_fusion_time']
        self.metrics['average_fusion_time'] = (
            (current_avg_time * (total - 1) + result.fusion_time) / total
        )
        
        current_avg_quality = self.metrics['average_quality_improvement']
        self.metrics['average_quality_improvement'] = (
            (current_avg_quality * (total - 1) + result.quality_improvement) / total
        )
        
        # Track source diversity improvements
        if result.final_evidence_count > result.original_discovered_count:
            self.metrics['source_diversity_improvements'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get fusion performance metrics"""
        metrics = self.metrics.copy()
        
        # Calculate derived metrics
        if metrics['total_fusions'] > 0:
            metrics['success_rate'] = metrics['successful_fusions'] / metrics['total_fusions']
            metrics['average_deduplication_per_fusion'] = metrics['evidence_deduplicated'] / metrics['total_fusions']
        else:
            metrics['success_rate'] = 0.0
            metrics['average_deduplication_per_fusion'] = 0.0
        
        return metrics
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.debug("Evidence Fusion Manager cleanup complete")
