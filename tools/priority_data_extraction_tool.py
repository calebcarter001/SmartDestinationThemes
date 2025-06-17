import logging
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

class PriorityDataExtractor:
    """
    Extracts structured priority data about safety, accessibility, visa requirements,
    health advisories, and other critical travel information from text content.
    Uses LLM-based extraction with confidence scoring and data completeness assessment.
    """
    def __init__(self, llm=None, config: dict = None):
        self.logger = logging.getLogger("app.priority_extractor")
        self.llm = llm
        self.config = config or {}
        
        # Data completeness weights
        self.completeness_weights = {
            'safety_concerns': 0.25,
            'visa_requirements': 0.20,
            'health_advisories': 0.20,
            'accessibility_features': 0.15,
            'transportation_info': 0.10,
            'emergency_contacts': 0.10
        }
        
        # Safety keyword patterns
        self.safety_patterns = {
            'crime': ['theft', 'robbery', 'pickpocket', 'scam', 'fraud', 'crime', 'mugging'],
            'natural': ['earthquake', 'tsunami', 'hurricane', 'flood', 'volcano', 'wildfire'],
            'political': ['protest', 'demonstration', 'unrest', 'conflict', 'tension'],
            'health': ['outbreak', 'disease', 'epidemic', 'contamination', 'water safety'],
            'transport': ['road safety', 'traffic', 'accident', 'transportation risk']
        }
        
        # Accessibility indicators
        self.accessibility_indicators = {
            'wheelchair': ['wheelchair', 'accessible', 'disability', 'ramp', 'elevator'],
            'visual': ['braille', 'audio guide', 'visually impaired', 'blind'],
            'hearing': ['sign language', 'hearing impaired', 'deaf', 'audio loop'],
            'mobility': ['mobility aid', 'walking difficulty', 'physical disability']
        }
        
        # Visa requirement keywords
        self.visa_keywords = {
            'visa_free': ['visa free', 'no visa required', 'visa waiver', 'visa exempt'],
            'visa_required': ['visa required', 'visa necessary', 'must obtain visa'],
            'visa_on_arrival': ['visa on arrival', 'arrival visa', 'VOA'],
            'eVisa': ['electronic visa', 'e-visa', 'online visa', 'digital visa']
        }
        
        # Health advisory patterns
        self.health_patterns = {
            'vaccination': ['vaccination', 'vaccine', 'immunization', 'shot', 'hepatitis', 'yellow fever'],
            'medication': ['malaria', 'prophylaxis', 'medication', 'prescription'],
            'water': ['water safety', 'bottled water', 'tap water', 'water quality'],
            'food': ['food safety', 'street food', 'foodborne illness']
        }

    def extract_all_priority_data(self, content: str, url: str, destination: str = "") -> dict:
        """
        Extracts comprehensive priority data from content using multiple extraction methods.
        
        Args:
            content: Text content to analyze
            url: Source URL for credibility assessment
            destination: Destination name for context
            
        Returns:
            Dictionary with extracted priority data and quality metrics
        """
        self.logger.info(f"Extracting priority data from {url}")
        
        if not content or len(content.strip()) < 50:
            self.logger.warning(f"Content too short for meaningful extraction: {len(content)} chars")
            return self._empty_extraction(url)
        
        # Extract different types of priority data
        safety_data = self._extract_safety_concerns(content, url)
        visa_data = self._extract_visa_requirements(content, destination)
        health_data = self._extract_health_advisories(content)
        accessibility_data = self._extract_accessibility_features(content)
        transport_data = self._extract_transportation_info(content)
        emergency_data = self._extract_emergency_contacts(content)
        
        # Calculate overall confidence and completeness
        extraction_confidence = self._calculate_extraction_confidence([
            safety_data, visa_data, health_data, accessibility_data, transport_data, emergency_data
        ])
        
        data_completeness = self._calculate_data_completeness({
            'safety_concerns': safety_data,
            'visa_requirements': visa_data,
            'health_advisories': health_data,
            'accessibility_features': accessibility_data,
            'transportation_info': transport_data,
            'emergency_contacts': emergency_data
        })
        
        # Use LLM for additional structured extraction if available
        llm_enhanced_data = {}
        if self.llm and extraction_confidence < 0.7:
            llm_enhanced_data = self._llm_enhanced_extraction(content, destination)
        
        result = {
            "extraction_confidence": round(extraction_confidence, 3),
            "data_completeness": round(data_completeness, 3),
            "source_url": url,
            "extracted_at": datetime.now().isoformat(),
            "content_length": len(content),
            
            # Priority data categories
            "safety_concerns": safety_data.get('items', []),
            "safety_score": safety_data.get('confidence', 0.0),
            
            "visa_requirements": visa_data.get('info', "No information found."),
            "visa_confidence": visa_data.get('confidence', 0.0),
            
            "health_advisories": health_data.get('items', []),
            "health_score": health_data.get('confidence', 0.0),
            
            "accessibility_features": accessibility_data.get('items', []),
            "accessibility_score": accessibility_data.get('confidence', 0.0),
            
            "transportation_info": transport_data.get('items', []),
            "transport_score": transport_data.get('confidence', 0.0),
            
            "emergency_contacts": emergency_data.get('items', []),
            "emergency_score": emergency_data.get('confidence', 0.0),
            
            # LLM enhancement (if used)
            "llm_enhanced": llm_enhanced_data,
            "extraction_method": "hybrid" if llm_enhanced_data else "pattern_based"
        }
        
        self.logger.info(f"Extraction complete. Confidence: {extraction_confidence:.3f}, Completeness: {data_completeness:.3f}")
        return result
    
    def _extract_safety_concerns(self, content: str, url: str) -> dict:
        """Extract safety-related information from content."""
        content_lower = content.lower()
        safety_items = []
        confidence_scores = []
        
        # Check for safety patterns
        for category, keywords in self.safety_patterns.items():
            found_items = []
            for keyword in keywords:
                if keyword in content_lower:
                    # Extract surrounding context
                    context = self._extract_context(content, keyword, 100)
                    if context and len(context.strip()) > 20:
                        found_items.append({
                            'category': category,
                            'keyword': keyword,
                            'context': context.strip(),
                            'severity': self._assess_safety_severity(context)
                        })
            
            if found_items:
                safety_items.extend(found_items)
                confidence_scores.append(0.8)  # High confidence for keyword matches
        
        # Assess source credibility
        source_credibility = self._assess_source_credibility(url)
        
        # Calculate overall confidence
        base_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        adjusted_confidence = min(1.0, base_confidence * source_credibility)
        
        return {
            'items': safety_items,
            'confidence': adjusted_confidence,
            'source_credibility': source_credibility
        }
    
    def _extract_visa_requirements(self, content: str, destination: str) -> dict:
        """Extract visa requirement information."""
        content_lower = content.lower()
        visa_info = "No information found."
        confidence = 0.0
        
        # Look for visa-related information
        for category, keywords in self.visa_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    context = self._extract_context(content, keyword, 200)
                    if context:
                        visa_info = context.strip()
                        confidence = 0.8
                        break
            if confidence > 0:
                break
        
        # Look for country-specific visa information
        if destination and confidence < 0.5:
            destination_lower = destination.lower()
            visa_patterns = [
                f"visa.*{destination_lower}",
                f"{destination_lower}.*visa",
                f"entry.*{destination_lower}",
                f"{destination_lower}.*entry"
            ]
            
            for pattern in visa_patterns:
                if re.search(pattern, content_lower):
                    context = self._extract_context(content, destination, 150)
                    if context and 'visa' in context.lower():
                        visa_info = context.strip()
                        confidence = 0.6
                        break
        
        return {
            'info': visa_info,
            'confidence': confidence
        }
    
    def _extract_health_advisories(self, content: str) -> dict:
        """Extract health and medical advisory information."""
        content_lower = content.lower()
        health_items = []
        confidence_scores = []
        
        for category, keywords in self.health_patterns.items():
            found_items = []
            for keyword in keywords:
                if keyword in content_lower:
                    context = self._extract_context(content, keyword, 120)
                    if context and len(context.strip()) > 15:
                        found_items.append({
                            'category': category,
                            'advisory': context.strip(),
                            'urgency': self._assess_health_urgency(context)
                        })
            
            if found_items:
                health_items.extend(found_items)
                confidence_scores.append(0.7)
        
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return {
            'items': health_items,
            'confidence': overall_confidence
        }
    
    def _extract_accessibility_features(self, content: str) -> dict:
        """Extract accessibility-related information."""
        content_lower = content.lower()
        accessibility_items = []
        confidence_scores = []
        
        for category, keywords in self.accessibility_indicators.items():
            found_items = []
            for keyword in keywords:
                if keyword in content_lower:
                    context = self._extract_context(content, keyword, 100)
                    if context:
                        found_items.append({
                            'category': category,
                            'feature': context.strip(),
                            'availability': self._assess_accessibility_availability(context)
                        })
            
            if found_items:
                accessibility_items.extend(found_items)
                confidence_scores.append(0.8)
        
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return {
            'items': accessibility_items,
            'confidence': overall_confidence
        }
    
    def _extract_transportation_info(self, content: str) -> dict:
        """Extract transportation-related information."""
        transport_keywords = ['airport', 'train', 'bus', 'taxi', 'metro', 'subway', 'transport', 'getting around']
        content_lower = content.lower()
        transport_items = []
        
        for keyword in transport_keywords:
            if keyword in content_lower:
                context = self._extract_context(content, keyword, 150)
                if context and len(context.strip()) > 20:
                    transport_items.append({
                        'type': keyword,
                        'info': context.strip()
                    })
        
        confidence = min(1.0, len(transport_items) * 0.2) if transport_items else 0.0
        
        return {
            'items': transport_items,
            'confidence': confidence
        }
    
    def _extract_emergency_contacts(self, content: str) -> dict:
        """Extract emergency contact information."""
        # Look for phone numbers and emergency-related text
        phone_pattern = r'(\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})'
        emergency_keywords = ['emergency', 'police', 'hospital', 'embassy', 'consulate', 'help']
        
        content_lower = content.lower()
        emergency_items = []
        
        for keyword in emergency_keywords:
            if keyword in content_lower:
                context = self._extract_context(content, keyword, 100)
                if context:
                    # Look for phone numbers in the context
                    phones = re.findall(phone_pattern, context)
                    if phones:
                        emergency_items.append({
                            'type': keyword,
                            'contact': context.strip(),
                            'phones': phones
                        })
        
        confidence = min(1.0, len(emergency_items) * 0.3) if emergency_items else 0.0
        
        return {
            'items': emergency_items,
            'confidence': confidence
        }
    
    def _extract_context(self, content: str, keyword: str, context_length: int = 100) -> str:
        """Extract surrounding context for a keyword."""
        content_lower = content.lower()
        keyword_lower = keyword.lower()
        
        start_pos = content_lower.find(keyword_lower)
        if start_pos == -1:
            return ""
        
        # Find sentence boundaries
        start = max(0, start_pos - context_length)
        end = min(len(content), start_pos + len(keyword) + context_length)
        
        context = content[start:end]
        
        # Try to clean up sentence fragments
        sentences = context.split('.')
        if len(sentences) > 1:
            # Keep the sentence with the keyword and adjacent sentences
            for i, sentence in enumerate(sentences):
                if keyword_lower in sentence.lower():
                    start_idx = max(0, i - 1)
                    end_idx = min(len(sentences), i + 2)
                    return '. '.join(sentences[start_idx:end_idx]).strip()
        
        return context.strip()
    
    def _assess_safety_severity(self, context: str) -> str:
        """Assess the severity of a safety concern."""
        context_lower = context.lower()
        
        high_severity = ['dangerous', 'avoid', 'warning', 'risk', 'unsafe', 'threat']
        medium_severity = ['caution', 'careful', 'aware', 'concern']
        
        if any(word in context_lower for word in high_severity):
            return "high"
        elif any(word in context_lower for word in medium_severity):
            return "medium"
        else:
            return "low"
    
    def _assess_health_urgency(self, context: str) -> str:
        """Assess the urgency of a health advisory."""
        context_lower = context.lower()
        
        urgent_keywords = ['required', 'mandatory', 'must', 'essential']
        recommended_keywords = ['recommended', 'advised', 'should']
        
        if any(word in context_lower for word in urgent_keywords):
            return "required"
        elif any(word in context_lower for word in recommended_keywords):
            return "recommended"
        else:
            return "optional"
    
    def _assess_accessibility_availability(self, context: str) -> str:
        """Assess availability of accessibility features."""
        context_lower = context.lower()
        
        available_keywords = ['available', 'provided', 'accessible', 'equipped']
        limited_keywords = ['limited', 'partial', 'some']
        unavailable_keywords = ['not available', 'no access', 'unavailable']
        
        if any(word in context_lower for word in unavailable_keywords):
            return "unavailable"
        elif any(word in context_lower for word in limited_keywords):
            return "limited"
        elif any(word in context_lower for word in available_keywords):
            return "available"
        else:
            return "unknown"
    
    def _assess_source_credibility(self, url: str) -> float:
        """Assess the credibility of the source URL."""
        url_lower = url.lower()
        
        # High credibility sources
        if any(domain in url_lower for domain in ['.gov', '.edu', 'who.int', 'cdc.gov', 'state.gov']):
            return 1.0
        
        # Medium credibility sources
        if any(domain in url_lower for domain in ['lonelyplanet', 'tripadvisor', 'timeout', 'frommers']):
            return 0.8
        
        # Standard credibility
        if any(domain in url_lower for domain in ['.org', 'wikipedia', 'travel']):
            return 0.6
        
        # Default credibility
        return 0.5
    
    def _calculate_extraction_confidence(self, extraction_results: List[dict]) -> float:
        """Calculate overall extraction confidence from individual results."""
        confidences = []
        for result in extraction_results:
            if isinstance(result, dict) and 'confidence' in result:
                confidences.append(result['confidence'])
        
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def _calculate_data_completeness(self, data_categories: dict) -> float:
        """Calculate data completeness score based on filled categories."""
        completeness_score = 0.0
        
        for category, weight in self.completeness_weights.items():
            if category in data_categories:
                data = data_categories[category]
                if isinstance(data, dict):
                    if data.get('items') or data.get('info'):
                        completeness_score += weight
                elif data:  # Non-empty data
                    completeness_score += weight
        
        return completeness_score
    
    def _llm_enhanced_extraction(self, content: str, destination: str) -> dict:
        """Use LLM for enhanced structured extraction when available."""
        if not self.llm:
            return {}
        
        try:
            prompt = f"""
            Analyze the following travel content for {destination} and extract structured priority information:

            Content: {content[:2000]}...

            Please extract and format the following information as JSON:
            {{
                "safety_concerns": ["list of safety issues"],
                "visa_requirements": "visa information",
                "health_advisories": ["list of health recommendations"],
                "accessibility_features": ["list of accessibility options"],
                "emergency_contacts": ["list of emergency information"]
            }}

            If information is not available, use "Not specified" or empty array.
            """
            
            # This would call the LLM - implementation depends on LLM interface
            # For now, return empty dict since LLM integration is not yet connected
            return {}
            
        except Exception as e:
            self.logger.error(f"LLM extraction failed: {e}")
            return {}
    
    def _empty_extraction(self, url: str) -> dict:
        """Return empty extraction result for invalid content."""
        return {
            "extraction_confidence": 0.0,
            "data_completeness": 0.0,
            "source_url": url,
            "extracted_at": datetime.now().isoformat(),
            "content_length": 0,
            "safety_concerns": [],
            "safety_score": 0.0,
            "visa_requirements": "No information found.",
            "visa_confidence": 0.0,
            "health_advisories": [],
            "health_score": 0.0,
            "accessibility_features": [],
            "accessibility_score": 0.0,
            "transportation_info": [],
            "transport_score": 0.0,
            "emergency_contacts": [],
            "emergency_score": 0.0,
            "llm_enhanced": {},
            "extraction_method": "none"
        } 