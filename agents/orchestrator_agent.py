"""
Orchestrator Agent

Coordinates all major process agents for intelligent destination processing workflow.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from .base_agent import BaseAgent, AgentMessage, AgentState
from .web_discovery_agent import WebDiscoveryAgent
from .llm_orchestration_agent import LLMOrchestrationAgent
from .intelligence_enhancement_agent import IntelligenceEnhancementAgent
from .evidence_validation_agent import EvidenceValidationAgent
from .quality_assurance_agent import QualityAssuranceAgent
from .seasonal_image_agent import SeasonalImageAgent
from .data_models import WorkflowResult

logger = logging.getLogger(__name__)

@dataclass
class WorkflowState:
    """State tracking for destination processing workflow"""
    workflow_id: str
    destination: str
    current_phase: str
    phase_results: Dict[str, Any]
    start_time: datetime
    estimated_completion: Optional[datetime] = None
    quality_metrics: Dict[str, float] = None
    resource_allocation: Dict[str, Any] = None
    error_count: int = 0
    retry_count: int = 0

# WorkflowResult is now imported from data_models

class AgentOrchestrator(BaseAgent):
    """
    Central orchestrator that coordinates all major process agents.
    
    Manages:
    - Workflow state and dependencies
    - Resource allocation across agents
    - Error handling and recovery
    - Performance optimization
    - Quality assurance throughout pipeline
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("orchestrator", config)
        
        # Agent configuration
        agent_config = config.get('agents', {})
        self.parallel_destinations = agent_config.get('max_parallel_destinations', 3)
        self.quality_threshold = agent_config.get('quality_threshold', 0.75)
        self.max_workflow_retries = agent_config.get('max_workflow_retries', 2)
        
        # Initialize process agents
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_channels: Dict[str, asyncio.Queue] = {}
        
        # Workflow management
        self.active_workflows: Dict[str, WorkflowState] = {}
        self.completed_workflows: Dict[str, WorkflowResult] = {}
        
        # Resource management
        self.resource_allocator = ResourceAllocator(config)
        self.decision_engine = DecisionEngine(config)
        
    async def _initialize_agent_specific(self):
        """Initialize all process agents"""
        self.logger.info("Initializing process agents...")
        
        try:
            # Create agent instances
            self.agents['web_discovery'] = WebDiscoveryAgent(self.config)
            self.agents['llm_orchestration'] = LLMOrchestrationAgent(self.config)
            self.agents['intelligence_enhancement'] = IntelligenceEnhancementAgent(self.config)
            self.agents['evidence_validation'] = EvidenceValidationAgent(self.config)
            self.agents['seasonal_image'] = SeasonalImageAgent(self.config)
            self.agents['quality_assurance'] = QualityAssuranceAgent(self.config)
            
            # Initialize agents and set up communication channels
            for agent_id, agent in self.agents.items():
                # Create communication channel
                channel = asyncio.Queue(maxsize=100)
                self.agent_channels[agent_id] = channel
                agent.set_orchestrator_channel(self.message_queue)
                
                # Initialize agent
                success = await agent.initialize()
                if not success:
                    raise Exception(f"Failed to initialize agent: {agent_id}")
                
                self.logger.info(f"✅ Initialized {agent_id} agent")
            
            # Register workflow message handlers
            self.register_message_handler("workflow_request", self._handle_workflow_request)
            self.register_message_handler("agent_response", self._handle_agent_response)
            self.register_message_handler("quality_intervention", self._handle_quality_intervention)
            
            self.logger.info("All process agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize process agents: {e}")
            raise
    
    async def _execute_task_specific(self, task_id: str, task_definition: Dict[str, Any]) -> Any:
        """Execute orchestrator-specific tasks"""
        task_type = task_definition.get('task_type')
        task_data = task_definition.get('data', {})
        
        if task_type == 'process_destination_workflow':
            destination = task_data.get('destination')
            if not destination:
                raise ValueError("Destination is required for workflow processing")
            
            # Execute workflow for single destination
            result = await self._execute_destination_workflow(
                f"task_{task_id}_{destination.lower().replace(' ', '_').replace(',', '')}", 
                destination
            )
            return result.__dict__ if hasattr(result, '__dict__') else result
            
        elif task_type == 'process_multiple_destinations':
            destinations = task_data.get('destinations', [])
            if not destinations:
                raise ValueError("Destinations list is required")
            
            # Execute workflow for multiple destinations
            results = await self.execute_workflow(destinations)
            return {'workflow_results': {k: v.__dict__ if hasattr(v, '__dict__') else v for k, v in results.items()}}
            
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def execute_workflow(self, destinations: List[str]) -> Dict[str, WorkflowResult]:
        """Execute the complete workflow for multiple destinations"""
        self.logger.info(f"🚀 Starting workflow execution for {len(destinations)} destinations")
        
        # Create workflow instances
        workflow_tasks = []
        for destination in destinations:
            workflow_id = f"workflow_{destination.lower().replace(' ', '_').replace(',', '')}_{int(time.time())}"
            task = asyncio.create_task(
                self._execute_destination_workflow(workflow_id, destination)
            )
            workflow_tasks.append(task)
        
        # Execute workflows with controlled parallelism
        semaphore = asyncio.Semaphore(self.parallel_destinations)
        
        async def execute_with_semaphore(task):
            async with semaphore:
                return await task
        
        # Wait for all workflows to complete
        results = await asyncio.gather(
            *[execute_with_semaphore(task) for task in workflow_tasks],
            return_exceptions=True
        )
        
        # Process results
        final_results = {}
        for i, result in enumerate(results):
            destination = destinations[i]
            if isinstance(result, Exception):
                self.logger.error(f"Workflow failed for {destination}: {result}")
                final_results[destination] = WorkflowResult(
                    workflow_id=f"failed_{destination}",
                    destination=destination,
                    success=False,
                    final_data={},
                    processing_time=0.0,
                    quality_score=0.0,
                    phases_completed=[],
                    error_messages=[str(result)],
                    performance_metrics={}
                )
            else:
                final_results[destination] = result
        
        self.logger.info(f"🎉 Workflow execution complete: {len([r for r in final_results.values() if r.success])}/{len(destinations)} successful")
        return final_results
    
    async def _execute_destination_workflow(self, workflow_id: str, destination: str) -> WorkflowResult:
        """Execute workflow for a single destination"""
        start_time = time.time()
        workflow_state = WorkflowState(
            workflow_id=workflow_id,
            destination=destination,
            current_phase="initialization",
            phase_results={},
            start_time=datetime.now()
        )
        
        self.active_workflows[workflow_id] = workflow_state
        
        try:
            self.logger.info(f"🎯 Starting workflow for {destination}")
            
            # Phase 1: Web Discovery with intelligent strategy
            self.logger.info(f"📊 Phase 1: Web Discovery for {destination}")
            workflow_state.current_phase = "web_discovery"
            
            discovery_strategy = await self.decision_engine.plan_discovery_strategy(destination)
            discovery_task_result = await self._execute_agent_task(
                'web_discovery',
                'execute_discovery',
                {
                    'destination': destination,
                    'strategy': discovery_strategy,
                    'requirements': {'quality_threshold': self.quality_threshold}
                }
            )
            
            # Extract the actual DiscoveryResult from the task result
            if hasattr(discovery_task_result, 'data') and discovery_task_result.data:
                # AgentResponse format - use .data property
                discovery_result = discovery_task_result.data
            elif hasattr(discovery_task_result, 'result'):
                # Legacy format - use .result property
                discovery_result = discovery_task_result.result
            elif isinstance(discovery_task_result, dict):
                # Dict format - may contain nested AgentResponse
                nested_result = discovery_task_result.get('result')
                
                # Check if nested result is an AgentResponse
                if hasattr(nested_result, 'data') and nested_result.data:
                    discovery_result = nested_result.data
                else:
                    discovery_result = nested_result
            else:
                discovery_result = discovery_task_result
            
            workflow_state.phase_results['web_discovery'] = discovery_result
            
            # Quality gate: Check discovery quality
            discovery_quality = await self._assess_phase_quality('web_discovery', discovery_result)
            if discovery_quality < 0.5 and workflow_state.retry_count < self.max_workflow_retries:
                self.logger.warning(f"Discovery quality low ({discovery_quality:.2f}), retrying...")
                workflow_state.retry_count += 1
                return await self._execute_destination_workflow(workflow_id, destination)
            
            # Phase 2: LLM Processing with adaptive resource allocation
            self.logger.info(f"🧠 Phase 2: LLM Processing for {destination}")
            workflow_state.current_phase = "llm_processing"
            
            # Convert DiscoveryResult to dict for resource allocation
            discovery_dict = discovery_result.__dict__ if hasattr(discovery_result, '__dict__') else discovery_result
            llm_resources = await self.resource_allocator.allocate_llm_resources(
                discovery_dict, workflow_state.resource_allocation
            )
            
            # Format web content for LLM processing
            content_list = discovery_result.content if hasattr(discovery_result, 'content') else []
            
            # Convert WebContent objects to dictionaries for agents
            content_dicts = []
            for content_item in content_list:
                if hasattr(content_item, '__dict__'):
                    # WebContent object - convert to dict
                    content_dict = {
                        'url': getattr(content_item, 'url', ''),
                        'title': getattr(content_item, 'title', ''),
                        'content': getattr(content_item, 'content', ''),
                        'relevance_score': getattr(content_item, 'relevance_score', 0.5),
                        'quality_score': getattr(content_item, 'quality_score', 0.5),
                        'authority_score': getattr(content_item, 'authority_score', 0.5),
                        'metadata': getattr(content_item, 'metadata', {})
                    }
                    content_dicts.append(content_dict)
                elif isinstance(content_item, dict):
                    # Already a dict
                    content_dicts.append(content_item)
            
            web_content = {
                'content': content_dicts
            }
            
            llm_task_result = await self._execute_agent_task(
                'llm_orchestration',
                'execute_llm_pipeline',
                {
                    'destination': destination,
                    'web_content': web_content,
                    'resource_allocation': llm_resources
                }
            )
            
            # Extract the actual LLMProcessingResult from the task result (same as integration fix)
            if hasattr(llm_task_result, 'data') and llm_task_result.data:
                # AgentResponse format - use .data property
                actual_llm_result = llm_task_result.data
            elif hasattr(llm_task_result, 'result'):
                # Legacy format - use .result property
                actual_llm_result = llm_task_result.result
            elif isinstance(llm_task_result, dict) and 'result' in llm_task_result:
                # AgentResponse dictionary format - extract from 'result' key
                actual_llm_result = llm_task_result['result']
            else:
                actual_llm_result = llm_task_result
            
            workflow_state.phase_results['llm_processing'] = actual_llm_result
            
            # Extract themes for next phases using the actual LLMProcessingResult
            if hasattr(actual_llm_result, '__dict__'):
                # Check if this is an AgentResponse with nested data
                if hasattr(actual_llm_result, 'data') and actual_llm_result.data:
                    # Extract from the nested .data field (LLMProcessingResult)
                    llm_data = actual_llm_result.data
                    themes = getattr(llm_data, 'themes', [])
                    affinities = getattr(llm_data, 'affinities', [])
                else:
                    # Object format (direct LLMProcessingResult)
                    themes = getattr(actual_llm_result, 'themes', [])
                    affinities = getattr(actual_llm_result, 'affinities', [])
            elif isinstance(actual_llm_result, dict):
                # Dictionary format
                themes = actual_llm_result.get('themes', [])
                affinities = actual_llm_result.get('affinities', [])
            else:
                themes = []
                affinities = []
            
            # Phase 3: Parallel Evidence Validation and Intelligence Enhancement
            self.logger.info(f"⚡ Phase 3: Parallel Enhancement for {destination}")
            workflow_state.current_phase = "parallel_enhancement"
            
            # Execute evidence validation and intelligence enhancement in parallel
            evidence_task = self._execute_agent_task(
                'evidence_validation',
                'validate_comprehensive_evidence',
                {
                    'themes': affinities,  # Pass raw affinities for evidence validation
                    'web_sources': web_content,
                    'destination': destination
                }
            )
            
            enhancement_task = self._execute_agent_task(
                'intelligence_enhancement',
                'enhance_themes',
                {
                    'themes': affinities,  # Pass raw affinities for enhancement
                    'destination_context': {'destination': destination},
                    'evidence_data': web_content,  # Pass web content for evidence validation
                    'web_sources': web_content  # Pass web sources for comprehensive processing
                }
            )
            
            evidence_result, enhancement_result = await asyncio.gather(
                evidence_task, enhancement_task, return_exceptions=True
            )
            
            # Store actual result data directly (now receiving unwrapped data objects)
            workflow_state.phase_results['evidence_validation'] = evidence_result
            workflow_state.phase_results['intelligence_enhancement'] = enhancement_result
            
            # Phase 3.5: Seasonal Image Generation (Parallel with processing)
            self.logger.info(f"🎨 Phase 3.5: Seasonal Image Generation for {destination}")
            workflow_state.current_phase = "seasonal_image_generation"
            
            # Determine output directory for images
            output_dir = None
            if workflow_state.resource_allocation:
                output_dir = workflow_state.resource_allocation.get('output_directory')
            
            if not output_dir:
                # Try to extract timestamp from workflow_id for session directory
                import re
                timestamp_match = re.search(r'(\d+)$', workflow_id)
                if timestamp_match:
                    timestamp = timestamp_match.group(1)
                    output_dir = f"outputs/session_agent_{timestamp}"
                else:
                    # Fallback to current timestamp
                    import time
                    current_timestamp = int(time.time())
                    output_dir = f"outputs/session_agent_{current_timestamp}"
            
            # Generate seasonal images
            seasonal_image_result = await self._execute_agent_task(
                'seasonal_image',
                'generate_seasonal_images',
                {
                    'destination': destination,
                    'output_dir': output_dir,
                    'enhanced_themes': workflow_state.phase_results.get('intelligence_enhancement', {}),
                    'workflow_context': {
                        'workflow_id': workflow_id,
                        'destination': destination
                    }
                }
            )
            
            # Store seasonal image results
            workflow_state.phase_results['seasonal_image_generation'] = seasonal_image_result
            
            # Phase 4: Quality Assurance and Final Integration
            self.logger.info(f"🔍 Phase 4: Quality Assurance for {destination}")
            workflow_state.current_phase = "quality_assurance"
            
            qa_result = await self._execute_agent_task(
                'quality_assurance',
                'continuous_quality_monitoring',
                {
                    'workflow_state': workflow_state,
                    'all_results': workflow_state.phase_results
                }
            )
            
            # Store actual result data directly (now receiving unwrapped data objects)
            workflow_state.phase_results['quality_assurance'] = qa_result
            
            # Final Integration
            final_data = await self._integrate_workflow_results(workflow_state)
            final_quality = await self._calculate_final_quality(workflow_state)
            
            processing_time = time.time() - start_time
            
            # Create final result
            result = WorkflowResult(
                workflow_id=workflow_id,
                destination=destination,
                success=True,
                final_data=final_data,
                processing_time=processing_time,
                quality_score=final_quality,
                phases_completed=list(workflow_state.phase_results.keys()),
                error_messages=[],
                performance_metrics=await self._collect_performance_metrics(workflow_state)
            )
            
            self.completed_workflows[workflow_id] = result
            del self.active_workflows[workflow_id]
            
            self.logger.info(f"✅ Workflow complete for {destination}: Quality {final_quality:.3f}, Time {processing_time:.1f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"❌ Workflow failed for {destination}: {e}")
            
            result = WorkflowResult(
                workflow_id=workflow_id,
                destination=destination,
                success=False,
                final_data={},
                processing_time=processing_time,
                quality_score=0.0,
                phases_completed=list(workflow_state.phase_results.keys()),
                error_messages=[str(e)],
                performance_metrics={}
            )
            
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            return result
    
    async def _execute_agent_task(self, agent_id: str, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task on a specific agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            raise Exception(f"Agent {agent_id} not found")
        
        task_id = f"{agent_id}_{task_type}_{int(time.time())}"
        
        result = await agent.execute_task(task_id, {
            'task_type': task_type,
            'data': task_data
        })
        
        # Handle both AgentResponse objects and legacy dict responses
        if hasattr(result, 'is_success'):
            # New AgentResponse format
            if not result.is_success:
                raise Exception(f"Agent task failed: {result.error_message}")
            # Return the actual data, not the wrapper
            return result.data if result.data is not None else result
        else:
            # Legacy dict format
            if isinstance(result, dict):
                if result.get('status') != 'success':
                    raise Exception(f"Agent task failed: {result.get('error', 'Unknown error')}")
            return result
    
    async def _assess_phase_quality(self, phase: str, phase_result: Any) -> float:
        """Assess the quality of a completed phase"""
        # Implement quality assessment logic based on phase type
        if phase == 'web_discovery':
            # Handle DiscoveryResult object
            if hasattr(phase_result, 'content'):
                content_count = len(phase_result.content)
                average_quality = getattr(phase_result, 'average_quality', 0.5)
                
                # Combine content count and quality score
                base_score = 0.0
                if content_count >= 5:
                    base_score = 0.9
                elif content_count >= 3:
                    base_score = 0.7
                elif content_count >= 1:
                    base_score = 0.5
                else:
                    base_score = 0.2
                
                # Weight with average quality
                return min((base_score * 0.7) + (average_quality * 0.3), 1.0)
            
            # Fallback for dict format
            elif isinstance(phase_result, dict):
                result_data = phase_result.get('result', {})
                if isinstance(result_data, dict):
                    content_count = len(result_data.get('content', []))
                    if content_count >= 5:
                        return 0.9
                    elif content_count >= 3:
                        return 0.7
                    elif content_count >= 1:
                        return 0.5
                    else:
                        return 0.2
        
        # Handle seasonal image generation
        elif phase == 'seasonal_image_generation':
            if hasattr(phase_result, 'data') and phase_result.data:
                # AgentResponse with SeasonalImageResult
                seasonal_data = phase_result.data
                if getattr(seasonal_data, 'success', False):
                    # Quality based on successful image generation
                    images_count = len(getattr(seasonal_data, 'images_generated', {}))
                    collage_created = getattr(seasonal_data, 'collage_created', False)
                    
                    base_score = 0.6  # Base score for enabled but no images
                    if images_count >= 4:  # All seasons
                        base_score = 0.9
                    elif images_count >= 2:  # Some seasons
                        base_score = 0.7
                    elif images_count >= 1:  # At least one image
                        base_score = 0.6
                    
                    # Bonus for collage
                    if collage_created:
                        base_score = min(base_score + 0.1, 1.0)
                    
                    return base_score
                else:
                    # Failed but graceful degradation
                    graceful_degradation = getattr(seasonal_data, 'metadata', {}).get('graceful_degradation', False)
                    return 0.5 if graceful_degradation else 0.2
            else:
                # Disabled or failed initialization
                return 0.5  # Neutral score for disabled feature
        
        # Handle AgentResponse objects
        if hasattr(phase_result, 'is_success'):
            # AgentResponse object
            return 0.8 if phase_result.is_success else 0.3
        elif isinstance(phase_result, dict):
            # Dict format
            return 0.8 if phase_result.get('status') == 'success' else 0.3
        else:
            # For other types, assume success if no errors
            return 0.8
    
    async def _integrate_workflow_results(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Integrate all phase results into final destination data"""
        integrated_data = {
            'destination': workflow_state.destination,
            'workflow_id': workflow_state.workflow_id,
            'processing_metadata': {
                'total_processing_time': (datetime.now() - workflow_state.start_time).total_seconds(),
                'phases_completed': list(workflow_state.phase_results.keys()),
                'agent_system_version': '1.0.0'
            }
        }
        
        # Integrate web discovery data
        if 'web_discovery' in workflow_state.phase_results:
            web_discovery_result = workflow_state.phase_results['web_discovery']
            if hasattr(web_discovery_result, '__dict__'):
                # Handle DiscoveryResult object
                integrated_data['web_discovery_summary'] = {
                    'sources_analyzed': getattr(web_discovery_result, 'sources_analyzed', 0),
                    'sources_successful': getattr(web_discovery_result, 'sources_successful', 0),
                    'average_quality': getattr(web_discovery_result, 'average_quality', 0.0),
                    'processing_time': getattr(web_discovery_result, 'processing_time', 0.0)
                }
            elif isinstance(web_discovery_result, dict):
                # Handle dict format
                web_data = web_discovery_result.get('result', {})
                integrated_data['web_discovery_summary'] = web_data.get('summary', {})
        
        # Integrate LLM processing results
        if 'llm_processing' in workflow_state.phase_results:
            actual_llm_result = workflow_state.phase_results['llm_processing']
            
            if hasattr(actual_llm_result, '__dict__'):
                # Handle AgentResponse wrapper - extract the actual data
                if hasattr(actual_llm_result, 'data') and actual_llm_result.data:
                    llm_processing_data = actual_llm_result.data
                else:
                    llm_processing_data = actual_llm_result
                
                # Handle LLMProcessingResult object
                integrated_data['themes'] = getattr(llm_processing_data, 'themes', [])
                integrated_data['affinities'] = getattr(llm_processing_data, 'affinities', [])
                integrated_data['llm_processing_summary'] = {
                    'processing_time': getattr(llm_processing_data, 'processing_time', 0.0),
                    'quality_score': getattr(llm_processing_data, 'quality_score', 0.0),
                    'cache_performance': getattr(llm_processing_data, 'cache_performance', {}),
                    'errors': getattr(llm_processing_data, 'errors', [])
                }
            elif isinstance(actual_llm_result, dict):
                # Handle dict format
                integrated_data['themes'] = actual_llm_result.get('themes', [])
                integrated_data['affinities'] = actual_llm_result.get('affinities', [])
        
        # Integrate enhancement results
        if 'intelligence_enhancement' in workflow_state.phase_results:
            enhancement_data = workflow_state.phase_results['intelligence_enhancement']

            if hasattr(enhancement_data, '__dict__'):
                # Handle IntelligenceEnhancementResult object
                enhanced_themes = getattr(enhancement_data, 'enhanced_themes', [])
                intelligence_insights = getattr(enhancement_data, 'intelligence_insights', {})
                
                integrated_data['enhanced_themes'] = enhanced_themes
                integrated_data['intelligence_insights'] = intelligence_insights
                integrated_data['composition_analysis'] = intelligence_insights.get('composition_analysis', {})
                integrated_data['quality_assessment'] = intelligence_insights.get('quality_assessment', {})
                integrated_data['enhanced_processing'] = True
                integrated_data['enhanced_processing_time'] = getattr(enhancement_data, 'processing_time', 0.0)
                
            elif isinstance(enhancement_data, dict):
                # Handle dict format - extract from 'result' key if present
                if 'result' in enhancement_data:
                    # Agent returned dict format with 'result' key containing the actual data
                    actual_enhancement_result = enhancement_data['result']
                    
                    if hasattr(actual_enhancement_result, 'data'):
                        # AgentResponse object - extract the actual data
                        enhancement_result_data = actual_enhancement_result.data
                        enhanced_themes = getattr(enhancement_result_data, 'enhanced_themes', [])
                        intelligence_insights = getattr(enhancement_result_data, 'intelligence_insights', {})
                    elif hasattr(actual_enhancement_result, '__dict__'):
                        # IntelligenceEnhancementResult object in 'result'
                        enhanced_themes = getattr(actual_enhancement_result, 'enhanced_themes', [])
                        intelligence_insights = getattr(actual_enhancement_result, 'intelligence_insights', {})
                    elif isinstance(actual_enhancement_result, dict):
                        # Dict format in 'result'
                        enhanced_themes = actual_enhancement_result.get('enhanced_themes', [])
                        intelligence_insights = actual_enhancement_result.get('intelligence_insights', {})
                    else:
                        enhanced_themes = []
                        intelligence_insights = {}
                else:
                    # Direct dict format
                    enhanced_themes = enhancement_data.get('enhanced_themes', [])
                    intelligence_insights = enhancement_data.get('intelligence_insights', {})
                
                integrated_data['enhanced_themes'] = enhanced_themes
                integrated_data['intelligence_insights'] = intelligence_insights
                integrated_data['composition_analysis'] = intelligence_insights.get('composition_analysis', {})
                integrated_data['quality_assessment'] = intelligence_insights.get('quality_assessment', {})
                integrated_data['enhanced_processing'] = True
        
        # Integrate evidence validation and apply to individual themes
        if 'evidence_validation' in workflow_state.phase_results:
            evidence_data = workflow_state.phase_results['evidence_validation']
            
            # Extract the actual EvidenceValidationResult from the agent response wrapper
            actual_result = None
            if isinstance(evidence_data, dict):
                if 'result' in evidence_data:
                    # Agent response wrapper - extract the actual result
                    actual_result = evidence_data['result']
                else:
                    # Direct data
                    actual_result = evidence_data
            else:
                # Object format
                actual_result = evidence_data
            
            # Get validation report from the actual result
            validation_report = {}
            if hasattr(actual_result, '__dict__'):
                # Check if it's an AgentResponse that contains the data
                if hasattr(actual_result, 'data') and actual_result.data:
                    # Extract from AgentResponse.data
                    evidence_result = actual_result.data
                    validation_report = getattr(evidence_result, 'validation_report', {})
                else:
                    # Direct EvidenceValidationResult object
                    validation_report = getattr(actual_result, 'validation_report', {})
            elif isinstance(actual_result, dict):
                # Dict format
                validation_report = actual_result.get('validation_report', {})
            
            integrated_data['evidence_validation_report'] = validation_report
            
            # Apply evidence validation to individual themes in both affinities and enhanced_themes
            if 'affinities' in integrated_data and validation_report:
                self._apply_evidence_to_themes(integrated_data['affinities'], validation_report)
            
            # Also apply evidence to enhanced_themes (which take priority in dashboard generation)
            if 'enhanced_themes' in integrated_data and validation_report:
                self._apply_evidence_to_themes(integrated_data['enhanced_themes'], validation_report)
        
        # Integrate seasonal image results
        if 'seasonal_image_generation' in workflow_state.phase_results:
            seasonal_result = workflow_state.phase_results['seasonal_image_generation']
            
            # Extract the actual SeasonalImageResult from the agent response
            if hasattr(seasonal_result, 'data') and seasonal_result.data:
                # AgentResponse format - extract the SeasonalImageResult
                seasonal_data = seasonal_result.data
                
                integrated_data['seasonal_imagery'] = {
                    'enabled': True,
                    'success': getattr(seasonal_data, 'success', False),
                    'images_generated': getattr(seasonal_data, 'images_generated', {}),
                    'collage_created': getattr(seasonal_data, 'collage_created', False),
                    'processing_time': getattr(seasonal_data, 'processing_time', 0.0),
                    'metadata': getattr(seasonal_data, 'metadata', {}),
                    'error_messages': getattr(seasonal_data, 'error_messages', [])
                }
                
                # Add image paths for dashboard integration
                if seasonal_data.images_generated:
                    integrated_data['seasonal_image_paths'] = {}
                    for season, image_data in seasonal_data.images_generated.items():
                        if 'local_path' in image_data:
                            integrated_data['seasonal_image_paths'][season] = image_data['local_path']
            
            elif isinstance(seasonal_result, dict):
                # Handle dict format
                integrated_data['seasonal_imagery'] = seasonal_result.get('seasonal_imagery', {})
        else:
            # No seasonal imagery generated
            integrated_data['seasonal_imagery'] = {
                'enabled': False,
                'success': False,
                'images_generated': {},
                'collage_created': False,
                'processing_time': 0.0,
                'metadata': {'disabled': True},
                'error_messages': []
            }
        
        # Integrate quality assessment
        if 'quality_assurance' in workflow_state.phase_results:
            qa_data = workflow_state.phase_results['quality_assurance']
            if hasattr(qa_data, '__dict__'):
                # Handle data model object
                integrated_data['quality_assessment'] = getattr(qa_data, 'quality_metrics', {})
            elif isinstance(qa_data, dict):
                # Handle dict format
                integrated_data['quality_assessment'] = qa_data.get('quality_metrics', {})
        
        return integrated_data
    
    async def _calculate_final_quality(self, workflow_state: WorkflowState) -> float:
        """Calculate final quality score for the workflow"""
        phase_qualities = []
        
        for phase_name, phase_result in workflow_state.phase_results.items():
            quality = await self._assess_phase_quality(phase_name, phase_result)
            phase_qualities.append(quality)
        
        if not phase_qualities:
            return 0.0
        
        # Weight different phases
        phase_weights = {
            'web_discovery': 0.18,
            'llm_processing': 0.28,
            'intelligence_enhancement': 0.22,
            'evidence_validation': 0.14,
            'seasonal_image_generation': 0.08,
            'quality_assurance': 0.1
        }
        
        weighted_quality = 0.0
        total_weight = 0.0
        
        for i, phase_name in enumerate(workflow_state.phase_results.keys()):
            weight = phase_weights.get(phase_name, 0.1)
            weighted_quality += phase_qualities[i] * weight
            total_weight += weight
        
        return weighted_quality / total_weight if total_weight > 0 else sum(phase_qualities) / len(phase_qualities)
    
    def _apply_evidence_to_themes(self, affinities: List[Dict[str, Any]], validation_report: Dict[str, Any]):
        """Apply evidence validation results to individual themes"""
        
        # Get theme evidence from validation report (it's a list, not a dict)
        theme_evidence_list = validation_report.get('theme_evidence', [])
        
        if not theme_evidence_list:
            return
        
        # Convert list to dictionary for easier lookup
        theme_evidence = {}
        for theme_ev in theme_evidence_list:
            if hasattr(theme_ev, '__dict__'):
                # Handle ThemeEvidence object
                theme_name = getattr(theme_ev, 'theme_name', 'Unknown')
                theme_evidence[theme_name] = theme_ev
            elif isinstance(theme_ev, dict):
                # Handle dict format
                theme_name = theme_ev.get('theme_name', 'Unknown')
                theme_evidence[theme_name] = theme_ev
        
        # Apply evidence to each theme
        applied_count = 0
        for affinity in affinities:
            theme_name = affinity.get('theme', 'Unknown Theme')
            
            # Find matching evidence for this theme
            matching_evidence = None
            for theme_key, evidence in theme_evidence.items():
                # Match by theme name (case insensitive)
                if theme_key.lower() == theme_name.lower():
                    matching_evidence = evidence
                    break
            
            if not matching_evidence:
                # Try partial matching as fallback
                for theme_key, evidence in theme_evidence.items():
                    if theme_name.lower() in theme_key.lower() or theme_key.lower() in theme_name.lower():
                        matching_evidence = evidence
                        break
            
            if matching_evidence:
                # Create comprehensive_attribute_evidence for this theme
                comprehensive_evidence = {
                    'main_theme': {
                        'evidence_pieces': []
                    }
                }
                
                # Extract evidence pieces with URLs
                if hasattr(matching_evidence, '__dict__'):
                    # Handle evidence object
                    evidence_pieces = getattr(matching_evidence, 'evidence_pieces', [])
                elif isinstance(matching_evidence, dict):
                    # Handle dict format
                    evidence_pieces = matching_evidence.get('evidence_pieces', [])
                else:
                    evidence_pieces = []
                
                # Convert evidence pieces to modal format
                for piece in evidence_pieces:
                    if hasattr(piece, '__dict__'):
                        # Handle evidence piece object
                        evidence_item = {
                            'text_content': getattr(piece, 'text_content', ''),
                            'source_url': getattr(piece, 'source_url', ''),
                            'source_title': getattr(piece, 'source_title', ''),
                            'authority_score': getattr(piece, 'authority_score', 0.0),
                            'quality_rating': getattr(piece, 'quality_rating', 'unknown'),
                            'source_type': getattr(piece, 'source_type', 'web')
                        }
                    elif isinstance(piece, dict):
                        # Handle dict format
                        evidence_item = {
                            'text_content': piece.get('text_content', ''),
                            'source_url': piece.get('source_url', ''),
                            'source_title': piece.get('source_title', ''),
                            'authority_score': piece.get('authority_score', 0.0),
                            'quality_rating': piece.get('quality_rating', 'unknown'),
                            'source_type': piece.get('source_type', 'web')
                        }
                    else:
                        continue
                    
                    comprehensive_evidence['main_theme']['evidence_pieces'].append(evidence_item)
                
                # Add the comprehensive evidence to the theme
                affinity['comprehensive_attribute_evidence'] = comprehensive_evidence
                applied_count += 1
    
    async def _collect_performance_metrics(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Collect performance metrics from all agents"""
        metrics = {}
        
        for agent_id, agent in self.agents.items():
            agent_metrics = agent.get_performance_metrics()
            metrics[agent_id] = agent_metrics
        
        return metrics
    
    async def _cleanup_agent_specific(self):
        """Cleanup all process agents"""
        self.logger.info("Shutting down all process agents...")
        
        shutdown_tasks = []
        for agent_id, agent in self.agents.items():
            shutdown_tasks.append(agent.shutdown())
        
        # Wait for all agents to shutdown
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        self.logger.info("All process agents shutdown complete")
    
    # Message handlers
    
    async def _handle_workflow_request(self, message: AgentMessage):
        """Handle workflow execution request"""
        destinations = message.payload.get('destinations', [])
        
        if not destinations:
            await self.send_message(AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="error_response",
                payload={'error': 'No destinations provided'},
                correlation_id=message.message_id
            ))
            return
        
        # Execute workflow
        results = await self.execute_workflow(destinations)
        
        # Send response
        await self.send_message(AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="workflow_response",
            payload={'results': results},
            correlation_id=message.message_id
        ))
    
    async def _handle_agent_response(self, message: AgentMessage):
        """Handle response from process agents"""
        # Process agent responses and update workflow state
        workflow_id = message.payload.get('workflow_id')
        if workflow_id and workflow_id in self.active_workflows:
            workflow_state = self.active_workflows[workflow_id]
            # Update workflow state based on agent response
            pass
    
    async def _handle_quality_intervention(self, message: AgentMessage):
        """Handle quality intervention requests"""
        intervention_type = message.payload.get('intervention_type')
        workflow_id = message.payload.get('workflow_id')
        
        if workflow_id in self.active_workflows:
            # Handle intervention based on type
            if intervention_type == 'retry_phase':
                # Retry specific phase
                pass
            elif intervention_type == 'adjust_threshold':
                # Adjust quality thresholds
                pass

class ResourceAllocator:
    """Manages resource allocation across agents"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def allocate_llm_resources(self, discovery_result: Dict[str, Any], 
                                   current_allocation: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Allocate LLM resources based on discovery results"""
        # Handle both DiscoveryResult object format and dict format
        if hasattr(discovery_result, 'content'):
            # Handle object format
            content_complexity = len(getattr(discovery_result, 'content', []))
        elif hasattr(discovery_result, 'sources_successful'):
            # Handle object format
            content_complexity = getattr(discovery_result, 'sources_successful', 0)
        elif isinstance(discovery_result, dict):
            # Handle dict format
            if 'content' in discovery_result:
                content_complexity = len(discovery_result.get('content', []))
            elif 'sources_successful' in discovery_result:
                content_complexity = discovery_result.get('sources_successful', 0)
            else:
                content_complexity = 0
        else:
            content_complexity = 0
        
        if content_complexity > 8:
            return {'pool_size': 'large', 'concurrent_requests': 8}
        elif content_complexity > 5:
            return {'pool_size': 'medium', 'concurrent_requests': 5}
        else:
            return {'pool_size': 'small', 'concurrent_requests': 3}

class DecisionEngine:
    """Makes intelligent decisions about workflow execution"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def plan_discovery_strategy(self, destination: str) -> Dict[str, Any]:
        """Plan web discovery strategy based on destination characteristics"""
        # Analyze destination to determine discovery approach
        if any(keyword in destination.lower() for keyword in ['tokyo', 'paris', 'london', 'new york']):
            return {
                'query_depth': 'comprehensive',
                'source_diversity': 'high',
                'max_sources': 12
            }
        else:
            return {
                'query_depth': 'standard',
                'source_diversity': 'medium',
                'max_sources': 8
            } 