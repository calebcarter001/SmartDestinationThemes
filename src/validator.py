import logging
import asyncio
import time
from typing import Dict, List
from sentence_transformers import SentenceTransformer, util
from tools.vectorize_processing_tool import ProcessContentWithVectorizeTool
from src.evidence_validator import EvidenceValidator
from src.evidence_schema import ValidationStatus

class AffinityValidator:
    """
    Handles the validation and reconciliation of affinities from different sources.
    Performs semantic clustering and comprehensive evidence-based validation against web content.
    """
    def __init__(self, config: dict, vectorizer: ProcessContentWithVectorizeTool):
        self.config = config
        self.vectorizer = vectorizer
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize comprehensive evidence validator
        self.evidence_validator = EvidenceValidator(config)
        self.logger = logging.getLogger("app.validator")

    async def validate_and_reconcile(self, llm_affinities: dict, web_signals: dict) -> dict:
        """
        Reconciles LLM-generated affinities with comprehensive evidence validation.
        """
        self.logger.info("Performing comprehensive validation and reconciliation...")
        
        if not llm_affinities.get("affinities"):
            self.logger.warning("No affinities from LLM to validate.")
            return llm_affinities

        # Get web pages for evidence validation
        web_pages = web_signals.get("pages", [])
        if not web_pages:
            self.logger.warning("No web pages found for evidence validation. Using basic validation.")
            return self._basic_validation(llm_affinities)

        destination_name = llm_affinities.get("destination_id", "Unknown")
        
        # --- Stage 1: Comprehensive Evidence Validation ---
        start_time = time.time()
        affinities = llm_affinities["affinities"]
        validated_affinities = []
        all_theme_evidence = []
        
        self.logger.info(f"Validating {len(affinities)} themes with comprehensive evidence analysis...")
        
        for affinity in affinities:
            theme = affinity.get("theme", "")
            category = affinity.get("category", "")
            
            # Validate theme with comprehensive evidence collection
            theme_evidence = self.evidence_validator.validate_theme_evidence(
                theme=theme,
                category=category,
                web_pages=web_pages,
                destination=destination_name
            )
            
            all_theme_evidence.append(theme_evidence)
            
            # Update affinity with evidence-based adjustments
            updated_affinity = self._apply_evidence_adjustments(affinity, theme_evidence)
            validated_affinities.append(updated_affinity)
            
            self.logger.debug(f"Theme '{theme}': {theme_evidence.validation_status.value}, "
                            f"Evidence: {theme_evidence.total_evidence_count} pieces, "
                            f"Confidence: {theme_evidence.validation_confidence:.3f}")
        
        # --- Stage 2: Generate Validation Report ---
        processing_time = time.time() - start_time
        validation_report = self.evidence_validator.generate_validation_report(
            destination=destination_name,
            themes_evidence=all_theme_evidence,
            processing_time=processing_time
        )
        
        # --- Stage 3: Semantic Clustering on Evidence-Adjusted Affinities ---
        final_affinities = self._semantic_clustering(validated_affinities)
        
        # --- Stage 4: Apply Evidence-Based Quality Gates ---
        quality_filtered_affinities = self._apply_evidence_quality_gates(final_affinities, all_theme_evidence)

        # Update result with comprehensive evidence data
        llm_affinities["affinities"] = quality_filtered_affinities
        llm_affinities["evidence_validation_report"] = validation_report.dict()
        llm_affinities["validation_metadata"] = {
            "total_themes_analyzed": len(affinities),
            "themes_with_evidence": validation_report.themes_validated,
            "validation_success_rate": validation_report.validation_success_rate,
            "total_evidence_pieces": validation_report.total_evidence_pieces,
            "unique_sources_used": validation_report.unique_sources_used,
            "processing_time_seconds": processing_time
        }
        
        self.logger.info(f"Evidence validation complete: {validation_report.themes_validated}/{len(affinities)} themes validated, "
                        f"{validation_report.total_evidence_pieces} evidence pieces from {validation_report.unique_sources_used} sources")
        
        return llm_affinities
    
    def _apply_evidence_adjustments(self, affinity: dict, theme_evidence) -> dict:
        """Apply evidence-based confidence and validation adjustments to affinity."""
        original_confidence = affinity.get('confidence', 0.5)
        
        # Calculate evidence-adjusted confidence
        evidence_boost = 0.0
        
        if theme_evidence.validation_status == ValidationStatus.VALIDATED:
            evidence_boost = 0.2  # Strong evidence boost
            validation_message = f"Validated with {theme_evidence.total_evidence_count} evidence pieces"
        elif theme_evidence.validation_status == ValidationStatus.PARTIALLY_VALIDATED:
            evidence_boost = 0.1  # Moderate evidence boost
            validation_message = f"Partially validated with {theme_evidence.total_evidence_count} evidence pieces"
        else:
            evidence_boost = -0.15  # Penalty for no evidence
            validation_message = "No supporting evidence found"
        
        # Apply authority score weighting
        if theme_evidence.average_authority_score > 0.7:
            evidence_boost += 0.05  # High authority sources bonus
        elif theme_evidence.average_authority_score < 0.4:
            evidence_boost -= 0.05  # Low authority sources penalty
        
        # Calculate final confidence
        adjusted_confidence = max(0.0, min(1.0, original_confidence + evidence_boost))
        
        # Update affinity with evidence data
        affinity.update({
            'confidence': adjusted_confidence,
            'original_confidence': original_confidence,
            'evidence_adjustment': evidence_boost,
            'validation': validation_message,
            'evidence_summary': {
                'validation_status': theme_evidence.validation_status.value,
                'evidence_count': theme_evidence.total_evidence_count,
                'unique_sources': theme_evidence.unique_source_count,
                'average_authority': theme_evidence.average_authority_score,
                'validation_confidence': theme_evidence.validation_confidence,
                'strongest_evidence_id': theme_evidence.strongest_evidence,
                'evidence_gaps': theme_evidence.evidence_gaps,
                'evidence_pieces': [
                    {
                        'text': piece.text_content,
                        'source_url': piece.source_url,
                        'source_title': piece.source_title,
                        'source_type': piece.source_type.value,
                        'authority_score': piece.authority_score,
                        'quality_rating': piece.quality_rating.value,
                        'relevance_score': piece.relevance_score,
                        'word_count': piece.word_count
                    }
                    for piece in theme_evidence.evidence_pieces[:5]  # Limit to top 5 for dashboard
                ]
            }
        })
        
        return affinity
    
    def _apply_evidence_quality_gates(self, affinities: List[Dict], theme_evidence_list: List) -> List[Dict]:
        """Apply quality gates based on evidence validation requirements."""
        filtered_affinities = []
        evidence_config = self.evidence_validator.validation_config
        
        for i, affinity in enumerate(affinities):
            theme_evidence = theme_evidence_list[i] if i < len(theme_evidence_list) else None
            
            if not theme_evidence:
                continue
            
            # Quality gate 1: Minimum evidence requirements
            if (theme_evidence.meets_min_evidence_requirement and 
                theme_evidence.meets_source_diversity_requirement and
                theme_evidence.meets_quality_threshold):
                filtered_affinities.append(affinity)
                continue
            
            # Quality gate 2: High confidence without evidence (exceptional themes)
            if (affinity.get('original_confidence', 0) >= 0.85 and
                theme_evidence.validation_status != ValidationStatus.UNVALIDATED):
                filtered_affinities.append(affinity)
                continue
            
            # Quality gate 3: Partial validation with decent confidence
            if (theme_evidence.validation_status == ValidationStatus.PARTIALLY_VALIDATED and
                affinity.get('confidence', 0) >= 0.6):
                filtered_affinities.append(affinity)
                continue
            
            self.logger.debug(f"Theme '{affinity.get('theme')}' filtered out: "
                            f"Evidence: {theme_evidence.total_evidence_count}, "
                            f"Confidence: {affinity.get('confidence', 0):.3f}")
        
        self.logger.info(f"Quality gates applied: {len(filtered_affinities)}/{len(affinities)} themes passed")
        return filtered_affinities
    
    def _basic_validation(self, llm_affinities: dict) -> dict:
        """Fallback to basic validation when no web content is available."""
        self.logger.info("Applying basic validation (no web content available)")
        
        affinities = llm_affinities["affinities"]
        for affinity in affinities:
            affinity['validation'] = "No web content available for evidence validation"
            affinity['evidence_summary'] = {
                'validation_status': 'pending',
                'evidence_count': 0,
                'unique_sources': 0,
                'validation_confidence': 0.0
            }
        
        # Apply semantic clustering
        final_affinities = self._semantic_clustering(affinities)
        llm_affinities["affinities"] = final_affinities
        
        return llm_affinities

    def _semantic_clustering(self, affinities: List[Dict]) -> List[Dict]:
        """
        Groups affinities based on the semantic similarity of their themes.
        Merges less confident affinities into more confident ones.
        """
        if len(affinities) < 2:
            return affinities

        themes = [affinity['theme'] for affinity in affinities]
        self.logger.info(f"Clustering themes: {themes}")

        embeddings = self.model.encode(themes, convert_to_tensor=True)
        similarity_matrix = util.pytorch_cos_sim(embeddings, embeddings)
        
        clusters = []
        visited = [False] * len(affinities)
        similarity_threshold = 0.8

        for i in range(len(affinities)):
            if visited[i]:
                continue
            
            current_cluster = [i]
            for j in range(i + 1, len(affinities)):
                if not visited[j] and similarity_matrix[i][j] > similarity_threshold:
                    visited[j] = True
                    current_cluster.append(j)
            
            clusters.append(current_cluster)
            visited[i] = True

        self.logger.info(f"Found {len(clusters)} semantic clusters.")

        merged_affinities = []
        for cluster in clusters:
            if not cluster: 
                continue
            
            # Select best affinity based on evidence-adjusted confidence
            best_affinity_in_cluster = max([affinities[i] for i in cluster], 
                                         key=lambda x: x.get('confidence', 0.0))
            merged_affinities.append(best_affinity_in_cluster)
            
            self.logger.info(f"From cluster with themes {[affinities[i]['theme'] for i in cluster]}, "
                           f"selected '{best_affinity_in_cluster['theme']}' "
                           f"(confidence: {best_affinity_in_cluster.get('confidence', 0):.3f})")

        return merged_affinities 