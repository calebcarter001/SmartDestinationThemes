import logging
import re
from typing import Dict, List, Optional
from collections import Counter
import statistics

class AffinityQualityScorer:
    """
    Sophisticated Evaluation Framework for scoring the quality of generated affinities
    based on multiple metrics including factual accuracy, thematic coverage, actionability,
    uniqueness, and source credibility.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = logging.getLogger("app.quality_scorer")
        
        # Quality thresholds and weights
        self.quality_thresholds = {
            'factual_accuracy': 0.7,
            'thematic_coverage': 0.6,
            'actionability': 0.8,
            'uniqueness': 0.5,
            'source_credibility': 0.6
        }
        
        # Metric weights for overall score
        self.metric_weights = {
            'factual_accuracy': 0.25,
            'thematic_coverage': 0.20,
            'actionability': 0.25,
            'uniqueness': 0.15,
            'source_credibility': 0.15
        }
        
        # Common travel categories for coverage analysis
        self.expected_categories = {
            'culture', 'adventure', 'nature', 'luxury', 'family', 'wellness'
        }
        
        # Actionability keywords
        self.actionable_indicators = {
            'high': ['visit', 'book', 'try', 'experience', 'explore', 'discover', 'enjoy'],
            'medium': ['see', 'view', 'learn', 'understand', 'appreciate'],
            'low': ['consider', 'think about', 'contemplate']
        }

    def score_affinity_set(self, affinities: dict, destination: str, web_signals: dict = None) -> dict:
        """
        Calculates a multi-metric quality score for a set of affinities.

        Args:
            affinities: The affinity data to be scored
            destination: The destination name
            web_signals: Optional web content for validation

        Returns:
            A dictionary of quality metrics and an overall weighted score
        """
        self.logger.info(f"Scoring affinities for {destination}")
        
        if not affinities or 'affinities' not in affinities:
            self.logger.warning(f"No affinities to score for {destination}")
            return self._empty_score()
        
        affinity_list = affinities['affinities']
        
        # Calculate individual metrics
        metrics = {
            'factual_accuracy': self._score_factual_accuracy(affinity_list, web_signals),
            'thematic_coverage': self._score_thematic_coverage(affinity_list),
            'actionability': self._score_actionability(affinity_list),
            'uniqueness': self._score_uniqueness(affinity_list, destination),
            'source_credibility': self._score_source_credibility(affinity_list)
        }
        
        # Calculate overall score
        overall_score = sum(
            metrics[metric] * self.metric_weights[metric]
            for metric in metrics
        )
        
        # Add quality assessment
        quality_assessment = self._assess_quality_level(overall_score, metrics)
        
        # Add recommendations for improvement
        recommendations = self._generate_recommendations(metrics)
        
        result = {
            "metrics": metrics,
            "overall_score": round(overall_score, 3),
            "quality_level": quality_assessment,
            "recommendations": recommendations,
            "meets_threshold": overall_score >= 0.7,
            "destination": destination,
            "total_affinities": len(affinity_list)
        }
        
        self.logger.info(f"Quality score for {destination}: {overall_score:.3f} ({quality_assessment})")
        return result
    
    def _score_factual_accuracy(self, affinities: List[Dict], web_signals: dict = None) -> float:
        """Score based on evidence validation and consistency."""
        if not affinities:
            return 0.0
        
        # If we have web signals, use evidence validation
        if web_signals and 'pages' in web_signals:
            evidence_scores = []
            for affinity in affinities:
                validation = affinity.get('validation', '')
                confidence = affinity.get('confidence', 0.5)
                
                if 'Evidence found' in validation:
                    evidence_scores.append(min(1.0, confidence + 0.2))  # Boost for evidence
                elif 'No evidence found' in validation:
                    evidence_scores.append(max(0.0, confidence - 0.1))  # Penalty for no evidence
                else:
                    evidence_scores.append(confidence)
            
            return statistics.mean(evidence_scores) if evidence_scores else 0.5
        
        # Fallback: use confidence scores as proxy for factual accuracy
        confidence_scores = [aff.get('confidence', 0.5) for aff in affinities]
        return statistics.mean(confidence_scores) if confidence_scores else 0.5
    
    def _score_thematic_coverage(self, affinities: List[Dict]) -> float:
        """Score based on diversity of categories and themes."""
        if not affinities:
            return 0.0
        
        # Check category diversity
        categories = [aff.get('category', '').lower() for aff in affinities]
        unique_categories = set(categories)
        category_coverage = len(unique_categories) / len(self.expected_categories)
        
        # Check theme uniqueness
        themes = [aff.get('theme', '').lower() for aff in affinities]
        unique_themes = len(set(themes))
        theme_diversity = unique_themes / len(themes) if themes else 0
        
        # Check traveler type coverage
        all_traveler_types = []
        for aff in affinities:
            all_traveler_types.extend(aff.get('traveler_types', []))
        unique_traveler_types = len(set(all_traveler_types))
        traveler_coverage = min(1.0, unique_traveler_types / 4)  # solo, couple, family, group
        
        # Weighted combination
        coverage_score = (
            category_coverage * 0.4 +
            theme_diversity * 0.4 +
            traveler_coverage * 0.2
        )
        
        return min(1.0, coverage_score)
    
    def _score_actionability(self, affinities: List[Dict]) -> float:
        """Score based on how actionable the recommendations are."""
        if not affinities:
            return 0.0
        
        actionability_scores = []
        
        for affinity in affinities:
            score = 0.0
            
            # Check theme actionability
            theme = affinity.get('theme', '').lower()
            rationale = affinity.get('rationale', '').lower()
            usps = ' '.join(affinity.get('unique_selling_points', [])).lower()
            
            text_to_analyze = f"{theme} {rationale} {usps}"
            
            # Score based on actionable language
            for level, keywords in self.actionable_indicators.items():
                matches = sum(1 for keyword in keywords if keyword in text_to_analyze)
                if level == 'high':
                    score += matches * 0.3
                elif level == 'medium':
                    score += matches * 0.2
                elif level == 'low':
                    score += matches * 0.1
            
            # Bonus for specific details
            if any(detail in text_to_analyze for detail in ['museum', 'restaurant', 'park', 'beach', 'trail']):
                score += 0.2
            
            # Bonus for seasonality information
            if affinity.get('seasonality', {}).get('peak'):
                score += 0.1
            
            # Bonus for price point information
            if affinity.get('price_point'):
                score += 0.1
                
            actionability_scores.append(min(1.0, score))
        
        return statistics.mean(actionability_scores) if actionability_scores else 0.0
    
    def _score_uniqueness(self, affinities: List[Dict], destination: str) -> float:
        """Score based on theme uniqueness and destination-specific insights."""
        if not affinities:
            return 0.0
        
        uniqueness_scores = []
        
        # Generic vs specific theme analysis
        generic_themes = {
            'shopping', 'dining', 'sightseeing', 'entertainment', 'relaxation'
        }
        
        for affinity in affinities:
            theme = affinity.get('theme', '').lower()
            sub_themes = [st.lower() for st in affinity.get('sub_themes', [])]
            usps = affinity.get('unique_selling_points', [])
            
            score = 0.5  # Base score
            
            # Penalty for generic themes
            if any(generic in theme for generic in generic_themes):
                score -= 0.2
            
            # Bonus for destination-specific elements
            destination_lower = destination.lower()
            if destination_lower in theme or any(destination_lower in st for st in sub_themes):
                score += 0.3
            
            # Bonus for specific, detailed USPs
            if len(usps) >= 2:
                score += 0.2
            
            # Bonus for unique sub-themes
            if len(sub_themes) >= 3:
                score += 0.1
                
            uniqueness_scores.append(max(0.0, min(1.0, score)))
        
        return statistics.mean(uniqueness_scores) if uniqueness_scores else 0.0
    
    def _score_source_credibility(self, affinities: List[Dict]) -> float:
        """Score based on confidence levels and validation status."""
        if not affinities:
            return 0.0
        
        credibility_scores = []
        
        for affinity in affinities:
            confidence = affinity.get('confidence', 0.5)
            validation = affinity.get('validation', '')
            
            # Base score from confidence
            score = confidence
            
            # Boost for evidence-backed themes
            if 'Evidence found' in validation:
                score = min(1.0, score + 0.15)
            
            # Penalty for unvalidated themes
            elif 'No evidence found' in validation:
                score = max(0.0, score - 0.1)
            
            credibility_scores.append(score)
        
        return statistics.mean(credibility_scores) if credibility_scores else 0.5
    
    def _assess_quality_level(self, overall_score: float, metrics: Dict[str, float]) -> str:
        """Assess overall quality level based on score and individual metrics."""
        if overall_score >= 0.85:
            return "Excellent"
        elif overall_score >= 0.75:
            return "Good"
        elif overall_score >= 0.65:
            return "Acceptable"
        elif overall_score >= 0.5:
            return "Needs Improvement"
        else:
            return "Poor"
    
    def _generate_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations for improvement."""
        recommendations = []
        
        for metric, score in metrics.items():
            threshold = self.quality_thresholds.get(metric, 0.6)
            if score < threshold:
                if metric == 'factual_accuracy':
                    recommendations.append("Improve fact-checking and evidence validation")
                elif metric == 'thematic_coverage':
                    recommendations.append("Expand theme diversity across more categories")
                elif metric == 'actionability':
                    recommendations.append("Add more specific, actionable recommendations")
                elif metric == 'uniqueness':
                    recommendations.append("Focus on destination-specific unique features")
                elif metric == 'source_credibility':
                    recommendations.append("Strengthen source validation and confidence scoring")
        
        if not recommendations:
            recommendations.append("Quality meets all thresholds - maintain current standards")
        
        return recommendations
    
    def _empty_score(self) -> dict:
        """Return empty score structure for invalid inputs."""
        return {
            "metrics": {
                'factual_accuracy': 0.0,
                'thematic_coverage': 0.0,
                'actionability': 0.0,
                'uniqueness': 0.0,
                'source_credibility': 0.0,
            },
            "overall_score": 0.0,
            "quality_level": "No Data",
            "recommendations": ["No affinities to evaluate"],
            "meets_threshold": False,
            "destination": "Unknown",
            "total_affinities": 0
        } 