"""
URL Validator - Simplified

Basic URL validation with essential checks for citation enhancement.
"""

import asyncio
import aiohttp
import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlparse
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    TIMEOUT = "timeout"
    ERROR = "error"

@dataclass
class URLValidationResult:
    """Simple URL validation result"""
    url: str
    status: ValidationStatus
    status_code: Optional[int]
    is_accessible: bool
    error_message: Optional[str] = None

class URLValidator:
    """Simple, efficient URL validator for citation enhancement"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        validation_config = config.get('llm_citation_enhancement', {}).get('url_validation', {})
        
        self.timeout = validation_config.get('request_timeout', 10.0)
        self.max_concurrent = validation_config.get('max_concurrent_validations', 5)
        self.user_agent = validation_config.get('user_agent', 'Destination-Insights-Discovery/1.0')
        
        self.session = None
        self.metrics = {'total': 0, 'valid': 0, 'invalid': 0}
    
    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            headers = {'User-Agent': self.user_agent}
            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return True
    
    async def validate_urls_batch(self, urls: List[str]) -> List[URLValidationResult]:
        """Validate multiple URLs efficiently"""
        if not urls:
            return []
        
        await self.initialize()
        
        # Process with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def validate_single(url):
            async with semaphore:
                return await self._validate_url(url)
        
        tasks = [validate_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        validated_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                validated_results.append(URLValidationResult(
                    url=urls[i],
                    status=ValidationStatus.ERROR,
                    status_code=None,
                    is_accessible=False,
                    error_message=str(result)
                ))
            else:
                validated_results.append(result)
        
        return validated_results
    
    async def _validate_url(self, url: str) -> URLValidationResult:
        """Validate single URL with basic checks"""
        # Basic URL structure check
        try:
            parsed = urlparse(url if url.startswith(('http://', 'https://')) else f'https://{url}')
            if not parsed.netloc or '.' not in parsed.netloc:
                return URLValidationResult(
                    url=url,
                    status=ValidationStatus.INVALID,
                    status_code=None,
                    is_accessible=False,
                    error_message="Invalid URL structure"
                )
        except Exception:
            return URLValidationResult(
                url=url,
                status=ValidationStatus.INVALID,
                status_code=None,
                is_accessible=False,
                error_message="URL parsing failed"
            )
        
        # HTTP check
        try:
            normalized_url = url if url.startswith(('http://', 'https://')) else f'https://{url}'
            async with self.session.head(normalized_url, allow_redirects=True) as response:
                is_valid = response.status < 400
                self.metrics['total'] += 1
                if is_valid:
                    self.metrics['valid'] += 1
                else:
                    self.metrics['invalid'] += 1
                
                return URLValidationResult(
                    url=url,
                    status=ValidationStatus.VALID if is_valid else ValidationStatus.INVALID,
                    status_code=response.status,
                    is_accessible=is_valid
                )
                
        except asyncio.TimeoutError:
            self.metrics['total'] += 1
            self.metrics['invalid'] += 1
            return URLValidationResult(
                url=url,
                status=ValidationStatus.TIMEOUT,
                status_code=None,
                is_accessible=False,
                error_message="Request timeout"
            )
        except Exception as e:
            self.metrics['total'] += 1
            self.metrics['invalid'] += 1
            return URLValidationResult(
                url=url,
                status=ValidationStatus.ERROR,
                status_code=None,
                is_accessible=False,
                error_message=str(e)
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get simple validation metrics"""
        if self.metrics['total'] > 0:
            self.metrics['success_rate'] = self.metrics['valid'] / self.metrics['total']
        return self.metrics.copy()
    
    async def cleanup(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()
            self.session = None 