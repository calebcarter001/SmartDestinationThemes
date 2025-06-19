"""
Citation Extractor

Extracts URL citations from LLM text outputs with context and quality filtering.
"""

import re
import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class ExtractedCitation:
    """Represents a citation extracted from LLM text"""
    url: str
    context_before: str
    context_after: str
    position: int
    confidence: float
    source_text: str
    extraction_method: str

@dataclass
class CitationExtractionResult:
    """Result of citation extraction from LLM response"""
    citations: List[ExtractedCitation]
    total_urls_found: int
    valid_urls_count: int
    extraction_time: float
    source_response_id: str
    extraction_method: str
    errors: List[str]

class CitationExtractor:
    """
    Advanced citation extractor that identifies and extracts URLs from LLM responses
    with context analysis and quality filtering.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Extract configuration
        citation_config = config.get('llm_citation_enhancement', {}).get('citation_extraction', {})
        
        # URL patterns (compiled for performance)
        self.url_patterns = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for pattern in citation_config.get('url_patterns', [
                r'https?://[\w\.-]+\.\w+[\w\-._~!$&\'()*+,;=:@/]*',
                r'www\.[\w\.-]+\.\w+[\w\-._~!$&\'()*+,;=:@/]*'
            ])
        ]
        
        # Context settings
        self.extract_context = citation_config.get('extract_surrounding_context', True)
        self.context_window = citation_config.get('context_window_chars', 200)
        self.max_citations = citation_config.get('max_citations_per_response', 50)
        self.min_url_length = citation_config.get('min_url_length', 10)
        
        # Quality filters
        self.exclude_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in citation_config.get('exclude_patterns', [
                'localhost', '127.0.0.1', 'example.com', 'test.com'
            ])
        ]
        
        # Performance settings
        self.extraction_timeout = citation_config.get('extraction_timeout', 5.0)
        self.parallel_extraction = citation_config.get('parallel_extraction', True)
        
        # Performance metrics
        self.metrics = {
            'total_extractions': 0,
            'total_urls_found': 0,
            'valid_urls_extracted': 0,
            'average_extraction_time': 0.0,
            'pattern_success_rates': {}
        }
        
        logger.info(f"Citation Extractor initialized with {len(self.url_patterns)} patterns")
    
    async def extract_citations_from_response(self, llm_response: str, response_id: str = None) -> CitationExtractionResult:
        """Extract citations from a single LLM response"""
        
        if not llm_response or not llm_response.strip():
            logger.warning(f"Empty response for citation extraction: {response_id}")
            return CitationExtractionResult(
                citations=[],
                total_urls_found=0,
                valid_urls_count=0,
                extraction_time=0.0,
                source_response_id=response_id or "empty",
                extraction_method="empty_response",
                errors=["Empty or invalid LLM response"]
            )
        
        start_time = time.time()
        logger.debug(f"Extracting citations from response {response_id}, length: {len(llm_response)}")
        
        # Extract URLs using regex patterns
        raw_citations = await self._extract_raw_citations(llm_response)
        
        # Filter and validate the extracted citations
        valid_citations = self._filter_and_validate_citations(raw_citations, llm_response)
        
        # Limit the number of citations if necessary
        if len(valid_citations) > self.max_citations:
            logger.warning(f"Found {len(valid_citations)} citations, limiting to {self.max_citations}")
            valid_citations = valid_citations[:self.max_citations]
        
        extraction_time = time.time() - start_time
        
        # Update performance metrics
        self._update_metrics(len(raw_citations), len(valid_citations), extraction_time)
        
        result = CitationExtractionResult(
            citations=valid_citations,
            total_urls_found=len(raw_citations),
            valid_urls_count=len(valid_citations),
            extraction_time=extraction_time,
            source_response_id=response_id or "unknown",
            extraction_method="pattern_matching",
            errors=[]
        )
        
        logger.info(f"Citation extraction complete: {len(valid_citations)}/{len(raw_citations)} valid citations")
        return result
    
    async def extract_citations_from_structured_themes(self, themes: List[Dict[str, Any]], context_id: str = None) -> CitationExtractionResult:
        """Extract citations from structured theme data with citations fields"""
        
        if not themes:
            logger.warning(f"No themes provided for structured citation extraction: {context_id}")
            return CitationExtractionResult(
                citations=[],
                total_urls_found=0,
                valid_urls_count=0,
                extraction_time=0.0,
                source_response_id=context_id or "empty_themes",
                extraction_method="structured_extraction",
                errors=["No themes provided"]
            )
        
        start_time = time.time()
        logger.debug(f"Extracting structured citations from {len(themes)} themes: {context_id}")
        
        all_citations = []
        total_structured_urls = 0
        
        for theme in themes:
            if not isinstance(theme, dict):
                continue
                
            theme_name = theme.get('theme', 'Unknown')
            structured_citations = theme.get('citations', [])
            
            if structured_citations and isinstance(structured_citations, list):
                total_structured_urls += len(structured_citations)
                
                # Process each structured citation
                for url in structured_citations:
                    if isinstance(url, str) and url.strip():
                        citation = self._create_citation_from_structured_url(
                            url.strip(), 
                            theme_name,
                            theme.get('description', '')
                        )
                        if citation:
                            all_citations.append(citation)
            
            # Also extract from theme description text as fallback
            description = theme.get('description', '')
            if description:
                text_citations = await self._extract_raw_citations(description)
                for url, context in text_citations:
                    citation = ExtractedCitation(
                        url=url,
                        context=f"Theme: {theme_name} - {context}",
                        confidence_score=0.7,  # Lower confidence for text-extracted
                        source_type="text_extraction",
                        metadata={
                            "theme": theme_name,
                            "extraction_method": "text_regex"
                        }
                    )
                    if self._is_valid_citation(citation):
                        all_citations.append(citation)
        
        # Remove duplicates and validate
        valid_citations = self._deduplicate_and_validate_citations(all_citations)
        
        # Limit citations if necessary
        if len(valid_citations) > self.max_citations:
            logger.warning(f"Found {len(valid_citations)} structured citations, limiting to {self.max_citations}")
            valid_citations = valid_citations[:self.max_citations]
        
        extraction_time = time.time() - start_time
        
        # Update metrics
        self._update_metrics(total_structured_urls, len(valid_citations), extraction_time)
        
        result = CitationExtractionResult(
            citations=valid_citations,
            total_urls_found=total_structured_urls,
            valid_urls_count=len(valid_citations),
            extraction_time=extraction_time,
            source_response_id=context_id or "structured_themes",
            extraction_method="structured_extraction",
            errors=[]
        )
        
        logger.info(f"Structured citation extraction complete: {len(valid_citations)}/{total_structured_urls} valid citations from {len(themes)} themes")
        return result
    
    def _create_citation_from_structured_url(self, url: str, theme_name: str, description: str) -> Optional[ExtractedCitation]:
        """Create a citation object from a structured URL"""
        
        # Basic URL validation
        if not url or len(url) < self.min_url_length:
            return None
        
        # Check against exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.lower() in url.lower():
                return None
        
        citation = ExtractedCitation(
            url=url,
            context=f"Theme: {theme_name} - {description[:100]}...",
            confidence_score=0.9,  # High confidence for structured citations
            source_type="structured_citation",
            metadata={
                "theme": theme_name,
                "extraction_method": "structured_json"
            }
        )
        
        return citation if self._is_valid_citation(citation) else None
    
    def _deduplicate_and_validate_citations(self, citations: List[ExtractedCitation]) -> List[ExtractedCitation]:
        """Remove duplicate citations and validate them"""
        
        seen_urls = set()
        deduplicated = []
        
        # Sort by confidence score (higher first) to keep the best version of duplicates
        sorted_citations = sorted(citations, key=lambda c: c.confidence_score, reverse=True)
        
        for citation in sorted_citations:
            normalized_url = citation.url.lower().strip('/')
            
            if normalized_url not in seen_urls:
                if self._is_valid_citation(citation):
                    seen_urls.add(normalized_url)
                    deduplicated.append(citation)
        
        return deduplicated
    
    def _is_valid_citation(self, citation: ExtractedCitation) -> bool:
        """Validate a citation object"""
        
        if not citation or not citation.url:
            return False
        
        url = citation.url.strip()
        
        # Length check
        if len(url) < self.min_url_length:
            return False
        
        # Must be a proper URL
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.lower() in url.lower():
                return False
        
        return True
    
    async def extract_citations_from_multiple_responses(self, responses: List[Dict[str, Any]]) -> List[CitationExtractionResult]:
        """Extract citations from multiple LLM responses in parallel"""
        if not responses:
            return []
        
        if self.parallel_extraction and len(responses) > 1:
            # Process in parallel
            tasks = []
            for response_data in responses:
                response_text = response_data.get('text', response_data.get('content', ''))
                response_id = response_data.get('id', response_data.get('response_id', ''))
                
                task = self.extract_citations_from_response(response_text, response_id)
                tasks.append(task)
            
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.extraction_timeout * len(responses)
                )
                
                # Handle any exceptions in results
                valid_results = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Parallel extraction failed for response {i}: {result}")
                        # Create error result
                        error_result = CitationExtractionResult(
                            citations=[],
                            total_urls_found=0,
                            valid_urls_count=0,
                            extraction_time=0.0,
                            source_response_id=f"failed_{i}",
                            extraction_method="parallel_failed",
                            errors=[str(result)]
                        )
                        valid_results.append(error_result)
                    else:
                        valid_results.append(result)
                
                return valid_results
                
            except asyncio.TimeoutError:
                logger.error(f"Parallel citation extraction timed out after {self.extraction_timeout * len(responses)} seconds")
                return []
                
        else:
            # Process sequentially
            results = []
            for response_data in responses:
                response_text = response_data.get('text', response_data.get('content', ''))
                response_id = response_data.get('id', response_data.get('response_id', ''))
                
                result = await self.extract_citations_from_response(response_text, response_id)
                results.append(result)
            
            return results
    
    async def _extract_raw_citations(self, text: str) -> List[Tuple[str, int, str]]:
        """Extract raw URLs using all patterns"""
        citations = []
        
        # Use ThreadPoolExecutor for CPU-intensive regex operations
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit pattern matching tasks
            futures = []
            for i, pattern in enumerate(self.url_patterns):
                future = executor.submit(self._extract_with_pattern, text, pattern, f"pattern_{i}")
                futures.append(future)
            
            # Collect results
            for future in futures:
                try:
                    pattern_citations = future.result(timeout=2.0)  # 2 second timeout per pattern
                    citations.extend(pattern_citations)
                except Exception as e:
                    logger.warning(f"Pattern matching failed: {e}")
        
        # Remove duplicates while preserving order
        seen_urls = set()
        unique_citations = []
        for url, pos, method in citations:
            if url not in seen_urls:
                seen_urls.add(url)
                unique_citations.append((url, pos, method))
        
        return unique_citations
    
    def _extract_with_pattern(self, text: str, pattern: re.Pattern, method: str) -> List[Tuple[str, int, str]]:
        """Extract URLs using a specific pattern"""
        citations = []
        
        try:
            for match in pattern.finditer(text):
                url = match.group(0)
                position = match.start()
                
                # Basic URL cleanup
                url = url.rstrip('.,;:!?)')  # Remove trailing punctuation
                
                citations.append((url, position, method))
                
        except Exception as e:
            logger.warning(f"Pattern extraction failed for {method}: {e}")
        
        return citations
    
    def _filter_and_validate_citations(self, raw_citations: List[Tuple[str, int, str]], source_text: str) -> List[ExtractedCitation]:
        """Filter and validate extracted citations"""
        valid_citations = []
        
        for url, position, method in raw_citations:
            try:
                # Length validation
                if len(url) < self.min_url_length:
                    continue
                
                # Exclude pattern validation
                if any(pattern.search(url) for pattern in self.exclude_patterns):
                    continue
                
                # URL structure validation
                if not self._is_valid_url_structure(url):
                    continue
                
                # Create citation object
                citation = self._create_citation_object(url, position, method, source_text)
                valid_citations.append(citation)
                
            except Exception as e:
                logger.debug(f"Citation validation failed for URL {url}: {e}")
        
        return valid_citations
    
    def _is_valid_url_structure(self, url: str) -> bool:
        """Validate URL structure"""
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = 'https://' + url
                else:
                    # Try to parse as-is first
                    parsed = urlparse(url)
                    if not parsed.netloc:
                        return False
            
            parsed = urlparse(url)
            
            # Check required components
            if not parsed.netloc:
                return False
            
            # Check domain structure
            if '.' not in parsed.netloc:
                return False
            
            # Check for reasonable TLD
            domain_parts = parsed.netloc.split('.')
            if len(domain_parts) < 2:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _create_citation_object(self, url: str, position: int, method: str, source_text: str) -> ExtractedCitation:
        """Create a citation object with context"""
        
        # Extract context if enabled
        context_before = ""
        context_after = ""
        
        if self.extract_context:
            # Context before
            start_pos = max(0, position - self.context_window)
            context_before = source_text[start_pos:position].strip()
            
            # Context after
            end_pos = min(len(source_text), position + len(url) + self.context_window)
            context_after = source_text[position + len(url):end_pos].strip()
        
        # Calculate confidence score
        confidence = self._calculate_citation_confidence(url, context_before, context_after)
        
        # Normalize URL
        normalized_url = self._normalize_url(url)
        
        return ExtractedCitation(
            url=normalized_url,
            context_before=context_before,
            context_after=context_after,
            position=position,
            confidence=confidence,
            source_text=source_text[max(0, position-50):position+len(url)+50],  # Small snippet
            extraction_method=method
        )
    
    def _calculate_citation_confidence(self, url: str, context_before: str, context_after: str) -> float:
        """Calculate confidence score for a citation"""
        confidence = 0.5  # Base confidence
        
        # URL structure quality
        parsed = urlparse(url if url.startswith(('http://', 'https://')) else 'https://' + url)
        
        # Boost for HTTPS
        if parsed.scheme == 'https':
            confidence += 0.1
        
        # Boost for well-known domains
        domain = parsed.netloc.lower()
        if any(tld in domain for tld in ['.edu', '.gov', '.org']):
            confidence += 0.2
        elif any(tld in domain for tld in ['.com', '.net']):
            confidence += 0.1
        
        # Context quality
        context_indicators = ['source:', 'reference:', 'see:', 'visit:', 'from:', 'according to']
        context_full = (context_before + ' ' + context_after).lower()
        
        for indicator in context_indicators:
            if indicator in context_full:
                confidence += 0.1
                break
        
        # Penalty for suspicious patterns
        if any(pattern in url.lower() for pattern in ['ads', 'click', 'track', 'affiliate']):
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL format"""
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = 'https://' + url
                else:
                    url = 'https://' + url
            
            # Parse and reconstruct
            parsed = urlparse(url)
            
            # Basic normalization
            normalized = f"{parsed.scheme}://{parsed.netloc.lower()}{parsed.path}"
            
            if parsed.query:
                normalized += f"?{parsed.query}"
            
            return normalized
            
        except Exception:
            return url
    
    def _update_metrics(self, total_found: int, valid_count: int, extraction_time: float):
        """Update performance metrics"""
        self.metrics['total_extractions'] += 1
        self.metrics['total_urls_found'] += total_found
        self.metrics['valid_urls_extracted'] += valid_count
        
        # Update average extraction time
        total_extractions = self.metrics['total_extractions']
        current_avg = self.metrics['average_extraction_time']
        self.metrics['average_extraction_time'] = (
            (current_avg * (total_extractions - 1) + extraction_time) / total_extractions
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get extraction performance metrics"""
        metrics = self.metrics.copy()
        
        # Calculate derived metrics
        if metrics['total_extractions'] > 0:
            metrics['average_urls_per_extraction'] = metrics['total_urls_found'] / metrics['total_extractions']
        else:
            metrics['average_urls_per_extraction'] = 0.0
        
        if metrics['total_urls_found'] > 0:
            metrics['validation_success_rate'] = metrics['valid_urls_extracted'] / metrics['total_urls_found']
        else:
            metrics['validation_success_rate'] = 0.0
        
        return metrics
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.debug("Citation Extractor cleanup complete") 