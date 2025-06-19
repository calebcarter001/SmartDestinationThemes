"""
Intelligence Enhancement Agent

Intelligent theme enhancement with adaptive attribute processing.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentMessage, AgentState
from .data_models import (
    IntelligenceEnhancementResult, ThemeData, AgentResponse, 
    ResponseFactory, TaskStatus, DataConverter
)

# Import existing components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.enhanced_data_processor import EnhancedDataProcessor

logger = logging.getLogger(__name__)

# EnhancementResult is now imported as IntelligenceEnhancementResult from data_models

class IntelligenceEnhancementAgent(BaseAgent):
    """
    Intelligence enhancement agent that provides adaptive attribute processing
    and context-aware theme enhancement.
    
    Features:
    - Adaptive attribute selection based on destination context
    - Dependency-aware processing order
    - Quality-driven optimization
    - Intelligent attribute prioritization
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("intelligence_enhancement", config)
        
        # Configuration
        agent_config = config.get('agents', {}).get('intelligence_enhancement', {})
        self.adaptive_processing = agent_config.get('adaptive_attribute_processing', True)
        self.dependency_aware = agent_config.get('dependency_aware_processing', True)
        self.quality_driven = agent_config.get('quality_driven_optimization', True)
        self.enable_prioritization = agent_config.get('enable_attribute_prioritization', True)
        
        # Initialize wrapped processor
        self.data_processor = None
        
        # Performance tracking
        self.enhancement_metrics = {
            'total_enhancements': 0,
            'successful_enhancements': 0,
            'average_processing_time': 0.0,
            'average_attributes_processed': 0.0,
            'average_quality_score': 0.0
        }
    
    async def _initialize_agent_specific(self):
        """Initialize intelligence enhancement components"""
        try:
            # Initialize the enhanced data processor
            self.data_processor = EnhancedDataProcessor(self.config)
            
            # Register task handlers
            self.register_message_handler("enhance_themes", self._handle_enhancement_request)
            self.register_message_handler("analyze_attributes", self._handle_attribute_analysis)
            
            self.logger.info("Intelligence Enhancement Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Intelligence Enhancement Agent: {e}")
            raise
    
    async def _execute_task_specific(self, task_id: str, task_definition: Dict[str, Any]) -> AgentResponse:
        """Execute intelligence enhancement tasks"""
        task_type = task_definition.get('task_type')
        task_data = task_definition.get('data', {})
        
        try:
            start_time = time.time()
            
            if task_type == 'enhance_themes':
                result = await self._enhance_themes(task_data)
                processing_time = time.time() - start_time
                return ResponseFactory.success(
                    data=result, 
                    agent_id=self.agent_id, 
                    task_id=task_id,
                    processing_time=processing_time
                )
            elif task_type == 'analyze_attributes':
                result = await self._analyze_attributes(task_data)
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
    
    async def _enhance_themes(self, task_data: Dict[str, Any]) -> IntelligenceEnhancementResult:
        """Execute intelligent theme enhancement"""
        themes = task_data.get('themes', [])
        destination_context = task_data.get('destination_context', {})
        evidence_data = task_data.get('evidence_data', {})
        
        destination = destination_context.get('destination', 'Unknown')
        
        if not themes:
            return IntelligenceEnhancementResult(
                destination=destination,
                enhanced_themes=[],
                intelligence_insights={},
                processing_time=0.0,
                errors=["No themes provided for enhancement"]
            )
        
        start_time = time.time()
        self.logger.info(f"🧠 Starting intelligence enhancement for {destination} with {len(themes)} themes")
        
        try:
            # Convert ThemeData objects to dictionary format expected by Enhanced Data Processor
            affinities_dicts = []
            for theme in themes:
                if hasattr(theme, '__dict__'):  # ThemeData object
                    theme_dict = {
                        'theme': theme.theme,
                        'category': theme.category,
                        'confidence': theme.confidence,
                        'description': theme.description,
                        'sub_themes': theme.nano_themes,  # Map nano_themes to sub_themes
                        'rationale': theme.description,
                        'price_insights': theme.price_insights or {},
                        'traveler_types': theme.traveler_types or []
                    }
                elif isinstance(theme, dict):  # Already dictionary format
                    theme_dict = theme
                else:
                    continue
                    
                affinities_dicts.append(theme_dict)
            
            # Create destination data structure compatible with existing processor
            destination_data = {
                'destination_name': destination,
                'affinities': affinities_dicts,  # Use 'affinities' key with dict format
                'processing_metadata': {
                    'agent_enhanced': True,
                    'enhancement_timestamp': time.time()
                }
            }
            
            self.logger.info(f"🔧 Processing {len(affinities_dicts)} affinities for intelligence enhancement")
            
            # Convert evidence_data to web_data format expected by Enhanced Data Processor
            web_data = {}
            if evidence_data and 'content' in evidence_data:
                web_data[destination] = evidence_data
            
            # Use existing enhanced data processor logic with proper web data
            enhanced_data = self.data_processor._process_single_destination_with_progress(
                destination_data, destination, web_data
            )
            
            # Extract enhanced themes and insights
            enhanced_themes_dicts = enhanced_data.get('affinities', [])
            intelligence_insights = enhanced_data.get('intelligence_insights', {})
            composition_analysis = enhanced_data.get('composition_analysis', {})
            quality_assessment = enhanced_data.get('quality_assessment', {})
            
            self.logger.info(f"🎯 Enhanced data processor returned {len(enhanced_themes_dicts)} enhanced themes")
            self.logger.info(f"📊 Intelligence insights keys: {list(intelligence_insights.keys())}")
            
            # Keep enhanced themes as dictionaries instead of converting to ThemeData objects
            # The enhanced themes have complex nested structures that are better preserved as dicts
            enhanced_themes = enhanced_themes_dicts  # Keep as dictionaries
            
            processing_time = time.time() - start_time
            
            # Create comprehensive intelligence insights including all enhanced data
            comprehensive_insights = {
                **intelligence_insights,
                'composition_analysis': composition_analysis,
                'quality_assessment': quality_assessment,
                'enhanced_themes_count': len(enhanced_themes),
                'processing_time': processing_time
            }
            
            result = IntelligenceEnhancementResult(
                destination=destination,
                enhanced_themes=enhanced_themes,  # Pass as dictionaries
                intelligence_insights=comprehensive_insights,
                processing_time=processing_time,
                errors=[]
            )
            
            # Update metrics
            self._update_enhancement_metrics(result)
            
            self.logger.info(f"✅ Enhancement complete for {destination}: {len(enhanced_themes)} themes enhanced, quality {result.quality_score:.3f}")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"❌ Enhancement failed for {destination}: {e}")
            import traceback
            traceback.print_exc()
            
            return IntelligenceEnhancementResult(
                destination=destination,
                enhanced_themes=[],
                intelligence_insights={},
                processing_time=processing_time,
                errors=[str(e)]
            )
    
    async def _analyze_attributes(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze theme attributes for processing optimization"""
        themes = task_data.get('themes', [])
        
        # Analyze attribute dependencies and priorities
        analysis = {
            'total_themes': len(themes),
            'attribute_distribution': self._analyze_attribute_distribution(themes),
            'processing_priority': self._determine_processing_priority(themes),
            'optimization_recommendations': self._generate_optimization_recommendations(themes)
        }
        
        return analysis
    
    def _analyze_attribute_distribution(self, themes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of attributes across themes"""
        
        categories = {}
        confidence_scores = []
        
        for theme in themes:
            category = theme.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
            
            confidence = theme.get('confidence', 0.5)
            confidence_scores.append(confidence)
        
        return {
            'category_distribution': categories,
            'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            'confidence_range': [min(confidence_scores), max(confidence_scores)] if confidence_scores else [0, 0]
        }
    
    def _determine_processing_priority(self, themes: List[Dict[str, Any]]) -> List[str]:
        """Determine processing priority for themes"""
        
        # Sort themes by confidence and category importance
        category_priority = {
            'culture': 1, 'nature': 2, 'adventure': 3, 'luxury': 4, 'food': 5,
            'family': 6, 'wellness': 7, 'nightlife': 8, 'shopping': 9, 'business': 10
        }
        
        sorted_themes = sorted(themes, key=lambda x: (
            category_priority.get(x.get('category', 'unknown'), 99),
            -x.get('confidence', 0.5)
        ))
        
        return [theme.get('theme', f'theme_{i}') for i, theme in enumerate(sorted_themes)]
    
    def _generate_optimization_recommendations(self, themes: List[Dict[str, Any]]) -> List[str]:
        """Generate optimization recommendations"""
        
        recommendations = []
        
        if len(themes) > 15:
            recommendations.append("Consider reducing theme count for focused processing")
        
        if len(themes) < 5:
            recommendations.append("Consider expanding theme discovery for better coverage")
        
        # Check confidence distribution
        confidence_scores = [theme.get('confidence', 0.5) for theme in themes]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        if avg_confidence < 0.6:
            recommendations.append("Low confidence themes detected - consider additional validation")
        
        return recommendations
    
    def _calculate_enhancement_quality(self, enhanced_themes: List[Dict[str, Any]]) -> float:
        """Calculate quality score for enhanced themes"""
        
        if not enhanced_themes:
            return 0.0
        
        # Quality factors
        theme_count_score = min(len(enhanced_themes) / 10.0, 1.0)  # Optimal around 10 themes
        
        # Check for intelligence insights
        intelligence_score = 0.0
        for theme in enhanced_themes:
            if theme.get('depth_analysis'):
                intelligence_score += 0.1
            if theme.get('authenticity_analysis'):
                intelligence_score += 0.1
            if theme.get('hidden_gem_score'):
                intelligence_score += 0.1
        
        intelligence_score = min(intelligence_score / len(enhanced_themes), 1.0)
        
        # Overall quality
        overall_quality = (theme_count_score * 0.4) + (intelligence_score * 0.6)
        
        return overall_quality
    
    def _update_enhancement_metrics(self, result: IntelligenceEnhancementResult):
        """Update agent performance metrics"""
        self.enhancement_metrics['total_enhancements'] += 1
        
        if result.enhanced_themes:
            self.enhancement_metrics['successful_enhancements'] += 1
        
        # Update running averages
        total = self.enhancement_metrics['total_enhancements']
        self.enhancement_metrics['average_processing_time'] = (
            (self.enhancement_metrics['average_processing_time'] * (total - 1) + result.processing_time) / total
        )
        self.enhancement_metrics['average_attributes_processed'] = (
            (self.enhancement_metrics['average_attributes_processed'] * (total - 1) + len(result.enhanced_themes) * 18) / total
        )
        self.enhancement_metrics['average_quality_score'] = (
            (self.enhancement_metrics['average_quality_score'] * (total - 1) + result.quality_score) / total
        )
    
    # Message handlers
    
    async def _handle_enhancement_request(self, message: AgentMessage):
        """Handle theme enhancement request"""
        task_data = message.payload
        
        try:
            result = await self._enhance_themes(task_data)
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="enhancement_response",
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
    
    async def _handle_attribute_analysis(self, message: AgentMessage):
        """Handle attribute analysis request"""
        task_data = message.payload
        
        try:
            analysis = await self._analyze_attributes(task_data)
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="analysis_response",
                payload={'analysis': analysis},
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