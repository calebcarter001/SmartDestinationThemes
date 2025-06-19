"""Quality Assurance Agent - Comprehensive Implementation"""

import asyncio
import logging
import time
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentMessage, AgentState
from .data_models import (
    QualityAssuranceResult, AgentResponse, ResponseFactory, 
    TaskStatus, DataConverter
)

logger = logging.getLogger(__name__)

class QualityAssuranceAgent(BaseAgent):
    """
    Quality Assurance agent that provides comprehensive quality monitoring
    and continuous improvement interventions.
    
    Features:
    - Real-time quality monitoring
    - Intervention recommendations
    - Performance optimization
    - Quality score calculation
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("quality_assurance", config)
        
        # Quality thresholds
        self.quality_threshold = config.get('quality', {}).get('minimum_threshold', 0.7)
        self.intervention_threshold = config.get('quality', {}).get('intervention_threshold', 0.6)
        
        # Performance tracking
        self.qa_metrics = {
            'total_assessments': 0,
            'interventions_applied': 0,
            'average_quality_score': 0.0
        }
    
    async def _initialize_agent_specific(self):
        """Initialize quality assurance components"""
        try:
            # Register task handlers
            self.register_message_handler("assess_quality", self._handle_quality_assessment)
            self.register_message_handler("recommend_interventions", self._handle_intervention_recommendations)
            
            self.logger.info("Quality Assurance Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Quality Assurance Agent: {e}")
            raise
    
    async def _execute_task_specific(self, task_id: str, task_definition: Dict[str, Any]) -> AgentResponse:
        """Execute quality assurance tasks"""
        task_type = task_definition.get('task_type')
        task_data = task_definition.get('data', {})
        
        try:
            start_time = time.time()
            
            if task_type == 'assess_quality':
                result = await self._assess_comprehensive_quality(task_data)
                processing_time = time.time() - start_time
                return ResponseFactory.success(
                    data=result, 
                    agent_id=self.agent_id, 
                    task_id=task_id,
                    processing_time=processing_time
                )
            elif task_type == 'recommend_interventions':
                result = await self._recommend_quality_interventions(task_data)
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
    
    async def _assess_comprehensive_quality(self, task_data: Dict[str, Any]) -> QualityAssuranceResult:
        """Assess comprehensive quality of workflow results"""
        workflow_state = task_data.get('workflow_state', {})
        destination = workflow_state.get('destination', 'Unknown')
        
        start_time = time.time()
        self.logger.info(f"🔍 Starting quality assessment for {destination}")
        
        try:
            # Assess different quality dimensions
            quality_metrics = {
                'completeness_score': self._assess_completeness(workflow_state),
                'accuracy_score': self._assess_accuracy(workflow_state),
                'relevance_score': self._assess_relevance(workflow_state),
                'diversity_score': self._assess_diversity(workflow_state),
                'consistency_score': self._assess_consistency(workflow_state)
            }
            
            # Calculate overall quality score
            overall_score = sum(quality_metrics.values()) / len(quality_metrics)
            quality_metrics['overall_score'] = overall_score
            
            # Determine interventions needed
            interventions = self._determine_interventions(quality_metrics)
            recommendations = self._generate_recommendations(quality_metrics, workflow_state)
            
            processing_time = time.time() - start_time
            
            result = QualityAssuranceResult(
                destination=destination,
                quality_metrics=quality_metrics,
                interventions=interventions,
                recommendations=recommendations,
                overall_score=overall_score,
                processing_time=processing_time,
                errors=[]
            )
            
            # Update metrics
            self._update_qa_metrics(result)
            
            self.logger.info(f"✅ Quality assessment complete for {destination}: overall score {overall_score:.3f}")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"❌ Quality assessment failed for {destination}: {e}")
            
            return QualityAssuranceResult(
                destination=destination,
                quality_metrics={'overall_score': 0.0},
                interventions=[],
                recommendations=[],
                overall_score=0.0,
                processing_time=processing_time,
                errors=[str(e)]
            )
    
    def _assess_completeness(self, workflow_state: Dict[str, Any]) -> float:
        """Assess completeness of workflow results"""
        score = 0.0
        
        # Check web discovery
        if workflow_state.get('web_discovery_completed'):
            score += 0.2
        
        # Check LLM processing
        if workflow_state.get('llm_processing_completed'):
            score += 0.3
        
        # Check enhancement
        if workflow_state.get('enhancement_completed'):
            score += 0.2
        
        # Check validation
        if workflow_state.get('validation_completed'):
            score += 0.3
        
        return min(score, 1.0)
    
    def _assess_accuracy(self, workflow_state: Dict[str, Any]) -> float:
        """Assess accuracy of results"""
        # Default good accuracy unless issues detected
        accuracy = 0.8
        
        # Check for validation confidence
        validation_data = workflow_state.get('validation_result', {})
        if validation_data:
            confidence = validation_data.get('confidence_score', 0.5)
            accuracy = accuracy * 0.7 + confidence * 0.3
        
        return min(accuracy, 1.0)
    
    def _assess_relevance(self, workflow_state: Dict[str, Any]) -> float:
        """Assess relevance of discovered content"""
        relevance = 0.7  # Default
        
        # Check web discovery quality
        web_data = workflow_state.get('web_discovery_result', {})
        if web_data and 'average_quality' in web_data:
            relevance = web_data['average_quality']
        
        return min(relevance, 1.0)
    
    def _assess_diversity(self, workflow_state: Dict[str, Any]) -> float:
        """Assess diversity of themes and content"""
        diversity = 0.5  # Default
        
        # Check theme categories
        llm_data = workflow_state.get('llm_processing_result', {})
        if llm_data and 'themes' in llm_data:
            themes = llm_data['themes']
            if isinstance(themes, list) and len(themes) > 0:
                categories = set()
                for theme in themes:
                    if isinstance(theme, dict):
                        categories.add(theme.get('category', 'unknown'))
                
                # More categories = higher diversity
                diversity = min(len(categories) / 5.0, 1.0)  # Max at 5 categories
        
        return diversity
    
    def _assess_consistency(self, workflow_state: Dict[str, Any]) -> float:
        """Assess consistency across workflow phases"""
        consistency = 0.8  # Default good consistency
        
        # Check for conflicts in validation
        validation_data = workflow_state.get('validation_result', {})
        if validation_data:
            evidence_summary = validation_data.get('evidence_summary', {})
            if evidence_summary:
                validated_themes = evidence_summary.get('validated_themes', 0)
                total_themes = evidence_summary.get('total_themes', 1)
                consistency = validated_themes / total_themes if total_themes > 0 else 0.5
        
        return min(consistency, 1.0)
    
    def _determine_interventions(self, quality_metrics: Dict[str, Any]) -> List[str]:
        """Determine quality interventions needed"""
        interventions = []
        
        if quality_metrics.get('completeness_score', 0) < 0.8:
            interventions.append("increase_discovery_coverage")
        
        if quality_metrics.get('accuracy_score', 0) < 0.7:
            interventions.append("enhance_validation_rigor")
        
        if quality_metrics.get('relevance_score', 0) < 0.6:
            interventions.append("improve_content_filtering")
        
        if quality_metrics.get('diversity_score', 0) < 0.5:
            interventions.append("expand_theme_categories")
        
        if quality_metrics.get('consistency_score', 0) < 0.7:
            interventions.append("resolve_content_conflicts")
        
        return interventions
    
    def _generate_recommendations(self, quality_metrics: Dict[str, Any], workflow_state: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        overall_score = quality_metrics.get('overall_score', 0)
        
        if overall_score < 0.6:
            recommendations.append("Consider re-running workflow with enhanced parameters")
        elif overall_score < 0.8:
            recommendations.append("Apply targeted quality improvements")
        else:
            recommendations.append("Quality meets standards - consider minor optimizations")
        
        # Specific recommendations based on weak areas
        if quality_metrics.get('diversity_score', 0) < 0.5:
            recommendations.append("Expand discovery queries to include more theme categories")
        
        if quality_metrics.get('accuracy_score', 0) < 0.7:
            recommendations.append("Increase evidence validation thresholds")
        
        return recommendations
    
    async def _recommend_quality_interventions(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend specific quality interventions"""
        quality_issues = task_data.get('quality_issues', [])
        
        intervention_recommendations = []
        
        for issue in quality_issues:
            if issue == 'low_completeness':
                intervention_recommendations.append({
                    'issue': issue,
                    'intervention': 'extend_discovery_time',
                    'priority': 'high',
                    'estimated_improvement': 0.15
                })
            elif issue == 'low_diversity':
                intervention_recommendations.append({
                    'issue': issue,
                    'intervention': 'expand_query_categories',
                    'priority': 'medium',
                    'estimated_improvement': 0.10
                })
        
        return {
            'total_issues': len(quality_issues),
            'intervention_recommendations': intervention_recommendations,
            'overall_improvement_estimate': sum(r['estimated_improvement'] for r in intervention_recommendations)
        }
    
    def _update_qa_metrics(self, result: QualityAssuranceResult):
        """Update quality assurance metrics"""
        self.qa_metrics['total_assessments'] += 1
        
        if result.interventions:
            self.qa_metrics['interventions_applied'] += len(result.interventions)
        
        # Update running average
        total = self.qa_metrics['total_assessments']
        self.qa_metrics['average_quality_score'] = (
            (self.qa_metrics['average_quality_score'] * (total - 1) + result.overall_score) / total
        )
    
    # Message handlers
    
    async def _handle_quality_assessment(self, message: AgentMessage):
        """Handle quality assessment request"""
        task_data = message.payload
        
        try:
            result = await self._assess_comprehensive_quality(task_data)
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="quality_response",
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
    
    async def _handle_intervention_recommendations(self, message: AgentMessage):
        """Handle intervention recommendation request"""
        task_data = message.payload
        
        try:
            recommendations = await self._recommend_quality_interventions(task_data)
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="recommendations_response",
                payload={'recommendations': recommendations},
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