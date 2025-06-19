"""
Web Discovery Agent

Intelligent web content discovery with adaptive query generation and quality assessment.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentMessage, AgentState
from .data_models import (
    WebDiscoveryResult, WebContent, AgentResponse, ResponseFactory, 
    TaskStatus, DataConverter
)

# Import existing tools
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from tools.web_discovery_tools import WebDiscoveryTool
from src.core.web_discovery_logic import WebDiscoveryLogic

logger = logging.getLogger(__name__)

@dataclass
class DiscoveryStrategy:
    """Strategy for web discovery operations"""
    query_depth: str  # 'basic', 'standard', 'comprehensive'
    source_diversity: str  # 'low', 'medium', 'high'
    max_sources: int
    quality_threshold: float
    fallback_enabled: bool = True
    custom_queries: List[str] = None

class WebDiscoveryAgent(BaseAgent):
    """
    Intelligent web discovery agent that enhances the existing WebDiscoveryTool
    with adaptive strategies and quality assessment.
    
    Features:
    - Adaptive query generation based on destination characteristics
    - Quality-driven source selection
    - Intelligent fallback strategies
    - Performance optimization
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("web_discovery", config)
        
        # Configuration
        discovery_config = config.get('web_discovery', {})
        self.max_sources_per_destination = discovery_config.get('max_sources_per_destination', 10)
        self.timeout_seconds = discovery_config.get('timeout_seconds', 30)
        self.enable_quality_assessment = discovery_config.get('enable_content_validation', True)
        
        # Quality thresholds
        self.min_content_quality = discovery_config.get('min_content_quality', 0.6)
        self.min_source_diversity = discovery_config.get('min_source_diversity', 0.7)
        
        # Initialize wrapped tools
        self.web_discovery_tool = None
        self.web_discovery_logic = None
        
        # Query generation intelligence
        self.destination_analyzer = DestinationAnalyzer()
        self.query_generator = IntelligentQueryGenerator()
        self.quality_assessor = ContentQualityAssessor()
        
        # Performance tracking
        self.discovery_metrics = {
            'total_discoveries': 0,
            'successful_discoveries': 0,
            'average_sources_per_destination': 0.0,
            'average_quality_score': 0.0,
            'fallback_usage_rate': 0.0
        }
    
    async def _initialize_agent_specific(self):
        """Initialize web discovery tools and intelligence components"""
        try:
            # Initialize wrapped tools
            self.web_discovery_tool = WebDiscoveryTool(self.config)
            
            # Initialize web discovery logic if API keys available
            brave_api_key = os.getenv('BRAVE_SEARCH_API_KEY')
            if brave_api_key:
                self.web_discovery_logic = WebDiscoveryLogic(brave_api_key, self.config)
            
            # Register task handlers
            self.register_message_handler("execute_discovery", self._handle_discovery_request)
            self.register_message_handler("assess_quality", self._handle_quality_assessment)
            self.register_message_handler("generate_queries", self._handle_query_generation)
            
            self.logger.info("Web Discovery Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Web Discovery Agent: {e}")
            raise
    
    async def _execute_task_specific(self, task_id: str, task_definition: Dict[str, Any]) -> AgentResponse:
        """Execute web discovery tasks"""
        task_type = task_definition.get('task_type')
        task_data = task_definition.get('data', {})
        
        try:
            start_time = time.time()
            
            if task_type == 'execute_discovery':
                result = await self._execute_discovery(task_data)
                processing_time = time.time() - start_time
                return ResponseFactory.success(
                    data=result, 
                    agent_id=self.agent_id, 
                    task_id=task_id,
                    processing_time=processing_time
                )
            elif task_type == 'assess_quality':
                result = await self._assess_content_quality(task_data)
                processing_time = time.time() - start_time
                return ResponseFactory.success(
                    data=result, 
                    agent_id=self.agent_id, 
                    task_id=task_id,
                    processing_time=processing_time
                )
            elif task_type == 'generate_queries':
                result = await self._generate_intelligent_queries(task_data)
                processing_time = time.time() - start_time
                return ResponseFactory.success(
                    data=result, 
                    agent_id=self.agent_id, 
                    task_id=task_id,
                    processing_time=processing_time
                )
            else:
                return ResponseFactory.error(
                    error_message=f"Unknown task type: {task_type}",
                    agent_id=self.agent_id,
                    task_id=task_id
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            return ResponseFactory.error(
                error_message=str(e),
                agent_id=self.agent_id,
                task_id=task_id,
                processing_time=processing_time
            )
    
    async def _execute_discovery(self, task_data: Dict[str, Any]) -> WebDiscoveryResult:
        """Execute intelligent web discovery for a destination"""
        destination = task_data.get('destination')
        strategy_config = task_data.get('strategy', {})
        requirements = task_data.get('requirements', {})
        
        if not destination:
            raise ValueError("Destination is required for discovery")
        
        start_time = time.time()
        self.logger.info(f"🔍 Starting intelligent discovery for {destination}")
        
        try:
            # Phase 1: Destination Analysis
            destination_profile = await self.destination_analyzer.analyze_destination(destination)
            self.logger.debug(f"Destination profile: {destination_profile}")
            
            # Phase 2: Strategy Planning
            discovery_strategy = await self._plan_discovery_strategy(
                destination_profile, strategy_config, requirements
            )
            self.logger.info(f"Using discovery strategy: {discovery_strategy.query_depth} depth, {discovery_strategy.max_sources} sources")
            
            # Phase 3: Intelligent Query Generation
            queries = await self.query_generator.generate_queries(destination, discovery_strategy, destination_profile)
            self.logger.info(f"Generated {len(queries)} intelligent queries")
            
            # Phase 4: Content Discovery with Quality Assessment
            discovery_results = await self._discover_with_quality_control(
                destination, queries, discovery_strategy
            )
            
            # Phase 5: Post-Processing and Quality Validation
            final_content_dicts = await self._post_process_content(discovery_results, discovery_strategy)
            
            # Convert to WebContent objects
            web_content = []
            for content_dict in final_content_dicts:
                web_content.append(DataConverter.web_content_from_dict(content_dict))
            
            processing_time = time.time() - start_time
            
            # Create standardized result
            result = WebDiscoveryResult(
                destination=destination,
                content=web_content,
                sources_analyzed=len(discovery_results.get('raw_results', [])),
                processing_time=processing_time,
                errors=discovery_results.get('errors', [])
            )
            
            # Update metrics
            self._update_discovery_metrics(result)
            
            self.logger.info(f"✅ Discovery complete for {destination}: {result.sources_successful} sources, avg quality {result.average_quality:.3f}")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"❌ Discovery failed for {destination}: {e}")
            
            return WebDiscoveryResult(
                destination=destination,
                content=[],
                sources_analyzed=0,
                processing_time=processing_time,
                errors=[str(e)]
            )
    
    async def _plan_discovery_strategy(self, destination_profile: Dict[str, Any], 
                                     strategy_config: Dict[str, Any], 
                                     requirements: Dict[str, Any]) -> DiscoveryStrategy:
        """Plan discovery strategy based on destination characteristics"""
        
        # Analyze destination complexity
        destination_type = destination_profile.get('type', 'unknown')
        popularity = destination_profile.get('popularity', 'medium')
        
        # Determine query depth
        if destination_type in ['major_city', 'famous_landmark'] or popularity == 'high':
            query_depth = strategy_config.get('query_depth', 'comprehensive')
            max_sources = strategy_config.get('max_sources', 12)
            source_diversity = 'high'
        elif destination_type in ['regional_city', 'tourist_area'] or popularity == 'medium':
            query_depth = strategy_config.get('query_depth', 'standard')
            max_sources = strategy_config.get('max_sources', 8)
            source_diversity = 'medium'
        else:
            query_depth = strategy_config.get('query_depth', 'basic')
            max_sources = strategy_config.get('max_sources', 6)
            source_diversity = 'low'
        
        quality_threshold = requirements.get('quality_threshold', 0.7)
        
        return DiscoveryStrategy(
            query_depth=query_depth,
            source_diversity=source_diversity,
            max_sources=max_sources,
            quality_threshold=quality_threshold,
            fallback_enabled=True
        )
    
    async def _discover_with_quality_control(self, destination: str, queries: List[str], 
                                           strategy: DiscoveryStrategy) -> Dict[str, Any]:
        """Perform discovery with real-time quality control"""
        
        all_results = []
        errors = []
        
        try:
            # Primary discovery using existing tool
            primary_results = await self.web_discovery_tool.discover_destination_content(destination)
            
            if primary_results and primary_results.get('content'):
                all_results.extend(primary_results['content'])
                self.logger.info(f"Primary discovery found {len(primary_results['content'])} sources")
            
            # If quality is insufficient, try enhanced queries
            current_quality = await self.quality_assessor.assess_batch_quality(all_results)
            
            if current_quality < strategy.quality_threshold and len(queries) > 0:
                self.logger.info(f"Current quality {current_quality:.3f} below threshold {strategy.quality_threshold:.3f}, trying enhanced queries")
                
                # Use enhanced query strategy
                enhanced_results = await self._execute_enhanced_queries(destination, queries[:3])
                if enhanced_results:
                    all_results.extend(enhanced_results)
            
            # Final quality check and source limitation
            if len(all_results) > strategy.max_sources:
                # Prioritize by quality
                sorted_results = await self.quality_assessor.rank_sources(all_results)
                all_results = sorted_results[:strategy.max_sources]
            
        except Exception as e:
            errors.append(f"Discovery error: {str(e)}")
            self.logger.error(f"Error in quality-controlled discovery: {e}")
        
        return {
            'raw_results': all_results,
            'errors': errors,
            'final_count': len(all_results)
        }
    
    async def _execute_enhanced_queries(self, destination: str, enhanced_queries: List[str]) -> List[Dict[str, Any]]:
        """Execute enhanced queries for better content discovery"""
        
        enhanced_results = []
        
        if self.web_discovery_logic:
            try:
                async with self.web_discovery_logic:
                    for query in enhanced_queries:
                        try:
                            query_results = await self.web_discovery_logic._fetch_brave_search(query)
                            
                            # Extract content from top results
                            for result in query_results[:3]:  # Top 3 per query
                                url = result.get('url')
                                if url:
                                    content = await self.web_discovery_logic._fetch_page_content(url, destination)
                                    if content:
                                        enhanced_results.append({
                                            'url': url,
                                            'title': result.get('title', ''),
                                            'content': content,
                                            'relevance_score': 0.8,  # Enhanced query results get higher score
                                            'source': 'enhanced_query'
                                        })
                                        
                        except Exception as e:
                            self.logger.warning(f"Enhanced query failed for '{query}': {e}")
                            continue
                            
            except Exception as e:
                self.logger.error(f"Enhanced query execution failed: {e}")
        
        return enhanced_results
    
    async def _post_process_content(self, discovery_results: Dict[str, Any], 
                                  strategy: DiscoveryStrategy) -> List[Dict[str, Any]]:
        """Post-process discovered content with quality enhancement"""
        
        raw_results = discovery_results.get('raw_results', [])
        
        if not raw_results:
            return []
        
        # Quality filtering
        quality_filtered = []
        for result in raw_results:
            quality_score = await self.quality_assessor.assess_content_quality(result)
            
            if quality_score >= self.min_content_quality:
                result['quality_score'] = quality_score
                quality_filtered.append(result)
        
        # Diversity enhancement
        if strategy.source_diversity == 'high':
            diverse_results = await self._enhance_source_diversity(quality_filtered)
        else:
            diverse_results = quality_filtered
        
        # Final ranking and selection
        final_results = await self.quality_assessor.rank_sources(diverse_results)
        
        return final_results[:strategy.max_sources]
    
    async def _enhance_source_diversity(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance source diversity by domain distribution"""
        
        from urllib.parse import urlparse
        
        domain_counts = {}
        diverse_results = []
        max_per_domain = 3
        
        # Sort by quality first
        sorted_results = sorted(results, key=lambda x: x.get('quality_score', 0.5), reverse=True)
        
        for result in sorted_results:
            url = result.get('url', '')
            domain = urlparse(url).netloc
            
            current_count = domain_counts.get(domain, 0)
            
            if current_count < max_per_domain:
                diverse_results.append(result)
                domain_counts[domain] = current_count + 1
        
        return diverse_results
    
    def _calculate_average_quality(self, content: List[Dict[str, Any]]) -> float:
        """Calculate average quality score of content"""
        if not content:
            return 0.0
        
        total_quality = sum(item.get('quality_score', 0.5) for item in content)
        return total_quality / len(content)
    
    def _update_discovery_metrics(self, result: WebDiscoveryResult):
        """Update agent performance metrics"""
        self.discovery_metrics['total_discoveries'] += 1
        
        if result.sources_successful > 0:
            self.discovery_metrics['successful_discoveries'] += 1
        
        # Update running averages
        total = self.discovery_metrics['total_discoveries']
        self.discovery_metrics['average_sources_per_destination'] = (
            (self.discovery_metrics['average_sources_per_destination'] * (total - 1) + result.sources_successful) / total
        )
        self.discovery_metrics['average_quality_score'] = (
            (self.discovery_metrics['average_quality_score'] * (total - 1) + result.average_quality) / total
        )
    
    # Message handlers
    
    async def _handle_discovery_request(self, message: AgentMessage):
        """Handle discovery request message"""
        task_data = message.payload
        
        try:
            result = await self._execute_discovery(task_data)
            
            # Convert result to dict for message payload
            result_dict = {
                'destination': result.destination,
                'content': [
                    {
                        'url': content.url,
                        'title': content.title,
                        'content': content.content,
                        'relevance_score': content.relevance_score,
                        'quality_score': content.quality_score,
                        'authority_score': content.authority_score,
                        'metadata': content.metadata
                    } for content in result.content
                ],
                'sources_analyzed': result.sources_analyzed,
                'sources_successful': result.sources_successful,
                'average_quality': result.average_quality,
                'processing_time': result.processing_time,
                'errors': result.errors
            }
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="discovery_response",
                payload={'result': result_dict},
                correlation_id=message.message_id
            )
            
        except Exception as e:
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="error_response",
                payload={'error': str(e)},
                correlation_id=message.message_id
            )
        
        await self.send_message(response)
    
    async def _handle_quality_assessment(self, message: AgentMessage):
        """Handle quality assessment request"""
        content = message.payload.get('content', [])
        
        try:
            quality_score = await self.quality_assessor.assess_batch_quality(content)
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="quality_response",
                payload={'quality_score': quality_score},
                correlation_id=message.message_id
            )
            
        except Exception as e:
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="error_response",
                payload={'error': str(e)},
                correlation_id=message.message_id
            )
        
        await self.send_message(response)
    
    async def _handle_query_generation(self, message: AgentMessage):
        """Handle query generation request"""
        destination = message.payload.get('destination')
        strategy = message.payload.get('strategy', {})
        
        try:
            destination_profile = await self.destination_analyzer.analyze_destination(destination)
            discovery_strategy = DiscoveryStrategy(**strategy) if strategy else DiscoveryStrategy('standard', 'medium', 8, 0.7)
            
            queries = await self.query_generator.generate_queries(destination, discovery_strategy, destination_profile)
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="queries_response",
                payload={'queries': queries},
                correlation_id=message.message_id
            )
            
        except Exception as e:
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="error_response",
                payload={'error': str(e)},
                correlation_id=message.message_id
            )
        
        await self.send_message(response)

# Intelligence Components

class DestinationAnalyzer:
    """Analyzes destination characteristics for discovery strategy planning"""
    
    async def analyze_destination(self, destination: str) -> Dict[str, Any]:
        """Analyze destination to determine characteristics"""
        
        destination_lower = destination.lower()
        
        # Destination type classification
        if any(city in destination_lower for city in ['tokyo', 'paris', 'london', 'new york', 'rome', 'barcelona']):
            dest_type = 'major_city'
            popularity = 'high'
        elif any(keyword in destination_lower for keyword in ['city', 'town', 'capital']):
            dest_type = 'regional_city'
            popularity = 'medium'
        elif any(keyword in destination_lower for keyword in ['island', 'beach', 'mountain', 'park']):
            dest_type = 'natural_area'
            popularity = 'medium'
        else:
            dest_type = 'general'
            popularity = 'low'
        
        # Language and region hints
        if any(country in destination_lower for country in ['japan', 'china', 'korea', 'thailand']):
            region = 'asia'
        elif any(country in destination_lower for country in ['france', 'italy', 'spain', 'germany', 'uk']):
            region = 'europe'
        elif any(country in destination_lower for country in ['usa', 'canada', 'mexico']):
            region = 'north_america'
        else:
            region = 'unknown'
        
        return {
            'type': dest_type,
            'popularity': popularity,
            'region': region,
            'complexity': 'high' if dest_type == 'major_city' else 'medium'
        }

class IntelligentQueryGenerator:
    """Generates intelligent queries based on destination analysis"""
    
    async def generate_queries(self, destination: str, strategy: DiscoveryStrategy, 
                             destination_profile: Dict[str, Any]) -> List[str]:
        """Generate intelligent queries for destination discovery"""
        
        base_queries = [
            f"{destination} travel guide attractions",
            f"{destination} things to do experiences", 
            f"{destination} local culture food",
        ]
        
        dest_type = destination_profile.get('type', 'general')
        region = destination_profile.get('region', 'unknown')
        
        # Type-specific queries
        if dest_type == 'major_city':
            base_queries.extend([
                f"{destination} hidden gems local secrets",
                f"{destination} neighborhood guide districts",
                f"{destination} best restaurants local food",
                f"{destination} museums galleries cultural sites",
                f"{destination} nightlife entertainment"
            ])
        elif dest_type == 'natural_area':
            base_queries.extend([
                f"{destination} outdoor activities hiking",
                f"{destination} scenic views photography",
                f"{destination} wildlife nature tours"
            ])
        
        # Region-specific queries
        if region == 'asia':
            base_queries.extend([
                f"{destination} traditional culture temples",
                f"{destination} local markets street food"
            ])
        elif region == 'europe':
            base_queries.extend([
                f"{destination} historical sites architecture",
                f"{destination} art museums galleries"
            ])
        
        # Strategy-based filtering
        if strategy.query_depth == 'comprehensive':
            return base_queries
        elif strategy.query_depth == 'standard':
            return base_queries[:6]
        else:  # basic
            return base_queries[:4]

class ContentQualityAssessor:
    """Assesses and ranks content quality"""
    
    async def assess_content_quality(self, content_item: Dict[str, Any]) -> float:
        """Assess quality of a single content item"""
        
        content = content_item.get('content', '')
        title = content_item.get('title', '')
        url = content_item.get('url', '')
        
        quality_score = 0.0
        
        # Content length score (0.3 weight)
        content_length = len(content)
        if content_length > 1000:
            quality_score += 0.3
        elif content_length > 500:
            quality_score += 0.2
        elif content_length > 200:
            quality_score += 0.1
        
        # Title quality score (0.2 weight)
        if title and len(title) > 10:
            quality_score += 0.2
        elif title:
            quality_score += 0.1
        
        # URL authority score (0.3 weight)
        authority_domains = [
            'lonelyplanet.com', 'tripadvisor.com', 'booking.com', 'expedia.com',
            'timeout.com', 'fodors.com', 'frommers.com', 'ricksteves.com'
        ]
        
        if any(domain in url for domain in authority_domains):
            quality_score += 0.3
        elif any(ext in url for ext in ['.gov', '.edu', '.org']):
            quality_score += 0.25
        else:
            quality_score += 0.1
        
        # Content relevance score (0.2 weight)
        travel_keywords = [
            'travel', 'tourism', 'visit', 'attraction', 'destination', 'guide',
            'hotel', 'restaurant', 'museum', 'tour', 'experience'
        ]
        
        content_lower = content.lower()
        keyword_matches = sum(1 for keyword in travel_keywords if keyword in content_lower)
        
        if keyword_matches >= 5:
            quality_score += 0.2
        elif keyword_matches >= 3:
            quality_score += 0.15
        elif keyword_matches >= 1:
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    async def assess_batch_quality(self, content_batch: List[Dict[str, Any]]) -> float:
        """Assess quality of a batch of content"""
        if not content_batch:
            return 0.0
        
        total_quality = 0.0
        for item in content_batch:
            quality = await self.assess_content_quality(item)
            total_quality += quality
        
        return total_quality / len(content_batch)
    
    async def rank_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank sources by quality score"""
        
        # Assess quality for each source
        for source in sources:
            if 'quality_score' not in source:
                source['quality_score'] = await self.assess_content_quality(source)
        
        # Sort by quality score (descending)
        return sorted(sources, key=lambda x: x.get('quality_score', 0.0), reverse=True) 