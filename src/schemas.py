from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from datetime import datetime

class ThemeDepthLevel(str, Enum):
    MACRO = "macro"
    MICRO = "micro"  
    NANO = "nano"

class ExperienceIntensity(str, Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"

class EmotionalResonance(str, Enum):
    PEACEFUL = "peaceful"
    EXHILARATING = "exhilarating"
    CONTEMPLATIVE = "contemplative"
    SOCIAL = "social"
    SOLITARY = "solitary"
    CHALLENGING = "challenging"
    COMFORTING = "comforting"
    INSPIRING = "inspiring"

class AuthenticityLevel(str, Enum):
    AUTHENTIC_LOCAL = "authentic_local"
    LOCAL_INFLUENCED = "local_influenced"
    BALANCED = "balanced"
    TOURIST_ORIENTED = "tourist_oriented"
    TOURIST_TRAP = "tourist_trap"

class CulturalSensitivity(BaseModel):
    appropriate: bool = True
    considerations: List[str] = Field(default_factory=list)
    religious_calendar_aware: bool = True
    local_customs_respected: bool = True
    language_requirements: Optional[str] = None

class MicroClimate(BaseModel):
    best_time_of_day: List[str] = Field(default_factory=list)
    weather_dependencies: List[str] = Field(default_factory=list)
    crowd_patterns: Dict[str, str] = Field(default_factory=dict)
    micro_season_timing: Optional[str] = None

class ThemeInterconnection(BaseModel):
    natural_combinations: List[str] = Field(default_factory=list)
    sequential_experiences: List[str] = Field(default_factory=list)
    skill_progression: Optional[str] = None
    energy_flow: str = "balanced"

class ExperienceContext(BaseModel):
    demographic_suitability: List[str] = Field(default_factory=list)
    group_dynamics: List[str] = Field(default_factory=list)
    experience_level_required: str = "beginner"
    accessibility_level: str = "accessible"

class HiddenGemScore(BaseModel):
    local_frequency_ratio: float = Field(ge=0, le=1)
    insider_knowledge_required: bool = False
    emerging_scene_indicator: bool = False
    off_peak_excellence: bool = False
    uniqueness_score: float = Field(ge=0, le=1)

class EnhancedAffinity(BaseModel):
    # Core theme information
    theme: str
    category: str
    depth_level: ThemeDepthLevel = ThemeDepthLevel.MACRO
    sub_themes: List[str] = Field(default_factory=list)
    nano_themes: List[str] = Field(default_factory=list)
    
    # Quality and validation
    confidence: float = Field(ge=0, le=1)
    authenticity_level: AuthenticityLevel = AuthenticityLevel.BALANCED
    authenticity_score: float = Field(ge=0, le=1, default=0.5)
    
    # Emotional and experiential
    emotional_resonance: List[EmotionalResonance] = Field(default_factory=list)
    experience_intensity: Dict[str, ExperienceIntensity] = Field(default_factory=dict)
    
    # Context and timing
    seasonality: Dict[str, List[str]] = Field(default_factory=dict)
    micro_climate: MicroClimate = Field(default_factory=MicroClimate)
    cultural_sensitivity: CulturalSensitivity = Field(default_factory=CulturalSensitivity)
    
    # Traveler matching
    traveler_types: List[str] = Field(default_factory=list)
    experience_context: ExperienceContext = Field(default_factory=ExperienceContext)
    
    # Interconnections and flow
    theme_interconnections: ThemeInterconnection = Field(default_factory=ThemeInterconnection)
    
    # Discovery and uniqueness
    hidden_gem_score: HiddenGemScore = Field(default_factory=HiddenGemScore)
    
    # Traditional fields
    price_point: str = "mid"
    rationale: str = ""
    unique_selling_points: List[str] = Field(default_factory=list)
    validation: str = "Generated"

class ThemeComposition(BaseModel):
    energy_flow_balance: Dict[str, float] = Field(default_factory=dict)
    sensory_variety_score: float = Field(ge=0, le=1, default=0.5)
    pace_variation_index: float = Field(ge=0, le=1, default=0.5)
    social_spectrum_coverage: Dict[str, int] = Field(default_factory=dict)
    learning_curve_progression: bool = False
    overall_composition_score: float = Field(ge=0, le=1, default=0.5)

class EnhancedQualityAssessment(BaseModel):
    # Existing metrics
    metrics: Dict[str, float] = Field(default_factory=dict)
    overall_score: float = Field(ge=0, le=1)
    quality_level: str = "Unknown"
    
    # New quality dimensions
    theme_depth_score: float = Field(ge=0, le=1, default=0.5)
    authenticity_distribution: Dict[AuthenticityLevel, int] = Field(default_factory=dict)
    emotional_coverage_score: float = Field(ge=0, le=1, default=0.5)
    cultural_sensitivity_score: float = Field(ge=0, le=1, default=1.0)
    context_relevance_score: float = Field(ge=0, le=1, default=0.5)
    hidden_gem_ratio: float = Field(ge=0, le=1, default=0.0)
    
    # Composition analysis
    theme_composition: ThemeComposition = Field(default_factory=ThemeComposition)
    
    # Enhanced recommendations
    recommendations: List[str] = Field(default_factory=list)
    composition_improvements: List[str] = Field(default_factory=list)
    meets_threshold: bool = False
    destination: str = ""
    total_affinities: int = 0

class EnhancedDestinationResult(BaseModel):
    destination_id: str
    affinities: List[EnhancedAffinity] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)
    quality_assessment: EnhancedQualityAssessment = Field(default_factory=EnhancedQualityAssessment)
    qa_workflow: Dict[str, Any] = Field(default_factory=dict)
    priority_data: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time_seconds: float = 0.0
    
    # New intelligence layers
    destination_intelligence: Dict[str, Any] = Field(default_factory=dict)
    theme_insights: Dict[str, Any] = Field(default_factory=dict)
    composition_analysis: Dict[str, Any] = Field(default_factory=dict)

class PageContent(BaseModel):
    """Represents the raw content scraped from a single web page."""
    url: str = Field(description="The URL of the scraped page.")
    title: str = Field(description="The title of the page.")
    content: str = Field(description="The main text content of the page.")
    content_length: int = Field(description="The length of the content in characters.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Source, access time, etc.")

class ProcessedPageChunk(BaseModel):
    """Represents a single chunk of processed text, ready for embedding."""
    chunk_id: str = Field(description="A unique identifier for this chunk (e.g., hash of URL + chunk index).")
    url: str = Field(description="The source URL of the content.")
    title: str = Field(description="The title of the source page.")
    text_chunk: str = Field(description="The text content of this specific chunk.")
    chunk_order: int = Field(description="The sequential order of this chunk within the page.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata from processing.")

class FetchPageInput(BaseModel):
    """Input schema for fetching a single web page."""
    url: str = Field(description="The URL of the web page to fetch.") 