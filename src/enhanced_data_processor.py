"""
Enhanced Data Processor - Adds intelligence layers to affinities and manages JSON persistence
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.scorer import AffinityQualityScorer

logger = logging.getLogger(__name__)

class EnhancedDataProcessor:
    """
    Processes and enhances destination affinity data with intelligence layers
    and manages JSON persistence with rich metadata.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.scorer = AffinityQualityScorer(config)
        
        # Intelligence enhancement mappings
        self.emotional_keywords = {
            'peaceful': ['quiet', 'serene', 'calm', 'tranquil', 'meditation', 'zen', 'peaceful'],
            'exhilarating': ['thrilling', 'exciting', 'adrenaline', 'extreme', 'adventure', 'rush'],
            'contemplative': ['historical', 'museum', 'spiritual', 'reflective', 'philosophical'],
            'social': ['festival', 'nightlife', 'community', 'group', 'celebration', 'party'],
            'solitary': ['solo', 'private', 'individual', 'personal', 'introspective'],
            'challenging': ['difficult', 'demanding', 'skill', 'expertise', 'advanced'],
            'comforting': ['familiar', 'cozy', 'comfortable', 'relaxing', 'soothing'],
            'inspiring': ['artistic', 'creative', 'innovative', 'motivational', 'uplifting']
        }
        
        self.authenticity_indicators = {
            'local_markers': ['local', 'neighborhood', 'authentic', 'traditional', 'family-owned', 'generations'],
            'tourist_markers': ['tourist', 'visitor', 'attraction', 'souvenir', 'tour bus', 'crowded'],
            'insider_markers': ['hidden', 'secret', 'locals only', 'off the beaten path', 'insider'],
            'commercial_markers': ['chain', 'franchise', 'commercialized', 'mass tourism', 'package']
        }
        
        self.intensity_levels = ['minimal', 'low', 'moderate', 'high', 'extreme']
        self.depth_levels = ['macro', 'micro', 'nano']

    def enhance_and_save_affinities(self, affinities_data: Dict[str, Any], 
                                  destination: str, output_file: str = None) -> Dict[str, Any]:
        """
        Enhance affinities with intelligence layers and save to JSON.
        
        Args:
            affinities_data: Raw affinity data
            destination: Destination name
            output_file: Optional output file path
        
        Returns:
            Enhanced affinities data with intelligence layers
        """
        logger.info(f"Enhancing affinities for {destination}")
        
        # Enhance each affinity with intelligence layers
        enhanced_affinities = []
        if 'affinities' in affinities_data:
            for affinity in affinities_data['affinities']:
                enhanced_affinity = self._enhance_single_affinity(affinity, destination)
                enhanced_affinities.append(enhanced_affinity)
        
        # Create enhanced dataset structure
        enhanced_data = {
            'destination_id': destination.lower().replace(' ', '_').replace(',', ''),
            'destination_name': destination,
            'affinities': enhanced_affinities,
            'meta': {
                **affinities_data.get('meta', {}),
                'enhancement_timestamp': datetime.now().isoformat(),
                'total_affinities': len(enhanced_affinities),
                'enhancement_version': '2.0'
            }
        }
        
        # Calculate enhanced quality assessment
        enhanced_data['quality_assessment'] = self.scorer.score_affinity_set(
            {'affinities': enhanced_affinities}, destination
        )
        
        # Add intelligence insights
        enhanced_data['intelligence_insights'] = self._generate_intelligence_insights(enhanced_affinities)
        
        # Add composition analysis
        enhanced_data['composition_analysis'] = self._analyze_composition(enhanced_affinities)
        
        # Add QA workflow status
        enhanced_data['qa_workflow'] = self._generate_qa_workflow(enhanced_data['quality_assessment'])
        
        # Save to JSON
        if output_file:
            self._save_to_json(enhanced_data, output_file)
        
        logger.info(f"Enhanced {len(enhanced_affinities)} affinities for {destination}")
        return enhanced_data

    def _enhance_single_affinity(self, affinity: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Enhance a single affinity with intelligence layers."""
        
        enhanced = affinity.copy()
        
        # Add depth analysis
        enhanced['depth_analysis'] = self._analyze_theme_depth(affinity)
        
        # Add authenticity scoring
        enhanced['authenticity_analysis'] = self._analyze_authenticity(affinity)
        
        # Add emotional profiling
        enhanced['emotional_profile'] = self._analyze_emotional_resonance(affinity)
        
        # Add experience intensity
        enhanced['experience_intensity'] = self._analyze_experience_intensity(affinity)
        
        # Add contextual information
        enhanced['contextual_info'] = self._analyze_context(affinity, destination)
        
        # Add micro-climate insights
        enhanced['micro_climate'] = self._analyze_micro_climate(affinity, destination)
        
        # Add cultural sensitivity assessment
        enhanced['cultural_sensitivity'] = self._assess_cultural_sensitivity(affinity, destination)
        
        # Add theme interconnections
        enhanced['theme_interconnections'] = self._analyze_theme_interconnections(affinity)
        
        # Add hidden gem potential
        enhanced['hidden_gem_score'] = self._calculate_hidden_gem_score(affinity)
        
        return enhanced

    def _analyze_theme_depth(self, affinity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze theme depth and granularity."""
        theme = affinity.get('theme', '')
        sub_themes = affinity.get('sub_themes', [])
        rationale = affinity.get('rationale', '')
        
        # Generate nano themes
        nano_themes = self._generate_nano_themes(theme, sub_themes, rationale)
        
        # Determine depth level
        if len(nano_themes) >= 3 and len(sub_themes) >= 2:
            depth_level = 'nano'
            depth_score = 1.0
        elif len(sub_themes) >= 2:
            depth_level = 'micro'
            depth_score = 0.7
        else:
            depth_level = 'macro'
            depth_score = 0.4
        
        return {
            'depth_level': depth_level,
            'depth_score': depth_score,
            'nano_themes': nano_themes,
            'theme_specificity': len(rationale.split()) / 50.0,  # Normalized by length
            'sub_theme_count': len(sub_themes)
        }

    def _generate_nano_themes(self, theme: str, sub_themes: List[str], rationale: str) -> List[str]:
        """Generate specific nano-level themes."""
        nano_themes = []
        theme_lower = theme.lower()
        rationale_lower = rationale.lower()
        
        # Theme-specific nano theme generation
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
        if 'museum' in rationale_lower:
            nano_themes.append('specialized museums')
        if 'beach' in rationale_lower:
            nano_themes.append('secluded beach coves')
        if 'mountain' in rationale_lower:
            nano_themes.append('alpine meadow trails')
        
        return list(set(nano_themes[:4]))  # Limit to 4 most relevant

    def _analyze_authenticity(self, affinity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze authenticity level and characteristics."""
        theme = affinity.get('theme', '')
        rationale = affinity.get('rationale', '')
        text = f"{theme} {rationale}".lower()
        
        # Count authenticity indicators
        local_score = sum(1 for marker in self.authenticity_indicators['local_markers'] if marker in text)
        tourist_score = sum(1 for marker in self.authenticity_indicators['tourist_markers'] if marker in text)
        insider_score = sum(1 for marker in self.authenticity_indicators['insider_markers'] if marker in text)
        commercial_score = sum(1 for marker in self.authenticity_indicators['commercial_markers'] if marker in text)
        
        # Determine authenticity level
        positive_signals = local_score + insider_score
        negative_signals = tourist_score + commercial_score
        
        if positive_signals > negative_signals and insider_score > 0:
            authenticity_level = 'authentic_local'
            authenticity_score = 0.9
        elif positive_signals > negative_signals:
            authenticity_level = 'local_influenced'
            authenticity_score = 0.7
        elif negative_signals > positive_signals:
            authenticity_level = 'tourist_oriented'
            authenticity_score = 0.3
        elif commercial_score > 2:
            authenticity_level = 'tourist_trap'
            authenticity_score = 0.1
        else:
            authenticity_level = 'balanced'
            authenticity_score = 0.5
        
        return {
            'authenticity_level': authenticity_level,
            'authenticity_score': authenticity_score,
            'local_indicators': local_score,
            'tourist_indicators': tourist_score,
            'insider_indicators': insider_score,
            'commercial_indicators': commercial_score
        }

    def _analyze_emotional_resonance(self, affinity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze emotional resonance and appeal."""
        theme = affinity.get('theme', '')
        rationale = affinity.get('rationale', '')
        sub_themes = affinity.get('sub_themes', [])
        text = f"{theme} {rationale} {' '.join(sub_themes)}".lower()
        
        detected_emotions = []
        emotion_scores = {}
        
        for emotion, keywords in self.emotional_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > 0:
                detected_emotions.append(emotion)
                emotion_scores[emotion] = min(1.0, matches / 3.0)  # Normalize
        
        # Default emotion if none detected
        if not detected_emotions:
            theme_lower = theme.lower()
            if 'adventure' in theme_lower:
                detected_emotions.append('exhilarating')
                emotion_scores['exhilarating'] = 0.7
            elif 'culture' in theme_lower:
                detected_emotions.append('contemplative')
                emotion_scores['contemplative'] = 0.7
            elif 'nightlife' in theme_lower:
                detected_emotions.append('social')
                emotion_scores['social'] = 0.7
            elif 'spa' in theme_lower or 'wellness' in theme_lower:
                detected_emotions.append('peaceful')
                emotion_scores['peaceful'] = 0.7
            else:
                detected_emotions.append('inspiring')
                emotion_scores['inspiring'] = 0.5
        
        return {
            'primary_emotions': detected_emotions[:3],
            'emotion_scores': emotion_scores,
            'emotional_variety_score': min(1.0, len(detected_emotions) / 3.0),
            'emotional_intensity': max(emotion_scores.values()) if emotion_scores else 0.5
        }

    def _analyze_experience_intensity(self, affinity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze experience intensity across dimensions."""
        theme = affinity.get('theme', '')
        rationale = affinity.get('rationale', '')
        text = f"{theme} {rationale}".lower()
        
        # Physical intensity
        physical_intensity = 'low'
        if any(word in text for word in ['extreme', 'climbing', 'hiking', 'demanding']):
            physical_intensity = 'high'
        elif any(word in text for word in ['walking', 'strolling', 'gentle']):
            physical_intensity = 'low'
        elif any(word in text for word in ['active', 'moderate', 'biking']):
            physical_intensity = 'moderate'
        elif any(word in text for word in ['relaxing', 'spa', 'peaceful']):
            physical_intensity = 'minimal'
        
        # Cultural intensity
        cultural_intensity = 'moderate'
        if any(word in text for word in ['immersive', 'deep', 'traditional', 'authentic']):
            cultural_intensity = 'high'
        elif any(word in text for word in ['surface', 'casual', 'brief']):
            cultural_intensity = 'low'
        
        # Social intensity
        social_intensity = 'moderate'
        if any(word in text for word in ['party', 'festival', 'crowded', 'social']):
            social_intensity = 'high'
        elif any(word in text for word in ['solo', 'quiet', 'private', 'peaceful']):
            social_intensity = 'low'
        
        return {
            'physical': physical_intensity,
            'cultural': cultural_intensity,
            'social': social_intensity,
            'overall_intensity': self._calculate_overall_intensity(physical_intensity, cultural_intensity, social_intensity)
        }

    def _calculate_overall_intensity(self, physical: str, cultural: str, social: str) -> str:
        """Calculate overall intensity level."""
        intensity_values = {'minimal': 0, 'low': 1, 'moderate': 2, 'high': 3, 'extreme': 4}
        
        avg_intensity = (intensity_values[physical] + intensity_values[cultural] + intensity_values[social]) / 3
        
        if avg_intensity >= 3.5:
            return 'extreme'
        elif avg_intensity >= 2.5:
            return 'high'
        elif avg_intensity >= 1.5:
            return 'moderate'
        elif avg_intensity >= 0.5:
            return 'low'
        else:
            return 'minimal'

    def _analyze_context(self, affinity: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Analyze contextual information and suitability."""
        theme = affinity.get('theme', '')
        traveler_types = affinity.get('traveler_types', [])
        
        # Demographic suitability
        demographics = []
        if 'family' in traveler_types:
            demographics.extend(['families with children', 'multi-generational groups'])
        if 'solo' in traveler_types:
            demographics.append('solo travelers')
        if 'couple' in traveler_types:
            demographics.append('couples')
        if 'group' in traveler_types:
            demographics.append('friend groups')
        
        # Experience level required
        experience_level = 'beginner'
        theme_lower = theme.lower()
        if 'extreme' in theme_lower or 'advanced' in theme_lower:
            experience_level = 'advanced'
        elif 'intermediate' in theme_lower:
            experience_level = 'intermediate'
        
        # Accessibility level
        accessibility = 'accessible'
        if 'hiking' in theme_lower or 'climbing' in theme_lower:
            accessibility = 'requires mobility'
        elif 'extreme' in theme_lower:
            accessibility = 'high physical demands'
        
        return {
            'demographic_suitability': demographics,
            'experience_level_required': experience_level,
            'accessibility_level': accessibility,
            'group_dynamics': self._determine_group_dynamics(theme),
            'time_commitment': self._estimate_time_commitment(theme)
        }

    def _determine_group_dynamics(self, theme: str) -> List[str]:
        """Determine suitable group dynamics."""
        theme_lower = theme.lower()
        dynamics = []
        
        if 'nightlife' in theme_lower:
            dynamics.extend(['social groups', 'party atmosphere'])
        elif 'museum' in theme_lower:
            dynamics.extend(['quiet contemplation', 'educational discussions'])
        elif 'adventure' in theme_lower:
            dynamics.extend(['team building', 'shared challenges'])
        elif 'food' in theme_lower:
            dynamics.extend(['social dining', 'shared experiences'])
        else:
            dynamics.append('flexible')
        
        return dynamics

    def _estimate_time_commitment(self, theme: str) -> str:
        """Estimate time commitment for the theme."""
        theme_lower = theme.lower()
        
        if any(word in theme_lower for word in ['tour', 'day trip', 'excursion']):
            return 'full day'
        elif any(word in theme_lower for word in ['museum', 'gallery', 'show']):
            return '2-4 hours'
        elif any(word in theme_lower for word in ['dining', 'restaurant', 'bar']):
            return '1-3 hours'
        elif any(word in theme_lower for word in ['hiking', 'adventure']):
            return '3-8 hours'
        else:
            return 'flexible'

    def _analyze_micro_climate(self, affinity: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Analyze micro-climate and timing factors."""
        theme = affinity.get('theme', '')
        seasonality = affinity.get('seasonality', {})
        theme_lower = theme.lower()
        
        # Best times of day
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
        else:
            crowd_patterns = {'weekdays': 'moderate', 'weekends': 'high'}
        
        return {
            'best_time_of_day': best_times,
            'weather_dependencies': weather_deps,
            'crowd_patterns': crowd_patterns,
            'seasonal_variations': seasonality,
            'micro_season_timing': self._extract_micro_season(seasonality)
        }

    def _extract_micro_season(self, seasonality: Dict[str, List[str]]) -> Optional[str]:
        """Extract micro-season timing information."""
        if 'peak' in seasonality and seasonality['peak']:
            months = seasonality['peak']
            if len(months) <= 2:
                return f"Short season: {', '.join(months)}"
            elif 'March' in months and 'April' in months:
                return "Spring bloom period"
            elif 'September' in months and 'October' in months:
                return "Fall foliage season"
        return None

    def _assess_cultural_sensitivity(self, affinity: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Assess cultural sensitivity requirements."""
        theme = affinity.get('theme', '')
        rationale = affinity.get('rationale', '')
        text = f"{theme} {rationale}".lower()
        
        considerations = []
        religious_aware = True
        customs_respected = True
        language_req = None
        
        # Check for religious considerations
        if any(keyword in text for keyword in ['mosque', 'temple', 'church', 'shrine', 'sacred', 'holy']):
            considerations.append("Respect religious customs and dress codes")
            religious_aware = True
        
        # Check for dress code requirements
        if any(keyword in text for keyword in ['modest', 'covered', 'formal', 'traditional dress']):
            considerations.append("Modest dress required")
        
        # Check for custom awareness
        if any(keyword in text for keyword in ['tradition', 'custom', 'protocol', 'etiquette']):
            considerations.append("Learn local customs and etiquette")
        
        # Language requirements
        if any(keyword in text for keyword in ['language', 'translation', 'local language']):
            language_req = "Basic local language helpful"
        
        return {
            'appropriate': True,  # Default to appropriate
            'considerations': considerations,
            'religious_calendar_aware': religious_aware,
            'local_customs_respected': customs_respected,
            'language_requirements': language_req,
            'cultural_immersion_level': self._assess_cultural_immersion(text)
        }

    def _assess_cultural_immersion(self, text: str) -> str:
        """Assess level of cultural immersion required."""
        if any(word in text for word in ['deep', 'immersive', 'traditional', 'authentic']):
            return 'high'
        elif any(word in text for word in ['surface', 'casual', 'tourist']):
            return 'low'
        else:
            return 'moderate'

    def _analyze_theme_interconnections(self, affinity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how this theme connects with others."""
        theme = affinity.get('theme', '')
        category = affinity.get('category', '')
        sub_themes = affinity.get('sub_themes', [])
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
        energy_flow = 'balanced'
        if 'extreme' in theme_lower or 'adventure' in theme_lower:
            energy_flow = 'high-energy'
        elif 'spa' in theme_lower or 'meditation' in theme_lower:
            energy_flow = 'restorative'
        elif 'nightlife' in theme_lower:
            energy_flow = 'evening-peak'
        
        return {
            'natural_combinations': combinations,
            'sequential_experiences': sequences,
            'energy_flow': energy_flow,
            'complementary_activities': self._suggest_complementary_activities(theme_lower),
            'skill_progression': self._assess_skill_progression(theme_lower)
        }

    def _suggest_complementary_activities(self, theme_lower: str) -> List[str]:
        """Suggest complementary activities."""
        if 'food' in theme_lower:
            return ['cooking classes', 'market tours', 'wine tastings']
        elif 'adventure' in theme_lower:
            return ['photography workshops', 'nature walks', 'equipment rental']
        elif 'culture' in theme_lower:
            return ['guided tours', 'local workshops', 'historical walks']
        else:
            return []

    def _assess_skill_progression(self, theme_lower: str) -> Optional[str]:
        """Assess if theme offers skill progression opportunities."""
        if any(word in theme_lower for word in ['class', 'workshop', 'lesson', 'course']):
            return 'learning opportunity'
        elif any(word in theme_lower for word in ['beginner', 'intermediate', 'advanced']):
            return 'skill levels available'
        else:
            return None

    def _calculate_hidden_gem_score(self, affinity: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate hidden gem potential score."""
        theme = affinity.get('theme', '')
        rationale = affinity.get('rationale', '')
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
        off_peak = any(word in text for word in ['avoid', 'off-season', 'quiet', 'less crowded'])
        
        # Overall uniqueness score
        uniqueness = 0.3  # Base score
        if local_ratio > 0.6:
            uniqueness += 0.3
        if insider_required:
            uniqueness += 0.2
        if emerging:
            uniqueness += 0.1
        if off_peak:
            uniqueness += 0.1
        
        uniqueness = min(1.0, uniqueness)
        
        return {
            'local_frequency_ratio': round(local_ratio, 3),
            'insider_knowledge_required': insider_required,
            'emerging_scene_indicator': emerging,
            'off_peak_excellence': off_peak,
            'uniqueness_score': round(uniqueness, 3),
            'hidden_gem_level': self._classify_hidden_gem_level(uniqueness)
        }

    def _classify_hidden_gem_level(self, uniqueness_score: float) -> str:
        """Classify hidden gem level based on uniqueness score."""
        if uniqueness_score >= 0.8:
            return 'true hidden gem'
        elif uniqueness_score >= 0.6:
            return 'local favorite'
        elif uniqueness_score >= 0.4:
            return 'off the beaten path'
        else:
            return 'mainstream'

    def _generate_intelligence_insights(self, enhanced_affinities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate high-level intelligence insights from enhanced affinities."""
        
        if not enhanced_affinities:
            return {}
        
        # Depth distribution
        depth_levels = [aff['depth_analysis']['depth_level'] for aff in enhanced_affinities]
        depth_distribution = {level: depth_levels.count(level) for level in set(depth_levels)}
        
        # Authenticity distribution
        auth_levels = [aff['authenticity_analysis']['authenticity_level'] for aff in enhanced_affinities]
        auth_distribution = {level: auth_levels.count(level) for level in set(auth_levels)}
        
        # Emotional variety
        all_emotions = set()
        for aff in enhanced_affinities:
            all_emotions.update(aff['emotional_profile']['primary_emotions'])
        
        # Intensity distribution
        intensity_levels = [aff['experience_intensity']['overall_intensity'] for aff in enhanced_affinities]
        intensity_distribution = {level: intensity_levels.count(level) for level in set(intensity_levels)}
        
        # Hidden gems count
        hidden_gems = sum(1 for aff in enhanced_affinities 
                         if aff['hidden_gem_score']['uniqueness_score'] > 0.6)
        
        return {
            'depth_distribution': depth_distribution,
            'authenticity_distribution': auth_distribution,
            'emotional_variety': {
                'total_emotions': len(all_emotions),
                'emotions_covered': list(all_emotions),
                'emotional_coverage_score': min(1.0, len(all_emotions) / 8)
            },
            'intensity_distribution': intensity_distribution,
            'hidden_gems_count': hidden_gems,
            'hidden_gems_ratio': round(hidden_gems / len(enhanced_affinities), 3),
            'average_depth_score': round(sum(aff['depth_analysis']['depth_score'] 
                                           for aff in enhanced_affinities) / len(enhanced_affinities), 3),
            'average_authenticity_score': round(sum(aff['authenticity_analysis']['authenticity_score'] 
                                                  for aff in enhanced_affinities) / len(enhanced_affinities), 3)
        }

    def _analyze_composition(self, enhanced_affinities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the overall composition of themes for balance and flow."""
        
        if not enhanced_affinities:
            return {}
        
        # Energy flow balance
        energy_flows = {}
        for aff in enhanced_affinities:
            flow = aff['theme_interconnections']['energy_flow']
            energy_flows[flow] = energy_flows.get(flow, 0) + 1
        
        total_themes = len(enhanced_affinities)
        energy_balance = {k: round(v / total_themes, 3) for k, v in energy_flows.items()}
        
        # Category diversity
        categories = [aff.get('category', 'unknown') for aff in enhanced_affinities]
        category_distribution = {cat: categories.count(cat) for cat in set(categories)}
        
        # Time commitment distribution
        time_commitments = [aff['contextual_info']['time_commitment'] for aff in enhanced_affinities]
        time_distribution = {time: time_commitments.count(time) for time in set(time_commitments)}
        
        # Social spectrum coverage
        social_coverage = {}
        for aff in enhanced_affinities:
            social_level = aff['experience_intensity']['social']
            social_coverage[social_level] = social_coverage.get(social_level, 0) + 1
        
        # Overall composition score
        composition_score = self._calculate_composition_score(
            energy_balance, category_distribution, time_distribution, social_coverage, total_themes
        )
        
        return {
            'energy_flow_balance': energy_balance,
            'category_distribution': category_distribution,
            'time_commitment_distribution': time_distribution,
            'social_intensity_distribution': social_coverage,
            'overall_composition_score': composition_score,
            'composition_quality': self._assess_composition_quality(composition_score),
            'balance_recommendations': self._generate_balance_recommendations(
                energy_balance, category_distribution, social_coverage
            )
        }

    def _calculate_composition_score(self, energy_balance: Dict[str, float], 
                                   category_distribution: Dict[str, int],
                                   time_distribution: Dict[str, int],
                                   social_coverage: Dict[str, int], 
                                   total_themes: int) -> float:
        """Calculate overall composition score."""
        
        # Energy variety (better if more balanced)
        energy_variety = 1.0 if len(energy_balance) > 1 else 0.5
        
        # Category variety (better with more categories)
        category_variety = min(1.0, len(category_distribution) / 6)  # Assuming 6 main categories
        
        # Time variety (better with different time commitments)
        time_variety = min(1.0, len(time_distribution) / 4)  # 4 main time categories
        
        # Social variety (better with different social levels)
        social_variety = min(1.0, len(social_coverage) / 4)  # 4 social intensity levels
        
        # Weighted combination
        composition_score = (
            energy_variety * 0.3 +
            category_variety * 0.3 +
            time_variety * 0.2 +
            social_variety * 0.2
        )
        
        return round(composition_score, 3)

    def _assess_composition_quality(self, score: float) -> str:
        """Assess composition quality level."""
        if score >= 0.8:
            return 'excellent'
        elif score >= 0.6:
            return 'good'
        elif score >= 0.4:
            return 'acceptable'
        else:
            return 'needs improvement'

    def _generate_balance_recommendations(self, energy_balance: Dict[str, float],
                                        category_distribution: Dict[str, int],
                                        social_coverage: Dict[str, int]) -> List[str]:
        """Generate recommendations for better balance."""
        recommendations = []
        
        # Check energy balance
        if len(energy_balance) == 1:
            recommendations.append("Add themes with different energy levels for better balance")
        
        # Check category diversity
        if len(category_distribution) < 4:
            recommendations.append("Include more diverse activity categories")
        
        # Check social coverage
        if len(social_coverage) < 3:
            recommendations.append("Add themes with varying social intensity levels")
        
        # Check for over-concentration
        max_category_count = max(category_distribution.values()) if category_distribution else 0
        if max_category_count > len(category_distribution) * 0.5:
            recommendations.append("Reduce concentration in dominant categories")
        
        return recommendations

    def _generate_qa_workflow(self, quality_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate QA workflow based on quality assessment."""
        
        overall_score = quality_assessment.get('overall_score', 0.0)
        quality_level = quality_assessment.get('quality_level', 'Unknown')
        
        # Determine workflow path
        if overall_score >= 0.85:
            workflow_path = 'auto_approve'
            review_required = False
            priority = 'low'
        elif overall_score >= 0.75:
            workflow_path = 'light_review'
            review_required = True
            priority = 'low'
        elif overall_score >= 0.65:
            workflow_path = 'standard_review'
            review_required = True
            priority = 'medium'
        else:
            workflow_path = 'detailed_review'
            review_required = True
            priority = 'high'
        
        return {
            'workflow_path': workflow_path,
            'review_required': review_required,
            'priority': priority,
            'quality_level': quality_level,
            'overall_score': overall_score,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending_review' if review_required else 'approved',
            'reviewer_notes': quality_assessment.get('recommendations', [])
        }

    def _save_to_json(self, data: Dict[str, Any], output_file: str) -> None:
        """Save enhanced data to JSON file."""
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Enhanced data saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving enhanced data to {output_path}: {e}")
            raise 