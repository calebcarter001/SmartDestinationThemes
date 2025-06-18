"""
Web Discovery Tools
Handles web content discovery for destinations to enhance LLM processing.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import aiohttp
import json
from urllib.parse import quote_plus
import os

logger = logging.getLogger(__name__)

@dataclass
class WebDiscoveryResult:
    """Container for web discovery results"""
    urls: List[str]
    content: List[Dict[str, Any]]
    summary: Dict[str, Any]

class WebDiscoveryTool:
    """Tool for discovering web content about destinations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        web_config = config.get('web_discovery', {})
        
        # Configuration from config file
        self.max_sources = web_config.get('max_sources_per_destination', 10)
        self.timeout = web_config.get('timeout_seconds', 30)
        self.enable_content_validation = web_config.get('enable_content_validation', True)
        
        # API configuration
        self.brave_api_key = os.getenv('BRAVE_SEARCH_API_KEY')
        self.jina_api_key = os.getenv('JINA_API_KEY')
        
    async def discover_destination_content(self, destination: str) -> Dict[str, Any]:
        """Discover web content for a destination"""
        
        logger.info(f"🔍 Starting web discovery for {destination}")
        
        try:
            # Generate search queries
            search_queries = self._generate_search_queries(destination)
            
            # Perform searches if API key is available
            search_results = []
            if self.brave_api_key:
                for query in search_queries:
                    try:
                        results = await self._search_web_brave(query)
                        search_results.extend(results)
                    except Exception as e:
                        logger.warning(f"Search failed for query '{query}': {e}")
                        continue
            else:
                logger.warning("No Brave Search API key found, skipping web search")
                search_results = self._get_fallback_sources(destination)
            
            # Deduplicate and limit results
            unique_urls = list(dict.fromkeys([r['url'] for r in search_results]))[:self.max_sources]
            
            # Extract content from top sources
            content_results = []
            for url in unique_urls:
                try:
                    content = await self._extract_content(url)
                    if content and self._validate_content(content):
                        content_results.append({
                            'url': url,
                            'title': content.get('title', ''),
                            'content': content.get('content', ''),
                            'relevance_score': content.get('relevance_score', 0.5)
                        })
                except Exception as e:
                    logger.warning(f"Content extraction failed for {url}: {e}")
                    continue
            
            # Create summary
            summary = {
                'total_sources': len(content_results),
                'search_queries_used': search_queries,
                'average_relevance': sum(c['relevance_score'] for c in content_results) / len(content_results) if content_results else 0,
                'api_used': 'brave' if self.brave_api_key else 'fallback'
            }
            
            logger.info(f"✅ Web discovery complete for {destination}: {len(content_results)} sources")
            
            return {
                'urls': unique_urls,
                'content': content_results,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Web discovery failed for {destination}: {e}")
            return {
                'urls': [],
                'content': [],
                'summary': {'error': str(e)}
            }
    
    def _generate_search_queries(self, destination: str) -> List[str]:
        """Generate search queries for destination discovery"""
        
        base_queries = [
            f"{destination} travel guide attractions",
            f"{destination} things to do experiences", 
            f"{destination} local culture food",
            f"{destination} tourist activities recommendations",
            f"visit {destination} best places"
        ]
        
        # Add custom queries from config if available
        custom_queries = self.config.get('web_discovery', {}).get('custom_queries', [])
        for template in custom_queries:
            base_queries.append(template.format(destination=destination))
        
        return base_queries
    
    def _get_fallback_sources(self, destination: str) -> List[Dict[str, Any]]:
        """Get fallback sources when no API key is available"""
        
        # Common travel websites that might have destination content
        fallback_sources = [
            f"https://www.tripadvisor.com/Tourism-{destination.replace(' ', '_').replace(',', '')}-Vacations.html",
            f"https://www.lonelyplanet.com/destinations/{destination.lower().replace(' ', '-').replace(',', '')}",
            f"https://www.timeout.com/{destination.lower().replace(' ', '-').replace(',', '')}/travel",
            f"https://travel.usnews.com/destinations/{destination.replace(' ', '_').replace(',', '')}",
            f"https://www.fodors.com/world/{destination.lower().replace(' ', '-').replace(',', '')}"
        ]
        
        return [{'url': url, 'title': f'{destination} Travel Guide', 'snippet': f'Travel information for {destination}'} 
                for url in fallback_sources]
    
    async def _search_web_brave(self, query: str) -> List[Dict[str, Any]]:
        """Perform web search using Brave Search API"""
        
        if not self.brave_api_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'X-Subscription-Token': self.brave_api_key,
                    'Accept': 'application/json'
                }
                
                params = {
                    'q': query,
                    'count': 10,
                    'search_lang': 'en',
                    'country': 'US',
                    'safesearch': 'moderate'
                }
                
                async with session.get(
                    'https://api.search.brave.com/res/v1/web/search',
                    headers=headers,
                    params=params,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        for result in data.get('web', {}).get('results', []):
                            results.append({
                                'url': result.get('url'),
                                'title': result.get('title'),
                                'snippet': result.get('description', '')
                            })
                        
                        return results
                    else:
                        logger.warning(f"Brave Search API returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Brave Search API error: {e}")
            return []
    
    async def _extract_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract content from a URL using Jina Reader API or fallback"""
        
        if self.jina_api_key:
            return await self._extract_content_jina(url)
        else:
            return await self._extract_content_fallback(url)
    
    async def _extract_content_jina(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract content using Jina Reader API"""
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.jina_api_key}',
                    'Accept': 'application/json'
                }
                
                jina_url = f'https://r.jina.ai/{url}'
                
                async with session.get(
                    jina_url,
                    headers=headers,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        return {
                            'title': f'Content from {url}',
                            'content': content[:2000],  # Limit content length
                            'relevance_score': 0.7
                        }
                    else:
                        logger.warning(f"Jina Reader API returned status {response.status} for {url}")
                        return None
        except Exception as e:
            logger.error(f"Jina Reader API error for {url}: {e}")
            return None
    
    async def _extract_content_fallback(self, url: str) -> Optional[Dict[str, Any]]:
        """Fallback content extraction using basic web scraping"""
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                async with session.get(url, headers=headers, timeout=self.timeout) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Basic HTML content extraction
                        extracted_content = self._extract_text_from_html(html_content)
                        
                        if extracted_content and len(extracted_content) > 100:
                            return {
                                'title': self._extract_title_from_html(html_content),
                                'content': extracted_content[:2000],  # Limit content length
                                'relevance_score': 0.6
                            }
                        else:
                            logger.warning(f"Insufficient content extracted from {url}")
                            return None
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        return None
                        
        except Exception as e:
            logger.warning(f"Web scraping failed for {url}: {e}")
            return None
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract readable text from HTML content"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except ImportError:
            # Fallback without BeautifulSoup - basic regex cleaning
            import re
            
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', html_content)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        except Exception as e:
            logger.warning(f"HTML text extraction failed: {e}")
            return ""
    
    def _extract_title_from_html(self, html_content: str) -> str:
        """Extract title from HTML content"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('title')
            
            if title_tag:
                return title_tag.get_text().strip()
            else:
                # Try to find h1 as fallback
                h1_tag = soup.find('h1')
                if h1_tag:
                    return h1_tag.get_text().strip()
                    
        except ImportError:
            # Fallback without BeautifulSoup - basic regex
            import re
            
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
            if title_match:
                return title_match.group(1).strip()
                
        except Exception as e:
            logger.warning(f"HTML title extraction failed: {e}")
            
        return "Web Content"
    
    def _validate_content(self, content: Dict[str, Any]) -> bool:
        """Validate extracted content quality"""
        
        if not self.enable_content_validation:
            return True
        
        # Basic validation criteria
        title = content.get('title', '')
        text_content = content.get('content', '')
        
        # Check minimum content length
        if len(text_content) < 50:
            return False
        
        # Check for spam indicators
        spam_indicators = ['click here', 'buy now', 'limited time', 'act fast']
        text_lower = text_content.lower()
        spam_count = sum(1 for indicator in spam_indicators if indicator in text_lower)
        
        if spam_count > 2:
            return False
        
        return True 