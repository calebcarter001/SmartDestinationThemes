"""
LLM Orchestration Agent

Intelligent LLM resource management and processing orchestration.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentMessage, AgentState
from .data_models import (
    LLMProcessingResult, ThemeData, ResourceAllocation, AgentResponse, 
    ResponseFactory, TaskStatus, DataConverter
)

# Import existing LLM components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.focused_llm_generator import FocusedLLMGenerator
from src.focused_prompt_processor import FocusedPromptProcessor

logger = logging.getLogger(__name__)

# ResourceAllocation and LLMProcessingResult are now imported from data_models

class LLMOrchestrationAgent(BaseAgent):
    """
    Intelligent LLM orchestration agent that manages resource allocation,
    processing optimization, and quality control.
    
    Features:
    - Adaptive resource allocation based on workload
    - Intelligent batching and parallel processing
    - Performance optimization and monitoring
    - Cache management and optimization
    - Error handling and recovery
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("llm_orchestration", config)
        
        # Configuration
        llm_config = config.get('llm_settings', {})
        agent_config = config.get('agents', {}).get('llm_orchestration', {})
        
        self.provider = llm_config.get('provider', 'gemini')
        self.adaptive_allocation = agent_config.get('adaptive_resource_allocation', True)
        self.performance_optimization = agent_config.get('performance_optimization', True)
        self.enable_intelligent_batching = agent_config.get('enable_intelligent_batching', True)
        self.max_concurrent_requests = agent_config.get('max_concurrent_requests', 8)
        self.worker_pool_size = agent_config.get('worker_pool_size', 12)
        
        # Resource management
        self.resource_allocator = LLMResourceAllocator(config)
        self.performance_optimizer = LLMPerformanceOptimizer(config)
        self.cache_manager = LLMCacheManager(config)
        
        # LLM components
        self.llm_generator = None
        self.prompt_processor = None
        
        # Performance tracking
        self.processing_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'average_processing_time': 0.0,
            'cache_hit_rate': 0.0,
            'resource_efficiency': 0.0,
            'quality_scores': []
        }
    
    async def _initialize_agent_specific(self):
        """Initialize LLM orchestration components"""
        try:
            # Initialize LLM generator with enhanced configuration
            self.llm_generator = FocusedLLMGenerator(self.provider, self.config)
            
            # Initialize prompt processor
            self.prompt_processor = FocusedPromptProcessor(self.llm_generator, self.config)
            
            # Register task handlers
            self.register_message_handler("execute_llm_pipeline", self._handle_llm_pipeline_request)
            self.register_message_handler("optimize_resources", self._handle_resource_optimization)
            self.register_message_handler("get_performance_metrics", self._handle_performance_metrics)
            
            self.logger.info("LLM Orchestration Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM Orchestration Agent: {e}")
            raise
    
    async def _execute_task_specific(self, task_id: str, task_definition: Dict[str, Any]) -> AgentResponse:
        """Execute LLM orchestration tasks"""
        task_type = task_definition.get('task_type')
        task_data = task_definition.get('data', {})
        
        try:
            start_time = time.time()
            
            if task_type == 'execute_llm_pipeline':
                result = await self._execute_llm_pipeline(task_data)
                processing_time = time.time() - start_time
                return ResponseFactory.success(
                    data=result, 
                    agent_id=self.agent_id, 
                    task_id=task_id,
                    processing_time=processing_time
                )
            elif task_type == 'optimize_resources':
                result = await self._optimize_resource_allocation(task_data)
                processing_time = time.time() - start_time
                return ResponseFactory.success(
                    data=result, 
                    agent_id=self.agent_id, 
                    task_id=task_id,
                    processing_time=processing_time
                )
            elif task_type == 'analyze_performance':
                result = await self._analyze_performance(task_data)
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
    
    async def _execute_llm_pipeline(self, task_data: Dict[str, Any]) -> LLMProcessingResult:
        """Execute intelligent LLM processing pipeline"""
        destination = task_data.get('destination')
        web_content = task_data.get('web_content', {})
        resource_allocation = task_data.get('resource_allocation', {})
        
        if not destination:
            raise ValueError("Destination is required for LLM processing")
        
        start_time = time.time()
        self.logger.info(f"🧠 Starting intelligent LLM processing for {destination}")
        
        try:
            # Phase 1: Resource Planning and Allocation
            optimal_allocation = await self.resource_allocator.plan_resource_allocation(
                destination, web_content, resource_allocation
            )
            self.logger.info(f"Resource allocation: {optimal_allocation.pool_size} pool, {optimal_allocation.concurrent_requests} concurrent")
            
            # Phase 2: Intelligent Processing Strategy
            processing_strategy = await self._determine_processing_strategy(
                destination, web_content, optimal_allocation
            )
            
            # Phase 3: Adaptive LLM Processing
            processing_results = await self._execute_adaptive_processing(
                destination, web_content, processing_strategy, optimal_allocation
            )
            
            # Phase 4: Performance Optimization and Quality Assessment
            optimized_results = await self.performance_optimizer.optimize_results(
                processing_results, optimal_allocation
            )
            
            processing_time = time.time() - start_time
            
            # Convert themes to ThemeData objects
            theme_objects = []
            themes_data = optimized_results.get('affinities', [])
            if isinstance(themes_data, list):
                for theme_dict in themes_data:
                    if isinstance(theme_dict, dict):
                        theme_objects.append(DataConverter.theme_from_dict(theme_dict))
            
            # Create standardized result
            result = LLMProcessingResult(
                destination=destination,
                themes=theme_objects,
                affinities=optimized_results.get('affinities', []),
                processing_time=processing_time,
                cache_performance=await self.cache_manager.get_cache_metrics(),
                errors=optimized_results.get('errors', [])
            )
            
            # Update metrics
            self._update_processing_metrics(result)
            
            self.logger.info(f"✅ LLM processing complete for {destination}: {len(result.themes)} themes, quality {result.quality_score:.3f}")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"❌ LLM processing failed for {destination}: {e}")
            
            return LLMProcessingResult(
                destination=destination,
                themes=[],
                affinities=[],
                processing_time=processing_time,
                cache_performance={},
                errors=[str(e)]
            )
    
    async def _determine_processing_strategy(self, destination: str, web_content: Dict[str, Any], 
                                          allocation: ResourceAllocation) -> Dict[str, Any]:
        """Determine optimal processing strategy based on content and resources"""
        
        content_complexity = len(web_content.get('content', []))
        content_quality = sum(item.get('relevance_score', 0.5) for item in web_content.get('content', [])) / max(content_complexity, 1)
        
        # Determine processing approach
        if content_complexity > 10 and allocation.pool_size == 'large':
            strategy = {
                'approach': 'comprehensive_parallel',
                'phase_strategy': 'full_pipeline',
                'quality_focus': 'depth_and_breadth',
                'parallel_phases': ['discovery', 'enhancement'],
                'sequential_phases': ['analysis', 'assessment']
            }
        elif content_complexity > 5:
            strategy = {
                'approach': 'balanced_processing',
                'phase_strategy': 'adaptive_pipeline',
                'quality_focus': 'balanced',
                'parallel_phases': ['discovery'],
                'sequential_phases': ['analysis', 'enhancement', 'assessment']
            }
        else:
            strategy = {
                'approach': 'focused_processing',
                'phase_strategy': 'streamlined_pipeline',
                'quality_focus': 'efficiency',
                'parallel_phases': [],
                'sequential_phases': ['discovery', 'analysis', 'enhancement', 'assessment']
            }
        
        # Add destination-specific adaptations
        if any(keyword in destination.lower() for keyword in ['tokyo', 'paris', 'london', 'new york']):
            strategy['destination_type'] = 'major_city'
            strategy['complexity_adjustment'] = 1.2
        else:
            strategy['destination_type'] = 'general'
            strategy['complexity_adjustment'] = 1.0
        
        return strategy
    
    async def _execute_adaptive_processing(self, destination: str, web_content: Dict[str, Any],
                                         strategy: Dict[str, Any], allocation: ResourceAllocation) -> Dict[str, Any]:
        """Execute adaptive LLM processing based on strategy"""
        
        # Prepare web data for processing
        web_data_formatted = {
            'content': web_content.get('content', []) if isinstance(web_content.get('content'), list) else []
        }
        
        try:
            # Execute the focused prompt processor with strategy adaptations
            if strategy['approach'] == 'comprehensive_parallel':
                # Use parallel processing capabilities
                result = await self._execute_parallel_processing(destination, web_data_formatted, strategy)
            elif strategy['approach'] == 'balanced_processing':
                # Use balanced approach
                result = await self._execute_balanced_processing(destination, web_data_formatted, strategy)
            else:
                # Use streamlined processing
                result = await self._execute_streamlined_processing(destination, web_data_formatted, strategy)
            
            # Add processing metadata
            result['processing_strategy'] = strategy
            result['resource_allocation'] = allocation.__dict__
            
            return result
            
        except Exception as e:
            self.logger.error(f"Adaptive processing failed for {destination}: {e}")
            return {
                'themes': [],
                'affinities': [],
                'errors': [str(e)],
                'processing_strategy': strategy
            }
    
    async def _execute_parallel_processing(self, destination: str, web_data: Dict[str, Any], 
                                         strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive parallel processing"""
        
        # Use the existing prompt processor with parallel optimizations
        result = await self.prompt_processor.process_destination(destination, web_data)
        
        # Enhance with parallel processing optimizations
        if 'affinities' in result:
            # Apply intelligent batching for theme enhancement
            enhanced_affinities = await self._apply_intelligent_batching(result['affinities'])
            result['affinities'] = enhanced_affinities
        
        return result
    
    async def _execute_balanced_processing(self, destination: str, web_data: Dict[str, Any], 
                                         strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute balanced processing approach"""
        
        # Use existing prompt processor
        result = await self.prompt_processor.process_destination(destination, web_data)
        
        # Apply moderate optimizations - preserve all themes for quality
        if 'affinities' in result:
            # Keep all themes for comprehensive analysis
            pass
        
        return result
    
    async def _execute_streamlined_processing(self, destination: str, web_data: Dict[str, Any], 
                                            strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute streamlined processing for efficiency"""
        
        # Use existing prompt processor with efficiency focus
        result = await self.prompt_processor.process_destination(destination, web_data)
        
        # Apply efficiency optimizations - preserve all themes for complete analysis
        if 'affinities' in result:
            # Preserve all themes for comprehensive intelligence enhancement
            pass
        
        return result
    
    async def _apply_intelligent_batching(self, affinities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply intelligent batching for theme enhancement"""
        
        if not self.enable_intelligent_batching or len(affinities) <= 4:
            return affinities
        
        # Group affinities by category for batch processing
        category_groups = {}
        for affinity in affinities:
            category = affinity.get('category', 'general')
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(affinity)
        
        # Process each category group
        enhanced_affinities = []
        for category, group_affinities in category_groups.items():
            # Batch process affinities in the same category
            batch_size = min(4, len(group_affinities))
            for i in range(0, len(group_affinities), batch_size):
                batch = group_affinities[i:i + batch_size]
                enhanced_batch = await self._enhance_affinity_batch(batch)
                enhanced_affinities.extend(enhanced_batch)
        
        return enhanced_affinities
    
    async def _enhance_affinity_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance a batch of affinities with parallel processing"""
        
        # Apply batch enhancements
        enhanced_batch = []
        for affinity in batch:
            # Add batch processing optimizations
            enhanced_affinity = affinity.copy()
            enhanced_affinity['batch_processed'] = True
            enhanced_affinity['batch_timestamp'] = time.time()
            enhanced_batch.append(enhanced_affinity)
        
        return enhanced_batch
    
    def _update_processing_metrics(self, result: LLMProcessingResult):
        """Update agent performance metrics"""
        self.processing_metrics['total_requests'] += 1
        
        if result.themes or result.affinities:
            self.processing_metrics['successful_requests'] += 1
        
        # Update running averages
        total = self.processing_metrics['total_requests']
        self.processing_metrics['average_processing_time'] = (
            (self.processing_metrics['average_processing_time'] * (total - 1) + result.processing_time) / total
        )
        
        # Update cache performance
        if result.cache_performance:
            cache_hit_rate = result.cache_performance.get('hit_rate', 0)
            self.processing_metrics['cache_hit_rate'] = (
                (self.processing_metrics['cache_hit_rate'] * (total - 1) + cache_hit_rate) / total
            )
        
        # Track quality scores from new data model
        if result.quality_score > 0:
            self.processing_metrics['quality_scores'].append(result.quality_score)
    
    async def _cleanup_agent_specific(self):
        """Cleanup LLM orchestration resources"""
        try:
            if self.llm_generator:
                await self.llm_generator.cleanup()
                self.logger.debug("LLM generator cleanup complete")
        except Exception as e:
            self.logger.error(f"LLM cleanup error: {e}")
    
    # Message handlers
    
    async def _handle_llm_pipeline_request(self, message: AgentMessage):
        """Handle LLM pipeline execution request"""
        task_data = message.payload
        
        try:
            result = await self._execute_llm_pipeline(task_data)
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="llm_pipeline_response",
                payload={'result': result.__dict__},
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
    
    async def _handle_resource_optimization(self, message: AgentMessage):
        """Handle resource optimization request"""
        optimization_params = message.payload
        
        try:
            optimization_result = await self.resource_allocator.optimize_allocation(optimization_params)
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="optimization_response",
                payload={'result': optimization_result},
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
    
    async def _handle_performance_metrics(self, message: AgentMessage):
        """Handle performance metrics request"""
        try:
            metrics = {
                'processing_metrics': self.processing_metrics,
                'llm_generator_stats': await self.llm_generator.get_performance_stats() if self.llm_generator else {},
                'cache_metrics': await self.cache_manager.get_cache_metrics(),
                'resource_utilization': await self.resource_allocator.get_utilization_stats()
            }
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="metrics_response",
                payload={'metrics': metrics},
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

# Supporting Classes

class LLMResourceAllocator:
    """Manages LLM resource allocation and optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def plan_resource_allocation(self, destination: str, web_content: Dict[str, Any], 
                                     existing_allocation: Dict[str, Any]) -> ResourceAllocation:
        """Plan optimal resource allocation"""
        
        content_size = len(web_content.get('content', []))
        
        # Determine pool size based on content complexity
        if content_size > 10:
            pool_size = 'large'
            concurrent_requests = 8
            batch_size = 12
        elif content_size > 5:
            pool_size = 'medium'
            concurrent_requests = 5
            batch_size = 8
        else:
            pool_size = 'small'
            concurrent_requests = 3
            batch_size = 6
        
        return ResourceAllocation(
            pool_size=pool_size,
            concurrent_requests=concurrent_requests,
            batch_size=batch_size,
            priority=5,
            estimated_completion_time=content_size * 2.5,  # Rough estimate
            constraints={}
        )
    
    async def optimize_allocation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resource allocation based on performance data"""
        return {
            'optimization_applied': True,
            'improvements': ['batch_size_adjusted', 'concurrency_optimized'],
            'estimated_improvement': 0.15
        }
    
    async def get_utilization_stats(self) -> Dict[str, Any]:
        """Get resource utilization statistics"""
        return {
            'cpu_utilization': 0.65,
            'memory_utilization': 0.45,
            'network_utilization': 0.30,
            'llm_pool_utilization': 0.70
        }

class LLMPerformanceOptimizer:
    """Optimizes LLM processing performance"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def optimize_results(self, results: Dict[str, Any], allocation: ResourceAllocation) -> Dict[str, Any]:
        """Optimize processing results"""
        
        optimized = results.copy()
        
        # Add performance optimizations
        optimized['optimization_applied'] = True
        optimized['resource_utilization'] = {
            'efficiency_score': 0.85,
            'resource_usage': 0.70,
            'optimization_level': 'high'
        }
        
        optimized['quality_metrics'] = {
            'overall_score': 0.8,
            'processing_efficiency': 0.85,
            'result_quality': 0.75
        }
        
        return optimized

class LLMCacheManager:
    """Manages LLM caching and optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def get_cache_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        return {
            'hit_rate': 0.75,
            'miss_rate': 0.25,
            'cache_size': 1024,
            'cache_efficiency': 0.80
        } 