import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from retry import retry
from bs4 import BeautifulSoup
from tqdm import tqdm # For synchronous loops
from tqdm.asyncio import tqdm as asyncio_tqdm # For asyncio.gather
import backoff
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import json
from urllib.parse import urlparse
import re
import hashlib
from nltk import sent_tokenize
import os

# Adjusted import path for caching module
from src.caching import read_from_cache, write_to_cache, PAGE_CONTENT_CACHE_EXPIRY_DAYS, BRAVE_SEARCH_CACHE_EXPIRY_DAYS

class WebDiscoveryLogic:
    """Core logic for web discovery using Brave Search API with caching and fallback."""
    
    def __init__(self, api_key: str, config: Dict[str, Any]):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Brave Search API key is required for WebDiscoveryLogic.")
        self.config = config
        self.logger = logging.getLogger("app.web_discovery")
        self.logger.setLevel(logging.INFO)
        
        wd_config = self.config.get("processing_settings", {}).get("web_discovery", {})
        self.search_params = {
            "count": wd_config.get('brave_search_count', 10),
            "result_filter": wd_config.get('brave_result_filter', 'web'),
        }
        self.min_content_length = wd_config.get("min_content_length_chars", 200)
        self.noisy_elements = wd_config.get('noisy_elements', ["script", "style", "nav", "footer", "header", "aside"])
        self._load_external_configs()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def _load_external_configs(self):
        """Loads JSON configs for domains and keywords."""
        self.logger.info("Loading external discovery configurations...")
        try:
            config_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
            
            with open(os.path.join(config_dir, 'travel_authority_domains.json'), 'r') as f:
                self.authority_domains = {item['url']: item for item in json.load(f)}
            
            with open(os.path.join(config_dir, 'default_tourist_gateway_keywords.json'), 'r') as f:
                self.tourist_gateway_keywords = json.load(f)

            self.logger.info(f"Loaded {len(self.authority_domains)} authority domains and {len(self.tourist_gateway_keywords.get('tourist_destination_cities', []))} gateway keywords.")
        except FileNotFoundError as e:
            self.logger.error(f"Could not find configuration file: {e}. Using empty configs.")
            self.authority_domains = {}
            self.tourist_gateway_keywords = {}

    @retry(tries=3, delay=2, backoff=2, jitter=(1,3))
    async def _fetch_brave_search(self, query: str) -> List[Dict]:
        """Performs a single Brave search query with caching."""
        cache_key = ["brave_search", query]
        cached_results = read_from_cache(cache_key, BRAVE_SEARCH_CACHE_EXPIRY_DAYS)
        if cached_results:
            self.logger.info(f"CACHE HIT: Brave search for query: '{query}'")
            return cached_results

        self.logger.info(f"CACHE MISS: Performing live Brave search for query: '{query}'")
        search_url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"X-Subscription-Token": self.api_key, "Accept": "application/json"}
        params = {"q": query, **self.search_params}
        
        async with self.session.get(search_url, headers=headers, params=params, timeout=20) as resp:
            resp.raise_for_status()
            data = await resp.json()
            results = data.get("web", {}).get("results", [])
            
            formatted_results = [{
                "url": r.get("url"), "title": r.get("title"), "description": r.get("description")
            } for r in results]
            
            write_to_cache(cache_key, formatted_results)
            return formatted_results

    @retry(tries=3, delay=2, backoff=2)
    async def _fetch_page_content(self, url: str, destination_name: Optional[str] = None) -> Optional[str]:
        """Fetches page content using aiohttp, with robust error handling and timeout."""
        cache_key = ["raw_html_content", url]
        cached_html = read_from_cache(cache_key, PAGE_CONTENT_CACHE_EXPIRY_DAYS)
        if cached_html:
            self.logger.info(f"CACHE HIT: Raw HTML for {url}")
            return cached_html

        self.logger.info(f"CACHE MISS: Fetching live content for {url}")
        try:
            async with self.session.get(url, timeout=30) as resp:
                if resp.status != 200:
                    self.logger.warning(f"Failed to fetch {url}. Status: {resp.status}")
                    return None
                html = await resp.text()
                
                # Basic parsing with BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")
                for element in self.noisy_elements:
                    for s in soup.select(element):
                        s.decompose()
                
                text_content = soup.get_text(separator=' ', strip=True)
                if len(text_content) > self.min_content_length:
                    write_to_cache(cache_key, text_content)
                    return text_content
                else:
                    self.logger.info(f"Content for {url} too short after cleaning ({len(text_content)} chars). Discarding.")
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching or parsing {url}: {e}", exc_info=True)
            return None

    async def discover_real_content(self, destination: str) -> List[Dict]:
        """Generates diverse queries and discovers a broad set of URLs."""
        self.logger.info(f"Starting full web discovery for {destination}...")
        query_templates = self.config.get('query_templates', [
            "{destination} travel guide",
            "things to do in {destination}",
        ])
        
        queries = [template.format(destination=destination) for template in query_templates]
        
        tasks = [self._fetch_brave_search(query) for query in queries]
        results_of_lists = await asyncio_tqdm.gather(*tasks, desc=f"Discovering sources for {destination}")
        
        unique_sources = {}
        for res_list in results_of_lists:
            for source in res_list:
                if source.get("url"):
                    unique_sources[source["url"]] = source
        
        final_sources = list(unique_sources.values())
        self.logger.info(f"Discovered {len(final_sources)} unique sources for {destination}.")
        return final_sources 