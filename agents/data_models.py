"""
Agent Data Models - Comprehensive Schema System

Bulletproof data models that eliminate dict/object/array confusion.
Every agent interaction uses these standardized models.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from datetime import datetime

# ==========================================
# CORE ENUMS
# ==========================================

class TaskStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"

class QualityLevel(Enum):
    EXCELLENT = "excellent"  # 0.8+
    GOOD = "good"           # 0.6-0.8
    ACCEPTABLE = "acceptable" # 0.4-0.6
    POOR = "poor"           # <0.4

# ==========================================
# BASE RESPONSE MODEL
# ==========================================

@dataclass
class AgentResponse:
    """Standardized response wrapper for ALL agent operations"""
    status: TaskStatus
    data: Any = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    agent_id: str = ""
    task_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Always returns a consistent dict format"""
        return {
            'status': self.status.value,
            'data': self.data,
            'error_message': self.error_message,
            'processing_time': self.processing_time,
            'agent_id': self.agent_id,
            'task_id': self.task_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentResponse':
        """Create from dictionary"""
        data_copy = data.copy()
        data_copy['status'] = TaskStatus(data_copy['status'])
        return cls(**data_copy)
    
    @property
    def is_success(self) -> bool:
        """Check if operation was successful"""
        return self.status == TaskStatus.SUCCESS
    
    @property
    def result(self) -> Any:
        """Get the result data - consistent access pattern"""
        return self.data

# ==========================================
# WEB DISCOVERY MODELS
# ==========================================

@dataclass
class WebContent:
    """Individual web content item"""
    url: str
    title: str
    content: str
    relevance_score: float = 0.5
    quality_score: float = 0.5
    authority_score: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate scores"""
        self.relevance_score = max(0.0, min(1.0, self.relevance_score))
        self.quality_score = max(0.0, min(1.0, self.quality_score))
        self.authority_score = max(0.0, min(1.0, self.authority_score))

@dataclass
class WebDiscoveryResult:
    """Web discovery result - ALWAYS use this format"""
    destination: str
    content: List[WebContent]
    sources_analyzed: int = 0
    sources_successful: int = 0
    average_quality: float = 0.0
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Auto-calculate derived fields"""
        self.sources_successful = len(self.content)
        if self.content:
            self.average_quality = sum(c.quality_score for c in self.content) / len(self.content)

# ==========================================
# LLM PROCESSING MODELS
# ==========================================

@dataclass
class ResourceAllocation:
    """LLM resource allocation configuration"""
    pool_size: str = "medium"  # small, medium, large
    concurrent_requests: int = 5
    batch_size: int = 8
    priority: int = 5  # 1=highest, 10=lowest
    estimated_completion_time: float = 0.0
    constraints: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ThemeData:
    """Individual theme with all 18 attributes"""
    theme: str
    category: str
    confidence: float = 0.5
    description: str = ""
    
    # Core attributes
    nano_themes: List[str] = field(default_factory=list)
    price_insights: Dict[str, Any] = field(default_factory=dict)
    seasonality: Dict[str, Any] = field(default_factory=dict)
    traveler_types: List[str] = field(default_factory=list)
    accessibility: Dict[str, Any] = field(default_factory=dict)
    authenticity_analysis: Dict[str, Any] = field(default_factory=dict)
    hidden_gem_score: float = 0.5
    depth_analysis: Dict[str, Any] = field(default_factory=dict)
    cultural_sensitivity: Dict[str, Any] = field(default_factory=dict)
    experience_intensity: Dict[str, Any] = field(default_factory=dict)
    time_commitment: Dict[str, Any] = field(default_factory=dict)
    local_transportation: Dict[str, Any] = field(default_factory=dict)
    accommodation_types: List[str] = field(default_factory=list)
    booking_considerations: Dict[str, Any] = field(default_factory=dict)
    
    # Content intelligence
    iconic_landmarks: List[Dict[str, Any]] = field(default_factory=list)
    practical_travel_intelligence: Dict[str, Any] = field(default_factory=dict)
    neighborhood_insights: List[Dict[str, Any]] = field(default_factory=list)
    content_discovery_intelligence: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate theme data"""
        self.confidence = max(0.0, min(1.0, self.confidence))
        self.hidden_gem_score = max(0.0, min(1.0, self.hidden_gem_score))

@dataclass
class LLMProcessingResult:
    """LLM processing result - ALWAYS use this format"""
    destination: str
    themes: List[ThemeData]
    affinities: List[Dict[str, Any]]  # Legacy compatibility
    processing_time: float = 0.0
    quality_score: float = 0.0
    cache_performance: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate quality score"""
        if self.themes:
            total_confidence = sum(theme.confidence for theme in self.themes)
            self.quality_score = total_confidence / len(self.themes)

# ==========================================
# INTELLIGENCE ENHANCEMENT MODELS
# ==========================================

@dataclass
class IntelligenceEnhancementResult:
    """Intelligence enhancement result - ALWAYS use this format"""
    destination: str
    enhanced_themes: List[ThemeData]
    intelligence_insights: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    quality_score: float = 0.0
    errors: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate quality score"""
        if self.enhanced_themes:
            total_confidence = 0
            count = 0
            
            for theme in self.enhanced_themes:
                if hasattr(theme, 'confidence'):
                    # ThemeData object
                    total_confidence += theme.confidence
                    count += 1
                elif isinstance(theme, dict) and 'confidence' in theme:
                    # Dictionary format
                    total_confidence += theme['confidence']
                    count += 1
                elif isinstance(theme, dict) and 'authenticity_score' in theme:
                    # Enhanced dictionary format with authenticity_score
                    total_confidence += theme['authenticity_score']
                    count += 1
                else:
                    # Default confidence for themes without confidence scores
                    total_confidence += 0.8
                    count += 1
            
            if count > 0:
                self.quality_score = total_confidence / count

# ==========================================
# EVIDENCE VALIDATION MODELS
# ==========================================

@dataclass
class EvidenceValidationResult:
    """Evidence validation result - ALWAYS use this format"""
    destination: str
    validation_report: Dict[str, Any] = field(default_factory=dict)
    evidence_summary: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    themes_validated: int = 0
    confidence_score: float = 0.0
    errors: List[str] = field(default_factory=list)

# ==========================================
# QUALITY ASSURANCE MODELS
# ==========================================

@dataclass
class QualityAssuranceResult:
    """Quality assurance result - ALWAYS use this format"""
    destination: str
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    interventions: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    overall_score: float = 0.0
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)

# ==========================================
# WORKFLOW MODELS
# ==========================================

@dataclass
class WorkflowResult:
    """Complete workflow result - ALWAYS use this format"""
    workflow_id: str
    destination: str
    success: bool
    final_data: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    quality_score: float = 0.0
    phases_completed: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

# ==========================================
# DESTINATION NUANCE MODELS (3-TIER SYSTEM)
# ==========================================

@dataclass
class NuancePhrase:
    """Individual nuance phrase with validation and scoring data"""
    phrase: str
    category: str  # 'destination', 'hotel', 'vacation_rental'
    score: float = 0.0
    search_hits: int = 0
    uniqueness_ratio: float = 0.0
    evidence_sources: List[str] = field(default_factory=list)
    source_urls: List[str] = field(default_factory=list)
    validation_metadata: Dict[str, Any] = field(default_factory=dict)
    contributing_models: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate scores"""
        self.score = max(0.0, min(1.0, self.score))
        self.uniqueness_ratio = max(0.0, self.uniqueness_ratio)

@dataclass 
class DestinationNuanceCollection:
    """Complete collection of all 3 nuance types"""
    destination_nuances: List[NuancePhrase] = field(default_factory=list)  # Min 8
    hotel_expectations: List[NuancePhrase] = field(default_factory=list)   # Min 6
    vacation_rental_expectations: List[NuancePhrase] = field(default_factory=list)  # Min 6
    
    def get_total_count(self) -> int:
        """Get total count across all categories"""
        return len(self.destination_nuances) + len(self.hotel_expectations) + len(self.vacation_rental_expectations)
    
    def get_category_count(self, category: str) -> int:
        """Get count for specific category"""
        if category == 'destination':
            return len(self.destination_nuances)
        elif category == 'hotel':
            return len(self.hotel_expectations)
        elif category == 'vacation_rental':
            return len(self.vacation_rental_expectations)
        return 0

@dataclass
class NuanceEvidence:
    """Evidence supporting a nuance phrase"""
    phrase: str
    category: str  # 'destination', 'hotel', 'vacation_rental'
    source_url: str
    source_type: str  # wikipedia, tripadvisor, government, etc.
    content_snippet: str
    relevance_score: float = 0.5
    authority_score: float = 0.5
    search_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate scores"""
        self.relevance_score = max(0.0, min(1.0, self.relevance_score))
        self.authority_score = max(0.0, min(1.0, self.authority_score))

@dataclass
class MultiLLMGenerationResult:
    """Result from multi-LLM nuance generation - now supports 3 categories"""
    destination: str
    model_responses: Dict[str, Dict[str, List[str]]] = field(default_factory=dict)  # model_name -> category -> phrases
    consensus_phrases: Dict[str, List[str]] = field(default_factory=dict)  # category -> phrases
    all_unique_phrases: Dict[str, List[str]] = field(default_factory=dict)  # category -> phrases
    generation_statistics: Dict[str, Any] = field(default_factory=dict)
    model_performance: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0

@dataclass
class SearchValidationResult:
    """Result from search validation of nuance phrases - now supports 3 categories"""
    destination: str
    validated_phrases: DestinationNuanceCollection = field(default_factory=DestinationNuanceCollection)
    failed_phrases: Dict[str, List[str]] = field(default_factory=dict)  # category -> failed phrases
    validation_statistics: Dict[str, Any] = field(default_factory=dict)
    cache_performance: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0

@dataclass
class DestinationNuanceResult:
    """Complete destination nuance result - ALWAYS use this format"""
    destination: str
    nuance_collection: DestinationNuanceCollection
    evidence: List[NuanceEvidence] = field(default_factory=list)
    generation_result: Optional[MultiLLMGenerationResult] = None
    validation_result: Optional[SearchValidationResult] = None
    quality_scores: Dict[str, float] = field(default_factory=dict)  # category -> quality score
    processing_time: float = 0.0
    statistics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate quality scores for each category"""
        if self.nuance_collection.destination_nuances:
            total_score = sum(nuance.score for nuance in self.nuance_collection.destination_nuances)
            self.quality_scores['destination'] = total_score / len(self.nuance_collection.destination_nuances)
            
        if self.nuance_collection.hotel_expectations:
            total_score = sum(nuance.score for nuance in self.nuance_collection.hotel_expectations)
            self.quality_scores['hotel'] = total_score / len(self.nuance_collection.hotel_expectations)
            
        if self.nuance_collection.vacation_rental_expectations:
            total_score = sum(nuance.score for nuance in self.nuance_collection.vacation_rental_expectations)
            self.quality_scores['vacation_rental'] = total_score / len(self.nuance_collection.vacation_rental_expectations)
    
    @property 
    def overall_quality_score(self) -> float:
        """Calculate overall quality score across all categories"""
        if not self.quality_scores:
            return 0.0
        return sum(self.quality_scores.values()) / len(self.quality_scores)

# ==========================================
# DATA CONVERSION UTILITIES
# ==========================================

class DataConverter:
    """Converts between legacy formats and new data models"""
    
    @staticmethod
    def web_content_from_dict(data: Dict[str, Any]) -> WebContent:
        """Convert dict to WebContent"""
        return WebContent(
            url=str(data.get('url', '')),
            title=str(data.get('title', '')),
            content=str(data.get('content', '')),
            relevance_score=float(data.get('relevance_score', 0.5)),
            quality_score=float(data.get('quality_score', 0.5)),
            authority_score=float(data.get('authority_score', 0.5)),
            metadata=data.get('metadata', {})
        )
    
    @staticmethod
    def web_discovery_from_legacy(legacy_data: Dict[str, Any], destination: str) -> WebDiscoveryResult:
        """Convert legacy web discovery data to new format"""
        content_list = legacy_data.get('content', [])
        web_content = []
        
        for item in content_list:
            if isinstance(item, dict):
                web_content.append(DataConverter.web_content_from_dict(item))
        
        return WebDiscoveryResult(
            destination=destination,
            content=web_content,
            sources_analyzed=legacy_data.get('sources_analyzed', len(content_list)),
            processing_time=legacy_data.get('processing_time', 0.0),
            errors=legacy_data.get('errors', [])
        )
    
    @staticmethod
    def theme_from_dict(data: Dict[str, Any]) -> ThemeData:
        """Convert dict to ThemeData"""
        return ThemeData(
            theme=str(data.get('theme', '')),
            category=str(data.get('category', 'general')),
            confidence=float(data.get('confidence', 0.5)),
            description=str(data.get('description', '')),
            nano_themes=data.get('nano_themes', []),
            price_insights=data.get('price_insights', {}),
            seasonality=data.get('seasonality', {}),
            traveler_types=data.get('traveler_types', []),
            accessibility=data.get('accessibility', {}),
            authenticity_analysis=data.get('authenticity_analysis', {}),
            hidden_gem_score=float(data.get('hidden_gem_score', 0.5)),
            depth_analysis=data.get('depth_analysis', {}),
            cultural_sensitivity=data.get('cultural_sensitivity', {}),
            experience_intensity=data.get('experience_intensity', {}),
            time_commitment=data.get('time_commitment', {}),
            local_transportation=data.get('local_transportation', {}),
            accommodation_types=data.get('accommodation_types', []),
            booking_considerations=data.get('booking_considerations', {}),
            iconic_landmarks=data.get('iconic_landmarks', []),
            practical_travel_intelligence=data.get('practical_travel_intelligence', {}),
            neighborhood_insights=data.get('neighborhood_insights', []),
            content_discovery_intelligence=data.get('content_discovery_intelligence', {})
        )

# ==========================================
# RESPONSE FACTORY
# ==========================================

class ResponseFactory:
    """Factory for creating standardized AgentResponse objects"""
    
    @staticmethod
    def success(data: Any, agent_id: str = "", task_id: str = "", processing_time: float = 0.0) -> AgentResponse:
        """Create success response"""
        return AgentResponse(
            status=TaskStatus.SUCCESS,
            data=data,
            agent_id=agent_id,
            task_id=task_id,
            processing_time=processing_time
        )
    
    @staticmethod
    def error(error_message: str, agent_id: str = "", task_id: str = "", processing_time: float = 0.0) -> AgentResponse:
        """Create error response"""
        return AgentResponse(
            status=TaskStatus.ERROR,
            error_message=error_message,
            agent_id=agent_id,
            task_id=task_id,
            processing_time=processing_time
        )
