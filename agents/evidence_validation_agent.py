"""
Evidence Validation Agent

Intelligent evidence validation with cross-source verification and conflict resolution.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentMessage, AgentState
from .data_models import (
    EvidenceValidationResult, AgentResponse, ResponseFactory, 
    TaskStatus, DataConverter
)

# Import existing components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.evidence_validator import EvidenceValidator
from src.schemas import PageContent

logger = logging.getLogger(__name__)

# ValidationResult is now imported as EvidenceValidationResult from data_models

class EvidenceValidationAgent(BaseAgent):
    """
    Evidence validation agent that provides comprehensive evidence validation
    with cross-source verification and conflict resolution.
    
    Features:
    - Cross-source validation and verification
    - Conflict resolution between sources
    - Authority scoring and credibility assessment
    - Real-time fact checking
    - Evidence sufficiency determination
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("evidence_validation", config)
        
        # Configuration
        agent_config = config.get('agents', {}).get('evidence_validation', {})
        self.cross_source_validation = agent_config.get('cross_source_validation', True)
        self.conflict_resolution = agent_config.get('conflict_resolution', True)
        self.authority_scoring = agent_config.get('authority_scoring', True)
        self.real_time_fact_checking = agent_config.get('real_time_fact_checking', True)
        self.evidence_threshold = agent_config.get('evidence_sufficiency_threshold', 0.7)
        
        # Initialize wrapped validator
        self.evidence_validator = None
        
        # Performance tracking
        self.validation_metrics = {
            'total_validations': 0,
            'successful_validations': 0,
            'average_processing_time': 0.0,
            'average_evidence_pieces': 0.0,
            'average_confidence_score': 0.0
        }
    
    async def _initialize_agent_specific(self):
        """Initialize evidence validation components"""
        try:
            # Initialize the evidence validator
            self.evidence_validator = EvidenceValidator(self.config)
            
            # Register task handlers
            self.register_message_handler("validate_comprehensive_evidence", self._handle_validation_request)
            self.register_message_handler("resolve_conflicts", self._handle_conflict_resolution)
            self.register_message_handler("assess_authority", self._handle_authority_assessment)
            
            self.logger.info("Evidence Validation Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Evidence Validation Agent: {e}")
            raise
    
    async def _execute_task_specific(self, task_id: str, task_definition: Dict[str, Any]) -> AgentResponse:
        """Execute evidence validation tasks"""
        task_type = task_definition.get('task_type')
        task_data = task_definition.get('data', {})
        
        try:
            start_time = time.time()
            
            if task_type == 'validate_comprehensive_evidence':
                result = await self._validate_comprehensive_evidence(task_data)
                processing_time = time.time() - start_time
                return ResponseFactory.success(
                    data=result, 
                    agent_id=self.agent_id, 
                    task_id=task_id,
                    processing_time=processing_time
                )
            elif task_type == 'resolve_conflicts':
                result = await self._resolve_evidence_conflicts(task_data)
                processing_time = time.time() - start_time
                return ResponseFactory.success(
                    data=result, 
                    agent_id=self.agent_id, 
                    task_id=task_id,
                    processing_time=processing_time
                )
            elif task_type == 'assess_authority':
                result = await self._assess_source_authority(task_data)
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
    
    async def _validate_comprehensive_evidence(self, task_data: Dict[str, Any]) -> EvidenceValidationResult:
        """Execute comprehensive evidence validation"""
        themes = task_data.get('themes', [])
        web_sources = task_data.get('web_sources', {})
        destination = task_data.get('destination', 'Unknown')
        
        if not themes:
            return EvidenceValidationResult(
                destination=destination,
                validation_report={},
                evidence_summary={},
                processing_time=0.0,
                themes_validated=0,
                confidence_score=0.0,
                errors=["No themes provided for validation"]
            )
        
        start_time = time.time()
        self.logger.info(f"🔍 Starting comprehensive evidence validation for {destination}")
        
        try:
            # Convert web sources to PageContent objects
            web_pages = self._convert_web_sources_to_pages(web_sources)
            
            # Validate themes using existing evidence validator
            themes_evidence = []
            total_evidence_pieces = 0
            
            for theme in themes:
                theme_name = theme.get('theme', 'Unknown Theme')
                theme_category = theme.get('category', 'general')
                
                # Validate theme evidence
                theme_evidence = self.evidence_validator.validate_theme_evidence(
                    theme_name, theme_category, web_pages, destination
                )
                
                themes_evidence.append(theme_evidence)
                total_evidence_pieces += theme_evidence.total_evidence_count
            
            # Generate comprehensive validation report
            processing_time = time.time() - start_time
            validation_report = self.evidence_validator.generate_validation_report(
                destination, themes_evidence, processing_time
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_validation_confidence(themes_evidence)
            
            result = EvidenceValidationResult(
                destination=destination,
                validation_report=validation_report.dict() if hasattr(validation_report, 'dict') else validation_report,
                evidence_summary=self._create_evidence_summary(themes_evidence),
                processing_time=processing_time,
                themes_validated=len(themes_evidence),
                confidence_score=confidence_score,
                errors=[]
            )
            
            # Update metrics
            self._update_validation_metrics(result)
            
            evidence_pieces = result.evidence_summary.get('total_evidence_pieces', 0)
            self.logger.info(f"✅ Evidence validation complete for {destination}: {result.themes_validated} themes, {evidence_pieces} evidence pieces")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"❌ Evidence validation failed for {destination}: {e}")
            
            return EvidenceValidationResult(
                destination=destination,
                validation_report={},
                evidence_summary={},
                processing_time=processing_time,
                themes_validated=0,
                confidence_score=0.0,
                errors=[str(e)]
            )
    
    def _convert_web_sources_to_pages(self, web_sources: Dict[str, Any]) -> List[PageContent]:
        """Convert web sources to PageContent objects"""
        
        web_pages = []
        
        # Handle different web source formats
        if 'content' in web_sources:
            content_list = web_sources['content']
            
            if isinstance(content_list, list):
                for item in content_list:
                    try:
                        page_content = PageContent(
                            url=item.get('url', ''),
                            title=item.get('title', ''),
                            content=item.get('content', ''),
                            content_length=len(item.get('content', '')),
                            metadata={
                                'relevance_score': item.get('relevance_score', 0.5),
                                'source': 'web_discovery'
                            }
                        )
                        web_pages.append(page_content)
                    except Exception as e:
                        self.logger.warning(f"Error converting web source to PageContent: {e}")
        
        return web_pages
    
    def _calculate_validation_confidence(self, themes_evidence: List) -> float:
        """Calculate overall validation confidence"""
        
        if not themes_evidence:
            return 0.0
        
        total_confidence = 0.0
        for theme_evidence in themes_evidence:
            if hasattr(theme_evidence, 'validation_confidence'):
                total_confidence += theme_evidence.validation_confidence
            else:
                total_confidence += 0.5  # Default confidence
        
        return total_confidence / len(themes_evidence)
    
    def _create_evidence_summary(self, themes_evidence: List) -> Dict[str, Any]:
        """Create summary of evidence validation results"""
        
        if not themes_evidence:
            return {}
        
        validated_count = 0
        partially_validated_count = 0
        unvalidated_count = 0
        total_evidence = 0
        
        for theme_evidence in themes_evidence:
            if hasattr(theme_evidence, 'validation_status'):
                status = theme_evidence.validation_status.value
                if status == 'validated':
                    validated_count += 1
                elif status == 'partially_validated':
                    partially_validated_count += 1
                else:
                    unvalidated_count += 1
            
            if hasattr(theme_evidence, 'total_evidence_count'):
                total_evidence += theme_evidence.total_evidence_count
        
        return {
            'total_themes': len(themes_evidence),
            'validated_themes': validated_count,
            'partially_validated_themes': partially_validated_count,
            'unvalidated_themes': unvalidated_count,
            'total_evidence_pieces': total_evidence,
            'validation_rate': validated_count / len(themes_evidence) if themes_evidence else 0
        }
    
    async def _resolve_evidence_conflicts(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflicts between evidence sources"""
        
        conflicting_evidence = task_data.get('conflicts', [])
        resolution_strategy = task_data.get('strategy', 'authority_based')
        
        # Simple conflict resolution based on source authority
        resolved_conflicts = []
        
        for conflict in conflicting_evidence:
            if resolution_strategy == 'authority_based':
                # Choose evidence from highest authority source
                evidence_pieces = conflict.get('evidence_pieces', [])
                if evidence_pieces:
                    best_evidence = max(evidence_pieces, key=lambda x: x.get('authority_score', 0))
                    resolved_conflicts.append({
                        'conflict_id': conflict.get('id'),
                        'resolution': 'authority_based',
                        'chosen_evidence': best_evidence,
                        'confidence': best_evidence.get('authority_score', 0.5)
                    })
        
        return {
            'total_conflicts': len(conflicting_evidence),
            'resolved_conflicts': len(resolved_conflicts),
            'resolution_strategy': resolution_strategy,
            'resolutions': resolved_conflicts
        }
    
    async def _assess_source_authority(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess authority and credibility of sources"""
        
        sources = task_data.get('sources', [])
        
        authority_assessments = []
        
        for source in sources:
            url = source.get('url', '')
            title = source.get('title', '')
            
            # Use existing authority scoring logic
            source_type = self.evidence_validator.classify_source_type(url, title)
            authority_score = self.evidence_validator.calculate_authority_score(source_type, url)
            
            authority_assessments.append({
                'url': url,
                'title': title,
                'source_type': source_type.value if hasattr(source_type, 'value') else str(source_type),
                'authority_score': authority_score,
                'credibility_level': self._classify_credibility(authority_score)
            })
        
        return {
            'total_sources': len(sources),
            'authority_assessments': authority_assessments,
            'average_authority': sum(a['authority_score'] for a in authority_assessments) / len(authority_assessments) if authority_assessments else 0
        }
    
    def _classify_credibility(self, authority_score: float) -> str:
        """Classify credibility level based on authority score"""
        
        if authority_score >= 0.8:
            return 'high'
        elif authority_score >= 0.6:
            return 'medium'
        elif authority_score >= 0.4:
            return 'low'
        else:
            return 'very_low'
    
    def _update_validation_metrics(self, result: EvidenceValidationResult):
        """Update agent performance metrics"""
        self.validation_metrics['total_validations'] += 1
        
        if result.validation_report:
            self.validation_metrics['successful_validations'] += 1
        
        # Update running averages
        total = self.validation_metrics['total_validations']
        self.validation_metrics['average_processing_time'] = (
            (self.validation_metrics['average_processing_time'] * (total - 1) + result.processing_time) / total
        )
        # Get evidence pieces from evidence summary
        evidence_pieces = result.evidence_summary.get('total_evidence_pieces', 0)
        self.validation_metrics['average_evidence_pieces'] = (
            (self.validation_metrics['average_evidence_pieces'] * (total - 1) + evidence_pieces) / total
        )
        self.validation_metrics['average_confidence_score'] = (
            (self.validation_metrics['average_confidence_score'] * (total - 1) + result.confidence_score) / total
        )
    
    # Message handlers
    
    async def _handle_validation_request(self, message: AgentMessage):
        """Handle comprehensive evidence validation request"""
        task_data = message.payload
        
        try:
            result = await self._validate_comprehensive_evidence(task_data)
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="validation_response",
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
    
    async def _handle_conflict_resolution(self, message: AgentMessage):
        """Handle evidence conflict resolution request"""
        task_data = message.payload
        
        try:
            resolution = await self._resolve_evidence_conflicts(task_data)
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="resolution_response",
                payload={'resolution': resolution},
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
    
    async def _handle_authority_assessment(self, message: AgentMessage):
        """Handle source authority assessment request"""
        task_data = message.payload
        
        try:
            assessment = await self._assess_source_authority(task_data)
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="assessment_response",
                payload={'assessment': assessment},
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