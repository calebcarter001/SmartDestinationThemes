"""
Enhanced Evidence Validator
Implements comprehensive evidence validation with storage, attribution, and quality assessment.
"""

import logging
import re
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

from src.evidence_schema import (
    EvidencePiece, ThemeEvidence, ValidationReport, EvidenceSourceType,
    EvidenceQuality, ValidationStatus, EvidenceValidationConfig
)
from src.schemas import PageContent

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class EvidenceValidator:
    """
    Comprehensive evidence validator that implements the full evidence validation design.
    Now includes evidence collection for all types of insights: themes, nano themes, 
    price data, authenticity markers, hidden gem indicators, and more.
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.validation_config = EvidenceValidationConfig(**self.config.get('evidence_validation', {}))
        self.logger = logging.getLogger("app.evidence_validator")
        
        # Initialize semantic model for similarity validation
        try:
            self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            self.logger.warning(f"Could not load semantic model: {e}")
            self.semantic_model = None
        
        # Source classification patterns
        self.source_patterns = {
            EvidenceSourceType.GOVERNMENT: [
                r'\.gov\b', r'official.*tourism', r'city.*hall', r'municipal',
                r'department.*tourism', r'visitor.*bureau', r'convention.*bureau'
            ],
            EvidenceSourceType.EDUCATION: [
                r'\.edu\b', r'university', r'college', r'academic', r'research',
                r'scholar', r'journal', r'study'
            ],
            EvidenceSourceType.MAJOR_TRAVEL: [
                r'tripadvisor', r'lonely.*planet', r'fodors', r'frommers',
                r'rick.*steves', r'national.*geographic', r'conde.*nast',
                r'travel.*leisure', r'rough.*guide'
            ],
            EvidenceSourceType.NEWS_MEDIA: [
                r'cnn', r'bbc', r'reuters', r'associated.*press', r'times',
                r'guardian', r'post', r'news', r'magazine', r'journal'
            ],
            EvidenceSourceType.TOURISM_BOARD: [
                r'visit.*', r'tourism.*board', r'destination.*', r'explore.*',
                r'discover.*', r'travel.*board'
            ],
            EvidenceSourceType.TRAVEL_BLOG: [
                r'blog', r'travel.*diary', r'journey', r'adventure.*blog',
                r'nomad', r'backpack', r'wanderlust'
            ],
            EvidenceSourceType.LOCAL_BUSINESS: [
                r'restaurant', r'hotel', r'shop', r'tour.*guide', r'local.*business',
                r'yelp', r'foursquare', r'google.*reviews'
            ],
            EvidenceSourceType.SOCIAL_MEDIA: [
                r'instagram', r'facebook', r'twitter', r'tiktok', r'youtube',
                r'social', r'influencer', r'vlog'
            ]
        }
        
        # Enhanced keyword patterns for different evidence types
        self.evidence_patterns = {
            'price': [
                r'\$\d+', r'cost', r'price', r'expensive', r'cheap', r'budget', r'affordable',
                r'free', r'admission', r'ticket', r'fee', r'charge', r'currency', r'dollar',
                r'euro', r'pound', r'yen', r'pesos', r'expensive', r'inexpensive'
            ],
            'authenticity': [
                r'local', r'authentic', r'traditional', r'genuine', r'native', r'indigenous',
                r'tourist trap', r'commercialized', r'touristy', r'mass tourism', r'chain',
                r'family.*owned', r'generations', r'heritage', r'cultural', r'historic'
            ],
            'hidden_gem': [
                r'hidden', r'secret', r'off.*beaten.*path', r'locals.*only', r'undiscovered',
                r'unknown', r'insider', r'crowd', r'popular', r'famous', r'busy', r'packed',
                r'quiet', r'peaceful', r'secluded', r'remote', r'untouched'
            ],
            'nano_themes': [
                r'specific', r'detailed', r'particular', r'specialty', r'unique', r'distinctive',
                r'artisan', r'craft', r'workshop', r'studio', r'boutique', r'specialized',
                r'micro', r'niche', r'custom', r'bespoke', r'handmade', r'artisanal'
            ],
            'depth_indicators': [
                r'deep', r'profound', r'comprehensive', r'thorough', r'extensive', r'detailed',
                r'in.*depth', r'specialized', r'expert', r'master', r'advanced', r'complex'
            ]
        }

    def classify_source_type(self, url: str, title: str = "") -> EvidenceSourceType:
        """Classify the source type based on URL and title patterns."""
        url_lower = url.lower()
        title_lower = title.lower()
        combined_text = f"{url_lower} {title_lower}"
        
        for source_type, patterns in self.source_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text):
                    return source_type
        
        return EvidenceSourceType.UNKNOWN
    
    def calculate_authority_score(self, source_type: EvidenceSourceType, url: str) -> float:
        """Calculate authority score based on source type and URL characteristics."""
        base_score = self.validation_config.authority_weights.get(source_type, 0.2)
        
        # Adjust based on URL characteristics
        url_lower = url.lower()
        
        # Boost for HTTPS
        if url.startswith('https://'):
            base_score += 0.05
        
        # Boost for established domains
        if any(domain in url_lower for domain in ['wikipedia', 'smithsonian', 'national-geographic']):
            base_score += 0.1
        
        # Penalty for suspicious domains
        if any(flag in url_lower for flag in ['free', 'cheap', 'discount', 'affiliate']):
            base_score -= 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def extract_evidence_from_content(self, content: str, theme: str, 
                                    destination: str, source_url: str, 
                                    source_title: str) -> List[EvidencePiece]:
        """Extract relevant evidence pieces from web content."""
        evidence_pieces = []
        
        # Tokenize content into sentences
        try:
            sentences = sent_tokenize(content)
        except:
            # Fallback if NLTK fails
            sentences = content.split('.')
        
        theme_lower = theme.lower()
        destination_lower = destination.lower()
        
        # Keywords to look for
        theme_keywords = [theme_lower] + theme_lower.split()
        destination_keywords = [destination_lower] + destination_lower.split(',')
        
        for sentence in sentences:
            sentence_clean = sentence.strip()
            if len(sentence_clean) < self.validation_config.min_content_length:
                continue
                
            sentence_lower = sentence_clean.lower()
            
            # Check for theme relevance
            theme_matches = [kw for kw in theme_keywords if kw in sentence_lower]
            destination_matches = [kw for kw in destination_keywords if kw in sentence_lower]
            
            # Must mention destination if required
            if self.validation_config.require_destination_mention and not destination_matches:
                continue
            
            # Must have theme relevance
            if not theme_matches:
                continue
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(
                sentence_lower, theme_keywords, destination_keywords
            )
            
            if relevance_score < self.validation_config.min_relevance_score:
                continue
            
            # Calculate semantic similarity
            semantic_similarity = None
            if self.validation_config.enable_semantic_validation:
                try:
                    theme_embedding = self.semantic_model.encode([theme])
                    sentence_embedding = self.semantic_model.encode([sentence_clean])
                    semantic_similarity = float(util.cos_sim(theme_embedding, sentence_embedding)[0][0])
                    
                    if semantic_similarity < self.validation_config.semantic_similarity_threshold:
                        continue
                except:
                    semantic_similarity = None
            
            # Classify source
            source_type = self.classify_source_type(source_url, source_title)
            authority_score = self.calculate_authority_score(source_type, source_url)
            
            if authority_score < self.validation_config.min_authority_score:
                continue
            
            # Create evidence piece
            evidence_id = hashlib.md5(f"{source_url}_{sentence_clean}".encode()).hexdigest()[:12]
            
            evidence_piece = EvidencePiece(
                evidence_id=evidence_id,
                text_content=sentence_clean[:1000],  # Limit to 1000 chars
                source_url=source_url,
                source_title=source_title,
                source_type=source_type,
                authority_score=authority_score,
                quality_rating=self._assess_evidence_quality(sentence_clean, authority_score),
                relevance_score=relevance_score,
                word_count=len(word_tokenize(sentence_clean)) if sentence_clean else 0,
                contains_destination_mention=bool(destination_matches),
                contains_theme_keywords=theme_matches,
                semantic_similarity=semantic_similarity
            )
            
            evidence_pieces.append(evidence_piece)
            
            # Limit evidence per source
            if len(evidence_pieces) >= self.validation_config.max_evidence_per_source:
                break
        
        return evidence_pieces
    
    def extract_specialized_evidence(self, content: str, evidence_type: str, 
                                   target_keywords: List[str], destination: str,
                                   source_url: str, source_title: str) -> List[EvidencePiece]:
        """Extract evidence for specialized insights like price, authenticity, hidden gems."""
        evidence_pieces = []
        
        # Get patterns for this evidence type
        patterns = self.evidence_patterns.get(evidence_type, [])
        
        try:
            sentences = sent_tokenize(content)
        except:
            sentences = content.split('.')
        
        destination_lower = destination.lower()
        destination_keywords = [destination_lower] + destination_lower.split(',')
        
        for sentence in sentences:
            sentence_clean = sentence.strip()
            if len(sentence_clean) < self.validation_config.min_content_length:
                continue
                
            sentence_lower = sentence_clean.lower()
            
            # Check for destination mention
            destination_matches = [kw for kw in destination_keywords if kw in sentence_lower]
            if self.validation_config.require_destination_mention and not destination_matches:
                continue
            
            # Check for evidence type patterns
            pattern_matches = []
            for pattern in patterns:
                if re.search(pattern, sentence_lower):
                    pattern_matches.append(pattern)
            
            # Check for target keywords
            keyword_matches = [kw for kw in target_keywords if kw.lower() in sentence_lower]
            
            # Must have either pattern or keyword match
            if not pattern_matches and not keyword_matches:
                continue
            
            # Calculate relevance based on matches
            relevance_score = self._calculate_specialized_relevance_score(
                sentence_lower, pattern_matches, keyword_matches, destination_keywords
            )
            
            if relevance_score < 0.3:  # Lower threshold for specialized evidence
                continue
            
            # Classify source and calculate authority
            source_type = self.classify_source_type(source_url, source_title)
            authority_score = self.calculate_authority_score(source_type, source_url)
            
            if authority_score < self.validation_config.min_authority_score:
                continue
            
            # Create evidence piece
            evidence_id = hashlib.md5(f"{source_url}_{evidence_type}_{sentence_clean}".encode()).hexdigest()[:12]
            
            evidence_piece = EvidencePiece(
                evidence_id=evidence_id,
                text_content=sentence_clean[:1000],
                source_url=source_url,
                source_title=source_title,
                source_type=source_type,
                authority_score=authority_score,
                quality_rating=self._assess_evidence_quality(sentence_clean, authority_score),
                relevance_score=relevance_score,
                word_count=len(word_tokenize(sentence_clean)) if sentence_clean else 0,
                contains_destination_mention=bool(destination_matches),
                contains_theme_keywords=keyword_matches + pattern_matches,
                semantic_similarity=None  # Not using semantic similarity for specialized evidence
            )
            
            evidence_pieces.append(evidence_piece)
            
            # Limit evidence per source
            if len(evidence_pieces) >= self.validation_config.max_evidence_per_source:
                break
        
        return evidence_pieces
    
    def validate_nano_themes_evidence(self, nano_themes: List[str], main_theme: str,
                                    web_pages: List[PageContent], destination: str) -> Dict[str, ThemeEvidence]:
        """Validate nano themes with specialized evidence collection."""
        nano_evidence = {}
        
        for nano_theme in nano_themes:
            # Extract evidence for this nano theme
            all_evidence = []
            
            for page in web_pages:
                if not page.content:
                    continue
                
                # Use specialized extraction for nano themes
                nano_evidence_pieces = self.extract_specialized_evidence(
                    content=page.content,
                    evidence_type='nano_themes',
                    target_keywords=[nano_theme, main_theme],
                    destination=destination,
                    source_url=page.url,
                    source_title=page.title
                )
                
                all_evidence.extend(nano_evidence_pieces)
            
            # Create theme evidence for this nano theme
            theme_evidence = self._create_theme_evidence(
                theme_name=nano_theme,
                theme_category='nano_theme',
                evidence_pieces=all_evidence
            )
            
            nano_evidence[nano_theme] = theme_evidence
        
        return nano_evidence
    
    def validate_price_evidence(self, web_pages: List[PageContent], destination: str) -> ThemeEvidence:
        """Collect evidence specifically for price and cost information."""
        all_evidence = []
        
        for page in web_pages:
            if not page.content:
                continue
            
            price_evidence = self.extract_specialized_evidence(
                content=page.content,
                evidence_type='price',
                target_keywords=['cost', 'price', 'budget', 'expensive', 'cheap', 'free'],
                destination=destination,
                source_url=page.url,
                source_title=page.title
            )
            
            all_evidence.extend(price_evidence)
        
        return self._create_theme_evidence(
            theme_name='Price Information',
            theme_category='price_analysis',
            evidence_pieces=all_evidence
        )
    
    def validate_authenticity_evidence(self, web_pages: List[PageContent], destination: str) -> ThemeEvidence:
        """Collect evidence for authenticity markers (local vs tourist)."""
        all_evidence = []
        
        for page in web_pages:
            if not page.content:
                continue
            
            auth_evidence = self.extract_specialized_evidence(
                content=page.content,
                evidence_type='authenticity',
                target_keywords=['local', 'authentic', 'traditional', 'tourist', 'commercial'],
                destination=destination,
                source_url=page.url,
                source_title=page.title
            )
            
            all_evidence.extend(auth_evidence)
        
        return self._create_theme_evidence(
            theme_name='Authenticity Markers',
            theme_category='authenticity_analysis',
            evidence_pieces=all_evidence
        )
    
    def validate_hidden_gem_evidence(self, web_pages: List[PageContent], destination: str) -> ThemeEvidence:
        """Collect evidence for hidden gem indicators."""
        all_evidence = []
        
        for page in web_pages:
            if not page.content:
                continue
            
            gem_evidence = self.extract_specialized_evidence(
                content=page.content,
                evidence_type='hidden_gem',
                target_keywords=['hidden', 'secret', 'crowd', 'popular', 'quiet', 'busy'],
                destination=destination,
                source_url=page.url,
                source_title=page.title
            )
            
            all_evidence.extend(gem_evidence)
        
        return self._create_theme_evidence(
            theme_name='Hidden Gem Indicators',
            theme_category='hidden_gem_analysis',
            evidence_pieces=all_evidence
        )

    def _calculate_relevance_score(self, text: str, theme_keywords: List[str], 
                                 destination_keywords: List[str]) -> float:
        """Calculate relevance score based on keyword density and context."""
        if not text:
            return 0.0
        
        words = text.split()
        total_words = len(words)
        
        if total_words == 0:
            return 0.0
        
        # Count keyword matches
        theme_matches = sum(1 for word in words if any(kw in word for kw in theme_keywords))
        destination_matches = sum(1 for word in words if any(kw in word for kw in destination_keywords))
        
        # Calculate density scores
        theme_density = theme_matches / total_words
        destination_density = destination_matches / total_words
        
        # Combined relevance score
        relevance_score = (theme_density * 0.7) + (destination_density * 0.3)
        
        return min(1.0, relevance_score * 10)  # Scale up and cap at 1.0
    
    def _calculate_specialized_relevance_score(self, text: str, pattern_matches: List[str],
                                             keyword_matches: List[str], destination_keywords: List[str]) -> float:
        """Calculate relevance for specialized evidence types."""
        if not text:
            return 0.0
        
        words = text.split()
        total_words = len(words)
        
        if total_words == 0:
            return 0.0
        
        # Pattern match score
        pattern_score = len(pattern_matches) * 0.3
        
        # Keyword match score
        keyword_score = len(keyword_matches) * 0.4
        
        # Destination mention score
        destination_matches = sum(1 for word in words if any(kw in word for kw in destination_keywords))
        destination_score = min(1.0, destination_matches / total_words * 10) * 0.3
        
        return min(1.0, pattern_score + keyword_score + destination_score)
    
    def _assess_evidence_quality(self, text: str, authority_score: float) -> EvidenceQuality:
        """Assess the quality of evidence based on content and authority."""
        if authority_score >= 0.8 and len(text) >= 200:
            return EvidenceQuality.EXCELLENT
        elif authority_score >= 0.6 and len(text) >= 100:
            return EvidenceQuality.GOOD
        elif authority_score >= 0.4 and len(text) >= 50:
            return EvidenceQuality.ACCEPTABLE
        elif authority_score >= 0.2:
            return EvidenceQuality.POOR
        else:
            return EvidenceQuality.REJECTED
    
    def _create_theme_evidence(self, theme_name: str, theme_category: str, 
                             evidence_pieces: List[EvidencePiece]) -> ThemeEvidence:
        """Create a ThemeEvidence object from evidence pieces."""
        # Sort by quality and limit
        evidence_pieces.sort(key=lambda e: (e.authority_score, e.relevance_score), reverse=True)
        limited_evidence = evidence_pieces[:self.validation_config.max_evidence_pieces]
        
        # Calculate metrics
        unique_sources = len(set(e.source_url for e in limited_evidence))
        avg_authority = sum(e.authority_score for e in limited_evidence) / len(limited_evidence) if limited_evidence else 0.0
        avg_relevance = sum(e.relevance_score for e in limited_evidence) / len(limited_evidence) if limited_evidence else 0.0
        
        # Determine validation status
        validation_status = self._determine_validation_status(limited_evidence, unique_sources)
        
        # Calculate validation confidence
        validation_confidence = self._calculate_validation_confidence(limited_evidence, unique_sources)
        
        # Check requirements
        meets_min_evidence = len(limited_evidence) >= self.validation_config.min_evidence_pieces
        meets_source_diversity = unique_sources >= self.validation_config.min_unique_sources
        meets_quality = avg_authority >= self.validation_config.min_authority_score
        
        return ThemeEvidence(
            theme_name=theme_name,
            theme_category=theme_category,
            evidence_pieces=limited_evidence,
            total_evidence_count=len(limited_evidence),
            unique_source_count=unique_sources,
            validation_status=validation_status,
            validation_confidence=validation_confidence,
            average_authority_score=avg_authority,
            average_relevance_score=avg_relevance,
            source_diversity_score=min(1.0, unique_sources / 5.0),
            meets_min_evidence_requirement=meets_min_evidence,
            meets_source_diversity_requirement=meets_source_diversity,
            meets_quality_threshold=meets_quality,
            strongest_evidence=limited_evidence[0].evidence_id if limited_evidence else None,
            evidence_gaps=self._identify_evidence_gaps(theme_name, limited_evidence),
            conflicting_evidence=[]
        )

    def validate_theme_evidence(self, theme: str, category: str, 
                              web_pages: List[PageContent], 
                              destination: str) -> ThemeEvidence:
        """Validate a single theme against web evidence."""
        all_evidence = []
        source_counts = {}
        
        # Extract evidence from each web page
        for page in web_pages:
            if not page.content:
                continue
                
            page_evidence = self.extract_evidence_from_content(
                page.content, theme, destination, page.url, page.title
            )
            
            # Limit evidence per source
            source_domain = urlparse(page.url).netloc
            if source_domain not in source_counts:
                source_counts[source_domain] = 0
            
            for evidence in page_evidence:
                if source_counts[source_domain] < self.validation_config.max_evidence_per_source:
                    all_evidence.append(evidence)
                    source_counts[source_domain] += 1
        
        return self._create_theme_evidence(theme, category, all_evidence)
    
    def _determine_validation_status(self, evidence_pieces: List[EvidencePiece], 
                                   unique_sources: int) -> ValidationStatus:
        """Determine validation status based on evidence quality and quantity."""
        if not evidence_pieces:
            return ValidationStatus.UNVALIDATED
        
        high_quality_count = sum(1 for e in evidence_pieces 
                               if e.quality_rating in [EvidenceQuality.EXCELLENT, EvidenceQuality.GOOD])
        
        if (len(evidence_pieces) >= self.validation_config.min_evidence_pieces and 
            unique_sources >= self.validation_config.min_unique_sources and
            high_quality_count >= 2):
            return ValidationStatus.VALIDATED
        elif len(evidence_pieces) >= 2 and unique_sources >= 1:
            return ValidationStatus.PARTIALLY_VALIDATED
        else:
            return ValidationStatus.UNVALIDATED
    
    def _calculate_validation_confidence(self, evidence_pieces: List[EvidencePiece], 
                                       unique_sources: int) -> float:
        """Calculate confidence in validation based on evidence strength."""
        if not evidence_pieces:
            return 0.0
        
        # Base confidence from evidence count
        evidence_confidence = min(1.0, len(evidence_pieces) / self.validation_config.min_evidence_pieces)
        
        # Source diversity confidence
        source_confidence = min(1.0, unique_sources / self.validation_config.min_unique_sources)
        
        # Quality confidence
        avg_authority = sum(e.authority_score for e in evidence_pieces) / len(evidence_pieces)
        quality_confidence = avg_authority
        
        # Combined confidence
        overall_confidence = (evidence_confidence * 0.4 + source_confidence * 0.3 + quality_confidence * 0.3)
        
        return round(overall_confidence, 3)
    
    def _identify_evidence_gaps(self, theme: str, evidence_pieces: List[EvidencePiece]) -> List[str]:
        """Identify gaps in evidence coverage."""
        gaps = []
        
        if not evidence_pieces:
            gaps.append("No evidence found")
            return gaps
        
        # Check for source type diversity
        source_types = set(e.source_type for e in evidence_pieces)
        if EvidenceSourceType.GOVERNMENT not in source_types:
            gaps.append("Missing official/government sources")
        if EvidenceSourceType.MAJOR_TRAVEL not in source_types:
            gaps.append("Missing major travel publication sources")
        
        # Check for quality distribution
        quality_counts = {}
        for evidence in evidence_pieces:
            quality_counts[evidence.quality_rating] = quality_counts.get(evidence.quality_rating, 0) + 1
        
        if quality_counts.get(EvidenceQuality.EXCELLENT, 0) == 0:
            gaps.append("No excellent quality evidence")
        
        return gaps
    
    def generate_validation_report(self, destination: str, themes_evidence: List[ThemeEvidence], 
                                 processing_time: float) -> ValidationReport:
        """Generate comprehensive validation report."""
        validated_themes = sum(1 for te in themes_evidence 
                             if te.validation_status == ValidationStatus.VALIDATED)
        
        total_evidence = sum(te.total_evidence_count for te in themes_evidence)
        unique_sources = len(set(ep.source_url for te in themes_evidence for ep in te.evidence_pieces))
        
        avg_quality = 0.0
        if total_evidence > 0:
            all_evidence = [ep for te in themes_evidence for ep in te.evidence_pieces]
            avg_quality = sum(ep.authority_score for ep in all_evidence) / len(all_evidence)
        
        # Quality distribution
        quality_dist = {}
        source_dist = {}
        
        for te in themes_evidence:
            for ep in te.evidence_pieces:
                quality_dist[ep.quality_rating] = quality_dist.get(ep.quality_rating, 0) + 1
                source_dist[ep.source_type] = source_dist.get(ep.source_type, 0) + 1
        
        return ValidationReport(
            destination_name=destination,
            destination_id=destination.lower().replace(' ', '_').replace(',', ''),
            total_themes_analyzed=len(themes_evidence),
            themes_validated=validated_themes,
            themes_rejected=len(themes_evidence) - validated_themes,
            validation_success_rate=validated_themes / len(themes_evidence) if themes_evidence else 0.0,
            total_evidence_pieces=total_evidence,
            unique_sources_used=unique_sources,
            average_evidence_quality=avg_quality,
            theme_evidence=themes_evidence,
            evidence_quality_distribution=quality_dist,
            source_type_distribution=source_dist,
            processing_time_seconds=processing_time,
            validation_config=self.validation_config.dict()
        )

    def validate_all_theme_attributes(self, theme_data: Dict[str, Any], 
                                     web_pages: List[PageContent], 
                                     destination: str) -> Dict[str, Any]:
        """
        Comprehensive validation of ALL theme attributes with evidence collection.
        This validates every piece of LLM-generated metadata.
        """
        theme_name = theme_data.get('theme', 'Unknown Theme')
        
        # Initialize comprehensive evidence collection
        all_evidence = {}
        
        # 1. Main Theme Evidence
        main_theme_evidence = self.validate_theme_evidence(
            theme_name, theme_data.get('category', 'general'), web_pages, destination
        )
        all_evidence['main_theme'] = main_theme_evidence
        
        # 2. Nano Themes Evidence
        nano_themes = theme_data.get('depth_analysis', {}).get('nano_themes', [])
        if nano_themes:
            nano_evidence = self.validate_nano_themes_evidence(nano_themes, theme_name, web_pages, destination)
            all_evidence['nano_themes'] = nano_evidence
        
        # 3. Price Insights Evidence
        price_insights = theme_data.get('price_insights', {})
        if price_insights:
            price_evidence = self.validate_price_evidence(web_pages, destination)
            all_evidence['price_insights'] = price_evidence
        
        # 4. Authenticity Analysis Evidence
        authenticity = theme_data.get('authenticity_analysis', {})
        if authenticity:
            auth_evidence = self.validate_authenticity_evidence(web_pages, destination)
            all_evidence['authenticity_analysis'] = auth_evidence
        
        # 5. Hidden Gem Evidence
        hidden_gem = theme_data.get('hidden_gem_score', {})
        if hidden_gem:
            gem_evidence = self.validate_hidden_gem_evidence(web_pages, destination)
            all_evidence['hidden_gem_score'] = gem_evidence
        
        # 6. Experience Intensity Evidence
        intensity = theme_data.get('experience_intensity', {})
        if intensity:
            intensity_evidence = self.validate_experience_intensity_evidence(intensity, web_pages, destination)
            all_evidence['experience_intensity'] = intensity_evidence
        
        # 7. Emotional Resonance Evidence
        emotions = theme_data.get('emotional_profile', {})
        if emotions:
            emotion_evidence = self.validate_emotional_resonance_evidence(emotions, web_pages, destination)
            all_evidence['emotional_profile'] = emotion_evidence
        
        # 8. Group Dynamics Evidence
        contextual_info = theme_data.get('contextual_info', {})
        demographics = contextual_info.get('demographic_suitability', [])
        if demographics:
            demo_evidence = self.validate_demographic_evidence(demographics, web_pages, destination)
            all_evidence['demographic_suitability'] = demo_evidence
        
        # 9. Time Commitment Evidence
        time_commitment = contextual_info.get('time_commitment', '')
        if time_commitment:
            time_evidence = self.validate_time_commitment_evidence(time_commitment, web_pages, destination)
            all_evidence['time_commitment'] = time_evidence
        
        # 10. Weather/Climate Evidence
        micro_climate = theme_data.get('micro_climate', {})
        if micro_climate:
            weather_evidence = self.validate_weather_evidence(micro_climate, web_pages, destination)
            all_evidence['micro_climate'] = weather_evidence
        
        # 11. Cultural Sensitivity Evidence
        cultural_sensitivity = theme_data.get('cultural_sensitivity', {})
        if cultural_sensitivity:
            cultural_evidence = self.validate_cultural_evidence(cultural_sensitivity, web_pages, destination)
            all_evidence['cultural_sensitivity'] = cultural_evidence
        
        # 12. Theme Interconnections Evidence
        interconnections = theme_data.get('theme_interconnections', {})
        if interconnections:
            connection_evidence = self.validate_interconnection_evidence(interconnections, web_pages, destination)
            all_evidence['theme_interconnections'] = connection_evidence
        
        return all_evidence

    def validate_experience_intensity_evidence(self, intensity_data: Dict[str, Any], 
                                             web_pages: List[PageContent], 
                                             destination: str) -> ThemeEvidence:
        """Validate experience intensity claims with evidence."""
        intensity_keywords = []
        
        # Physical intensity keywords
        physical = intensity_data.get('physical', 'moderate')
        if physical == 'high':
            intensity_keywords.extend(['strenuous', 'demanding', 'challenging', 'difficult', 'extreme'])
        elif physical == 'low':
            intensity_keywords.extend(['easy', 'gentle', 'relaxed', 'leisurely', 'comfortable'])
        
        # Cultural intensity keywords
        cultural = intensity_data.get('cultural', 'moderate')
        if cultural == 'high':
            intensity_keywords.extend(['immersive', 'deep cultural', 'traditional', 'authentic', 'ceremonial'])
        elif cultural == 'low':
            intensity_keywords.extend(['surface level', 'casual', 'brief visit', 'tourist-friendly'])
        
        # Social intensity keywords
        social = intensity_data.get('social', 'moderate')
        if social == 'high':
            intensity_keywords.extend(['crowded', 'social', 'party', 'festival', 'group activity'])
        elif social == 'low':
            intensity_keywords.extend(['quiet', 'peaceful', 'solo', 'private', 'secluded'])
        
        evidence_pieces = self.extract_specialized_evidence(
            '\n'.join([page.content for page in web_pages]),
            'experience_intensity',
            intensity_keywords,
            destination,
            web_pages[0].url if web_pages else '',
            web_pages[0].title if web_pages else ''
        )
        
        return self._create_theme_evidence(
            'Experience Intensity',
            'experience_analysis',
            evidence_pieces
        )

    def validate_emotional_resonance_evidence(self, emotion_data: Dict[str, Any], 
                                            web_pages: List[PageContent], 
                                            destination: str) -> ThemeEvidence:
        """Validate emotional resonance claims with evidence."""
        primary_emotions = emotion_data.get('primary_emotions', [])
        emotion_keywords = []
        
        emotion_keyword_map = {
            'peaceful': ['peaceful', 'serene', 'tranquil', 'calm', 'relaxing', 'zen'],
            'exhilarating': ['exciting', 'thrilling', 'adrenaline', 'exhilarating', 'rush'],
            'contemplative': ['contemplative', 'reflective', 'meditative', 'thoughtful', 'spiritual'],
            'inspiring': ['inspiring', 'motivating', 'uplifting', 'breathtaking', 'awe-inspiring'],
            'social': ['social', 'community', 'gathering', 'interactive', 'group'],
            'challenging': ['challenging', 'demanding', 'test yourself', 'push limits']
        }
        
        for emotion in primary_emotions:
            emotion_keywords.extend(emotion_keyword_map.get(emotion, [emotion]))
        
        evidence_pieces = self.extract_specialized_evidence(
            '\n'.join([page.content for page in web_pages]),
            'emotional_resonance',
            emotion_keywords,
            destination,
            web_pages[0].url if web_pages else '',
            web_pages[0].title if web_pages else ''
        )
        
        return self._create_theme_evidence(
            'Emotional Resonance',
            'emotional_analysis',
            evidence_pieces
        )

    def validate_demographic_evidence(self, demographics: List[str], 
                                    web_pages: List[PageContent], 
                                    destination: str) -> ThemeEvidence:
        """Validate demographic suitability claims with evidence."""
        demo_keywords = []
        
        demo_keyword_map = {
            'families with children': ['family friendly', 'kids', 'children', 'family', 'all ages'],
            'couples': ['romantic', 'couples', 'date night', 'intimate', 'honeymoon'],
            'solo travelers': ['solo', 'individual', 'personal', 'self-guided', 'independent'],
            'friend groups': ['groups', 'friends', 'party', 'together', 'social'],
            'multi-generational': ['all ages', 'grandparents', 'generations', 'elderly', 'accessible']
        }
        
        for demo in demographics:
            demo_keywords.extend(demo_keyword_map.get(demo, demo.split()))
        
        evidence_pieces = self.extract_specialized_evidence(
            '\n'.join([page.content for page in web_pages]),
            'demographic_suitability',
            demo_keywords,
            destination,
            web_pages[0].url if web_pages else '',
            web_pages[0].title if web_pages else ''
        )
        
        return self._create_theme_evidence(
            'Demographic Suitability',
            'demographic_analysis',
            evidence_pieces
        )

    def validate_time_commitment_evidence(self, time_commitment: str, 
                                        web_pages: List[PageContent], 
                                        destination: str) -> ThemeEvidence:
        """Validate time commitment estimates with evidence."""
        time_keywords = []
        
        if 'hour' in time_commitment.lower():
            time_keywords.extend(['hour', 'hours', 'duration', 'time needed'])
        if 'day' in time_commitment.lower():
            time_keywords.extend(['full day', 'all day', 'day trip', 'entire day'])
        if 'quick' in time_commitment.lower() or 'short' in time_commitment.lower():
            time_keywords.extend(['quick', 'brief', 'short visit', 'minutes', '30 min'])
        if 'extended' in time_commitment.lower() or 'long' in time_commitment.lower():
            time_keywords.extend(['extended', 'long visit', 'several hours', 'half day'])
        
        evidence_pieces = self.extract_specialized_evidence(
            '\n'.join([page.content for page in web_pages]),
            'time_commitment',
            time_keywords,
            destination,
            web_pages[0].url if web_pages else '',
            web_pages[0].title if web_pages else ''
        )
        
        return self._create_theme_evidence(
            'Time Commitment',
            'time_analysis',
            evidence_pieces
        )

    def validate_weather_evidence(self, micro_climate: Dict[str, Any], 
                                web_pages: List[PageContent], 
                                destination: str) -> ThemeEvidence:
        """Validate weather/climate requirements with evidence."""
        weather_keywords = []
        
        weather_deps = micro_climate.get('weather_dependencies', [])
        best_time = micro_climate.get('best_time_of_day', [])
        seasonal = micro_climate.get('seasonal_considerations', [])
        
        for weather in weather_deps:
            if 'sunny' in weather:
                weather_keywords.extend(['sunny', 'clear weather', 'good weather', 'sunshine'])
            elif 'rain' in weather:
                weather_keywords.extend(['rain', 'wet weather', 'indoor', 'covered'])
            elif 'wind' in weather:
                weather_keywords.extend(['windy', 'wind conditions', 'breeze'])
        
        for time in best_time:
            weather_keywords.extend([time, f'{time} hours', f'best {time}'])
        
        for season in seasonal:
            weather_keywords.extend([season, f'{season} season', f'during {season}'])
        
        evidence_pieces = self.extract_specialized_evidence(
            '\n'.join([page.content for page in web_pages]),
            'weather_climate',
            weather_keywords,
            destination,
            web_pages[0].url if web_pages else '',
            web_pages[0].title if web_pages else ''
        )
        
        return self._create_theme_evidence(
            'Weather/Climate Requirements',
            'weather_analysis',
            evidence_pieces
        )

    def validate_cultural_evidence(self, cultural_sensitivity: Dict[str, Any], 
                                 web_pages: List[PageContent], 
                                 destination: str) -> ThemeEvidence:
        """Validate cultural sensitivity requirements with evidence."""
        cultural_keywords = []
        
        considerations = cultural_sensitivity.get('considerations', [])
        immersion_level = cultural_sensitivity.get('cultural_immersion_level', '')
        
        for consideration in considerations:
            cultural_keywords.extend(consideration.split())
        
        if 'high' in immersion_level:
            cultural_keywords.extend(['traditional', 'authentic', 'local customs', 'cultural protocol'])
        elif 'moderate' in immersion_level:
            cultural_keywords.extend(['respectful', 'cultural awareness', 'local etiquette'])
        
        cultural_keywords.extend(['dress code', 'cultural norms', 'respect', 'tradition', 'customs'])
        
        evidence_pieces = self.extract_specialized_evidence(
            '\n'.join([page.content for page in web_pages]),
            'cultural_sensitivity',
            cultural_keywords,
            destination,
            web_pages[0].url if web_pages else '',
            web_pages[0].title if web_pages else ''
        )
        
        return self._create_theme_evidence(
            'Cultural Sensitivity',
            'cultural_analysis',
            evidence_pieces
        )

    def validate_interconnection_evidence(self, interconnections: Dict[str, Any], 
                                        web_pages: List[PageContent], 
                                        destination: str) -> ThemeEvidence:
        """Validate theme interconnection claims with evidence."""
        interconnection_keywords = []
        
        natural_combos = interconnections.get('natural_combinations', [])
        complementary = interconnections.get('complementary_activities', [])
        
        for combo in natural_combos:
            interconnection_keywords.extend(combo.split())
        
        for activity in complementary:
            interconnection_keywords.extend(activity.split())
        
        interconnection_keywords.extend(['combine with', 'pair with', 'also visit', 'nearby', 'walking distance'])
        
        evidence_pieces = self.extract_specialized_evidence(
            '\n'.join([page.content for page in web_pages]),
            'theme_interconnections',
            interconnection_keywords,
            destination,
            web_pages[0].url if web_pages else '',
            web_pages[0].title if web_pages else ''
        )
        
        return self._create_theme_evidence(
            'Theme Interconnections',
            'interconnection_analysis',
            evidence_pieces
        ) 