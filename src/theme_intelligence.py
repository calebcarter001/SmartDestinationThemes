"""
Theme Intelligence Engine - Advanced theme quality and composition analysis
"""

import re
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from src.schemas import (
    EnhancedAffinity, ThemeDepthLevel, ExperienceIntensity, EmotionalResonance,
    AuthenticityLevel, CulturalSensitivity, MicroClimate, ThemeInterconnection,
    ExperienceContext, HiddenGemScore, ThemeComposition, EnhancedQualityAssessment
)

logger = logging.getLogger(__name__)

class ThemeIntelligenceEngine:
    """Advanced theme analysis and enhancement engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Theme Intelligence Engine with configuration."""
        self.config = config or {}
        
        # Load demographic mapping from config
        self.demographic_mapping = self.config.get('demographic_mapping', {
            'family': ['families with children', 'multi-generational groups'],
            'solo': ['solo travelers'],
            'couple': ['couples'],
            'group': ['friend groups']
        })
        
        # Load experience level keywords from config
        self.experience_keywords = self.config.get('experience_level_keywords', {
            'advanced': ['extreme', 'advanced', 'expert', 'professional'],
            'intermediate': ['intermediate', 'moderate', 'some experience'],
            'beginner': ['beginner', 'easy', 'introductory', 'basic']
        })
        
        # Load accessibility keywords from config
        self.accessibility_keywords = self.config.get('accessibility_keywords', {
            'high physical demands': ['extreme', 'strenuous', 'challenging', 'demanding'],
            'requires mobility': ['hiking', 'climbing', 'walking', 'stairs', 'uneven terrain'],
            'accessible': ['accessible', 'wheelchair', 'easy access', 'level ground']
        })
        
        self.emotional_keywords = {
            EmotionalResonance.PEACEFUL: ['quiet', 'serene', 'calm', 'tranquil', 'meditation', 'zen', 'peaceful'],
            EmotionalResonance.EXHILARATING: ['thrilling', 'exciting', 'adrenaline', 'extreme', 'adventure', 'rush'],
            EmotionalResonance.CONTEMPLATIVE: ['historical', 'museum', 'spiritual', 'reflective', 'philosophical'],
            EmotionalResonance.SOCIAL: ['festival', 'nightlife', 'community', 'group', 'celebration', 'party'],
            EmotionalResonance.SOLITARY: ['solo', 'private', 'individual', 'personal', 'introspective'],
            EmotionalResonance.CHALLENGING: ['difficult', 'demanding', 'skill', 'expertise', 'advanced'],
            EmotionalResonance.COMFORTING: ['familiar', 'cozy', 'comfortable', 'relaxing', 'soothing'],
            EmotionalResonance.INSPIRING: ['artistic', 'creative', 'innovative', 'motivational', 'uplifting']
        }
        
        self.authenticity_indicators = {
            'local_markers': ['local', 'neighborhood', 'authentic', 'traditional', 'family-owned', 'generations'],
            'tourist_markers': ['tourist', 'visitor', 'attraction', 'souvenir', 'tour bus', 'crowded'],
            'insider_markers': ['hidden', 'secret', 'locals only', 'off the beaten path', 'insider'],
            'commercial_markers': ['chain', 'franchise', 'commercialized', 'mass tourism', 'package']
        }
        
        self.cultural_sensitivity_keywords = {
            'religious': ['mosque', 'temple', 'church', 'shrine', 'sacred', 'holy', 'prayer'],
            'dress_code': ['modest', 'covered', 'formal', 'traditional dress', 'respectful attire'],
            'customs': ['etiquette', 'tradition', 'custom', 'protocol', 'respect', 'courtesy'],
            'language': ['language barrier', 'translation', 'local language', 'communication']
        }
        
        self.intensity_mapping = {
            'physical': {
                'walking': ExperienceIntensity.LOW,
                'hiking': ExperienceIntensity.MODERATE,
                'climbing': ExperienceIntensity.HIGH,
                'extreme sports': ExperienceIntensity.EXTREME,
                'relaxing': ExperienceIntensity.MINIMAL
            },
            'cultural': {
                'familiar': ExperienceIntensity.LOW,
                'immersive': ExperienceIntensity.MODERATE,
                'deep cultural': ExperienceIntensity.HIGH,
                'language intensive': ExperienceIntensity.EXTREME
            },
            'social': {
                'solo': ExperienceIntensity.MINIMAL,
                'small group': ExperienceIntensity.LOW,
                'social': ExperienceIntensity.MODERATE,
                'party': ExperienceIntensity.HIGH,
                'festival': ExperienceIntensity.EXTREME
            }
        }

    def enhance_affinity(self, basic_affinity: Dict[str, Any], destination: str) -> EnhancedAffinity:
        """Transform a basic affinity into an enhanced one with all intelligence layers"""
        
        # Extract basic information
        theme = basic_affinity.get('theme', '')
        category = basic_affinity.get('category', 'general')
        sub_themes = basic_affinity.get('sub_themes', [])
        confidence = basic_affinity.get('confidence', 0.5)
        rationale = basic_affinity.get('rationale', '')
        
        # Generate nano themes
        nano_themes = self._generate_nano_themes(theme, sub_themes, rationale)
        
        # Determine depth level
        depth_level = self._determine_depth_level(theme, sub_themes, nano_themes)
        
        # Assess authenticity
        authenticity_level, authenticity_score = self._assess_authenticity(theme, rationale, destination)
        
        # Analyze emotional resonance
        emotional_resonance = self._analyze_emotional_resonance(theme, rationale, sub_themes)
        
        # Calculate experience intensity
        experience_intensity = self._calculate_experience_intensity(theme, rationale, category)
        
        # Analyze micro-climate factors
        micro_climate = self._analyze_micro_climate(theme, destination, basic_affinity.get('seasonality', {}))
        
        # Assess cultural sensitivity
        cultural_sensitivity = self._assess_cultural_sensitivity(theme, rationale, destination)
        
        # Generate experience context
        experience_context = self._generate_experience_context(theme, basic_affinity.get('traveler_types', []))
        
        # Analyze theme interconnections
        theme_interconnections = self._analyze_theme_interconnections(theme, category, sub_themes)
        
        # Calculate hidden gem score
        hidden_gem_score = self._calculate_hidden_gem_score(theme, rationale, authenticity_level)
        
        return EnhancedAffinity(
            theme=theme,
            category=category,
            depth_level=depth_level,
            sub_themes=sub_themes,
            nano_themes=nano_themes,
            confidence=confidence,
            authenticity_level=authenticity_level,
            authenticity_score=authenticity_score,
            emotional_resonance=emotional_resonance,
            experience_intensity=experience_intensity,
            seasonality=basic_affinity.get('seasonality', {}),
            micro_climate=micro_climate,
            cultural_sensitivity=cultural_sensitivity,
            traveler_types=basic_affinity.get('traveler_types', []),
            experience_context=experience_context,
            theme_interconnections=theme_interconnections,
            hidden_gem_score=hidden_gem_score,
            price_point=basic_affinity.get('price_point', 'mid'),
            rationale=rationale,
            unique_selling_points=basic_affinity.get('unique_selling_points', []),
            validation=basic_affinity.get('validation', 'Generated')
        )

    def _generate_nano_themes(self, theme: str, sub_themes: List[str], rationale: str) -> List[str]:
        """Generate specific nano-level themes"""
        nano_themes = []
        
        # Theme-specific nano theme generation
        theme_lower = theme.lower()
        
        if 'food' in theme_lower or 'culinary' in theme_lower:
            nano_themes.extend(['street food markets', 'local family recipes', 'chef-owned restaurants', 'food tours'])
        
        if 'adventure' in theme_lower or 'outdoor' in theme_lower:
            nano_themes.extend(['sunrise hikes', 'technical climbing routes', 'wildlife photography', 'backcountry camping'])
        
        if 'culture' in theme_lower or 'art' in theme_lower:
            nano_themes.extend(['local artist studios', 'traditional craft workshops', 'underground music venues', 'neighborhood galleries'])
        
        if 'nightlife' in theme_lower or 'entertainment' in theme_lower:
            nano_themes.extend(['rooftop cocktail bars', 'jazz speakeasies', 'late-night food scenes', 'live music venues'])
        
        if 'shopping' in theme_lower:
            nano_themes.extend(['artisan markets', 'vintage boutiques', 'local designer shops', 'specialty bookstores'])
        
        # Extract specific mentions from rationale
        rationale_lower = rationale.lower()
        if 'museum' in rationale_lower:
            nano_themes.append('specialized museums')
        if 'beach' in rationale_lower:
            nano_themes.append('secluded beach coves')
        if 'mountain' in rationale_lower:
            nano_themes.append('alpine meadow trails')
        
        return list(set(nano_themes[:4]))  # Limit to 4 most relevant

    def _determine_depth_level(self, theme: str, sub_themes: List[str], nano_themes: List[str]) -> ThemeDepthLevel:
        """Determine the depth level of the theme"""
        if len(nano_themes) >= 3 and len(sub_themes) >= 2:
            return ThemeDepthLevel.NANO
        elif len(sub_themes) >= 2:
            return ThemeDepthLevel.MICRO
        else:
            return ThemeDepthLevel.MACRO

    def _assess_authenticity(self, theme: str, rationale: str, destination: str) -> Tuple[AuthenticityLevel, float]:
        """Assess the authenticity level and score of the theme"""
        text = f"{theme} {rationale}".lower()
        
        local_score = sum(1 for marker in self.authenticity_indicators['local_markers'] if marker in text)
        tourist_score = sum(1 for marker in self.authenticity_indicators['tourist_markers'] if marker in text)
        insider_score = sum(1 for marker in self.authenticity_indicators['insider_markers'] if marker in text)
        commercial_score = sum(1 for marker in self.authenticity_indicators['commercial_markers'] if marker in text)
        
        # Calculate authenticity score
        positive_signals = local_score + insider_score
        negative_signals = tourist_score + commercial_score
        
        if positive_signals > negative_signals and insider_score > 0:
            return AuthenticityLevel.AUTHENTIC_LOCAL, 0.9
        elif positive_signals > negative_signals:
            return AuthenticityLevel.LOCAL_INFLUENCED, 0.7
        elif negative_signals > positive_signals:
            return AuthenticityLevel.TOURIST_ORIENTED, 0.3
        elif commercial_score > 2:
            return AuthenticityLevel.TOURIST_TRAP, 0.1
        else:
            return AuthenticityLevel.BALANCED, 0.5

    def _analyze_emotional_resonance(self, theme: str, rationale: str, sub_themes: List[str]) -> List[EmotionalResonance]:
        """Analyze the emotional resonance of the theme"""
        text = f"{theme} {rationale} {' '.join(sub_themes)}".lower()
        resonances = []
        
        for emotion, keywords in self.emotional_keywords.items():
            if any(keyword in text for keyword in keywords):
                resonances.append(emotion)
        
        # Default resonances based on theme category
        if not resonances:
            theme_lower = theme.lower()
            if 'adventure' in theme_lower:
                resonances.append(EmotionalResonance.EXHILARATING)
            elif 'culture' in theme_lower:
                resonances.append(EmotionalResonance.CONTEMPLATIVE)
            elif 'nightlife' in theme_lower:
                resonances.append(EmotionalResonance.SOCIAL)
            elif 'spa' in theme_lower or 'wellness' in theme_lower:
                resonances.append(EmotionalResonance.PEACEFUL)
            else:
                resonances.append(EmotionalResonance.INSPIRING)
        
        return resonances[:3]  # Limit to top 3

    def _calculate_experience_intensity(self, theme: str, rationale: str, category: str) -> Dict[str, ExperienceIntensity]:
        """Calculate experience intensity across different dimensions"""
        text = f"{theme} {rationale}".lower()
        intensity = {}
        
        # Physical intensity
        for activity, level in self.intensity_mapping['physical'].items():
            if activity in text:
                intensity['physical'] = level
                break
        else:
            intensity['physical'] = ExperienceIntensity.LOW
        
        # Cultural intensity
        for activity, level in self.intensity_mapping['cultural'].items():
            if activity in text:
                intensity['cultural'] = level
                break
        else:
            intensity['cultural'] = ExperienceIntensity.MODERATE
        
        # Social intensity
        for activity, level in self.intensity_mapping['social'].items():
            if activity in text:
                intensity['social'] = level
                break
        else:
            intensity['social'] = ExperienceIntensity.MODERATE
        
        return intensity

    def _analyze_micro_climate(self, theme: str, destination: str, seasonality: Dict[str, List[str]]) -> MicroClimate:
        """Analyze micro-climate factors for optimal timing"""
        theme_lower = theme.lower()
        
        # Determine best times of day
        best_times = []
        if 'sunrise' in theme_lower or 'morning' in theme_lower:
            best_times.extend(['early morning', 'sunrise'])
        elif 'sunset' in theme_lower or 'evening' in theme_lower:
            best_times.extend(['evening', 'sunset'])
        elif 'nightlife' in theme_lower or 'night' in theme_lower:
            best_times.extend(['night', 'late evening'])
        elif 'photography' in theme_lower:
            best_times.extend(['golden hour', 'blue hour'])
        else:
            best_times.append('flexible')
        
        # Weather dependencies
        weather_deps = []
        if 'outdoor' in theme_lower or 'hiking' in theme_lower:
            weather_deps.extend(['clear weather', 'dry conditions'])
        elif 'beach' in theme_lower:
            weather_deps.extend(['sunny weather', 'calm seas'])
        elif 'snow' in theme_lower or 'skiing' in theme_lower:
            weather_deps.append('snow conditions')
        
        # Crowd patterns
        crowd_patterns = {}
        if 'museum' in theme_lower:
            crowd_patterns = {'weekday mornings': 'low', 'weekend afternoons': 'high'}
        elif 'restaurant' in theme_lower:
            crowd_patterns = {'lunch time': 'moderate', 'dinner time': 'high'}
        elif 'nightlife' in theme_lower:
            crowd_patterns = {'weeknights': 'moderate', 'weekends': 'high'}
        
        return MicroClimate(
            best_time_of_day=best_times,
            weather_dependencies=weather_deps,
            crowd_patterns=crowd_patterns,
            micro_season_timing=self._extract_micro_season(seasonality)
        )

    def _extract_micro_season(self, seasonality: Dict[str, List[str]]) -> Optional[str]:
        """Extract micro-season timing information"""
        if 'peak' in seasonality and seasonality['peak']:
            months = seasonality['peak']
            if len(months) <= 2:
                return f"Short season: {', '.join(months)}"
            elif 'March' in months and 'April' in months:
                return "Spring bloom period"
            elif 'September' in months and 'October' in months:
                return "Fall foliage season"
        return None

    def _assess_cultural_sensitivity(self, theme: str, rationale: str, destination: str) -> CulturalSensitivity:
        """Assess cultural sensitivity requirements"""
        text = f"{theme} {rationale}".lower()
        considerations = []
        
        # Check for religious considerations
        religious_aware = True
        if any(keyword in text for keyword in self.cultural_sensitivity_keywords['religious']):
            considerations.append("Respect religious customs and dress codes")
            religious_aware = True
        
        # Check for dress code requirements
        if any(keyword in text for keyword in self.cultural_sensitivity_keywords['dress_code']):
            considerations.append("Modest dress required")
        
        # Check for custom awareness
        customs_respected = True
        if any(keyword in text for keyword in self.cultural_sensitivity_keywords['customs']):
            considerations.append("Learn local customs and etiquette")
        
        # Language requirements
        language_req = None
        if any(keyword in text for keyword in self.cultural_sensitivity_keywords['language']):
            language_req = "Basic local language helpful"
        
        return CulturalSensitivity(
            appropriate=True,  # Default to appropriate
            considerations=considerations,
            religious_calendar_aware=religious_aware,
            local_customs_respected=customs_respected,
            language_requirements=language_req
        )

    def _generate_experience_context(self, theme: str, traveler_types: List[str]) -> ExperienceContext:
        """Generate experience context information"""
        theme_lower = theme.lower()
        
        # Demographic suitability
        demographics = []
        for traveler_type in traveler_types:
            demographics.extend(self.demographic_mapping.get(traveler_type, []))
        
        # Group dynamics
        group_dynamics = []
        if 'nightlife' in theme_lower:
            group_dynamics.extend(['social groups', 'party atmosphere'])
        elif 'museum' in theme_lower:
            group_dynamics.extend(['quiet contemplation', 'educational discussions'])
        elif 'adventure' in theme_lower:
            group_dynamics.extend(['team building', 'shared challenges'])
        
        # Experience level
        experience_level = "beginner"
        for level, keywords in self.experience_keywords.items():
            if any(keyword in theme_lower for keyword in keywords):
                experience_level = level
                break
        
        # Accessibility
        accessibility = "accessible"
        for level, keywords in self.accessibility_keywords.items():
            if any(keyword in theme_lower for keyword in keywords):
                accessibility = level
                break
        
        return ExperienceContext(
            demographic_suitability=demographics,
            group_dynamics=group_dynamics,
            experience_level_required=experience_level,
            accessibility_level=accessibility
        )

    def _analyze_theme_interconnections(self, theme: str, category: str, sub_themes: List[str]) -> ThemeInterconnection:
        """Analyze how this theme connects with others"""
        theme_lower = theme.lower()
        
        # Natural combinations
        combinations = []
        if 'food' in theme_lower:
            combinations.extend(['culture', 'nightlife', 'shopping'])
        elif 'adventure' in theme_lower:
            combinations.extend(['nature', 'photography', 'wellness'])
        elif 'culture' in theme_lower:
            combinations.extend(['food', 'art', 'history'])
        elif 'nightlife' in theme_lower:
            combinations.extend(['food', 'music', 'social'])
        
        # Sequential experiences
        sequences = []
        if 'morning' in theme_lower:
            sequences.append('afternoon relaxation')
        elif 'adventure' in theme_lower:
            sequences.extend(['post-activity dining', 'evening relaxation'])
        elif 'cultural' in theme_lower:
            sequences.append('reflective dining')
        
        # Energy flow
        energy_flow = "balanced"
        if 'extreme' in theme_lower or 'adventure' in theme_lower:
            energy_flow = "high-energy"
        elif 'spa' in theme_lower or 'meditation' in theme_lower:
            energy_flow = "restorative"
        elif 'nightlife' in theme_lower:
            energy_flow = "evening-peak"
        
        return ThemeInterconnection(
            natural_combinations=combinations,
            sequential_experiences=sequences,
            energy_flow=energy_flow
        )

    def _calculate_hidden_gem_score(self, theme: str, rationale: str, authenticity_level: AuthenticityLevel) -> HiddenGemScore:
        """Calculate hidden gem potential score"""
        text = f"{theme} {rationale}".lower()
        
        # Local frequency ratio (inverse of tourist mentions)
        tourist_mentions = sum(1 for marker in self.authenticity_indicators['tourist_markers'] if marker in text)
        local_mentions = sum(1 for marker in self.authenticity_indicators['local_markers'] if marker in text)
        
        local_ratio = max(0.1, (local_mentions + 1) / (tourist_mentions + local_mentions + 2))
        
        # Insider knowledge required
        insider_required = any(marker in text for marker in self.authenticity_indicators['insider_markers'])
        
        # Emerging scene indicator
        emerging_keywords = ['new', 'emerging', 'up-and-coming', 'recently opened', 'trending']
        emerging = any(keyword in text for keyword in emerging_keywords)
        
        # Off-peak excellence
        off_peak = 'avoid' in text or 'off-season' in text or 'quiet' in text
        
        # Overall uniqueness score
        uniqueness = 0.3  # Base score
        if authenticity_level == AuthenticityLevel.AUTHENTIC_LOCAL:
            uniqueness += 0.4
        elif authenticity_level == AuthenticityLevel.LOCAL_INFLUENCED:
            uniqueness += 0.2
        
        if insider_required:
            uniqueness += 0.2
        if emerging:
            uniqueness += 0.1
        
        uniqueness = min(1.0, uniqueness)
        
        return HiddenGemScore(
            local_frequency_ratio=local_ratio,
            insider_knowledge_required=insider_required,
            emerging_scene_indicator=emerging,
            off_peak_excellence=off_peak,
            uniqueness_score=uniqueness
        )

    def analyze_theme_composition(self, enhanced_affinities: List[EnhancedAffinity]) -> ThemeComposition:
        """Analyze the overall composition of themes for balance and flow"""
        
        if not enhanced_affinities:
            return ThemeComposition()
        
        # Energy flow balance
        energy_flows = {}
        for affinity in enhanced_affinities:
            flow = affinity.theme_interconnections.energy_flow
            energy_flows[flow] = energy_flows.get(flow, 0) + 1
        
        total_themes = len(enhanced_affinities)
        energy_balance = {k: v / total_themes for k, v in energy_flows.items()}
        
        # Sensory variety (based on categories and emotional resonance)
        categories = set(affinity.category for affinity in enhanced_affinities)
        emotions = set()
        for affinity in enhanced_affinities:
            emotions.update(affinity.emotional_resonance)
        
        sensory_variety = min(1.0, (len(categories) + len(emotions)) / 15)  # Normalize
        
        # Pace variation (based on intensity levels)
        intensities = []
        for affinity in enhanced_affinities:
            for intensity in affinity.experience_intensity.values():
                intensities.append(intensity.value)
        
        unique_intensities = len(set(intensities))
        pace_variation = min(1.0, unique_intensities / 5)  # 5 intensity levels
        
        # Social spectrum coverage
        social_coverage = {}
        for affinity in enhanced_affinities:
            for traveler_type in affinity.traveler_types:
                social_coverage[traveler_type] = social_coverage.get(traveler_type, 0) + 1
        
        # Learning curve progression
        experience_levels = [affinity.experience_context.experience_level_required for affinity in enhanced_affinities]
        has_progression = len(set(experience_levels)) > 1
        
        # Overall composition score
        composition_score = (
            (1.0 if len(energy_balance) > 1 else 0.5) * 0.3 +  # Energy variety
            sensory_variety * 0.3 +
            pace_variation * 0.2 +
            (1.0 if len(social_coverage) >= 3 else 0.5) * 0.1 +  # Social variety
            (1.0 if has_progression else 0.7) * 0.1  # Learning progression
        )
        
        return ThemeComposition(
            energy_flow_balance=energy_balance,
            sensory_variety_score=sensory_variety,
            pace_variation_index=pace_variation,
            social_spectrum_coverage=social_coverage,
            learning_curve_progression=has_progression,
            overall_composition_score=composition_score
        )

    def generate_enhanced_quality_assessment(self, enhanced_affinities: List[EnhancedAffinity], 
                                           destination: str, base_quality: Dict[str, Any]) -> EnhancedQualityAssessment:
        """Generate comprehensive quality assessment with new dimensions"""
        
        if not enhanced_affinities:
            return EnhancedQualityAssessment(
                destination=destination,
                total_affinities=0
            )
        
        # Calculate new quality dimensions
        
        # Theme depth score
        depth_scores = []
        for affinity in enhanced_affinities:
            if affinity.depth_level == ThemeDepthLevel.NANO:
                depth_scores.append(1.0)
            elif affinity.depth_level == ThemeDepthLevel.MICRO:
                depth_scores.append(0.7)
            else:
                depth_scores.append(0.4)
        
        theme_depth_score = sum(depth_scores) / len(depth_scores)
        
        # Authenticity distribution
        auth_dist = {}
        for affinity in enhanced_affinities:
            level = affinity.authenticity_level
            auth_dist[level] = auth_dist.get(level, 0) + 1
        
        # Emotional coverage score
        all_emotions = set()
        for affinity in enhanced_affinities:
            all_emotions.update(affinity.emotional_resonance)
        
        emotional_coverage = min(1.0, len(all_emotions) / 8)  # 8 total emotions
        
        # Cultural sensitivity score
        cultural_scores = []
        for affinity in enhanced_affinities:
            if affinity.cultural_sensitivity.appropriate:
                cultural_scores.append(1.0)
            else:
                cultural_scores.append(0.0)
        
        cultural_sensitivity_score = sum(cultural_scores) / len(cultural_scores) if cultural_scores else 1.0
        
        # Context relevance score
        context_scores = []
        for affinity in enhanced_affinities:
            # Score based on context completeness
            context_score = 0.0
            if affinity.experience_context.demographic_suitability:
                context_score += 0.25
            if affinity.experience_context.group_dynamics:
                context_score += 0.25
            if affinity.micro_climate.best_time_of_day:
                context_score += 0.25
            if affinity.theme_interconnections.natural_combinations:
                context_score += 0.25
            context_scores.append(context_score)
        
        context_relevance_score = sum(context_scores) / len(context_scores)
        
        # Hidden gem ratio
        hidden_gems = sum(1 for affinity in enhanced_affinities if affinity.hidden_gem_score.uniqueness_score > 0.6)
        hidden_gem_ratio = hidden_gems / len(enhanced_affinities)
        
        # Theme composition analysis
        theme_composition = self.analyze_theme_composition(enhanced_affinities)
        
        # Generate enhanced recommendations
        recommendations = []
        composition_improvements = []
        
        if theme_depth_score < 0.6:
            recommendations.append("Add more specific, detailed themes with nano-level granularity")
        
        if emotional_coverage < 0.5:
            recommendations.append("Increase emotional variety to cover more traveler motivations")
        
        if hidden_gem_ratio < 0.2:
            recommendations.append("Include more unique, authentic local experiences")
        
        if theme_composition.overall_composition_score < 0.6:
            composition_improvements.append("Improve theme balance and flow for better experience composition")
        
        if theme_composition.pace_variation_index < 0.5:
            composition_improvements.append("Add more variety in experience intensity levels")
        
        # Calculate enhanced overall score
        enhanced_score = (
            base_quality.get('overall_score', 0.5) * 0.4 +  # Base quality
            theme_depth_score * 0.15 +
            emotional_coverage * 0.15 +
            cultural_sensitivity_score * 0.1 +
            context_relevance_score * 0.1 +
            theme_composition.overall_composition_score * 0.1
        )
        
        return EnhancedQualityAssessment(
            metrics=base_quality.get('metrics', {}),
            overall_score=enhanced_score,
            quality_level=self._determine_quality_level(enhanced_score),
            theme_depth_score=theme_depth_score,
            authenticity_distribution=auth_dist,
            emotional_coverage_score=emotional_coverage,
            cultural_sensitivity_score=cultural_sensitivity_score,
            context_relevance_score=context_relevance_score,
            hidden_gem_ratio=hidden_gem_ratio,
            theme_composition=theme_composition,
            recommendations=recommendations,
            composition_improvements=composition_improvements,
            meets_threshold=enhanced_score >= 0.75,
            destination=destination,
            total_affinities=len(enhanced_affinities)
        )

    def _determine_quality_level(self, score: float) -> str:
        """Determine quality level from score"""
        if score >= 0.85:
            return "Excellent"
        elif score >= 0.75:
            return "Good"
        elif score >= 0.65:
            return "Acceptable"
        else:
            return "Needs Improvement" 