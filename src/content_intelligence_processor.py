"""
Content Intelligence Processor
Extracts enhanced content attributes like iconic landmarks, practical intelligence, 
neighborhood insights, and content discovery metadata from web sources.
"""

import logging
import re
import json
from typing import Dict, List, Any, Optional
from src.schemas import (
    IconicLandmarks, PracticalTravelIntelligence, 
    NeighborhoodInsights, ContentDiscoveryIntelligence,
    PageContent
)

logger = logging.getLogger(__name__)

class ContentIntelligenceProcessor:
    """Processes web content to extract enhanced content intelligence attributes"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Travel authority domains for source validation
        self.travel_authority_domains = [
            'lonelyplanet.com', 'timeout.com', 'fodors.com', 'frommers.com',
            'ricksteves.com', 'tripadvisor.com', 'expedia.com', 'booking.com',
            'airbnb.com', 'viator.com', 'getyourguide.com', 'culture.org',
            'wikipedia.org', 'nationalgeographic.com', 'cntraveler.com',
            'travelandleisure.com', 'afar.com', 'roughguides.com'
        ]
        
        # Landmark indicator patterns
        self.landmark_patterns = [
            r'iconic\s+(?:landmark|attraction|monument|building)',
            r'famous\s+(?:for|landmark|attraction|monument)',
            r'must-see\s+(?:attraction|landmark|sight)',
            r'historic\s+(?:landmark|monument|site|building)',
            r'observation\s+(?:tower|deck|platform)',
            r'marketplace\s+known\s+for',
            r'cathedral|church|temple|mosque',
            r'museum\s+(?:featuring|known for|famous)',
            r'bridge\s+(?:spanning|connecting|famous)',
            r'square\s+(?:surrounded|featuring|known)',
        ]
        
        # Neighborhood indicator patterns
        self.neighborhood_patterns = [
            r'neighborhood\s+(?:known|famous|characterized)\s+(?:for|by)',
            r'district\s+(?:known|famous|characterized)\s+(?:for|by)',
            r'area\s+(?:known|famous|characterized)\s+(?:for|by)',
            r'quarter\s+(?:known|famous|characterized)\s+(?:for|by)',
            r'(?:best|top)\s+(?:areas?|neighborhoods?)\s+(?:to|for)',
            r'stay\s+in\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'vibrant\s+(?:neighborhood|district|area)',
            r'trendy\s+(?:neighborhood|district|area)',
        ]
        
        # Cost and practical patterns
        self.practical_patterns = [
            r'\$\d+(?:-\$\d+)?\s*(?:per|each|for)',
            r'(?:costs?|prices?)\s+(?:range|start)\s+(?:from\s+)?\$\d+',
            r'book\s+(?:\d+\s+)?(?:weeks?|months?|days?)\s+(?:in\s+)?advance',
            r'best\s+time\s+(?:to\s+visit|for)',
            r'avoid\s+(?:visiting\s+)?(?:during|in)\s+[A-Z][a-z]+',
            r'save\s+money\s+by',
            r'free\s+(?:admission|entry|access)',
            r'discounts?\s+(?:available|offered)',
        ]
    
    async def extract_content_intelligence(self, theme: str, destination: str, 
                                         web_pages: List[PageContent] = None,
                                         llm_generator=None) -> Dict[str, Any]:
        """Extract all content intelligence attributes for a theme"""
        
        logger.info(f"Extracting content intelligence for {theme} in {destination}")
        
        # Collect web content
        web_content = ""
        high_quality_sources = []
        
        if web_pages:
            for page in web_pages:
                web_content += f"\n{page.title}\n{page.content}"
                
                # Check if source is from travel authority
                domain = self._extract_domain(page.url)
                if any(auth_domain in domain.lower() for auth_domain in self.travel_authority_domains):
                    high_quality_sources.append(page.url)
        
        # Extract each intelligence type
        iconic_landmarks = await self._extract_iconic_landmarks(
            theme, destination, web_content, llm_generator
        )
        
        practical_intelligence = await self._extract_practical_intelligence(
            theme, destination, web_content, llm_generator
        )
        
        neighborhood_insights = await self._extract_neighborhood_insights(
            theme, destination, web_content, llm_generator
        )
        
        content_discovery = self._extract_content_discovery_intelligence(
            web_content, high_quality_sources
        )
        
        return {
            'iconic_landmarks': iconic_landmarks,
            'practical_travel_intelligence': practical_intelligence,
            'neighborhood_insights': neighborhood_insights,
            'content_discovery_intelligence': content_discovery
        }
    
    async def _extract_iconic_landmarks(self, theme: str, destination: str, 
                                      web_content: str, llm_generator=None) -> Dict[str, Any]:
        """Extract specific landmarks and their compelling descriptions"""
        
        # Pattern-based extraction first
        landmark_mentions = []
        descriptions = {}
        
        # Find landmark patterns in text
        for pattern in self.landmark_patterns:
            matches = re.finditer(pattern, web_content, re.IGNORECASE)
            for match in matches:
                # Extract surrounding context
                start = max(0, match.start() - 100)
                end = min(len(web_content), match.end() + 200)
                context = web_content[start:end].strip()
                landmark_mentions.append(context)
        
        # Use LLM to enhance extraction if available
        if llm_generator and landmark_mentions:
            prompt = self._create_landmark_extraction_prompt(
                theme, destination, landmark_mentions[:5]  # Top 5 mentions
            )
            
            try:
                response = await llm_generator.generate_response(prompt, max_tokens=800)
                llm_data = self._parse_landmark_response(response)
                
                return {
                    'specific_locations': llm_data.get('landmarks', []),
                    'landmark_descriptions': llm_data.get('descriptions', {}),
                    'what_makes_them_special': llm_data.get('special_features', []),
                    'landmark_categories': llm_data.get('categories', {})
                }
            except Exception as e:
                logger.warning(f"LLM landmark extraction failed: {e}")
        
        # Fallback to pattern-based extraction
        return {
            'specific_locations': self._extract_landmark_names(landmark_mentions),
            'landmark_descriptions': self._extract_descriptions(landmark_mentions),
            'what_makes_them_special': self._extract_special_features(landmark_mentions),
            'landmark_categories': {}
        }
    
    async def _extract_practical_intelligence(self, theme: str, destination: str,
                                            web_content: str, llm_generator=None) -> Dict[str, Any]:
        """Extract factual travel planning information"""
        
        # Pattern-based extraction
        cost_mentions = []
        timing_mentions = []
        booking_mentions = []
        
        for pattern in self.practical_patterns:
            matches = re.finditer(pattern, web_content, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(web_content), match.end() + 100)
                context = web_content[start:end].strip()
                
                if any(word in pattern for word in ['cost', 'price', '$']):
                    cost_mentions.append(context)
                elif any(word in pattern for word in ['book', 'advance', 'time']):
                    timing_mentions.append(context)
                elif 'book' in pattern:
                    booking_mentions.append(context)
        
        # Use LLM for structured extraction if available
        if llm_generator and (cost_mentions or timing_mentions):
            prompt = self._create_practical_extraction_prompt(
                theme, destination, cost_mentions[:3], timing_mentions[:3]
            )
            
            try:
                response = await llm_generator.generate_response(prompt, max_tokens=600)
                llm_data = self._parse_practical_response(response)
                
                return {
                    'specific_costs': llm_data.get('costs', {}),
                    'timing_intelligence': llm_data.get('timing', {}),
                    'booking_specifics': llm_data.get('booking', []),
                    'practical_tips': llm_data.get('tips', [])
                }
            except Exception as e:
                logger.warning(f"LLM practical extraction failed: {e}")
        
        # Fallback extraction
        return {
            'specific_costs': self._extract_cost_ranges(cost_mentions),
            'timing_intelligence': self._extract_timing_info(timing_mentions),
            'booking_specifics': self._extract_booking_info(booking_mentions),
            'practical_tips': []
        }
    
    async def _extract_neighborhood_insights(self, theme: str, destination: str,
                                           web_content: str, llm_generator=None) -> Dict[str, Any]:
        """Extract area-specific intelligence"""
        
        # Pattern-based neighborhood extraction
        neighborhood_mentions = []
        
        for pattern in self.neighborhood_patterns:
            matches = re.finditer(pattern, web_content, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 80)
                end = min(len(web_content), match.end() + 150)
                context = web_content[start:end].strip()
                neighborhood_mentions.append(context)
        
        # Use LLM for structured extraction
        if llm_generator and neighborhood_mentions:
            prompt = self._create_neighborhood_extraction_prompt(
                theme, destination, neighborhood_mentions[:4]
            )
            
            try:
                response = await llm_generator.generate_response(prompt, max_tokens=700)
                llm_data = self._parse_neighborhood_response(response)
                
                return {
                    'neighborhood_names': llm_data.get('neighborhoods', []),
                    'area_personalities': llm_data.get('personalities', {}),
                    'neighborhood_specialties': llm_data.get('specialties', {}),
                    'stay_recommendations': llm_data.get('stay_advice', {})
                }
            except Exception as e:
                logger.warning(f"LLM neighborhood extraction failed: {e}")
        
        # Fallback extraction
        return {
            'neighborhood_names': self._extract_neighborhood_names(neighborhood_mentions),
            'area_personalities': {},
            'neighborhood_specialties': {},
            'stay_recommendations': {}
        }
    
    def _extract_content_discovery_intelligence(self, web_content: str, 
                                              high_quality_sources: List[str]) -> Dict[str, Any]:
        """Extract source and extraction metadata"""
        
        # Extract compelling phrases (marketing language)
        compelling_phrases = self._extract_compelling_phrases(web_content)
        
        # Extract content themes
        content_themes = self._extract_content_themes(web_content)
        
        # Validate authority sources
        authority_validation = {
            'total_sources': len(high_quality_sources),
            'authority_domains': list(set([
                self._extract_domain(url) for url in high_quality_sources
            ])),
            'content_quality_score': min(1.0, len(high_quality_sources) / 3.0)
        }
        
        return {
            'high_quality_sources': high_quality_sources,
            'extracted_phrases': compelling_phrases,
            'content_themes': content_themes,
            'authority_validation': authority_validation
        }
    
    def _create_landmark_extraction_prompt(self, theme: str, destination: str, 
                                         mentions: List[str]) -> str:
        """Create prompt for landmark extraction"""
        context = "\n".join(mentions)
        
        return f"""
Extract specific landmarks and attractions for the theme "{theme}" in {destination}.

Context from sources:
{context}

Return JSON with this structure:
{{
    "landmarks": ["specific landmark names"],
    "descriptions": {{"landmark": "compelling description from sources"}},
    "special_features": ["what makes each landmark unique"],
    "categories": {{"landmark": "category like museum, monument, market"}}
}}

Focus on:
- Extract exact landmark names mentioned
- Use actual descriptive language from sources, not created descriptions  
- Identify what makes each landmark special/unique
- Categorize landmarks by type

JSON:"""
    
    def _create_practical_extraction_prompt(self, theme: str, destination: str,
                                          cost_mentions: List[str], timing_mentions: List[str]) -> str:
        """Create prompt for practical information extraction"""
        
        cost_context = "\n".join(cost_mentions) if cost_mentions else "No cost information found"
        timing_context = "\n".join(timing_mentions) if timing_mentions else "No timing information found"
        
        return f"""
Extract practical travel information for "{theme}" in {destination}.

Cost information:
{cost_context}

Timing information:
{timing_context}

Return JSON with this structure:
{{
    "costs": {{"category": "specific price range found"}},
    "timing": {{"season": ["timing advice"], "booking": ["booking timing"]}},
    "booking": ["specific booking advice"],
    "tips": ["money-saving and timing tips"]
}}

Focus on:
- Extract actual price ranges mentioned (with currency)
- Extract specific timing advice (when to visit, book, avoid)
- Extract factual booking information
- Extract money-saving tips mentioned

JSON:"""
    
    def _create_neighborhood_extraction_prompt(self, theme: str, destination: str,
                                             mentions: List[str]) -> str:
        """Create prompt for neighborhood extraction"""
        context = "\n".join(mentions)
        
        return f"""
Extract neighborhood information for "{theme}" in {destination}.

Context from sources:
{context}

Return JSON with this structure:
{{
    "neighborhoods": ["specific neighborhood names"],
    "personalities": {{"neighborhood": "character description from sources"}},
    "specialties": {{"neighborhood": ["what it's known for"]}},
    "stay_advice": {{"neighborhood": "accommodation advice"}}
}}

Focus on:
- Extract specific neighborhood/area names mentioned
- Use actual personality descriptions from sources
- Extract what each area is known for
- Extract accommodation/stay advice

JSON:"""
    
    def _parse_landmark_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for landmark data"""
        try:
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Failed to parse landmark JSON: {e}")
        
        return {'landmarks': [], 'descriptions': {}, 'special_features': [], 'categories': {}}
    
    def _parse_practical_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for practical data"""
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Failed to parse practical JSON: {e}")
        
        return {'costs': {}, 'timing': {}, 'booking': [], 'tips': []}
    
    def _parse_neighborhood_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for neighborhood data"""
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Failed to parse neighborhood JSON: {e}")
        
        return {'neighborhoods': [], 'personalities': {}, 'specialties': {}, 'stay_advice': {}}
    
    def _extract_landmark_names(self, mentions: List[str]) -> List[str]:
        """Extract landmark names from mentions"""
        landmarks = []
        
        # Common landmark name patterns
        patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Market|Tower|Bridge|Cathedral|Museum|Palace|Square)',
            r'(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:is|features|offers)',
        ]
        
        for mention in mentions:
            for pattern in patterns:
                matches = re.finditer(pattern, mention, re.IGNORECASE)
                for match in matches:
                    landmark_name = match.group(1).strip()
                    if len(landmark_name) > 3 and landmark_name not in landmarks:
                        landmarks.append(landmark_name)
        
        return landmarks[:5]  # Top 5 landmarks
    
    def _extract_descriptions(self, mentions: List[str]) -> Dict[str, str]:
        """Extract descriptions from mentions"""
        descriptions = {}
        
        for mention in mentions:
            # Look for descriptive phrases
            sentences = mention.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ['known for', 'famous for', 'featuring']):
                    # Extract potential landmark name and description
                    parts = sentence.split(' known for ')
                    if len(parts) == 2:
                        landmark = parts[0].strip().split()[-2:]  # Last 2 words as landmark
                        desc = parts[1].strip()
                        landmark_name = ' '.join(landmark)
                        if len(landmark_name) > 3:
                            descriptions[landmark_name] = desc
        
        return descriptions
    
    def _extract_special_features(self, mentions: List[str]) -> List[str]:
        """Extract special features from mentions"""
        features = []
        
        feature_patterns = [
            r'famous\s+for\s+([^.]+)',
            r'known\s+for\s+([^.]+)', 
            r'featuring\s+([^.]+)',
            r'unique\s+([^.]+)',
        ]
        
        for mention in mentions:
            for pattern in feature_patterns:
                matches = re.finditer(pattern, mention, re.IGNORECASE)
                for match in matches:
                    feature = match.group(1).strip()
                    if len(feature) > 5 and feature not in features:
                        features.append(feature)
        
        return features[:8]  # Top 8 features
    
    def _extract_cost_ranges(self, mentions: List[str]) -> Dict[str, str]:
        """Extract cost ranges from mentions"""
        costs = {}
        
        for mention in mentions:
            # Look for price patterns
            price_matches = re.finditer(r'\$(\d+)(?:-\$?(\d+))?', mention)
            for match in price_matches:
                if match:
                    low = match.group(1)
                    high = match.group(2) if match.group(2) else low
                    costs['general'] = f"${low}-${high}"
                    break
        
        return costs
    
    def _extract_timing_info(self, mentions: List[str]) -> Dict[str, List[str]]:
        """Extract timing information from mentions"""
        timing = {}
        
        for mention in mentions:
            if 'best time' in mention.lower():
                timing['best_time'] = [mention.strip()]
            elif 'avoid' in mention.lower():
                timing['avoid'] = [mention.strip()]
            elif 'book' in mention.lower() and 'advance' in mention.lower():
                timing['booking'] = [mention.strip()]
        
        return timing
    
    def _extract_booking_info(self, mentions: List[str]) -> List[str]:
        """Extract booking information from mentions"""
        booking_info = []
        
        for mention in mentions:
            if any(word in mention.lower() for word in ['book', 'reserve', 'advance']):
                booking_info.append(mention.strip())
        
        return booking_info[:3]  # Top 3 booking tips
    
    def _extract_neighborhood_names(self, mentions: List[str]) -> List[str]:
        """Extract neighborhood names from mentions"""
        neighborhoods = []
        
        # Patterns for neighborhood names
        patterns = [
            r'(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:neighborhood|district|area|quarter)',
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for mention in mentions:
            for pattern in patterns:
                matches = re.finditer(pattern, mention)
                for match in matches:
                    name = match.group(1).strip()
                    if len(name) > 3 and name not in neighborhoods:
                        neighborhoods.append(name)
        
        return neighborhoods[:6]  # Top 6 neighborhoods
    
    def _extract_compelling_phrases(self, web_content: str) -> List[str]:
        """Extract compelling marketing language"""
        phrases = []
        
        # Patterns for compelling language
        patterns = [
            r'bustling\s+[^.]+',
            r'vibrant\s+[^.]+',
            r'iconic\s+[^.]+',
            r'stunning\s+[^.]+',
            r'famous\s+for\s+[^.]+',
            r'known\s+for\s+[^.]+',
            r'renowned\s+[^.]+',
            r'spectacular\s+[^.]+',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, web_content, re.IGNORECASE)
            for match in matches:
                phrase = match.group(0).strip()
                if len(phrase) > 10 and phrase not in phrases:
                    phrases.append(phrase)
        
        return phrases[:10]  # Top 10 compelling phrases
    
    def _extract_content_themes(self, web_content: str) -> List[str]:
        """Extract content patterns"""
        themes = []
        
        # Common content themes in travel writing
        theme_patterns = [
            r'(?:cultural|historic|artistic|religious)\s+(?:heritage|significance|importance)',
            r'(?:culinary|food|dining)\s+(?:scene|culture|experience)',
            r'(?:outdoor|adventure|recreational)\s+(?:activities|experiences)',
            r'(?:nightlife|entertainment|shopping)\s+(?:scene|options)',
            r'(?:luxury|budget|family-friendly)\s+(?:options|experiences)',
        ]
        
        for pattern in theme_patterns:
            if re.search(pattern, web_content, re.IGNORECASE):
                theme_name = pattern.replace(r'(?:', '').replace(r')\s+(?:', ' ').replace(r')', '')
                themes.append(theme_name)
        
        return themes
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return url 