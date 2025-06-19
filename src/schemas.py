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

# Enhanced LLM Schema Models
class DestinationPersonality(BaseModel):
    primary_character: str = Field(description="Main personality of the destination")
    defining_features: List[str] = Field(default_factory=list, description="2-4 key characteristics")
    ideal_trip_length: str = Field(description="Recommended trip duration")
    best_known_for: List[str] = Field(default_factory=list, description="3-5 signature experiences")

class TravelerNuances(BaseModel):
    solo: Dict[str, List[str]] = Field(default_factory=dict, description="Solo traveler specific details")
    couple: Dict[str, List[str]] = Field(default_factory=dict, description="Couple specific details")
    family: Dict[str, List[str]] = Field(default_factory=dict, description="Family specific details")  
    group: Dict[str, List[str]] = Field(default_factory=dict, description="Group specific details")

class AccommodationInsights(BaseModel):
    recommended_areas: List[str] = Field(default_factory=list, description="Best neighborhoods/areas")
    accommodation_types: List[str] = Field(default_factory=list, description="Hotels, resorts, rentals")
    key_amenities: List[str] = Field(default_factory=list, description="Important features")
    booking_considerations: List[str] = Field(default_factory=list, description="Timing, pricing factors")

class LocalIntelligence(BaseModel):
    insider_tips: List[str] = Field(default_factory=list, description="Local knowledge")
    transportation_notes: List[str] = Field(default_factory=list, description="How to get around")
    cultural_etiquette: List[str] = Field(default_factory=list, description="Local customs")
    language_considerations: List[str] = Field(default_factory=list, description="Language help")
    currency_payment: List[str] = Field(default_factory=list, description="Payment methods")

class TemporalFactors(BaseModel):
    seasonality: Dict[str, List[str]] = Field(default_factory=dict, description="Peak, avoid, shoulder seasons")
    best_time_of_day: List[str] = Field(default_factory=list, description="Optimal timing")
    duration_recommendations: List[str] = Field(default_factory=list, description="How long to spend")
    advance_booking: str = Field(default="", description="How far ahead to book")

class AccessibilityInclusion(BaseModel):
    physical_accessibility: str = Field(default="", description="Mobility considerations")
    sensory_considerations: str = Field(default="", description="Visual, hearing accommodations")
    dietary_accommodations: List[str] = Field(default_factory=list, description="Food restrictions")
    budget_accessibility: str = Field(default="", description="Budget-friendly options")

class TypicalCosts(BaseModel):
    budget_range: str = Field(default="", description="Budget cost range")
    mid_range: str = Field(default="", description="Mid-range cost range") 
    luxury_range: str = Field(default="", description="Luxury cost range")

class PracticalDetails(BaseModel):
    price_point: str = Field(default="mid", description="Budget category")
    typical_costs: TypicalCosts = Field(default_factory=TypicalCosts, description="Cost ranges")
    booking_platforms: List[str] = Field(default_factory=list, description="Best booking sites")
    cancellation_policies: str = Field(default="", description="Flexibility considerations")

class ExperienceDepth(BaseModel):
    surface_level: List[str] = Field(default_factory=list, description="Easy/obvious experiences")
    deeper_exploration: List[str] = Field(default_factory=list, description="More involved experiences")
    local_immersion: List[str] = Field(default_factory=list, description="Authentic local experiences")
    hidden_gems: List[str] = Field(default_factory=list, description="Off-the-beaten-path")

class GettingThere(BaseModel):
    major_airports: List[str] = Field(default_factory=list, description="Airport codes and names")
    transportation_from_airport: List[str] = Field(default_factory=list, description="Airport to city options")
    alternative_arrival_methods: List[str] = Field(default_factory=list, description="Train, bus, car")

class GettingAround(BaseModel):
    public_transport: str = Field(default="", description="Metro, buses, efficiency")
    ride_sharing: str = Field(default="", description="Uber/Lyft availability")
    walking_walkability: str = Field(default="", description="Pedestrian-friendly rating")
    car_rental: str = Field(default="", description="Necessity and ease of driving")

class EssentialPrep(BaseModel):
    visa_requirements: str = Field(default="", description="Visa needs for US travelers")
    health_considerations: List[str] = Field(default_factory=list, description="Vaccinations, health tips")
    climate_preparation: List[str] = Field(default_factory=list, description="What to pack")
    tech_connectivity: str = Field(default="", description="Wifi, cell service, adapters")

class DestinationLogistics(BaseModel):
    getting_there: GettingThere = Field(default_factory=GettingThere, description="Transportation to destination")
    getting_around: GettingAround = Field(default_factory=GettingAround, description="Local transportation")
    essential_prep: EssentialPrep = Field(default_factory=EssentialPrep, description="Trip preparation")

class EnhancedBasicAffinity(BaseModel):
    """Enhanced basic affinity from LLM with destination nuances"""
    # Core theme information
    category: str
    theme: str
    sub_themes: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    
    # Enhanced traveler information
    traveler_nuances: TravelerNuances = Field(default_factory=TravelerNuances)
    
    # Accommodation and logistics
    accommodation_insights: AccommodationInsights = Field(default_factory=AccommodationInsights)
    local_intelligence: LocalIntelligence = Field(default_factory=LocalIntelligence)
    
    # Timing and accessibility
    temporal_factors: TemporalFactors = Field(default_factory=TemporalFactors)
    accessibility_inclusion: AccessibilityInclusion = Field(default_factory=AccessibilityInclusion)
    
    # Practical information
    practical_details: PracticalDetails = Field(default_factory=PracticalDetails)
    experience_depth: ExperienceDepth = Field(default_factory=ExperienceDepth)
    
    # Traditional fields
    rationale: str = ""
    unique_selling_points: List[str] = Field(default_factory=list)
    potential_drawbacks: List[str] = Field(default_factory=list)

class EnhancedBasicAffinitySet(BaseModel):
    """Complete enhanced affinity set from LLM"""
    destination_id: str
    destination_personality: DestinationPersonality = Field(default_factory=DestinationPersonality)
    affinities: List[EnhancedBasicAffinity] = Field(default_factory=list)
    destination_logistics: DestinationLogistics = Field(default_factory=DestinationLogistics)
    meta: Dict[str, Any] = Field(default_factory=dict)

# Original Enhanced Intelligence Models (keep existing)
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
    
    # Enhanced LLM fields (optional backward compatibility)
    traveler_nuances: Optional[TravelerNuances] = None
    accommodation_insights: Optional[AccommodationInsights] = None
    local_intelligence: Optional[LocalIntelligence] = None
    
    # Interconnections and flow
    theme_interconnections: ThemeInterconnection = Field(default_factory=ThemeInterconnection)
    
    # Discovery and uniqueness
    hidden_gem_score: HiddenGemScore = Field(default_factory=HiddenGemScore)
    
    # New Content Intelligence Attributes (additive to existing framework)
    iconic_landmarks: 'IconicLandmarks' = Field(default_factory=lambda: IconicLandmarks())
    practical_travel_intelligence: 'PracticalTravelIntelligence' = Field(default_factory=lambda: PracticalTravelIntelligence())
    neighborhood_insights: 'NeighborhoodInsights' = Field(default_factory=lambda: NeighborhoodInsights())
    content_discovery_intelligence: 'ContentDiscoveryIntelligence' = Field(default_factory=lambda: ContentDiscoveryIntelligence())
    
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
    
    # Enhanced LLM fields
    destination_personality: Optional[DestinationPersonality] = None
    destination_logistics: Optional[DestinationLogistics] = None
    
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

# New Content Intelligence Attributes (Additive to existing framework)

class IconicLandmarks(BaseModel):
    """Specific landmarks and their compelling descriptions"""
    specific_locations: List[str] = Field(default_factory=list, description="Named landmarks and attractions")
    landmark_descriptions: Dict[str, str] = Field(default_factory=dict, description="Compelling descriptions from sources")
    what_makes_them_special: List[str] = Field(default_factory=list, description="Unique characteristics extracted")
    landmark_categories: Dict[str, str] = Field(default_factory=dict, description="Type categorization")

class PracticalTravelIntelligence(BaseModel):
    """Factual travel planning information"""
    specific_costs: Dict[str, str] = Field(default_factory=dict, description="Actual price ranges found")
    timing_intelligence: Dict[str, List[str]] = Field(default_factory=dict, description="When to visit/book data")
    booking_specifics: List[str] = Field(default_factory=list, description="How far ahead, platforms, etc.")
    practical_tips: List[str] = Field(default_factory=list, description="Money-saving and timing advice")

class NeighborhoodInsights(BaseModel):
    """Area-specific intelligence"""
    neighborhood_names: List[str] = Field(default_factory=list, description="Specific area names")
    area_personalities: Dict[str, str] = Field(default_factory=dict, description="Character descriptions")
    neighborhood_specialties: Dict[str, List[str]] = Field(default_factory=dict, description="What each area is known for")
    stay_recommendations: Dict[str, str] = Field(default_factory=dict, description="Where to stay advice")

class ContentDiscoveryIntelligence(BaseModel):
    """Source and extraction metadata"""
    high_quality_sources: List[str] = Field(default_factory=list, description="Travel authority URLs found")
    extracted_phrases: List[str] = Field(default_factory=list, description="Compelling marketing language")
    content_themes: List[str] = Field(default_factory=list, description="Content patterns identified")
    authority_validation: Dict[str, Any] = Field(default_factory=dict, description="Source credibility data") 

# Rebuild model to resolve forward references
EnhancedAffinity.model_rebuild() 