"""
Enhanced Evidence and Validation Schema
Addresses the gaps in evidence storage and validation tracking for Smart Destination Themes.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from datetime import datetime

class EvidenceSourceType(str, Enum):
    GOVERNMENT = "government"          # .gov domains
    EDUCATION = "education"            # .edu domains  
    MAJOR_TRAVEL = "major_travel"      # TripAdvisor, Lonely Planet, etc.
    NEWS_MEDIA = "news_media"          # Major news outlets
    TRAVEL_BLOG = "travel_blog"        # Personal travel blogs
    SOCIAL_MEDIA = "social_media"      # Social media posts
    LOCAL_BUSINESS = "local_business"   # Local business websites
    TOURISM_BOARD = "tourism_board"    # Official tourism organizations
    UNKNOWN = "unknown"                # Unknown or unverified sources

class EvidenceQuality(str, Enum):
    EXCELLENT = "excellent"    # High authority, specific, detailed
    GOOD = "good"             # Good authority, relevant content
    ACCEPTABLE = "acceptable"  # Moderate authority, basic relevance
    POOR = "poor"             # Low authority, generic content
    REJECTED = "rejected"      # Below minimum standards

class ValidationStatus(str, Enum):
    VALIDATED = "validated"                    # Evidence found, theme confirmed
    PARTIALLY_VALIDATED = "partially_validated"  # Some evidence found
    UNVALIDATED = "unvalidated"               # No evidence found
    CONFLICTING = "conflicting"               # Evidence contradicts theme
    PENDING = "pending"                       # Validation not yet performed

class EvidencePiece(BaseModel):
    """Individual piece of evidence supporting a theme."""
    
    # Unique identification
    evidence_id: str = Field(description="Unique identifier for this evidence piece")
    
    # Content and source
    text_content: str = Field(description="The actual evidence text", max_length=1000)
    source_url: str = Field(description="URL where evidence was found")
    source_title: str = Field(description="Title of the source page")
    source_type: EvidenceSourceType = Field(description="Classification of evidence source")
    
    # Quality and authority
    authority_score: float = Field(ge=0, le=1, description="Authority score of the source")
    quality_rating: EvidenceQuality = Field(description="Quality assessment of evidence")
    relevance_score: float = Field(ge=0, le=1, description="How relevant to the theme")
    
    # Content analysis
    word_count: int = Field(ge=0, description="Number of words in evidence")
    contains_destination_mention: bool = Field(description="Evidence specifically mentions destination")
    contains_theme_keywords: List[str] = Field(default_factory=list, description="Matched theme keywords")
    
    # Processing metadata
    extracted_at: datetime = Field(default_factory=datetime.now, description="When evidence was extracted")
    processed_by: str = Field(default="enhanced_processor", description="System that processed evidence")
    validation_confidence: float = Field(ge=0, le=1, description="Confidence in validation")
    
    # Semantic analysis
    semantic_similarity: Optional[float] = Field(None, ge=0, le=1, description="Semantic similarity to theme")
    embedding_vector: Optional[List[float]] = Field(None, description="Text embedding vector")

class ThemeEvidence(BaseModel):
    """Collection of evidence for a specific theme."""
    
    # Theme identification
    theme_name: str = Field(description="Name of the theme being validated")
    theme_category: str = Field(description="Category of the theme")
    
    # Evidence collection
    evidence_pieces: List[EvidencePiece] = Field(default_factory=list, description="All evidence for this theme")
    total_evidence_count: int = Field(ge=0, description="Total number of evidence pieces")
    unique_source_count: int = Field(ge=0, description="Number of unique sources")
    
    # Validation results
    validation_status: ValidationStatus = Field(description="Overall validation status")
    validation_confidence: float = Field(ge=0, le=1, description="Confidence in validation")
    validation_timestamp: datetime = Field(default_factory=datetime.now, description="When validation was performed")
    
    # Evidence quality metrics
    average_authority_score: float = Field(ge=0, le=1, description="Average authority of all evidence")
    average_relevance_score: float = Field(ge=0, le=1, description="Average relevance of all evidence")
    source_diversity_score: float = Field(ge=0, le=1, description="Diversity of evidence sources")
    
    # Requirements satisfaction
    meets_min_evidence_requirement: bool = Field(description="Has minimum required evidence pieces")
    meets_source_diversity_requirement: bool = Field(description="Has sufficient source diversity")
    meets_quality_threshold: bool = Field(description="Meets minimum quality standards")
    
    # Evidence insights
    strongest_evidence: Optional[str] = Field(None, description="ID of strongest evidence piece")
    evidence_gaps: List[str] = Field(default_factory=list, description="Areas lacking evidence")
    conflicting_evidence: List[str] = Field(default_factory=list, description="Evidence that contradicts theme")

class ValidationReport(BaseModel):
    """Comprehensive validation report for a destination."""
    
    # Destination information
    destination_name: str = Field(description="Name of the destination")
    destination_id: str = Field(description="Unique destination identifier")
    
    # Validation overview
    total_themes_analyzed: int = Field(ge=0, description="Total number of themes analyzed")
    themes_validated: int = Field(ge=0, description="Number of themes with evidence")
    themes_rejected: int = Field(ge=0, description="Number of themes rejected due to lack of evidence")
    validation_success_rate: float = Field(ge=0, le=1, description="Percentage of themes validated")
    
    # Evidence summary
    total_evidence_pieces: int = Field(ge=0, description="Total evidence pieces collected")
    unique_sources_used: int = Field(ge=0, description="Number of unique sources used")
    average_evidence_quality: float = Field(ge=0, le=1, description="Average quality of all evidence")
    
    # Theme evidence details
    theme_evidence: List[ThemeEvidence] = Field(default_factory=list, description="Evidence for each theme")
    
    # Quality metrics
    evidence_quality_distribution: Dict[EvidenceQuality, int] = Field(default_factory=dict, description="Distribution of evidence quality")
    source_type_distribution: Dict[EvidenceSourceType, int] = Field(default_factory=dict, description="Distribution of source types")
    
    # Processing metadata
    validation_started_at: datetime = Field(default_factory=datetime.now, description="When validation started")
    validation_completed_at: Optional[datetime] = Field(None, description="When validation completed")
    processing_time_seconds: Optional[float] = Field(None, description="Total processing time")
    
    # Configuration used
    validation_config: Dict[str, Any] = Field(default_factory=dict, description="Validation configuration used")
    
    # Recommendations
    quality_recommendations: List[str] = Field(default_factory=list, description="Recommendations for improving evidence quality")
    coverage_recommendations: List[str] = Field(default_factory=list, description="Recommendations for improving evidence coverage")

class EnhancedThemeWithEvidence(BaseModel):
    """Enhanced theme model that includes comprehensive evidence tracking."""
    
    # Core theme information (from existing schema)
    theme: str
    category: str
    confidence: float = Field(ge=0, le=1)
    sub_themes: List[str] = Field(default_factory=list)
    
    # Evidence and validation
    evidence: ThemeEvidence = Field(description="Complete evidence tracking for this theme")
    validation_status: ValidationStatus = Field(description="Validation status")
    evidence_strength: float = Field(ge=0, le=1, description="Overall strength of evidence")
    
    # Enhanced metadata
    initial_confidence: float = Field(ge=0, le=1, description="Original confidence before evidence validation")
    evidence_adjusted_confidence: float = Field(ge=0, le=1, description="Confidence after evidence validation")
    confidence_adjustment: float = Field(description="Change in confidence due to evidence")
    
    # Quality gates
    passes_evidence_requirements: bool = Field(description="Meets all evidence requirements")
    passes_quality_threshold: bool = Field(description="Meets quality thresholds")
    recommended_for_inclusion: bool = Field(description="Recommended for final inclusion")
    
    # Processing lineage
    generated_by: str = Field(default="llm", description="How theme was generated")
    validated_by: str = Field(default="evidence_validator", description="How theme was validated")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class EvidenceValidationConfig(BaseModel):
    """Configuration for evidence validation requirements."""
    
    # Evidence quantity requirements
    min_evidence_pieces: int = Field(ge=1, default=3, description="Minimum evidence pieces required")
    max_evidence_pieces: int = Field(ge=1, default=10, description="Maximum evidence pieces to store")
    min_unique_sources: int = Field(ge=1, default=2, description="Minimum unique sources required")
    max_evidence_per_source: int = Field(ge=1, default=3, description="Maximum evidence from single source")
    
    # Quality thresholds
    min_authority_score: float = Field(ge=0, le=1, default=0.3, description="Minimum source authority required")
    min_relevance_score: float = Field(ge=0, le=1, default=0.5, description="Minimum relevance required")
    min_content_length: int = Field(ge=10, default=50, description="Minimum content length")
    
    # Confidence adjustments
    confidence_boost_per_evidence: float = Field(ge=0, le=0.2, default=0.05, description="Confidence boost per evidence piece")
    confidence_penalty_no_evidence: float = Field(ge=0, le=0.5, default=0.2, description="Confidence penalty for no evidence")
    max_confidence_adjustment: float = Field(ge=0, le=0.5, default=0.3, description="Maximum confidence adjustment")
    
    # Source authority weights
    authority_weights: Dict[EvidenceSourceType, float] = Field(
        default_factory=lambda: {
            EvidenceSourceType.GOVERNMENT: 1.0,
            EvidenceSourceType.EDUCATION: 0.9,
            EvidenceSourceType.MAJOR_TRAVEL: 0.8,
            EvidenceSourceType.NEWS_MEDIA: 0.7,
            EvidenceSourceType.TOURISM_BOARD: 0.75,
            EvidenceSourceType.TRAVEL_BLOG: 0.5,
            EvidenceSourceType.LOCAL_BUSINESS: 0.4,
            EvidenceSourceType.SOCIAL_MEDIA: 0.3,
            EvidenceSourceType.UNKNOWN: 0.2
        },
        description="Authority weights for different source types"
    )
    
    # Validation requirements
    require_destination_mention: bool = Field(default=True, description="Evidence must mention destination")
    require_source_diversity: bool = Field(default=True, description="Evidence must come from diverse sources")
    enable_semantic_validation: bool = Field(default=True, description="Use semantic similarity for validation")
    semantic_similarity_threshold: float = Field(ge=0, le=1, default=0.7, description="Minimum semantic similarity")

    @validator('max_evidence_pieces')
    def max_must_be_greater_than_min(cls, v, values):
        if 'min_evidence_pieces' in values and v < values['min_evidence_pieces']:
            raise ValueError('max_evidence_pieces must be >= min_evidence_pieces')
        return v 