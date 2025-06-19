"""
Citation Content Miner

Extracts and processes content from validated citation URLs using existing Jina Reader infrastructure.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Import existing Jina Reader tool
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from tools.jina_reader_tool import JinaReaderTool

logger = logging.getLogger(__name__)

@dataclass
class CitationContent:
    """Content extracted from a citation URL"""
    url: str
    title: str
    content: str
    content_length: int
    extraction_method: str
    quality_score: float
    relevance_score: float
    authority_score: float
    extraction_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class ContentMiningResult:
    """Result of content mining operation"""
    citation_contents: List[CitationContent]
    total_urls_processed: int
    successful_extractions: int
    failed_extractions: int
    total_mining_time: float
    average_content_length: float

class CitationContentMiner:
    """
    Efficient content miner that extracts usable content from citation URLs
    using the existing Jina Reader infrastructure.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Extract configuration
        mining_config = config.get('llm_citation_enhancement', {}).get('content_mining', {})
        
        # Mining strategy and settings
        self.strategy = mining_config.get('strategy', 'adaptive')
        self.use_jina_reader = mining_config.get('use_jina_reader', True)
        self.fallback_to_direct = mining_config.get('fallback_to_direct', True)
        
        # Content processing settings
        self.max_content_length = mining_config.get('max_content_length', 10000)
        self.min_content_length = mining_config.get('min_content_length', 200)
        
        # Quality filters
        self.content_quality_threshold = mining_config.get('content_quality_threshold', 0.6)
        self.relevance_threshold = mining_config.get('relevance_threshold', 0.5)
        self.authority_weight = mining_config.get('authority_weight', 0.3)
        
        # Performance settings
        self.mining_timeout = mining_config.get('mining_timeout', 30.0)
        self.max_concurrent = mining_config.get('max_concurrent_mining', 3)
        self.enable_caching = mining_config.get('enable_content_caching', True)
        
        # Initialize Jina Reader tool
        self.jina_reader = JinaReaderTool()
        
        # Content cache
        self.content_cache = {}
        self.cache_ttl = mining_config.get('cache_ttl', 3600)
        
        # Performance metrics
        self.metrics = {
            'total_mining_requests': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'cache_hits': 0,
            'average_extraction_time': 0.0,
            'average_content_length': 0.0
        }
        
        logger.info(f"Citation Content Miner initialized with {self.strategy} strategy")
    
    async def mine_citation_content(self, validated_urls: List[str], context_theme: str = None) -> ContentMiningResult:
        """Mine content from validated citation URLs"""
        start_time = time.time()
        
        if not validated_urls:
            return ContentMiningResult(
                citation_contents=[],
                total_urls_processed=0,
                successful_extractions=0,
                failed_extractions=0,
                total_mining_time=0.0,
                average_content_length=0.0
            )
        
        logger.info(f"Starting content mining for {len(validated_urls)} URLs")
        
        try:
            # Process URLs with concurrency control
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def mine_single_url(url):
                async with semaphore:
                    return await self._mine_single_citation(url, context_theme)
            
            # Execute mining tasks
            tasks = [mine_single_url(url) for url in validated_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            citation_contents = []
            successful_count = 0
            failed_count = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Content mining failed for URL {validated_urls[i]}: {result}")
                    failed_count += 1
                elif result and result.content_length >= self.min_content_length:
                    citation_contents.append(result)
                    successful_count += 1
                else:
                    failed_count += 1
            
            # Calculate statistics
            total_time = time.time() - start_time
            avg_content_length = (
                sum(c.content_length for c in citation_contents) / len(citation_contents)
                if citation_contents else 0.0
            )
            
            result = ContentMiningResult(
                citation_contents=citation_contents,
                total_urls_processed=len(validated_urls),
                successful_extractions=successful_count,
                failed_extractions=failed_count,
                total_mining_time=total_time,
                average_content_length=avg_content_length
            )
            
            # Update metrics
            self._update_metrics(result)
            
            logger.info(f"Content mining complete: {successful_count}/{len(validated_urls)} successful extractions")
            return result
            
        except Exception as e:
            logger.error(f"Content mining batch failed: {e}")
            return ContentMiningResult(
                citation_contents=[],
                total_urls_processed=len(validated_urls),
                successful_extractions=0,
                failed_extractions=len(validated_urls),
                total_mining_time=time.time() - start_time,
                average_content_length=0.0
            )
    
    async def _mine_single_citation(self, url: str, context_theme: str = None) -> Optional[CitationContent]:
        """Mine content from a single citation URL"""
        start_time = time.time()
        
        # Check cache first
        if self.enable_caching and url in self.content_cache:
            cached_content, cache_time = self.content_cache[url]
            if time.time() - cache_time < self.cache_ttl:
                self.metrics['cache_hits'] += 1
                logger.debug(f"Using cached content for {url}")
                return cached_content
        
        try:
            self.metrics['total_mining_requests'] += 1
            
            # Extract content using Jina Reader
            raw_content = await self._extract_content_with_jina(url)
            
            if not raw_content or len(raw_content) < self.min_content_length:
                logger.debug(f"Content too short for {url}: {len(raw_content) if raw_content else 0} chars")
                self.metrics['failed_extractions'] += 1
                return None
            
            # Process and score content
            processed_content = self._process_raw_content(raw_content)
            
            # Calculate quality scores
            quality_score = self._calculate_content_quality(processed_content)
            relevance_score = self._calculate_relevance(processed_content, context_theme)
            authority_score = self._calculate_authority_score(url)
            
            # Apply quality threshold
            if quality_score < self.content_quality_threshold:
                logger.debug(f"Content quality too low for {url}: {quality_score}")
                self.metrics['failed_extractions'] += 1
                return None
            
            extraction_time = time.time() - start_time
            
            # Create citation content object
            citation_content = CitationContent(
                url=url,
                title=self._extract_title(processed_content),
                content=processed_content[:self.max_content_length],
                content_length=len(processed_content),
                extraction_method="jina_reader",
                quality_score=quality_score,
                relevance_score=relevance_score,
                authority_score=authority_score,
                extraction_time=extraction_time,
                metadata={
                    'original_length': len(raw_content),
                    'processing_method': 'standard',
                    'context_theme': context_theme
                }
            )
            
            # Cache result
            if self.enable_caching:
                self.content_cache[url] = (citation_content, time.time())
            
            self.metrics['successful_extractions'] += 1
            return citation_content
            
        except Exception as e:
            self.metrics['failed_extractions'] += 1
            logger.error(f"Content extraction failed for {url}: {e}")
            return None
    
    async def _extract_content_with_jina(self, url: str) -> str:
        """Extract content using Jina Reader tool"""
        try:
            # Use the existing Jina Reader tool
            content = await self.jina_reader._arun(url)
            
            # Check if content indicates an error
            if content.startswith("Error:"):
                logger.debug(f"Jina Reader error for {url}: {content}")
                return ""
            
            return content.strip()
            
        except Exception as e:
            logger.warning(f"Jina Reader extraction failed for {url}: {e}")
            return ""
    
    def _process_raw_content(self, raw_content: str) -> str:
        """Process raw content for quality and relevance"""
        if not raw_content:
            return ""
        
        # Basic content cleaning
        lines = raw_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and navigation elements
            if not line:
                continue
            
            # Skip obvious navigation/UI elements
            if any(skip_word in line.lower() for skip_word in [
                'menu', 'navigation', 'footer', 'header', 'sidebar', 
                'advertisement', 'cookie', 'privacy policy', 'terms of service'
            ]):
                continue
            
            # Keep substantial content lines
            if len(line) > 20:  # Arbitrary threshold for meaningful content
                cleaned_lines.append(line)
        
        processed_content = '\n'.join(cleaned_lines)
        
        # Truncate if too long
        if len(processed_content) > self.max_content_length:
            processed_content = processed_content[:self.max_content_length] + "..."
        
        return processed_content
    
    def _extract_title(self, content: str) -> str:
        """Extract title from content"""
        if not content:
            return "Unknown Title"
        
        lines = content.split('\n')
        for line in lines[:5]:  # Check first few lines
            line = line.strip()
            if line and len(line) < 200:  # Reasonable title length
                return line
        
        return "Extracted Content"
    
    def _calculate_content_quality(self, content: str) -> float:
        """Calculate content quality score"""
        if not content:
            return 0.0
        
        quality = 0.5  # Base score
        
        # Length factor
        if len(content) > 500:
            quality += 0.2
        elif len(content) > 200:
            quality += 0.1
        
        # Sentence structure
        sentences = content.count('.') + content.count('!') + content.count('?')
        if sentences > 3:
            quality += 0.1
        
        # Paragraph structure
        paragraphs = content.count('\n\n')
        if paragraphs > 1:
            quality += 0.1
        
        # Information density
        words = len(content.split())
        if words > 100:
            quality += 0.1
        
        return min(1.0, quality)
    
    def _calculate_relevance(self, content: str, context_theme: str) -> float:
        """Calculate content relevance to context theme"""
        if not content or not context_theme:
            return 0.5  # Neutral relevance
        
        content_lower = content.lower()
        theme_words = context_theme.lower().split()
        
        # Count theme word matches
        matches = sum(1 for word in theme_words if word in content_lower)
        
        # Calculate relevance score
        if theme_words:
            relevance = matches / len(theme_words)
        else:
            relevance = 0.5
        
        # Boost for exact phrase matches
        if context_theme.lower() in content_lower:
            relevance += 0.2
        
        return min(1.0, relevance)
    
    def _calculate_authority_score(self, url: str) -> float:
        """Calculate authority score based on URL characteristics"""
        authority = 0.5  # Base score
        
        url_lower = url.lower()
        
        # Government and educational domains
        if any(domain in url_lower for domain in ['.gov', '.edu']):
            authority += 0.3
        
        # Organizational domains
        elif '.org' in url_lower:
            authority += 0.2
        
        # Well-known travel authorities
        travel_authorities = [
            'tripadvisor', 'lonelyplanet', 'fodors', 'frommers',
            'nationalgeographic', 'travel.state.gov', 'unesco',
            'cntraveler', 'travelandleisure', 'roughguides'
        ]
        
        if any(auth in url_lower for auth in travel_authorities):
            authority += 0.2
        
        # HTTPS boost
        if url.startswith('https://'):
            authority += 0.1
        
        return min(1.0, authority)
    
    def _update_metrics(self, result: ContentMiningResult):
        """Update mining performance metrics"""
        # Update running averages
        total_requests = self.metrics['total_mining_requests']
        
        if total_requests > 0:
            # Update average extraction time
            total_time = result.total_mining_time / result.total_urls_processed if result.total_urls_processed > 0 else 0
            current_avg_time = self.metrics['average_extraction_time']
            self.metrics['average_extraction_time'] = (
                (current_avg_time * (total_requests - result.total_urls_processed) + total_time * result.total_urls_processed) / total_requests
            )
            
            # Update average content length
            current_avg_length = self.metrics['average_content_length']
            self.metrics['average_content_length'] = (
                (current_avg_length * (total_requests - result.total_urls_processed) + result.average_content_length * result.total_urls_processed) / total_requests
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get content mining performance metrics"""
        metrics = self.metrics.copy()
        
        # Calculate derived metrics
        if metrics['total_mining_requests'] > 0:
            metrics['success_rate'] = metrics['successful_extractions'] / metrics['total_mining_requests']
            metrics['cache_hit_rate'] = metrics['cache_hits'] / metrics['total_mining_requests']
        else:
            metrics['success_rate'] = 0.0
            metrics['cache_hit_rate'] = 0.0
        
        return metrics
    
    async def cleanup(self):
        """Cleanup resources"""
        # Clear content cache
        self.content_cache.clear()
        logger.debug("Citation Content Miner cleanup complete")
