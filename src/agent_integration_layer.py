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
from pathlib import Path

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

# Import new incremental processing systems
from src.theme_lifecycle_manager import ThemeLifecycleManager
from src.session_consolidation_manager import SessionConsolidationManager
from src.enhanced_caching_system import ConsolidatedDataCache
from src.export_system import DestinationDataExporter

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
        
        # New incremental processing systems
        self.theme_lifecycle_manager = ThemeLifecycleManager(config)
        self.session_consolidator = SessionConsolidationManager(config)
        self.consolidated_cache = ConsolidatedDataCache(config)
        self.data_exporter = DestinationDataExporter(config)
        
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
        """Process destinations using the configured migration mode and processing controls"""
        
        # Check processing mode configuration
        processing_mode = self.config.get('processing_mode', {})
        
        # Handle theme-only mode
        if processing_mode.get('theme_controls', {}).get('theme_only_mode', False):
            logger.info("🎨 Theme-only processing mode enabled")
            return await self._process_themes_only(destinations)
        
        # Handle nuance-only mode
        if processing_mode.get('nuance_controls', {}).get('nuance_only_mode', False):
            logger.info("🎯 Nuance-only processing mode enabled")
            return await self._process_nuances_only(destinations)
        
        # Handle disabled theme processing
        if not processing_mode.get('enable_theme_processing', True):
            logger.info("🛡️ Theme processing disabled - preserving existing themes")
            if processing_mode.get('enable_nuance_processing', True):
                logger.info("🎯 Running nuance processing only")
                return await self._process_nuances_only(destinations)
            else:
                logger.warning("⚠️ Both theme and nuance processing disabled - no processing will occur")
                return ProcessingResult(
                    destinations_processed=len(destinations),
                    successful_destinations=0,
                    processing_time=0.0,
                    system_used="no_processing",
                    processed_files={}
                )
        
        # Handle disabled nuance processing (theme-only mode without explicit flag)
        if not processing_mode.get('enable_nuance_processing', True):
            logger.info("🛡️ Nuance processing disabled - preserving existing nuances")
            if processing_mode.get('enable_theme_processing', True):
                logger.info("🎨 Running theme processing only")
                return await self._process_themes_only(destinations)
        
        # Standard processing modes
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
    
    async def _process_nuances_only(self, destinations: List[str]) -> ProcessingResult:
        """Process only destination nuances, preserving existing theme data"""
        logger.info("🎯 Processing destination nuances only (preserving existing themes)")
        start_time = time.time()
        
        try:
            # Initialize the destination nuance agent directly if orchestrator not available
            if not self.orchestrator:
                from agents.destination_nuance_agent import DestinationNuanceAgent
                nuance_agent = DestinationNuanceAgent(self.config)
                await nuance_agent.initialize()
                
                # Process each destination for nuances only
                nuance_results = {}
                successful_destinations = 0
                
                for destination in destinations:
                    try:
                        # Check if incremental update is needed
                        existing_nuance_data = self._check_existing_nuance_data(destination)
                        
                        if existing_nuance_data and not self._should_do_incremental_update(destination):
                            logger.info(f"🛡️ Preserving existing nuances for {destination} (sufficient quality)")
                            nuance_results[destination] = existing_nuance_data
                            successful_destinations += 1
                            continue
                        
                        logger.info(f"🎯 Generating nuances for {destination}")
                        task_result = await nuance_agent.execute_task(
                            f"nuance_{destination.replace(' ', '_')}",
                            {
                                'task_type': 'generate_nuances',
                                'data': {'destination': destination}
                            }
                        )
                        
                        if task_result and task_result.is_success:
                            # Merge with existing data if available
                            if existing_nuance_data:
                                merged_data = self._merge_with_existing_data(destination, task_result.data)
                                nuance_results[destination] = merged_data
                                logger.info(f"✅ Nuances merged with existing data for {destination}")
                            else:
                                nuance_results[destination] = task_result.data
                                logger.info(f"✅ New nuances generated for {destination}")
                            successful_destinations += 1
                        else:
                            logger.error(f"❌ Nuance generation failed for {destination}: {task_result.error_message if task_result else 'Unknown error'}")
                            
                    except Exception as e:
                        logger.error(f"❌ Nuance processing failed for {destination}: {e}")
                
                # Create session with nuance files only
                processed_files = await self._create_nuance_only_session(destinations, nuance_results)
                
                processing_time = time.time() - start_time
                
                return ProcessingResult(
                    destinations_processed=len(destinations),
                    successful_destinations=successful_destinations,
                    processing_time=processing_time,
                    system_used="nuance_only",
                    processed_files=processed_files
                )
                
            else:
                # Use orchestrator but only for nuance processing
                logger.info("🤖 Using orchestrator for nuance-only processing")
                
                # Execute nuance workflow only
                nuance_results = {}
                successful_destinations = 0
                
                for destination in destinations:
                    try:
                        logger.info(f"🎯 Processing nuances for {destination} via orchestrator")
                        
                        # Execute only the nuance task
                        task_result = await self.orchestrator._execute_agent_task(
                            'destination_nuance',
                            'generate_nuances',
                            {'destination': destination}
                        )
                        
                        if task_result:
                            nuance_results[destination] = task_result
                            successful_destinations += 1
                            logger.info(f"✅ Nuances processed for {destination}")
                        else:
                            logger.error(f"❌ Nuance processing failed for {destination}")
                            
                    except Exception as e:
                        logger.error(f"❌ Orchestrator nuance processing failed for {destination}: {e}")
                
                # Create session with nuance files only
                processed_files = await self._create_nuance_only_session(destinations, nuance_results)
                
                processing_time = time.time() - start_time
                
                return ProcessingResult(
                    destinations_processed=len(destinations),
                    successful_destinations=successful_destinations,
                    processing_time=processing_time,
                    system_used="nuance_only_orchestrator",
                    processed_files=processed_files
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Nuance-only processing failed: {e}")
            
            return ProcessingResult(
                destinations_processed=len(destinations),
                successful_destinations=0,
                processing_time=processing_time,
                system_used="nuance_only_failed",
                processed_files={},
                comparison_data={"error": str(e)}
            )
    
    async def _process_themes_only(self, destinations: List[str]) -> ProcessingResult:
        """Process only destination themes, preserving existing nuance data"""
        logger.info("🎨 Processing destination themes only (preserving existing nuances)")
        start_time = time.time()
        
        try:
            # Use orchestrator for comprehensive theme processing
            if self.orchestrator:
                logger.info("🤖 Using orchestrator for theme-only processing")
                
                # Execute theme-focused workflow
                theme_results = {}
                successful_destinations = 0
                
                for destination in destinations:
                    try:
                        logger.info(f"🎨 Processing themes for {destination} via orchestrator")
                        
                        # Check if incremental update is needed
                        existing_theme_data = self.theme_lifecycle_manager._get_existing_themes(destination)
                        
                        if existing_theme_data and not self.theme_lifecycle_manager.should_update_themes(destination):
                            logger.info(f"🛡️ Preserving existing themes for {destination} (sufficient quality)")
                            theme_results[destination] = existing_theme_data
                            successful_destinations += 1
                            continue
                        
                        # Execute full agent workflow but only save theme data
                        workflow_result = await self.orchestrator.execute_workflow([destination])
                        
                        if destination in workflow_result and workflow_result[destination].success:
                            # Convert and process theme data
                            theme_data = self._convert_workflow_result_to_legacy_data(destination, workflow_result[destination])
                            
                            # Apply incremental processing if we have existing themes
                            if existing_theme_data:
                                merged_themes = self.theme_lifecycle_manager.merge_theme_data(
                                    destination,
                                    theme_data.get('affinities', []),
                                    existing_theme_data
                                )
                                theme_results[destination] = merged_themes
                                logger.info(f"✅ Themes merged with existing data for {destination}")
                            else:
                                theme_results[destination] = theme_data
                                logger.info(f"✅ New themes generated for {destination}")
                            
                            successful_destinations += 1
                        else:
                            logger.error(f"❌ Theme generation failed for {destination}")
                            
                    except Exception as e:
                        logger.error(f"❌ Theme processing failed for {destination}: {e}")
                
                # Create session with theme files only
                processed_files = await self._create_theme_only_session(destinations, theme_results)
                
                processing_time = time.time() - start_time
                
                return ProcessingResult(
                    destinations_processed=len(destinations),
                    successful_destinations=successful_destinations,
                    processing_time=processing_time,
                    system_used="theme_only_orchestrator",
                    processed_files=processed_files
                )
                
            else:
                logger.error("❌ No orchestrator available for theme processing")
                processing_time = time.time() - start_time
                
                return ProcessingResult(
                    destinations_processed=len(destinations),
                    successful_destinations=0,
                    processing_time=processing_time,
                    system_used="theme_only_failed",
                    processed_files={},
                    comparison_data={"error": "No orchestrator available"}
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Theme-only processing failed: {e}")
            
            return ProcessingResult(
                destinations_processed=len(destinations),
                successful_destinations=0,
                processing_time=processing_time,
                system_used="theme_only_failed",
                processed_files={},
                comparison_data={"error": str(e)}
            )
    
    async def _create_theme_only_session(self, destinations: List[str], theme_results: Dict[str, Any]) -> Dict[str, str]:
        """Create a session directory with only theme files, preserving existing nuance data"""
        import json
        import os
        from datetime import datetime
        from src.dev_staging_manager import DevStagingManager
        
        # Create session directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = f"outputs/session_theme_{timestamp}"
        json_dir = os.path.join(session_dir, "json")
        dashboard_dir = os.path.join(session_dir, "dashboard")
        
        os.makedirs(json_dir, exist_ok=True)
        os.makedirs(dashboard_dir, exist_ok=True)
        
        processed_files = {}
        
        logger.info(f"🔄 Creating theme-only session in {session_dir}")
        
        for destination in destinations:
            dest_filename = destination.lower().replace(', ', '__').replace(' ', '_')
            
            # Only create theme files
            if destination in theme_results:
                enhanced_file_path = os.path.join(json_dir, f"{dest_filename}_enhanced.json")
                evidence_file_path = os.path.join(json_dir, f"{dest_filename}_evidence.json")
                
                try:
                    theme_data = theme_results[destination]
                    
                    # Save enhanced themes JSON
                    with open(enhanced_file_path, 'w', encoding='utf-8') as f:
                        json.dump(theme_data, f, indent=2, ensure_ascii=False)
                    
                    # Create or copy evidence file (may be empty if no evidence collected)
                    evidence_data = theme_data.get('evidence', [])
                    with open(evidence_file_path, 'w', encoding='utf-8') as f:
                        json.dump(evidence_data, f, indent=2, ensure_ascii=False)
                    
                    processed_files[destination] = enhanced_file_path
                    logger.info(f"✅ Saved theme files for {destination}")
                    
                except Exception as e:
                    logger.error(f"❌ Error saving theme files for {destination}: {e}")
        
        # Copy existing nuance data to the new session (read-only mode)
        logger.info("🛡️ Copying existing nuance data for dashboard display...")
        await self._copy_existing_nuance_data_to_session(session_dir, destinations)
        
        # Generate dashboard that shows both new themes and preserved nuances
        await self._generate_theme_debugging_dashboard(session_dir, destinations)
        
        # Stage the session with processed destinations
        try:
            staging_manager = DevStagingManager()
            if staging_manager.stage_session_selective(session_dir, destinations):
                logger.info(f"✅ Theme session staged for development: {session_dir}")
            else:
                logger.warning(f"⚠️ Theme session staging failed: {session_dir}")
        except Exception as e:
            logger.error(f"❌ Staging error: {e}")
        
        return processed_files
    
    async def _copy_existing_nuance_data_to_session(self, session_dir: str, destinations: List[str]):
        """Copy existing nuance data to the new session for dashboard display"""
        import glob
        import shutil
        import os
        
        json_dir = os.path.join(session_dir, "json")
        
        # Find the most recent session with nuance data
        existing_sessions = sorted(glob.glob("outputs/session_nuance_*") + glob.glob("outputs/session_agent_*"), reverse=True)
        
        for existing_session in existing_sessions:
            existing_json_dir = os.path.join(existing_session, "json")
            if not os.path.exists(existing_json_dir):
                continue
                
            copied_count = 0
            for destination in destinations:
                dest_filename = destination.lower().replace(', ', '__').replace(' ', '_')
                
                # Copy nuance files (nuances.json and nuances_evidence.json)
                nuances_file = os.path.join(existing_json_dir, f"{dest_filename}_nuances.json")
                nuances_evidence_file = os.path.join(existing_json_dir, f"{dest_filename}_nuances_evidence.json")
                
                if os.path.exists(nuances_file):
                    shutil.copy2(nuances_file, json_dir)
                    copied_count += 1
                    
                if os.path.exists(nuances_evidence_file):
                    shutil.copy2(nuances_evidence_file, json_dir)
            
            if copied_count > 0:
                logger.info(f"🛡️ Copied {copied_count} nuance files from {existing_session}")
                break
        else:
            logger.warning("⚠️ No existing nuance data found to copy")
    
    async def _generate_theme_debugging_dashboard(self, session_dir: str, destinations: List[str]):
        """Generate a dashboard for theme debugging that shows new themes + preserved nuances"""
        try:
            from src.enhanced_viewer_generator import EnhancedViewerGenerator
            
            dashboard_dir = os.path.join(session_dir, "dashboard")
            json_dir = os.path.join(session_dir, "json")
            
            viewer_generator = EnhancedViewerGenerator()
            
            # Generate pages for destinations that have theme data
            json_files = []
            for destination in destinations:
                dest_filename = destination.lower().replace(', ', '__').replace(' ', '_')
                enhanced_file = os.path.join(json_dir, f"{dest_filename}_enhanced.json")
                
                if os.path.exists(enhanced_file):
                    json_files.append(enhanced_file)
                    
                    # Generate individual destination page
                    viewer_generator.generate_destination_viewer(
                        json_file=enhanced_file,
                        output_dir=dashboard_dir
                    )
            
            if json_files:
                # Generate multi-destination index
                viewer_generator.generate_multi_destination_viewer(
                    json_files=json_files,
                    output_dir=dashboard_dir
                )
                logger.info(f"✅ Generated theme debugging dashboard with {len(json_files)} destinations")
            else:
                logger.warning("⚠️ No theme data available for dashboard generation")
                
        except Exception as e:
            logger.error(f"❌ Dashboard generation failed: {e}")
    
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
                nuances_file_path = os.path.join(json_dir, f"{dest_filename}_nuances.json")
                nuances_evidence_file_path = os.path.join(json_dir, f"{dest_filename}_nuances_evidence.json")
                
                # Convert WorkflowResult to legacy format
                legacy_data = self._convert_workflow_result_to_legacy_data(destination, workflow_result)
                
                # Save enhanced data JSON
                with open(json_file_path, 'w', encoding='utf-8') as f:
                    json.dump(legacy_data['enhanced_data'], f, indent=2, ensure_ascii=False)
                
                # Save evidence data JSON  
                with open(evidence_file_path, 'w', encoding='utf-8') as f:
                    json.dump(legacy_data['evidence_data'], f, indent=2, ensure_ascii=False)
                
                # Save destination nuances JSON (NEW)
                if 'nuances_data' in legacy_data and legacy_data['nuances_data']:
                    with open(nuances_file_path, 'w', encoding='utf-8') as f:
                        json.dump(legacy_data['nuances_data'], f, indent=2, ensure_ascii=False)
                    
                    # Save nuances evidence JSON (NEW)
                    if 'nuances_evidence_data' in legacy_data:
                        with open(nuances_evidence_file_path, 'w', encoding='utf-8') as f:
                            json.dump(legacy_data['nuances_evidence_data'], f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"✅ Saved nuance data for {destination}: {nuances_file_path}")
                
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
                
                # Stage the session for development server with processed destinations
                staging_manager = DevStagingManager()
                try:
                    processed_destinations = list(dashboard_data.keys())
                    if staging_manager.stage_session_selective(session_dir, processed_destinations):
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
    
    async def export_destination_data(self, destination: str, export_format: str = None) -> Dict[str, Any]:
        """Export consolidated destination data"""
        try:
            logger.info(f"🚀 Starting export for {destination}")
            
            # Step 1: Check cache first
            cached_data = await self.consolidated_cache.get_consolidated_data(destination)
            
            if cached_data:
                logger.info(f"📦 Using cached consolidated data for {destination}")
                consolidated_data = cached_data['data']
            else:
                logger.info(f"🔄 Consolidating data from sessions for {destination}")
                
                # Step 2: Consolidate data from all sessions
                consolidated = await self.session_consolidator.consolidate_destination_data(destination)
                
                # Convert to dict format
                consolidated_data = {
                    'destination': consolidated.destination,
                    'themes': consolidated.themes,
                    'nuances': consolidated.nuances,
                    'images': consolidated.images,
                    'evidence': consolidated.evidence,
                    'metadata': consolidated.metadata,
                    'source_sessions': consolidated.source_sessions
                }
                
                # Step 3: Cache the consolidated data
                await self.consolidated_cache.cache_consolidated_data(destination, consolidated_data)
            
            # Step 4: Export the data
            export_result = await self.data_exporter.export_destination(
                destination, 
                consolidated_data, 
                export_format
            )
            
            logger.info(f"✅ Export complete for {destination}: {export_result['export_path']}")
            return export_result
            
        except Exception as e:
            logger.error(f"❌ Export failed for {destination}: {e}")
            raise
    
    async def export_all_destinations(self, export_format: str = None) -> Dict[str, Any]:
        """Export all available destinations"""
        try:
            # Discover all destinations with data
            available_destinations = await self._discover_all_destinations()
            
            if not available_destinations:
                return {
                    'status': 'no_data',
                    'message': 'No destination data found for export',
                    'exported_destinations': []
                }
            
            logger.info(f"🚀 Starting bulk export for {len(available_destinations)} destinations")
            
            export_results = {}
            successful_exports = 0
            
            for destination in available_destinations:
                try:
                    result = await self.export_destination_data(destination, export_format)
                    export_results[destination] = result
                    successful_exports += 1
                except Exception as e:
                    logger.error(f"❌ Export failed for {destination}: {e}")
                    export_results[destination] = {'error': str(e)}
            
            return {
                'status': 'complete',
                'total_destinations': len(available_destinations),
                'successful_exports': successful_exports,
                'export_results': export_results
            }
            
        except Exception as e:
            logger.error(f"❌ Bulk export failed: {e}")
            raise
    
    async def _discover_all_destinations(self) -> List[str]:
        """Discover all destinations that have data available"""
        destinations = set()
        
        try:
            # Look through all session directories
            outputs_dir = Path("outputs")
            if not outputs_dir.exists():
                return []
            
            for session_dir in outputs_dir.glob("session_*"):
                if not session_dir.is_dir():
                    continue
                
                json_dir = session_dir / "json"
                if not json_dir.exists():
                    continue
                
                # Parse destination names from file names
                for json_file in json_dir.glob("*_enhanced.json"):
                    dest_name = json_file.stem.replace('_enhanced', '').replace('__', ', ').replace('_', ' ')
                    destinations.add(dest_name.title())
                
                for json_file in json_dir.glob("*_nuances.json"):
                    dest_name = json_file.stem.replace('_nuances', '').replace('__', ', ').replace('_', ' ')
                    destinations.add(dest_name.title())
            
            return sorted(list(destinations))
            
        except Exception as e:
            logger.error(f"Failed to discover destinations: {e}")
            return []
    
    async def get_consolidation_statistics(self, destination: str = None) -> Dict[str, Any]:
        """Get consolidation and cache statistics"""
        try:
            stats = {
                'system_statistics': {
                    'cache_stats': await self.consolidated_cache.get_cache_statistics(),
                    'export_stats': await self.data_exporter.get_export_statistics()
                }
            }
            
            if destination:
                stats['destination_statistics'] = {
                    'consolidation_stats': await self.session_consolidator.get_consolidation_statistics(destination),
                    'theme_stats': self.theme_lifecycle_manager.get_theme_statistics(destination)
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {'error': str(e)}
    
    def _convert_nuance_result_to_json_format(self, destination: str, nuance_result: Any) -> Dict[str, Any]:
        """Convert DestinationNuanceResult to proper JSON format for dashboard display"""
        from datetime import datetime
        
        # Handle the actual data structure: dict with 'result' key containing AgentResponse
        if isinstance(nuance_result, dict) and 'result' in nuance_result:
            agent_response = nuance_result['result']  # AgentResponse object
            nuance_data = agent_response.data  # DestinationNuanceResult object
        elif hasattr(nuance_result, 'data'):
            nuance_data = nuance_result.data
        else:
            nuance_data = nuance_result
        
        # Extract nuance collection and evidence
        nuance_collection = getattr(nuance_data, 'nuance_collection', None)
        evidence_list = getattr(nuance_data, 'evidence', [])
        
        # Create 3-tier nuances structure
        nuances_data = {
            'destination': destination,
            'destination_id': destination.lower().replace(', ', '_').replace(' ', '_'),
            'destination_nuances': [],
            'hotel_expectations': [],
            'vacation_rental_expectations': [],
            'quality_score': getattr(nuance_data, 'overall_quality_score', 0.0),
            'processing_time': getattr(nuance_data, 'processing_time', 0.0),
            'statistics': getattr(nuance_data, 'statistics', {}),
            'processing_metadata': {
                'processing_date': datetime.now().isoformat(),
                'source_system': 'destination_nuance_agent',
                'success': True,
                'enabled': True,
                'fallback_mode': False
            }
        }
        
        # Convert nuance collection to proper format
        if nuance_collection:
            # Process destination nuances
            for nuance in nuance_collection.destination_nuances:
                nuance_info = {
                    'phrase': nuance.phrase,
                    'score': nuance.score,
                    'category': nuance.category,
                    'confidence': nuance.score,
                    'source_models': getattr(nuance, 'contributing_models', []),
                    'search_hits': nuance.search_hits,
                    'uniqueness_ratio': nuance.uniqueness_ratio,
                    'evidence_sources': nuance.evidence_sources,
                    'source_urls': getattr(nuance, 'source_urls', []),
                    'validation_data': nuance.validation_metadata
                }
                nuances_data['destination_nuances'].append(nuance_info)
            
            # Process hotel expectations
            for nuance in nuance_collection.hotel_expectations:
                nuance_info = {
                    'phrase': nuance.phrase,
                    'score': nuance.score,
                    'category': nuance.category,
                    'confidence': nuance.score,
                    'source_models': getattr(nuance, 'contributing_models', []),
                    'search_hits': nuance.search_hits,
                    'uniqueness_ratio': nuance.uniqueness_ratio,
                    'evidence_sources': nuance.evidence_sources,
                    'source_urls': getattr(nuance, 'source_urls', []),
                    'validation_data': nuance.validation_metadata
                }
                nuances_data['hotel_expectations'].append(nuance_info)
            
            # Process vacation rental expectations
            for nuance in nuance_collection.vacation_rental_expectations:
                nuance_info = {
                    'phrase': nuance.phrase,
                    'score': nuance.score,
                    'category': nuance.category,
                    'confidence': nuance.score,
                    'source_models': getattr(nuance, 'contributing_models', []),
                    'search_hits': nuance.search_hits,
                    'uniqueness_ratio': nuance.uniqueness_ratio,
                    'evidence_sources': nuance.evidence_sources,
                    'source_urls': getattr(nuance, 'source_urls', []),
                    'validation_data': nuance.validation_metadata
                }
                nuances_data['vacation_rental_expectations'].append(nuance_info)
        
        # Update counts and metadata
        total_nuances = (len(nuances_data['destination_nuances']) + 
                        len(nuances_data['hotel_expectations']) + 
                        len(nuances_data['vacation_rental_expectations']))
        
        nuances_data['processing_metadata'].update({
            'nuances_count': total_nuances,
            'destination_nuances_count': len(nuances_data['destination_nuances']),
            'hotel_expectations_count': len(nuances_data['hotel_expectations']),
            'vacation_rental_expectations_count': len(nuances_data['vacation_rental_expectations'])
        })
        
        # Create evidence data with proper URL extraction
        nuances_evidence_data = []
        for evidence_item in evidence_list:
            # Extract real website URLs from search metadata instead of search engine URL
            real_urls = []
            search_metadata = getattr(evidence_item, 'search_metadata', {})
            
            # Get primary source URL (the main validated website)
            primary_source = search_metadata.get('primary_source', '')
            if primary_source and primary_source != 'https://search.brave.com/':
                real_urls.append(primary_source)
            
            # Find corresponding nuance to get all source URLs
            phrase = evidence_item.phrase
            category = evidence_item.category
            
            # Look for this phrase in the nuance collection to get source_urls
            all_nuances = []
            if nuance_collection:
                all_nuances.extend(nuance_collection.destination_nuances)
                all_nuances.extend(nuance_collection.hotel_expectations) 
                all_nuances.extend(nuance_collection.vacation_rental_expectations)
            
            for nuance in all_nuances:
                if nuance.phrase == phrase and nuance.category == category:
                    source_urls = getattr(nuance, 'source_urls', [])
                    for url in source_urls:
                        if url and url != 'https://search.brave.com/' and url not in real_urls:
                            real_urls.append(url)
                    break
            
            # Fallback to search engine URL only if no real URLs found
            if not real_urls:
                real_urls = [evidence_item.source_url] if hasattr(evidence_item, 'source_url') else []
            
            evidence_info = {
                'phrase': evidence_item.phrase,
                'category': evidence_item.category,
                'search_hits': getattr(evidence_item, 'search_hits', 0),
                'uniqueness_ratio': getattr(evidence_item, 'uniqueness_ratio', 1.0),
                'authority_sources': real_urls,  # Now contains real website URLs
                'evidence_diversity': evidence_item.authority_score,
                'content_snippet': evidence_item.content_snippet,
                'relevance_score': evidence_item.relevance_score,
                'metadata': evidence_item.search_metadata
            }
            nuances_evidence_data.append(evidence_info)
        
        # Format evidence data structure
        evidence_json = {
            'destination': destination,
            'evidence': nuances_evidence_data,
            'metadata': {
                'generation_timestamp': datetime.now().isoformat(),
                'total_evidence_pieces': len(nuances_evidence_data),
                'processing_mode': 'nuance_only',
                'evidence_by_category': {
                    'destination': len([e for e in nuances_evidence_data if e['category'] == 'destination']),
                    'hotel': len([e for e in nuances_evidence_data if e['category'] == 'hotel']),
                    'vacation_rental': len([e for e in nuances_evidence_data if e['category'] == 'vacation_rental'])
                }
            }
        }
        
        return {
            'nuances_data': nuances_data,
            'nuances_evidence_data': evidence_json
        }
    
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
        
        # Extract destination nuances (NEW)
        destination_nuances_data = final_data.get('destination_nuances', {})
        
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
        
        # Process destination nuances (NEW)
        nuances_data = {}
        nuances_evidence_data = []
        
        if destination_nuances_data and destination_nuances_data.get('enabled', False):
            nuances_list = destination_nuances_data.get('nuances', [])
            evidence_list = destination_nuances_data.get('evidence', [])
            
            # Format nuances in the expected structure - CONVERT 3-TIER TO DISPLAY FORMAT
            formatted_nuances = []
            for nuance_item in nuances_list:
                if isinstance(nuance_item, dict):
                    # Dict format - extract real evidence data
                    nuance_info = {
                        'phrase': nuance_item.get('phrase', ''),
                        'score': nuance_item.get('score', 0.0),
                        'category': nuance_item.get('category', 'destination'),
                        'confidence': nuance_item.get('score', 0.8),  # Use score as confidence
                        'source_models': nuance_item.get('contributing_models', []),
                        'search_hits': nuance_item.get('search_hits', 0),
                        'uniqueness_ratio': nuance_item.get('uniqueness_ratio', 1.0),
                        'evidence_sources': nuance_item.get('evidence_sources', []),
                        'source_urls': nuance_item.get('source_urls', []),  # REAL URLs from search validation
                        'validation_data': nuance_item.get('validation_metadata', {})
                    }
                elif hasattr(nuance_item, '__dict__'):  # NuancePhrase object
                    nuance_info = {
                        'phrase': getattr(nuance_item, 'phrase', ''),
                        'score': getattr(nuance_item, 'score', 0.0),
                        'category': getattr(nuance_item, 'category', 'destination'),
                        'confidence': getattr(nuance_item, 'score', 0.8),
                        'source_models': getattr(nuance_item, 'contributing_models', []),
                        'search_hits': getattr(nuance_item, 'search_hits', 0),
                        'uniqueness_ratio': getattr(nuance_item, 'uniqueness_ratio', 1.0),
                        'evidence_sources': getattr(nuance_item, 'evidence_sources', []),
                        'source_urls': getattr(nuance_item, 'source_urls', []),  # REAL URLs
                        'validation_data': getattr(nuance_item, 'validation_metadata', {})
                    }
                else:
                    continue
                
                formatted_nuances.append(nuance_info)
            
            # Format nuances evidence - CONVERT TO DISPLAY FORMAT WITH REAL URLS
            for evidence_item in evidence_list:
                if isinstance(evidence_item, dict):
                    evidence_info = {
                        'phrase': evidence_item.get('phrase', ''),
                        'search_hits': evidence_item.get('search_hits', 0),
                        'uniqueness_ratio': evidence_item.get('uniqueness_ratio', 1.0),
                        'authority_sources': evidence_item.get('source_urls', []),  # Use source_urls as authority sources
                        'evidence_diversity': evidence_item.get('authority_score', 0.8),  # Use authority score as diversity
                        'metadata': evidence_item.get('search_metadata', {})
                    }
                elif hasattr(evidence_item, '__dict__'):  # NuanceEvidence object
                    evidence_info = {
                        'phrase': getattr(evidence_item, 'phrase', ''),
                        'search_hits': getattr(evidence_item, 'search_hits', 0),
                        'uniqueness_ratio': getattr(evidence_item, 'uniqueness_ratio', 1.0),
                        'authority_sources': [getattr(evidence_item, 'source_url', '')],  # Single URL as list
                        'evidence_diversity': getattr(evidence_item, 'authority_score', 0.8),
                        'metadata': getattr(evidence_item, 'search_metadata', {})
                    }
                else:
                    continue
                
                nuances_evidence_data.append(evidence_info)
            
            # Create nuances data structure - SUMMARY WITH REAL STATS
            nuances_data = {
                'destination': destination,
                'destination_id': destination.lower().replace(', ', '_').replace(' ', '_'),
                'nuances': formatted_nuances,
                'quality_score': destination_nuances_data.get('quality_score', 0.0),
                'processing_time': destination_nuances_data.get('processing_time', 0.0),
                'statistics': destination_nuances_data.get('statistics', {}),
                'processing_metadata': {
                    'processing_date': datetime.now().isoformat(),
                    'source_system': 'destination_nuance_agent',
                    'nuances_count': len(formatted_nuances),
                    'evidence_count': len(nuances_evidence_data),
                    'success': destination_nuances_data.get('success', False),
                    'enabled': True,
                    'fallback_mode': not destination_nuances_data.get('statistics', {}).get('search_validation_enabled', True)  # Check if real search was used
                }
            }
        
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
            'destination_nuances_summary': {  # NEW: Add nuances summary to enhanced data
                'enabled': bool(nuances_data),
                'nuances_count': len(nuances_data.get('nuances', [])) if nuances_data else 0,
                'quality_score': nuances_data.get('quality_score', 0.0) if nuances_data else 0.0,
                'processing_time': nuances_data.get('processing_time', 0.0) if nuances_data else 0.0,
                'success': nuances_data.get('processing_metadata', {}).get('success', False) if nuances_data else False
            },
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
            'evidence_data': evidence_data,
            'nuances_data': nuances_data,
            'nuances_evidence_data': nuances_evidence_data
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
    
    def _check_existing_nuance_data(self, destination: str) -> Optional[Dict[str, Any]]:
        """Check if existing nuance data exists for a destination"""
        try:
            # Check for existing data in outputs directories
            outputs_dir = Path("outputs")
            if not outputs_dir.exists():
                return None
            
            # Look for the most recent session with nuance data for this destination
            destination_id = destination.lower().replace(', ', '_').replace(' ', '_')
            
            # Look through session directories (most recent first)
            session_dirs = sorted([d for d in outputs_dir.iterdir() if d.is_dir()], 
                                 key=lambda x: x.stat().st_mtime, reverse=True)
            
            for session_dir in session_dirs:
                json_dir = session_dir / "json"
                if not json_dir.exists():
                    continue
                
                nuance_file = json_dir / f"{destination_id}_nuances.json"
                if nuance_file.exists():
                    with open(nuance_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                    
                    # Check if data is recent enough to preserve
                    processing_date = existing_data.get('processing_metadata', {}).get('processing_date', '')
                    if self._is_data_recent_enough(processing_date):
                        logger.info(f"Found existing nuance data for {destination} from {processing_date}")
                        return existing_data
            
            return None
            
        except Exception as e:
            logger.warning(f"Error checking existing nuance data for {destination}: {e}")
            return None
    
    def _should_preserve_existing_data(self) -> bool:
        """Check if existing data should be preserved based on configuration"""
        lifecycle_config = self.config.get('destination_nuances', {}).get('data_lifecycle', {})
        return lifecycle_config.get('preserve_existing_data', True)
    
    def _should_do_incremental_update(self, destination: str) -> bool:
        """Check if an incremental update should be performed"""
        lifecycle_config = self.config.get('destination_nuances', {}).get('data_lifecycle', {})
        
        if not lifecycle_config.get('enable_incremental_updates', True):
            return False
        
        existing_data = self._check_existing_nuance_data(destination)
        if not existing_data:
            return False
        
        # Check if data is old enough to warrant update
        processing_date = existing_data.get('processing_metadata', {}).get('processing_date', '')
        threshold_days = lifecycle_config.get('incremental_update_threshold_days', 7)
        
        return not self._is_data_recent_enough(processing_date, threshold_days)
    
    def _is_data_recent_enough(self, processing_date: str, threshold_days: int = 1) -> bool:
        """Check if data is recent enough based on threshold"""
        if not processing_date:
            return False
        
        try:
            from datetime import datetime, timedelta
            processed_at = datetime.fromisoformat(processing_date.replace('Z', '+00:00'))
            threshold = datetime.now() - timedelta(days=threshold_days)
            return processed_at > threshold
        except Exception:
            return False
    
    def _merge_with_existing_data(self, destination: str, new_data: Any) -> Dict[str, Any]:
        """Merge new data with existing data for incremental updates"""
        existing_data = self._check_existing_nuance_data(destination)
        if not existing_data:
            return self._convert_nuance_result_to_json_format(destination, new_data)
        
        # Convert new data to JSON format
        new_json_data = self._convert_nuance_result_to_json_format(destination, new_data)
        
        # Simple merge strategy: use new data if quality is better, otherwise keep existing
        new_quality = new_json_data['nuances_data'].get('quality_score', 0.0)
        existing_quality = existing_data.get('quality_score', 0.0)
        
        if new_quality > existing_quality:
            logger.info(f"Using new data for {destination} (quality: {new_quality:.3f} > {existing_quality:.3f})")
            return new_json_data
        else:
            logger.info(f"Preserving existing data for {destination} (quality: {existing_quality:.3f} >= {new_quality:.3f})")
            return {
                'nuances_data': existing_data,
                'nuances_evidence_data': existing_data  # Simplified for now
            }
    
    async def _create_nuance_only_session(self, destinations: List[str], nuance_results: Dict[str, Any]) -> Dict[str, str]:
        """Create a session directory with only nuance files, preserving existing theme data"""
        import json
        import os
        from datetime import datetime
        from src.dev_staging_manager import DevStagingManager
        
        # Create session directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = f"outputs/session_nuance_{timestamp}"
        json_dir = os.path.join(session_dir, "json")
        dashboard_dir = os.path.join(session_dir, "dashboard")
        
        os.makedirs(json_dir, exist_ok=True)
        os.makedirs(dashboard_dir, exist_ok=True)
        
        processed_files = {}
        
        logger.info(f"🔄 Creating nuance-only session in {session_dir}")
        
        for destination in destinations:
            dest_filename = destination.lower().replace(', ', '__').replace(' ', '_')
            
            # Only create nuance files
            if destination in nuance_results:
                nuances_file_path = os.path.join(json_dir, f"{dest_filename}_nuances.json")
                nuances_evidence_file_path = os.path.join(json_dir, f"{dest_filename}_nuances_evidence.json")
                
                try:
                    nuance_data = nuance_results[destination]
                    
                    # Convert DestinationNuanceResult to proper JSON format
                    converted_data = self._convert_nuance_result_to_json_format(destination, nuance_data)
                    
                    # Check if JSON minification is enabled
                    file_config = self.config.get('destination_nuances', {}).get('file_organization', {})
                    optimize_json = file_config.get('optimize_json_storage', True)
                    
                    # Save nuances JSON (minified if enabled)
                    with open(nuances_file_path, 'w', encoding='utf-8') as f:
                        if optimize_json:
                            json.dump(converted_data['nuances_data'], f, separators=(',', ':'), ensure_ascii=False)
                        else:
                            json.dump(converted_data['nuances_data'], f, indent=2, ensure_ascii=False)
                    
                    # Save nuances evidence JSON (minified if enabled)
                    with open(nuances_evidence_file_path, 'w', encoding='utf-8') as f:
                        if optimize_json:
                            json.dump(converted_data['nuances_evidence_data'], f, separators=(',', ':'), ensure_ascii=False)
                        else:
                            json.dump(converted_data['nuances_evidence_data'], f, indent=2, ensure_ascii=False)
                    
                    processed_files[destination] = nuances_file_path
                    logger.info(f"✅ Saved nuance files for {destination}")
                    
                except Exception as e:
                    logger.error(f"❌ Error saving nuance files for {destination}: {e}")
        
        # Copy existing theme data to the new session (read-only mode)
        logger.info("🛡️ Copying existing theme data for dashboard display...")
        await self._copy_existing_theme_data_to_session(session_dir, destinations)
        
        # Generate dashboard that shows both preserved themes and new nuances
        await self._generate_nuance_debugging_dashboard(session_dir, destinations)
        
        # Stage the session with processed destinations
        try:
            staging_manager = DevStagingManager()
            if staging_manager.stage_session_selective(session_dir, destinations):
                logger.info(f"✅ Nuance session staged for development: {session_dir}")
            else:
                logger.warning(f"⚠️ Nuance session staging failed: {session_dir}")
        except Exception as e:
            logger.error(f"❌ Staging error: {e}")
        
        return processed_files
    
    async def _copy_existing_theme_data_to_session(self, session_dir: str, destinations: List[str]):
        """Copy existing theme data to the new session for dashboard display"""
        import glob
        import shutil
        import os
        
        json_dir = os.path.join(session_dir, "json")
        
        # Find the most recent session with theme data
        existing_sessions = sorted(glob.glob("outputs/session_agent_*") + glob.glob("outputs/session_theme_*"), reverse=True)
        
        for existing_session in existing_sessions:
            existing_json_dir = os.path.join(existing_session, "json")
            if not os.path.exists(existing_json_dir):
                continue
                
            copied_count = 0
            for destination in destinations:
                dest_filename = destination.lower().replace(', ', '__').replace(' ', '_')
                
                # Copy theme files (enhanced.json and evidence.json)
                enhanced_file = os.path.join(existing_json_dir, f"{dest_filename}_enhanced.json")
                evidence_file = os.path.join(existing_json_dir, f"{dest_filename}_evidence.json")
                
                if os.path.exists(enhanced_file):
                    shutil.copy2(enhanced_file, json_dir)
                    copied_count += 1
                    
                if os.path.exists(evidence_file):
                    shutil.copy2(evidence_file, json_dir)
            
            if copied_count > 0:
                logger.info(f"🛡️ Copied {copied_count} theme files from {existing_session}")
                break
        else:
            logger.warning("⚠️ No existing theme data found to copy")
    
    async def _generate_nuance_debugging_dashboard(self, session_dir: str, destinations: List[str]):
        """Generate a dashboard for nuance debugging that shows preserved themes + new nuances"""
        try:
            from src.enhanced_viewer_generator import EnhancedViewerGenerator
            
            dashboard_dir = os.path.join(session_dir, "dashboard")
            json_dir = os.path.join(session_dir, "json")
            
            viewer_generator = EnhancedViewerGenerator()
            
            # Generate pages for destinations that have theme data
            json_files = []
            for destination in destinations:
                dest_filename = destination.lower().replace(', ', '__').replace(' ', '_')
                enhanced_file = os.path.join(json_dir, f"{dest_filename}_enhanced.json")
                
                if os.path.exists(enhanced_file):
                    json_files.append(enhanced_file)
                    
                    # Generate individual destination page
                    viewer_generator.generate_destination_viewer(
                        json_file=enhanced_file,
                        output_dir=dashboard_dir
                    )
            
            if json_files:
                # Generate multi-destination index
                viewer_generator.generate_multi_destination_viewer(
                    json_files=json_files,
                    output_dir=dashboard_dir
                )
                logger.info(f"✅ Generated nuance debugging dashboard with {len(json_files)} destinations")
            else:
                logger.warning("⚠️ No theme data available for dashboard generation")
                
        except Exception as e:
            logger.error(f"❌ Dashboard generation failed: {e}")
    
    async def _process_themes_incrementally(self, destinations: List[str], agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process themes with incremental updates using the theme lifecycle manager"""
        processed_themes = {}
        
        for destination in destinations:
            try:
                # Check if theme update is needed
                if not self.theme_lifecycle_manager.should_update_themes(destination):
                    logger.info(f"🛡️ Preserving existing themes for {destination}")
                    existing_themes = self.theme_lifecycle_manager._get_existing_themes(destination)
                    if existing_themes:
                        processed_themes[destination] = existing_themes
                    continue
                
                # Get new theme data from agent results
                if destination in agent_results:
                    new_theme_data = agent_results[destination]
                    
                    # Check if we have existing themes to merge
                    existing_themes = self.theme_lifecycle_manager._get_existing_themes(destination)
                    
                    if existing_themes:
                        # Merge with existing themes
                        logger.info(f"🔄 Merging themes for {destination}")
                        merged_themes = self.theme_lifecycle_manager.merge_theme_data(
                            destination, 
                            new_theme_data.get('affinities', []), 
                            existing_themes
                        )
                        processed_themes[destination] = merged_themes
                        logger.info(f"✅ Themes merged for {destination}")
                    else:
                        # New theme data
                        processed_themes[destination] = new_theme_data
                        logger.info(f"✅ New themes processed for {destination}")
                
            except Exception as e:
                logger.error(f"❌ Theme incremental processing failed for {destination}: {e}")
        
        return processed_themes 