"""
Seasonal Image Agent

Agent responsible for generating seasonal images for travel destinations using DALL-E.
Integrates with the multi-agent workflow to add visual enhancements to destination content.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentMessage, AgentState
from .data_models import AgentResponse, ResponseFactory
from src.seasonal_image_generator import SeasonalImageGenerator

logger = logging.getLogger(__name__)

@dataclass
class SeasonalImageResult:
    """Result from seasonal image generation"""
    destination: str
    images_generated: Dict[str, Dict[str, Any]]  # season -> image metadata
    collage_created: bool
    processing_time: float
    success: bool
    error_messages: List[str]
    metadata: Dict[str, Any]

class SeasonalImageAgent(BaseAgent):
    """
    Agent responsible for generating seasonal images for destinations.
    
    Features:
    - DALL-E 3 integration for high-quality image generation
    - Seasonal prompt templates for consistent styling
    - Collage creation from individual seasonal images
    - Graceful error handling and fallback strategies
    - Integration with the multi-agent workflow
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("seasonal_image", config)
        
        # Configuration
        self.seasonal_config = config.get('seasonal_imagery', {})
        self.enabled = self.seasonal_config.get('enabled', True)
        self.max_retries = self.seasonal_config.get('max_retries', 2)
        self.graceful_degradation = self.seasonal_config.get('graceful_degradation', True)
        
        # Image generator instance
        self.image_generator = None
        
    async def _initialize_agent_specific(self):
        """Initialize the seasonal image generator"""
        if not self.enabled:
            self.logger.info("🎨 Seasonal imagery disabled in configuration")
            return
        
        try:
            # Initialize the image generator
            self.image_generator = SeasonalImageGenerator(self.config)
            
            # Register message handlers
            self.register_message_handler("generate_seasonal_images", self._handle_generate_seasonal_images)
            
            self.logger.info("🎨 Seasonal Image Agent initialized successfully")
            
        except Exception as e:
            if self.graceful_degradation:
                self.logger.warning(f"🎨 Seasonal Image Agent initialization failed (graceful degradation): {e}")
                self.enabled = False
            else:
                self.logger.error(f"❌ Seasonal Image Agent initialization failed: {e}")
                raise
    
    async def _execute_task_specific(self, task_id: str, task_definition: Dict[str, Any]) -> Any:
        """Execute seasonal image specific tasks"""
        task_type = task_definition.get('task_type')
        task_data = task_definition.get('data', {})
        
        if task_type == 'generate_seasonal_images':
            return await self._handle_generate_seasonal_images(task_id, task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _handle_generate_seasonal_images(self, task_id: str, task_data: Dict[str, Any]) -> AgentResponse:
        """Generate seasonal images for a destination"""
        
        if not self.enabled:
            return ResponseFactory.success(
                data=SeasonalImageResult(
                    destination=task_data.get('destination', 'Unknown'),
                    images_generated={},
                    collage_created=False,
                    processing_time=0.0,
                    success=False,
                    error_messages=['Seasonal imagery disabled'],
                    metadata={'disabled': True}
                ),
                agent_id=self.agent_id,
                task_id=task_id,
                processing_time=0.0
            )
        
        start_time = time.time()
        destination = task_data.get('destination')
        output_dir = task_data.get('output_dir')
        
        if not destination:
            return ResponseFactory.error(
                error_message="Destination is required for seasonal image generation",
                agent_id=self.agent_id,
                task_id=task_id,
                processing_time=time.time() - start_time
            )
        
        if not output_dir:
            return ResponseFactory.error(
                error_message="Output directory is required for seasonal image generation",
                agent_id=self.agent_id,
                task_id=task_id,
                processing_time=time.time() - start_time
            )
        
        try:
            self.logger.info(f"🎨 Generating seasonal images for {destination}")
            
            # Create images directory within the session output
            images_dir = Path(output_dir) / "images"
            images_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate seasonal images
            retry_count = 0
            last_error = None
            
            while retry_count <= self.max_retries:
                try:
                    images_generated = await asyncio.get_event_loop().run_in_executor(
                        None, 
                        self.image_generator.generate_seasonal_images,
                        destination,
                        images_dir
                    )
                    
                    # Success! Create result
                    processing_time = time.time() - start_time
                    
                    result = SeasonalImageResult(
                        destination=destination,
                        images_generated=images_generated,
                        collage_created='collage' in images_generated and not images_generated['collage'].get('error'),
                        processing_time=processing_time,
                        success=True,
                        error_messages=[],
                        metadata={
                            'images_directory': str(images_dir.relative_to(Path(output_dir).parent)),
                            'total_images': len([k for k in images_generated.keys() if k != 'collage']),
                            'generation_time': processing_time,
                            'retry_count': retry_count
                        }
                    )
                    
                    self.logger.info(f"✅ Seasonal images generated for {destination}: {len(images_generated)} items in {processing_time:.1f}s")
                    
                    return ResponseFactory.success(
                        data=result,
                        agent_id=self.agent_id,
                        task_id=task_id,
                        processing_time=processing_time
                    )
                    
                except Exception as e:
                    retry_count += 1
                    last_error = str(e)
                    
                    if retry_count <= self.max_retries:
                        self.logger.warning(f"🎨 Seasonal image generation failed (attempt {retry_count}/{self.max_retries + 1}): {e}")
                        await asyncio.sleep(1.0 * retry_count)  # Progressive backoff
                    else:
                        self.logger.error(f"❌ Seasonal image generation failed after {retry_count} attempts: {e}")
                        break
            
            # All retries failed
            processing_time = time.time() - start_time
            
            if self.graceful_degradation:
                # Return success with error metadata for graceful degradation
                result = SeasonalImageResult(
                    destination=destination,
                    images_generated={},
                    collage_created=False,
                    processing_time=processing_time,
                    success=False,
                    error_messages=[last_error or "Unknown error"],
                    metadata={
                        'graceful_degradation': True,
                        'retry_count': retry_count,
                        'final_error': last_error
                    }
                )
                
                self.logger.warning(f"🎨 Seasonal image generation failed for {destination}, continuing with graceful degradation")
                
                return ResponseFactory.success(
                    data=result,
                    agent_id=self.agent_id,
                    task_id=task_id,
                    processing_time=processing_time
                )
            else:
                return ResponseFactory.error(
                    error_message=f"Seasonal image generation failed: {last_error}",
                    agent_id=self.agent_id,
                    task_id=task_id,
                    processing_time=processing_time
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"❌ Unexpected error in seasonal image generation for {destination}: {e}")
            
            return ResponseFactory.error(
                error_message=f"Unexpected error: {str(e)}",
                agent_id=self.agent_id,
                task_id=task_id,
                processing_time=processing_time
            )
    
    async def _cleanup_agent_specific(self):
        """Cleanup seasonal image specific resources"""
        self.image_generator = None
        self.logger.info("🎨 Seasonal Image Agent cleanup complete") 