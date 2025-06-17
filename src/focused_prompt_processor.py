"""
Focused Prompt Processor
Implements decomposed prompt strategy for better LLM responses and reduced truncation.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)

@dataclass
class ThemeDiscovery:
    """Container for discovered themes from Phase 1"""
    cultural: List[Dict[str, str]]
    culinary: List[Dict[str, str]]
    adventure: List[Dict[str, str]]
    entertainment: List[Dict[str, str]]
    luxury: List[Dict[str, str]]

@dataclass
class ThemeAnalysis:
    """Container for theme analysis from Phase 2"""
    seasonality: Dict[str, Dict[str, List[str]]]
    traveler_types: Dict[str, List[str]]
    pricing: Dict[str, str]
    confidence: Dict[str, float]

@dataclass
class ThemeEnhancement:
    """Container for theme enhancement from Phase 3"""
    sub_themes: Dict[str, List[str]]
    rationales: Dict[str, str]
    unique_selling_points: Dict[str, List[str]]

@dataclass
class QualityAssessment:
    """Container for quality assessment from Phase 4"""
    authenticity_scores: Dict[str, float]
    overlap_analysis: Dict[str, Any]
    overall_quality: Dict[str, Any]

class FocusedPromptProcessor:
    """Processes destinations using focused, decomposed prompts"""
    
    def __init__(self, llm_generator, config: Dict[str, Any]):
        self.llm_generator = llm_generator
        self.config = config
        self.max_parallel_requests = 5
        
    async def process_destination(self, destination: str, web_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a destination using the focused prompt strategy"""
        
        logger.info(f"🎯 Starting focused prompt processing for {destination}")
        start_time = time.time()
        
        try:
            # Phase 1: Theme Discovery (Parallel)
            logger.info(f"📋 Phase 1: Theme Discovery for {destination}")
            discovery = await self._phase1_theme_discovery(destination, web_data)
            
            # Phase 2: Theme Analysis (Sequential)
            logger.info(f"🔍 Phase 2: Theme Analysis for {destination}")
            analysis = await self._phase2_theme_analysis(destination, discovery)
            
            # Phase 3: Content Enhancement (Parallel)
            logger.info(f"✨ Phase 3: Content Enhancement for {destination}")
            enhancement = await self._phase3_content_enhancement(destination, discovery, analysis)
            
            # Phase 4: Quality Assessment (Sequential)
            logger.info(f"🎯 Phase 4: Quality Assessment for {destination}")
            quality = await self._phase4_quality_assessment(destination, discovery, analysis, enhancement)
            
            # Final Assembly
            logger.info(f"🔧 Final Assembly for {destination}")
            final_profile = self._assemble_destination_profile(
                destination, discovery, analysis, enhancement, quality
            )
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Completed focused processing for {destination} in {processing_time:.2f}s")
            
            return final_profile
            
        except Exception as e:
            logger.error(f"❌ Failed to process {destination}: {e}")
            raise
    
    async def _phase1_theme_discovery(self, destination: str, web_data: Optional[Dict[str, Any]] = None) -> ThemeDiscovery:
        """Phase 1: Discover themes across different categories (Parallel)"""
        
        # Prepare web context if available
        web_context = ""
        if web_data and web_data.get('content'):
            web_context = self._create_web_context(web_data)
        
        # Define focused discovery prompts
        prompts = {
            'cultural': self._create_cultural_discovery_prompt(destination, web_context),
            'culinary': self._create_culinary_discovery_prompt(destination, web_context),
            'adventure': self._create_adventure_discovery_prompt(destination, web_context),
            'entertainment': self._create_entertainment_discovery_prompt(destination, web_context),
            'luxury': self._create_luxury_discovery_prompt(destination, web_context)
        }
        
        # Execute prompts in parallel
        tasks = []
        for category, prompt in prompts.items():
            task = self._execute_discovery_prompt(category, prompt)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Parse results
        discovery_data = {}
        for i, (category, result) in enumerate(zip(prompts.keys(), results)):
            if isinstance(result, Exception):
                logger.warning(f"Discovery failed for {category}: {result}")
                discovery_data[category] = []
            else:
                discovery_data[category] = result
        
        return ThemeDiscovery(**discovery_data)
    
    def _create_web_context(self, web_data: Dict[str, Any]) -> str:
        """Create web context from discovered content"""
        if not web_data.get('content'):
            return ""
        
        context_parts = []
        for item in web_data['content'][:3]:  # Use top 3 sources
            title = item.get('title', '')
            content = item.get('content', '')[:500]  # Limit content length
            if title and content:
                context_parts.append(f"Source: {title}\n{content}")
        
        if context_parts:
            return f"\n\nWeb Research Context:\n{chr(10).join(context_parts)}\n\nUse this information to enhance your theme discovery."
        return ""
    
    async def _phase2_theme_analysis(self, destination: str, discovery: ThemeDiscovery) -> ThemeAnalysis:
        """Phase 2: Analyze discovered themes (Sequential)"""
        
        # Collect all themes
        all_themes = self._collect_all_themes(discovery)
        
        # Sequential analysis prompts
        seasonality = await self._analyze_seasonality(destination, all_themes)
        traveler_types = await self._analyze_traveler_types(destination, all_themes)
        pricing = await self._analyze_pricing(destination, all_themes)
        confidence = await self._analyze_confidence(destination, all_themes)
        
        return ThemeAnalysis(
            seasonality=seasonality,
            traveler_types=traveler_types,
            pricing=pricing,
            confidence=confidence
        )
    
    async def _phase3_content_enhancement(self, destination: str, discovery: ThemeDiscovery, 
                                        analysis: ThemeAnalysis) -> ThemeEnhancement:
        """Phase 3: Enhance themes with detailed content (Parallel)"""
        
        all_themes = self._collect_all_themes(discovery)
        
        # Parallel enhancement tasks
        tasks = [
            self._generate_sub_themes(destination, all_themes),
            self._generate_rationales(destination, all_themes, analysis),
            self._generate_unique_selling_points(destination, all_themes, analysis)
        ]
        
        sub_themes, rationales, usps = await asyncio.gather(*tasks)
        
        return ThemeEnhancement(
            sub_themes=sub_themes,
            rationales=rationales,
            unique_selling_points=usps
        )
    
    async def _phase4_quality_assessment(self, destination: str, discovery: ThemeDiscovery,
                                       analysis: ThemeAnalysis, enhancement: ThemeEnhancement) -> QualityAssessment:
        """Phase 4: Assess quality and validate (Sequential)"""
        
        all_themes = self._collect_all_themes(discovery)
        
        # Sequential quality checks
        authenticity = await self._check_authenticity(destination, all_themes)
        overlap = await self._detect_overlap(all_themes, enhancement)
        overall_quality = await self._assess_overall_quality(destination, all_themes, analysis, enhancement)
        
        return QualityAssessment(
            authenticity_scores=authenticity,
            overlap_analysis=overlap,
            overall_quality=overall_quality
        )
    
    def _create_cultural_discovery_prompt(self, destination: str, web_context: str = "") -> str:
        """Create focused prompt for cultural theme discovery"""
        return f"""Discover cultural experiences and themes for {destination}.

Focus ONLY on cultural aspects like:
- Historical sites and heritage
- Museums and art galleries
- Traditional festivals and events
- Local customs and traditions
- Architecture and landmarks
- Religious and spiritual sites

For each cultural theme you identify, provide:
- Theme name (2-4 words)
- Brief description (1 sentence)

Return as JSON array: [{{"theme": "name", "description": "brief description"}}]

Limit: 5-7 cultural themes maximum.
Be specific to {destination} - avoid generic themes.{web_context}"""
    
    def _create_culinary_discovery_prompt(self, destination: str, web_context: str = "") -> str:
        """Create focused prompt for culinary theme discovery"""
        return f"""Discover food and dining experiences for {destination}.

Focus ONLY on culinary aspects like:
- Local cuisine specialties
- Street food scenes
- Fine dining experiences
- Food markets and vendors
- Cooking classes and food tours
- Signature dishes and drinks

For each culinary theme you identify, provide:
- Theme name (2-4 words)
- Brief description (1 sentence)

Return as JSON array: [{{"theme": "name", "description": "brief description"}}]

Limit: 4-6 culinary themes maximum.
Be specific to {destination} - focus on what makes the food scene unique.{web_context}"""
    
    def _create_adventure_discovery_prompt(self, destination: str, web_context: str = "") -> str:
        """Create focused prompt for adventure theme discovery"""
        return f"""Discover adventure and outdoor activities for {destination}.

Focus ONLY on adventure aspects like:
- Outdoor sports and activities
- Nature exploration
- Extreme sports and thrills
- Hiking and trekking
- Water sports and activities
- Adventure tours and experiences

For each adventure theme you identify, provide:
- Theme name (2-4 words)
- Brief description (1 sentence)

Return as JSON array: [{{"theme": "name", "description": "brief description"}}]

Limit: 4-6 adventure themes maximum.
Be specific to {destination} - what unique adventures are available there?{web_context}"""
    
    def _create_entertainment_discovery_prompt(self, destination: str, web_context: str = "") -> str:
        """Create focused prompt for entertainment theme discovery"""
        return f"""Discover entertainment and nightlife for {destination}.

Focus ONLY on entertainment aspects like:
- Nightlife and clubs
- Live music and concerts
- Theater and shows
- Casinos and gaming
- Entertainment districts
- Festivals and events

For each entertainment theme you identify, provide:
- Theme name (2-4 words)
- Brief description (1 sentence)

Return as JSON array: [{{"theme": "name", "description": "brief description"}}]

Limit: 4-6 entertainment themes maximum.
Be specific to {destination} - what makes the entertainment scene special?{web_context}"""
    
    def _create_luxury_discovery_prompt(self, destination: str, web_context: str = "") -> str:
        """Create focused prompt for luxury theme discovery"""
        return f"""Discover luxury and premium experiences for {destination}.

Focus ONLY on luxury aspects like:
- High-end accommodations
- Luxury shopping
- Premium spas and wellness
- VIP experiences and services
- Exclusive tours and access
- Upscale dining and venues

For each luxury theme you identify, provide:
- Theme name (2-4 words)
- Brief description (1 sentence)

Return as JSON array: [{{"theme": "name", "description": "brief description"}}]

Limit: 3-5 luxury themes maximum.
Be specific to {destination} - what luxury experiences are uniquely available?{web_context}"""
    
    async def _execute_discovery_prompt(self, category: str, prompt: str) -> List[Dict[str, str]]:
        """Execute a discovery prompt and parse the JSON response"""
        try:
            response = await self.llm_generator.generate_response(prompt, max_tokens=600)
            
            # Try to parse JSON response
            if response.strip().startswith('['):
                themes = json.loads(response)
            else:
                # If not JSON, try to extract JSON from response
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    themes = json.loads(json_match.group())
                else:
                    logger.warning(f"Could not parse JSON from {category} discovery response")
                    return []
            
            # Validate structure
            if isinstance(themes, list) and all(isinstance(t, dict) and 'theme' in t for t in themes):
                logger.info(f"✅ Discovered {len(themes)} {category} themes")
                return themes
            else:
                logger.warning(f"Invalid theme structure for {category}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to execute {category} discovery: {e}")
            return []
    
    def _collect_all_themes(self, discovery: ThemeDiscovery) -> List[str]:
        """Collect all theme names from discovery results"""
        all_themes = []
        for category_themes in [discovery.cultural, discovery.culinary, discovery.adventure, 
                              discovery.entertainment, discovery.luxury]:
            for theme_data in category_themes:
                if 'theme' in theme_data:
                    all_themes.append(theme_data['theme'])
        return all_themes
    
    async def _analyze_seasonality(self, destination: str, themes: List[str]) -> Dict[str, Dict[str, List[str]]]:
        """Analyze seasonality for all themes"""
        prompt = f"""Analyze the best and worst seasons for these activities/themes in {destination}:

Themes: {', '.join(themes)}

For each theme, determine:
- Peak months (best time to experience this)
- Avoid months (worst time due to weather, crowds, closures, etc.)

Return as JSON object:
{{
  "theme_name": {{
    "peak": ["month1", "month2", ...],
    "avoid": ["month1", "month2", ...]
  }}
}}

Consider {destination}'s climate, tourist seasons, and activity-specific factors.
Use full month names (January, February, etc.)."""

        try:
            response = await self.llm_generator.generate_response(prompt, max_tokens=800)
            return json.loads(response) if response.strip().startswith('{') else {}
        except Exception as e:
            logger.error(f"Seasonality analysis failed: {e}")
            return {}
    
    async def _analyze_traveler_types(self, destination: str, themes: List[str]) -> Dict[str, List[str]]:
        """Analyze target traveler types for themes"""
        prompt = f"""Determine the best traveler types for these themes in {destination}:

Themes: {', '.join(themes)}

For each theme, select the most suitable traveler types from:
- solo (solo travelers)
- couple (romantic couples)
- family (families with children)
- group (friend groups, tour groups)

Return as JSON object:
{{
  "theme_name": ["traveler_type1", "traveler_type2", ...]
}}

Consider the nature of each activity and who would most enjoy it."""

        try:
            response = await self.llm_generator.generate_response(prompt, max_tokens=600)
            return json.loads(response) if response.strip().startswith('{') else {}
        except Exception as e:
            logger.error(f"Traveler type analysis failed: {e}")
            return {}
    
    async def _analyze_pricing(self, destination: str, themes: List[str]) -> Dict[str, str]:
        """Analyze pricing levels for themes"""
        prompt = f"""Determine the typical price level for these themes in {destination}:

Themes: {', '.join(themes)}

For each theme, assign ONE price category:
- budget (affordable, under $50 per person)
- mid (moderate pricing, $50-200 per person)
- luxury (premium pricing, $200+ per person)

Return as JSON object:
{{
  "theme_name": "price_category"
}}

Consider typical costs for these experiences in {destination}."""

        try:
            response = await self.llm_generator.generate_response(prompt, max_tokens=400)
            return json.loads(response) if response.strip().startswith('{') else {}
        except Exception as e:
            logger.error(f"Pricing analysis failed: {e}")
            return {}
    
    async def _analyze_confidence(self, destination: str, themes: List[str]) -> Dict[str, float]:
        """Analyze confidence scores for themes"""
        prompt = f"""Rate the confidence level (0.0 to 1.0) for how well each theme represents {destination}:

Themes: {', '.join(themes)}

Consider:
- How iconic/representative is this theme for {destination}?
- How accessible/available is this experience?
- How unique is this to {destination} vs generic?

Return as JSON object:
{{
  "theme_name": 0.85
}}

Use decimal values between 0.0 (not confident) and 1.0 (very confident)."""

        try:
            response = await self.llm_generator.generate_response(prompt, max_tokens=500)
            return json.loads(response) if response.strip().startswith('{') else {}
        except Exception as e:
            logger.error(f"Confidence analysis failed: {e}")
            return {}
    
    async def _generate_sub_themes(self, destination: str, themes: List[str]) -> Dict[str, List[str]]:
        """Generate sub-themes for each main theme"""
        prompt = f"""Generate 3-4 specific sub-themes for each main theme in {destination}:

Main themes: {', '.join(themes)}

For each main theme, create specific sub-activities or aspects.

Return as JSON object:
{{
  "main_theme": ["sub_theme1", "sub_theme2", "sub_theme3"]
}}

Make sub-themes specific and actionable."""

        try:
            response = await self.llm_generator.generate_response(prompt, max_tokens=700)
            return json.loads(response) if response.strip().startswith('{') else {}
        except Exception as e:
            logger.error(f"Sub-theme generation failed: {e}")
            return {}
    
    async def _generate_rationales(self, destination: str, themes: List[str], 
                                 analysis: ThemeAnalysis) -> Dict[str, str]:
        """Generate compelling rationales for each theme"""
        prompt = f"""Create compelling 2-3 sentence rationales explaining why each theme is appealing in {destination}:

Themes: {', '.join(themes)}

For each theme, write a rationale that:
- Explains why this experience is special in {destination}
- Highlights what makes it appealing to travelers
- Mentions specific aspects that set it apart

Return as JSON object:
{{
  "theme_name": "compelling rationale text"
}}

Keep each rationale concise but persuasive."""

        try:
            response = await self.llm_generator.generate_response(prompt, max_tokens=800)
            return json.loads(response) if response.strip().startswith('{') else {}
        except Exception as e:
            logger.error(f"Rationale generation failed: {e}")
            return {}
    
    async def _generate_unique_selling_points(self, destination: str, themes: List[str], 
                                            analysis: ThemeAnalysis) -> Dict[str, List[str]]:
        """Generate unique selling points for each theme"""
        prompt = f"""Identify 3-4 unique selling points for each theme in {destination}:

Themes: {', '.join(themes)}

For each theme, list what makes it distinctive and valuable:
- What's unique about this experience in {destination}?
- What competitive advantages does it offer?
- What memorable aspects will travelers remember?

Return as JSON object:
{{
  "theme_name": ["selling_point1", "selling_point2", "selling_point3"]
}}

Focus on distinctive, memorable value propositions."""

        try:
            response = await self.llm_generator.generate_response(prompt, max_tokens=600)
            return json.loads(response) if response.strip().startswith('{') else {}
        except Exception as e:
            logger.error(f"USP generation failed: {e}")
            return {}
    
    async def _check_authenticity(self, destination: str, themes: List[str]) -> Dict[str, float]:
        """Check authenticity of themes for the destination"""
        prompt = f"""Rate the authenticity (0.0 to 1.0) of each theme for {destination}:

Themes: {', '.join(themes)}

Consider:
- Is this theme genuinely representative of {destination}?
- Does it reflect real local culture/offerings?
- Is it a tourist trap or authentic experience?

Return as JSON object:
{{
  "theme_name": 0.90
}}

Use decimal values between 0.0 (inauthentic) and 1.0 (very authentic)."""

        try:
            response = await self.llm_generator.generate_response(prompt, max_tokens=600)
            return json.loads(response) if response.strip().startswith('{') else {}
        except Exception as e:
            logger.error(f"Authenticity check failed: {e}")
            return {}
    
    async def _detect_overlap(self, themes: List[str], enhancement: ThemeEnhancement) -> Dict[str, Any]:
        """Detect overlapping themes and suggest consolidation"""
        prompt = f"""Analyze these themes for overlap and suggest consolidations:

Themes: {', '.join(themes)}

Identify:
- Which themes overlap significantly?
- Which themes could be combined?
- Which themes are too similar?

Return as JSON object:
{{
  "overlapping_groups": [
    {{
      "themes": ["theme1", "theme2"],
      "overlap_reason": "reason",
      "suggestion": "consolidation suggestion"
    }}
  ],
  "unique_themes": ["theme1", "theme2", ...]
}}"""

        try:
            response = await self.llm_generator.generate_response(prompt, max_tokens=500)
            return json.loads(response) if response.strip().startswith('{') else {}
        except Exception as e:
            logger.error(f"Overlap detection failed: {e}")
            return {}
    
    async def _assess_overall_quality(self, destination: str, themes: List[str], 
                                    analysis: ThemeAnalysis, enhancement: ThemeEnhancement) -> Dict[str, Any]:
        """Assess overall quality of the destination profile"""
        prompt = f"""Assess the overall quality of this destination profile for {destination}:

Themes: {', '.join(themes)}
Total theme count: {len(themes)}

Rate (0.0 to 1.0):
- Theme diversity (variety across categories)
- Theme quality (how compelling/interesting)
- Destination coverage (how well it represents {destination})
- Overall completeness

Return as JSON object:
{{
  "diversity_score": 0.85,
  "quality_score": 0.90,
  "coverage_score": 0.80,
  "completeness_score": 0.75,
  "overall_score": 0.82,
  "recommendations": ["suggestion1", "suggestion2"]
}}"""

        try:
            response = await self.llm_generator.generate_response(prompt, max_tokens=400)
            return json.loads(response) if response.strip().startswith('{') else {}
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return {}
    
    def _assemble_destination_profile(self, destination: str, discovery: ThemeDiscovery,
                                    analysis: ThemeAnalysis, enhancement: ThemeEnhancement,
                                    quality: QualityAssessment) -> Dict[str, Any]:
        """Assemble all components into final destination profile"""
        
        # Collect all themes with their data
        affinities = []
        
        # Process each category
        for category, themes in [
            ('culture', discovery.cultural),
            ('food', discovery.culinary),
            ('adventure', discovery.adventure),
            ('entertainment', discovery.entertainment),
            ('luxury', discovery.luxury)
        ]:
            for theme_data in themes:
                theme_name = theme_data.get('theme', '')
                if not theme_name:
                    continue
                
                affinity = {
                    "category": category,
                    "theme": theme_name,
                    "sub_themes": enhancement.sub_themes.get(theme_name, []),
                    "confidence": analysis.confidence.get(theme_name, 0.7),
                    "seasonality": analysis.seasonality.get(theme_name, {"peak": [], "avoid": []}),
                    "traveler_types": analysis.traveler_types.get(theme_name, ["couple"]),
                    "price_point": analysis.pricing.get(theme_name, "mid"),
                    "rationale": enhancement.rationales.get(theme_name, f"Experience {theme_name} in {destination}"),
                    "unique_selling_points": enhancement.unique_selling_points.get(theme_name, []),
                    "authenticity_score": quality.authenticity_scores.get(theme_name, 0.8)
                }
                affinities.append(affinity)
        
        # Create final profile
        profile = {
            "destination": destination,
            "affinities": affinities,
            "processing_metadata": {
                "total_themes": len(affinities),
                "categories_covered": len(set(a['category'] for a in affinities)),
                "average_confidence": sum(a['confidence'] for a in affinities) / len(affinities) if affinities else 0,
                "quality_assessment": quality.overall_quality,
                "overlap_analysis": quality.overlap_analysis,
                "processing_method": "focused_prompts"
            }
        }
        
        logger.info(f"✅ Assembled profile for {destination}: {len(affinities)} themes across {profile['processing_metadata']['categories_covered']} categories")
        
        return profile 