"""
Agent Integration Layer

Provides backward compatibility and gradual migration from legacy pipeline to agent system.
Supports parallel execution modes for comparison and validation.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

# Import agent system
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents import AgentOrchestrator
from agents.data_models import WorkflowResult, AgentResponse

# Import legacy components
from src.enhanced_data_processor import EnhancedDataProcessor
from src.focused_llm_generator import FocusedLLMGenerator
from src.focused_prompt_processor import FocusedPromptProcessor
from tools.web_discovery_tools import WebDiscoveryTool

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Unified result format for both agent and legacy systems"""
    destinations_processed: int
    successful_destinations: int
    processing_time: float
    system_used: str
    processed_files: Dict[str, str]
    agent_results: Optional[Dict[str, WorkflowResult]] = None
    legacy_results: Optional[Dict[str, Any]] = None
    comparison_data: Optional[Dict[str, Any]] = None

class AgentCompatibilityLayer:
    """
    Integration layer that provides backward compatibility while enabling
    gradual migration to the agent system.
    
    Supports multiple modes:
    - legacy_only: Use only the existing pipeline
    - agent_only: Use only the agent system  
    - parallel: Run both systems for comparison
    - fallback: Try agents first, fallback to legacy on failure
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent_config = config.get('agents', {})
        
        # Migration settings
        self.enabled = self.agent_config.get('enabled', False)
        self.migration_mode = self.agent_config.get('migration_mode', 'legacy_only')
        self.fallback_enabled = self.agent_config.get('fallback_enabled', True)
        
        # Components
        self.orchestrator = None
        self.legacy_processor = None
        self.llm_generator = None
        self.prompt_processor = None
        self.web_discovery = None
        
        # Performance tracking
        self.performance_data = {
            'agent_calls': 0,
            'legacy_calls': 0,
            'agent_total_time': 0.0,
            'legacy_total_time': 0.0,
            'agent_successes': 0,
            'legacy_successes': 0
        }
        
        logger.info(f"Agent Compatibility Layer initialized - Mode: {self.migration_mode}")
    
    async def initialize(self):
        """Initialize the integration layer components"""
        logger.info("Initializing Agent Compatibility Layer...")
        
        try:
            # Initialize agent system if enabled
            if self.enabled or self.migration_mode in ['parallel', 'fallback', 'agent_only']:
                logger.info("Initializing agent orchestrator...")
                self.orchestrator = AgentOrchestrator(self.config)
                await self.orchestrator.initialize()
                logger.info("✅ Agent orchestrator initialized")
            
            # Initialize legacy system if needed
            if self.migration_mode in ['legacy_only', 'parallel', 'fallback']:
                logger.info("Initializing legacy components...")
                await self._initialize_legacy_components()
                logger.info("✅ Legacy components initialized")
            
            logger.info(f"Integration layer ready - Mode: {self.migration_mode}")
            
        except Exception as e:
            logger.error(f"Failed to initialize integration layer: {e}")
            if self.fallback_enabled and self.migration_mode != 'legacy_only':
                logger.warning("Falling back to legacy-only mode")
                self.migration_mode = 'legacy_only'
                await self._initialize_legacy_components()
            else:
                raise
    
    async def _initialize_legacy_components(self):
        """Initialize legacy processing components"""
        try:
            # Initialize LLM generator
            primary_provider = self.config.get('llm_settings', {}).get('provider', 'gemini')
            self.llm_generator = FocusedLLMGenerator(primary_provider, self.config)
            
            # Initialize prompt processor
            self.prompt_processor = FocusedPromptProcessor(self.llm_generator, self.config)
            
            # Initialize web discovery
            self.web_discovery = WebDiscoveryTool(self.config)
            
            # Initialize enhanced data processor
            self.legacy_processor = EnhancedDataProcessor(self.config)
            
        except Exception as e:
            logger.error(f"Failed to initialize legacy components: {e}")
            raise
    
    async def process_destinations(self, destinations: List[str]) -> ProcessingResult:
        """Process destinations using the configured migration mode"""
        
        if self.migration_mode == 'agent_only':
            return await self._process_agent_only(destinations)
        elif self.migration_mode == 'legacy_only':
            return await self._process_legacy_only(destinations)
        elif self.migration_mode == 'parallel':
            return await self._process_parallel(destinations)
        elif self.migration_mode == 'fallback':
            return await self._process_with_fallback(destinations)
        else:
            raise ValueError(f"Unknown migration mode: {self.migration_mode}")
    
    async def _process_agent_only(self, destinations: List[str]) -> ProcessingResult:
        """Process using only the agent system"""
        logger.info("🤖 Processing with agent system only")
        start_time = time.time()
        
        try:
            # Execute agent workflow
            agent_results = await self.orchestrator.execute_workflow(destinations)
            processing_time = time.time() - start_time
            
            # Convert agent results to legacy-compatible format
            processed_files = await self._convert_agent_results_to_legacy_format(agent_results)
            
            # Track performance
            self.performance_data['agent_calls'] += 1
            self.performance_data['agent_total_time'] += processing_time
            successful = sum(1 for result in agent_results.values() if result.success)
            self.performance_data['agent_successes'] += successful
            
            return ProcessingResult(
                destinations_processed=len(destinations),
                successful_destinations=successful,
                processing_time=processing_time,
                system_used="agent_only",
                processed_files=processed_files,
                agent_results=agent_results
            )
            
        except Exception as e:
            logger.error(f"Agent-only processing failed: {e}")
            raise
    
    async def _process_legacy_only(self, destinations: List[str]) -> ProcessingResult:
        """Process using only the legacy system"""
        logger.info("🔧 Processing with legacy system only")
        start_time = time.time()
        
        try:
            # Execute legacy workflow
            processed_files = await self._execute_legacy_pipeline(destinations)
            processing_time = time.time() - start_time
            
            # Track performance
            self.performance_data['legacy_calls'] += 1
            self.performance_data['legacy_total_time'] += processing_time
            self.performance_data['legacy_successes'] += len(processed_files)
            
            return ProcessingResult(
                destinations_processed=len(destinations),
                successful_destinations=len(processed_files),
                processing_time=processing_time,
                system_used="legacy_only",
                processed_files=processed_files,
                legacy_results=processed_files
            )
            
        except Exception as e:
            logger.error(f"Legacy-only processing failed: {e}")
            raise
    
    async def _process_parallel(self, destinations: List[str]) -> ProcessingResult:
        """Process using both systems in parallel for comparison"""
        logger.info("🔀 Processing with both systems in parallel")
        start_time = time.time()
        
        try:
            # Execute both systems concurrently
            agent_task = asyncio.create_task(self._process_agent_only(destinations))
            legacy_task = asyncio.create_task(self._process_legacy_only(destinations))
            
            # Wait for both to complete
            agent_result, legacy_result = await asyncio.gather(
                agent_task, legacy_task, return_exceptions=True
            )
            
            processing_time = time.time() - start_time
            
            # Handle exceptions
            agent_success = not isinstance(agent_result, Exception)
            legacy_success = not isinstance(legacy_result, Exception)
            
            if not agent_success:
                logger.error(f"Agent system failed in parallel mode: {agent_result}")
            if not legacy_success:
                logger.error(f"Legacy system failed in parallel mode: {legacy_result}")
            
            # Choose primary result (prefer agents if both succeed)
            if agent_success and legacy_success:
                primary_result = agent_result
                comparison_data = self._create_comparison_data(agent_result, legacy_result)
                system_used = "parallel_both_success"
            elif agent_success:
                primary_result = agent_result
                primary_result.system_used = "parallel_agent_only"
                system_used = "parallel_agent_only"
                comparison_data = {"error": "Legacy system failed", "legacy_error": str(legacy_result)}
            elif legacy_success:
                primary_result = legacy_result
                primary_result.system_used = "parallel_legacy_only"
                system_used = "parallel_legacy_only"
                comparison_data = {"error": "Agent system failed", "agent_error": str(agent_result)}
            else:
                raise Exception(f"Both systems failed - Agent: {agent_result}, Legacy: {legacy_result}")
            
            # Add comparison data
            primary_result.comparison_data = comparison_data
            primary_result.processing_time = processing_time
            primary_result.system_used = system_used
            
            return primary_result
            
        except Exception as e:
            logger.error(f"Parallel processing failed: {e}")
            raise
    
    async def _process_with_fallback(self, destinations: List[str]) -> ProcessingResult:
        """Process with agents first, fallback to legacy on failure"""
        logger.info("🛡️ Processing with agent fallback mode")
        
        try:
            # Try agent system first
            result = await self._process_agent_only(destinations)
            result.system_used = "fallback_agent_success"
            return result
            
        except Exception as agent_error:
            logger.warning(f"Agent system failed, falling back to legacy: {agent_error}")
            
            try:
                # Fallback to legacy system
                result = await self._process_legacy_only(destinations)
                result.system_used = "fallback_legacy_used"
                return result
                
            except Exception as legacy_error:
                logger.error(f"Both systems failed - Agent: {agent_error}, Legacy: {legacy_error}")
                raise Exception(f"Fallback failed - Agent error: {agent_error}, Legacy error: {legacy_error}")
    
    async def _execute_legacy_pipeline(self, destinations: List[str]) -> Dict[str, str]:
        """Execute the legacy processing pipeline"""
        # Web discovery phase
        discovery_results = {}
        for destination in destinations:
            try:
                discovery_results[destination] = await self.web_discovery.discover_destination_content(destination)
            except Exception as e:
                logger.error(f"Legacy web discovery failed for {destination}: {e}")
                discovery_results[destination] = []
        
        # LLM processing phase
        destinations_data = {}
        for destination_name, web_data in discovery_results.items():
            try:
                web_data_formatted = {
                    'content': web_data if isinstance(web_data, list) else []
                }
                
                destination_profile = await self.prompt_processor.process_destination(
                    destination_name, web_data_formatted
                )
                destinations_data[destination_name] = destination_profile
                
            except Exception as e:
                logger.error(f"Legacy LLM processing failed for {destination_name}: {e}")
                destinations_data[destination_name] = {
                    'destination': destination_name,
                    'affinities': [],
                    'processing_metadata': {'error': str(e)}
                }
        
        # Enhanced processing phase
        processed_files = self.legacy_processor.process_destinations_with_progress(
            destinations_data,
            web_data=discovery_results,
            generate_dashboard=True
        )
        
        return processed_files
    
    async def _convert_agent_results_to_legacy_format(self, agent_results: Dict[str, WorkflowResult]) -> Dict[str, str]:
        """Convert agent workflow results to legacy processed files format and generate dashboard"""
        import json
        import os
        from datetime import datetime
        from src.enhanced_viewer_generator import EnhancedViewerGenerator
        from src.dev_staging_manager import DevStagingManager
        
        # Create session directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = f"outputs/session_agent_{timestamp}"
        json_dir = os.path.join(session_dir, "json")
        dashboard_dir = os.path.join(session_dir, "dashboard")
        
        os.makedirs(json_dir, exist_ok=True)
        os.makedirs(dashboard_dir, exist_ok=True)
        
        processed_files = {}
        dashboard_data = {}
        
        logger.info(f"🔄 Converting agent results to dashboard format in {session_dir}")
        
        for destination, workflow_result in agent_results.items():
            if workflow_result.success:
                # Create filename
                dest_filename = destination.lower().replace(', ', '__').replace(' ', '_')
                json_file_path = os.path.join(json_dir, f"{dest_filename}_enhanced.json")
                evidence_file_path = os.path.join(json_dir, f"{dest_filename}_evidence.json")
                
                # Convert WorkflowResult to legacy format
                legacy_data = self._convert_workflow_result_to_legacy_data(destination, workflow_result)
                
                # Save enhanced data JSON
                with open(json_file_path, 'w', encoding='utf-8') as f:
                    json.dump(legacy_data['enhanced_data'], f, indent=2, ensure_ascii=False)
                
                # Save evidence data JSON  
                with open(evidence_file_path, 'w', encoding='utf-8') as f:
                    json.dump(legacy_data['evidence_data'], f, indent=2, ensure_ascii=False)
                
                processed_files[destination] = json_file_path
                dashboard_data[destination] = legacy_data
                
                logger.info(f"✅ Saved agent data for {destination}: {json_file_path}")
        
        # Generate HTML dashboard
        if dashboard_data:
            try:
                logger.info("🎨 Generating HTML dashboard from agent results...")
                viewer_generator = EnhancedViewerGenerator()
                
                # Generate individual destination pages
                for destination, data in dashboard_data.items():
                    dest_filename = destination.lower().replace(', ', '__').replace(' ', '_')
                    html_file = os.path.join(dashboard_dir, f"{dest_filename}.html")
                    json_file = os.path.join(json_dir, f"{dest_filename}_enhanced.json")
                    
                    # Use the correct method name and parameters
                    viewer_generator.generate_destination_viewer(
                        json_file=json_file,
                        output_dir=dashboard_dir
                    )
                    logger.info(f"✅ Generated HTML for {destination}: {html_file}")
                
                # Generate index page
                index_file = os.path.join(dashboard_dir, "index.html")
                session_summary = {
                    'session_info': {
                        'timestamp': timestamp,
                        'processing_date': datetime.now().isoformat(),
                        'output_directory': session_dir,
                        'destinations_processed': len(dashboard_data)
                    },
                    'processed_destinations': {
                        dest: {
                            'file_path': processed_files[dest],
                            'theme_count': len(data['enhanced_data'].get('affinities', [])),
                            'quality_score': data['enhanced_data'].get('processing_metadata', {}).get('quality_score', 0.8),
                            'hidden_gems_count': len([a for a in data['enhanced_data'].get('affinities', []) if a.get('hidden_gem', False)]),
                            'quality_level': 'excellent' if data['enhanced_data'].get('processing_metadata', {}).get('quality_score', 0.8) > 0.85 else 'good'
                        }
                        for dest, data in dashboard_data.items()
                    }
                }
                
                # Generate multi-destination index page
                json_files = [processed_files[dest] for dest in dashboard_data.keys()]
                viewer_generator.generate_multi_destination_viewer(
                    json_files=json_files,
                    output_dir=dashboard_dir
                )
                logger.info(f"✅ Generated dashboard index: {index_file}")
                
                # Stage the session for development server
                staging_manager = DevStagingManager()
                try:
                    if staging_manager.stage_latest_session(session_dir):
                        logger.info(f"✅ Dashboard staged for development: {session_dir}")
                    else:
                        logger.warning(f"⚠️ Dashboard staging failed for: {session_dir}")
                except Exception as staging_error:
                    logger.error(f"❌ Dashboard staging error: {staging_error}")
                    # Continue without staging
                
            except Exception as e:
                logger.error(f"❌ Dashboard generation failed: {e}")
                # Continue with file paths even if dashboard generation fails
        
        return processed_files
    
    def _create_comparison_data(self, agent_result: ProcessingResult, legacy_result: ProcessingResult) -> Dict[str, Any]:
        """Create comparison data between agent and legacy results"""
        return {
            'comparison_metrics': {
                'performance_comparison': {
                    'agent_time': agent_result.processing_time,
                    'legacy_time': legacy_result.processing_time,
                    'speedup_factor': legacy_result.processing_time / agent_result.processing_time if agent_result.processing_time > 0 else 0
                },
                'success_comparison': {
                    'agent_successes': agent_result.successful_destinations,
                    'legacy_successes': legacy_result.successful_destinations,
                    'agent_success_rate': agent_result.successful_destinations / agent_result.destinations_processed,
                    'legacy_success_rate': legacy_result.successful_destinations / legacy_result.destinations_processed
                }
            },
            'agent_details': {
                'total_destinations': agent_result.destinations_processed,
                'successful_destinations': agent_result.successful_destinations,
                'processing_time': agent_result.processing_time
            },
            'legacy_details': {
                'total_destinations': legacy_result.destinations_processed,
                'successful_destinations': legacy_result.successful_destinations,
                'processing_time': legacy_result.processing_time
            }
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for both systems"""
        agent_avg_time = (self.performance_data['agent_total_time'] / 
                         self.performance_data['agent_calls']) if self.performance_data['agent_calls'] > 0 else 0
        
        legacy_avg_time = (self.performance_data['legacy_total_time'] / 
                          self.performance_data['legacy_calls']) if self.performance_data['legacy_calls'] > 0 else 0
        
        agent_success_rate = (self.performance_data['agent_successes'] / 
                             self.performance_data['agent_calls']) if self.performance_data['agent_calls'] > 0 else 0
        
        legacy_success_rate = (self.performance_data['legacy_successes'] / 
                              self.performance_data['legacy_calls']) if self.performance_data['legacy_calls'] > 0 else 0
        
        return {
            'agent_performance': {
                'total_calls': self.performance_data['agent_calls'],
                'total_successes': self.performance_data['agent_successes'],
                'average_processing_time': agent_avg_time,
                'average_success_rate': agent_success_rate,
                'total_time': self.performance_data['agent_total_time']
            },
            'legacy_performance': {
                'total_calls': self.performance_data['legacy_calls'],
                'total_successes': self.performance_data['legacy_successes'],
                'average_processing_time': legacy_avg_time,
                'average_success_rate': legacy_success_rate,
                'total_time': self.performance_data['legacy_total_time']
            },
            'migration_status': {
                'mode': self.migration_mode,
                'agents_enabled': self.enabled,
                'fallback_enabled': self.fallback_enabled
            }
        }
    
    async def cleanup(self):
        """Cleanup both agent and legacy components"""
        try:
            if self.orchestrator:
                await self.orchestrator.shutdown()
                logger.debug("Agent orchestrator cleanup complete")
        except Exception as e:
            logger.warning(f"Agent cleanup error: {e}")
        
        try:
            if self.llm_generator:
                await self.llm_generator.cleanup()
                logger.debug("Legacy LLM cleanup complete")
        except Exception as e:
            logger.warning(f"Legacy cleanup error: {e}")
        
        logger.info("Integration layer cleanup complete")
    
    def _convert_workflow_result_to_legacy_data(self, destination: str, workflow_result: WorkflowResult) -> Dict[str, Any]:
        """Convert agent WorkflowResult to legacy dashboard format"""
        from datetime import datetime
        
        # Access the final_data from WorkflowResult
        final_data = workflow_result.final_data or {}
        

        # Extract enhanced data from Intelligence Enhancement Agent if available
        intelligence_insights = final_data.get('intelligence_insights', {})
        composition_analysis = final_data.get('composition_analysis', {})
        quality_assessment = final_data.get('quality_assessment', {})
        evidence_validation_report = final_data.get('evidence_validation_report', {})
        enhanced_themes = final_data.get('enhanced_themes', [])
        
        # Convert datetime objects to ISO strings in evidence validation report
        if evidence_validation_report:
            evidence_validation_report = self._serialize_evidence_report(evidence_validation_report)
        
        # Convert agent themes to legacy format
        # Use enhanced themes if available, otherwise fall back to basic affinities
        if enhanced_themes:
            logger.info(f"Using {len(enhanced_themes)} enhanced themes from Intelligence Enhancement Agent")
            theme_data = enhanced_themes
        else:
            logger.info(f"Using {len(final_data.get('affinities', []))} basic affinities from LLM processing")
            theme_data = final_data.get('affinities', [])
            
        web_content = final_data.get('web_content', [])
        
        # Create legacy theme format
        themes = []
        evidence_data = []
        
        for theme_item in theme_data:
            if hasattr(theme_item, '__dict__'):  # ThemeData object
                theme_info = theme_item.__dict__
                theme_name = theme_info.get('theme', 'Unknown Theme')
            elif isinstance(theme_item, dict):  # Dict format
                theme_info = theme_item
                theme_name = theme_info.get('theme', theme_info.get('name', 'Unknown Theme'))
            else:
                continue
                
            # Preserve ALL intelligence attributes from Enhanced Data Processor
            legacy_theme = {
                # Basic theme attributes
                'category': theme_info.get('category', 'culture'),
                'theme': theme_name,
                'sub_themes': theme_info.get('sub_themes', []),
                'confidence': theme_info.get('confidence', 0.8),
                'rationale': theme_info.get('rationale', f"Generated theme for {destination}"),
                'unique_selling_points': theme_info.get('unique_selling_points', []),
                'authenticity_score': theme_info.get('authenticity_score', 0.8),
                'price_point': theme_info.get('price_point', 'mid'),
                
                # Core Intelligence Attributes (14 required attributes)
                'nano_themes': theme_info.get('nano_themes', theme_info.get('sub_themes', [])),
                'price_insights': theme_info.get('price_insights', {}),
                'seasonality': theme_info.get('seasonality', {}),
                'traveler_types': theme_info.get('traveler_types', []),
                'depth_analysis': theme_info.get('depth_analysis', {}),
                'authenticity_analysis': theme_info.get('authenticity_analysis', {}),
                'hidden_gem_score': theme_info.get('hidden_gem_score', {}),
                'cultural_sensitivity': theme_info.get('cultural_sensitivity', {}),
                'experience_intensity': theme_info.get('experience_intensity', {}),
                'contextual_info': theme_info.get('contextual_info', {}),
                'micro_climate': theme_info.get('micro_climate', {}),
                'theme_interconnections': theme_info.get('theme_interconnections', {}),
                'emotional_profile': theme_info.get('emotional_profile', {}),
                
                # Content Intelligence Attributes (4 specialized attributes)
                'iconic_landmarks': theme_info.get('iconic_landmarks', []),
                'practical_travel_intelligence': theme_info.get('practical_travel_intelligence', {}),
                'neighborhood_insights': theme_info.get('neighborhood_insights', {}),
                'content_discovery_intelligence': theme_info.get('content_discovery_intelligence', {}),
                
                # Evidence and metadata
                'comprehensive_attribute_evidence': theme_info.get('comprehensive_attribute_evidence', {}),
                'processing_metadata': {
                    'source': 'agent_system',
                    'quality_score': theme_info.get('confidence', 0.8),
                    'enhanced_processing': True,
                    'intelligence_layers_applied': 18
                }
            }
            themes.append(legacy_theme)
        
        # Convert web content to evidence format
        for idx, content in enumerate(web_content):
            if hasattr(content, '__dict__'):  # WebContent object
                content_info = content.__dict__
            elif isinstance(content, dict):  # Dict format
                content_info = content
            else:
                continue
                
            evidence_item = {
                'url': content_info.get('url', f'https://example.com/source_{idx}'),
                'title': content_info.get('title', f'Source {idx + 1}'),
                'content': content_info.get('content', ''),
                'authority_score': content_info.get('authority_score', 0.7),
                'relevance_score': content_info.get('relevance_score', 0.8),
                'metadata': {
                    'source': 'agent_web_discovery',
                    'processing_date': datetime.now().isoformat(),
                    'quality_score': content_info.get('quality_score', 0.8)
                }
            }
            evidence_data.append(evidence_item)
        
        # Create legacy enhanced data format
        enhanced_data = {
            'destination': destination,
            'destination_id': destination.lower().replace(', ', '_').replace(' ', '_'),
            'destination_name': destination,
            'affinities': themes,
            'intelligence_insights': intelligence_insights,
            'composition_analysis': composition_analysis,
            'quality_assessment': quality_assessment,
            'evidence_validation_report': evidence_validation_report,
            'processing_metadata': {
                'processing_date': datetime.now().isoformat(),
                'quality_score': workflow_result.quality_score,
                'success': workflow_result.success,
                'processing_time': workflow_result.processing_time,
                'source_system': 'agent_orchestrator',
                'theme_count': len(themes),
                'evidence_count': len(evidence_data),
                'workflow_id': workflow_result.workflow_id,
                'enhanced_processing': bool(enhanced_themes)
            },
            'session_metadata': {
                'session_type': 'agent_generated',
                'agent_version': '1.0',
                'workflow_id': workflow_result.workflow_id,
                'quality_level': 'excellent' if workflow_result.quality_score > 0.85 else 'good'
            }
        }
        
        return {
            'enhanced_data': enhanced_data,
            'evidence_data': evidence_data
        }
    
    def _extract_hidden_gem_boolean(self, theme_info: Dict[str, Any]) -> bool:
        """Extract boolean hidden gem status from theme info, handling both dict and float formats"""
        hidden_gem_score = theme_info.get('hidden_gem_score')
        
        if isinstance(hidden_gem_score, dict):
            # Agent system format - extract uniqueness_score from the dict
            uniqueness_score = hidden_gem_score.get('uniqueness_score', 0.0)
            return uniqueness_score > 0.9
        elif isinstance(hidden_gem_score, (int, float)):
            # Legacy float format
            return hidden_gem_score > 0.9
        else:
            # Fallback to confidence score
            confidence = theme_info.get('confidence', 0.8)
            return confidence > 0.9
    
    def _serialize_evidence_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Convert datetime objects in evidence validation report to ISO strings"""
        from datetime import datetime
        import copy
        
        # Make a deep copy to avoid modifying the original
        serialized_report = copy.deepcopy(report)
        
        # Convert datetime fields to ISO strings
        datetime_fields = ['validation_started_at', 'validation_completed_at']
        for field in datetime_fields:
            if field in serialized_report and isinstance(serialized_report[field], datetime):
                serialized_report[field] = serialized_report[field].isoformat()
        
        # Handle theme_evidence list which might contain datetime objects
        if 'theme_evidence' in serialized_report and isinstance(serialized_report['theme_evidence'], list):
            for theme_evidence in serialized_report['theme_evidence']:
                if isinstance(theme_evidence, dict):
                    for key, value in theme_evidence.items():
                        if isinstance(value, datetime):
                            theme_evidence[key] = value.isoformat()
                        elif isinstance(value, list):
                            # Handle evidence_pieces which might contain datetime objects
                            for item in value:
                                if isinstance(item, dict):
                                    for sub_key, sub_value in item.items():
                                        if isinstance(sub_value, datetime):
                                            item[sub_key] = sub_value.isoformat()
        
        return serialized_report 