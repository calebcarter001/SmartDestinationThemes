"""
Enhanced Data Processor - Adds intelligence layers to affinities and manages JSON persistence
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from tqdm import tqdm

from src.scorer import AffinityQualityScorer
from src.evidence_validator import EvidenceValidator
from src.content_intelligence_processor import ContentIntelligenceProcessor
from src.schemas import PageContent

logger = logging.getLogger(__name__)

class EnhancedDataProcessor:
    """
    Processes and enhances destination affinity data with intelligence layers
    and manages JSON persistence with rich metadata.
    Now includes comprehensive evidence collection for all insights and progress tracking.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.scorer = AffinityQualityScorer(config)
        self.evidence_validator = EvidenceValidator(config)
        self.content_intelligence_processor = ContentIntelligenceProcessor(config)
        
        # Session management for batch processing
        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_output_dir = "outputs"
        self.session_output_dir = os.path.join(self.base_output_dir, f"session_{self.session_timestamp}")
        
        # Intelligence enhancement mappings
        self.emotional_keywords = {
            'peaceful': ['quiet', 'serene', 'calm', 'tranquil', 'meditation', 'zen', 'peaceful'],
            'exhilarating': ['thrilling', 'exciting', 'adrenaline', 'extreme', 'adventure', 'rush'],
            'contemplative': ['historical', 'museum', 'spiritual', 'reflective', 'philosophical'],
            'social': ['festival', 'nightlife', 'community', 'group', 'celebration', 'party'],
            'solitary': ['solo', 'private', 'individual', 'personal', 'introspective'],
            'challenging': ['difficult', 'demanding', 'skill', 'expertise', 'advanced'],
            'comforting': ['familiar', 'cozy', 'comfortable', 'relaxing', 'soothing'],
            'inspiring': ['artistic', 'creative', 'innovative', 'motivational', 'uplifting']
        }
        
        self.authenticity_indicators = {
            'local_markers': ['local', 'neighborhood', 'authentic', 'traditional', 'family-owned', 'generations'],
            'tourist_markers': ['tourist', 'visitor', 'attraction', 'souvenir', 'tour bus', 'crowded'],
            'insider_markers': ['hidden', 'secret', 'locals only', 'off the beaten path', 'insider'],
            'commercial_markers': ['chain', 'franchise', 'commercialized', 'mass tourism', 'package']
        }
        
        self.intensity_levels = ['minimal', 'low', 'moderate', 'high', 'extreme']
        self.depth_levels = ['macro', 'micro', 'nano']

    def process_destinations_with_progress(self, destinations_data: Dict[str, Any], 
                                         generate_dashboard: bool = True,
                                         web_data: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Process multiple destinations with progress tracking and organized output.
        
        Args:
            destinations_data: Dictionary of destination name -> destination data
            generate_dashboard: Whether to generate HTML dashboard
            web_data: Web discovery data for evidence collection
            
        Returns:
            Dictionary of destination name -> output file path
        """
        
        print(f"\n🚀 Processing {len(destinations_data)} destinations with Enhanced Intelligence")
        print(f"📁 Session output directory: {self.session_output_dir}")
        if web_data:
            print(f"🌐 Web evidence collection enabled for {len(web_data)} destinations")
        print("="*70)
        
        # Create session output directories
        os.makedirs(self.session_output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.session_output_dir, "json"), exist_ok=True)
        os.makedirs(os.path.join(self.session_output_dir, "dashboard"), exist_ok=True)
        
        # Track processed files for dashboard generation
        processed_files = {}
        dashboard_json_files = []
        
        # Create progress bar for destinations
        dest_progress = tqdm(destinations_data.items(), 
                           desc="Processing destinations",
                           unit="dest",
                           colour="blue")
        
        for destination_name, destination_data in dest_progress:
            dest_progress.set_description(f"Processing {destination_name}")
            
            try:
                # Get web data for this destination
                dest_web_data = web_data.get(destination_name, {}) if web_data else {}
                
                # Process single destination with progress and web data
                enhanced_data = self._process_single_destination_with_progress(
                    destination_data, destination_name, dest_web_data
                )
                
                # Save enhanced JSON
                json_filename = f"{self._sanitize_filename(destination_name)}_enhanced.json"
                json_filepath = os.path.join(self.session_output_dir, "json", json_filename)
                
                # Save evidence separately
                evidence_filename = f"{self._sanitize_filename(destination_name)}_evidence.json"
                evidence_filepath = os.path.join(self.session_output_dir, "json", evidence_filename)
                
                # Extract evidence data for separate file
                evidence_data = {
                    'destination_id': enhanced_data.get('destination_id', ''),
                    'destination_name': destination_name,
                    'evidence_metadata': {
                        'generation_timestamp': datetime.now().isoformat(),
                        'total_themes_with_evidence': 0,
                        'total_evidence_pieces': 0,
                        'evidence_summary': {}
                    },
                    'theme_evidence': {}
                }
                
                # Extract evidence from each theme
                for affinity in enhanced_data.get('affinities', []):
                    theme_name = affinity.get('theme', 'Unknown')
                    comprehensive_evidence = affinity.get('comprehensive_attribute_evidence', {})
                    
                    if comprehensive_evidence:
                        # Convert to JSON-serializable format properly
                        try:
                            serializable_evidence = self.evidence_validator.to_json_serializable(comprehensive_evidence)
                            evidence_data['theme_evidence'][theme_name] = serializable_evidence
                            evidence_data['evidence_metadata']['total_themes_with_evidence'] += 1
                            
                            # Count evidence pieces from serialized data
                            for attr_evidence in serializable_evidence.values():
                                if isinstance(attr_evidence, dict) and 'evidence_pieces' in attr_evidence:
                                    evidence_data['evidence_metadata']['total_evidence_pieces'] += len(attr_evidence['evidence_pieces'])
                        except Exception as e:
                            logger.error(f"Error serializing evidence for theme {theme_name}: {e}")
                            # Store as string representation as fallback
                            evidence_data['theme_evidence'][theme_name] = str(comprehensive_evidence)
                
                # Save evidence file without default=str to avoid string conversion
                with open(evidence_filepath, 'w', encoding='utf-8') as f:
                    json.dump(evidence_data, f, indent=2)
                
                # Remove comprehensive evidence from main JSON and add reference
                for affinity in enhanced_data.get('affinities', []):
                    if 'comprehensive_attribute_evidence' in affinity:
                        del affinity['comprehensive_attribute_evidence']
                
                # Add evidence file reference to main data
                enhanced_data['evidence_file_reference'] = evidence_filename
                
                with open(json_filepath, 'w', encoding='utf-8') as f:
                    json.dump(enhanced_data, f, indent=2, default=str)
                
                processed_files[destination_name] = json_filepath
                dashboard_json_files.append(json_filepath)
                
                logger.info(f"Enhanced data saved: {json_filepath}")
                
            except Exception as e:
                logger.error(f"Error processing {destination_name}: {e}")
                dest_progress.set_description(f"Error: {destination_name}")
                continue
        
        dest_progress.close()
        
        # Generate dashboard if requested
        if generate_dashboard and dashboard_json_files:
            print(f"\n🎨 Generating Enhanced Intelligence Dashboard...")
            
            dashboard_dir = os.path.join(self.session_output_dir, "dashboard")
            from src.enhanced_viewer_generator import EnhancedViewerGenerator
            generator = EnhancedViewerGenerator()
            
            try:
                dashboard_files = generator.generate_multi_destination_viewer(
                    dashboard_json_files, 
                    dashboard_dir
                )
                
                print(f"✅ Dashboard generated: {len(dashboard_files)} destination pages")
                print(f"📍 Index page: {os.path.join(dashboard_dir, 'index.html')}")
                
            except Exception as e:
                logger.error(f"Error generating dashboard: {e}")
                print(f"❌ Dashboard generation failed: {e}")
        
        # Generate session summary
        self._generate_session_summary(processed_files)
        
        print(f"\n🎉 Processing complete!")
        print(f"📊 {len(processed_files)} destinations processed successfully")
        print(f"📁 All outputs in: {self.session_output_dir}")
        
        return processed_files

    def _process_single_destination_with_progress(self, destination_data: Dict[str, Any], 
                                                destination_name: str,
                                                web_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a single destination with detailed progress tracking."""
        
        affinities = destination_data.get('affinities', [])
        if not affinities:
            return destination_data
        
        # Create progress bar for affinities processing
        affinity_progress = tqdm(affinities, 
                               desc=f"Enhancing {destination_name} themes",
                               unit="theme",
                               leave=False,
                               colour="green")
        
        enhanced_affinities = []
        
        for affinity in affinity_progress:
            theme_name = affinity.get('theme', 'Unknown')
            affinity_progress.set_description(f"Analyzing: {theme_name[:30]}...")
            
            try:
                # Apply all intelligence layers with sub-progress
                enhanced_affinity = self._enhance_single_affinity_with_progress(
                    affinity, destination_name, affinity_progress, web_data
                )
                enhanced_affinities.append(enhanced_affinity)
                
            except Exception as e:
                logger.error(f"Error enhancing affinity {theme_name}: {e}")
                enhanced_affinities.append(affinity)  # Keep original if enhancement fails
        
        affinity_progress.close()
        
        # Update destination data with enhanced affinities
        enhanced_destination_data = destination_data.copy()
        enhanced_destination_data['affinities'] = enhanced_affinities
        enhanced_destination_data['destination_name'] = destination_name
        
        # Generate intelligence insights with progress
        print(f"  🧠 Generating intelligence insights for {destination_name}...")
        enhanced_destination_data['intelligence_insights'] = self._generate_intelligence_insights(enhanced_affinities)
        
        # Generate composition analysis
        print(f"  🎨 Analyzing composition for {destination_name}...")
        enhanced_destination_data['composition_analysis'] = self._analyze_composition(enhanced_affinities)
        
        # Enhanced quality assessment with progress
        print(f"  📊 Calculating quality metrics for {destination_name}...")
        enhanced_destination_data['quality_assessment'] = self.scorer.score_affinity_set(
            enhanced_destination_data, destination_name
        )
        
        # QA workflow generation
        print(f"  🔒 Processing QA workflow for {destination_name}...")
        enhanced_destination_data['qa_workflow'] = self._generate_qa_workflow(enhanced_destination_data['quality_assessment'])
        
        # Add processing metadata
        enhanced_destination_data['processing_metadata'] = {
            'session_timestamp': self.session_timestamp,
            'processing_date': datetime.now().isoformat(),
            'enhanced_affinity_count': len(enhanced_affinities),
            'intelligence_layers_applied': 10,
            'processor_version': '2.0.0'
        }
        
        return enhanced_destination_data

    def _enhance_single_affinity_with_progress(self, affinity: Dict[str, Any], 
                                             destination_name: str, 
                                             parent_progress: tqdm,
                                             web_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhance a single affinity with detailed progress tracking."""
        
        # Convert web_data to PageContent objects for evidence validation
        web_pages = []
        if web_data and 'content' in web_data:
            for page_data in web_data['content']:
                try:
                    page_content = PageContent(
                        url=page_data.get('url', ''),
                        title=page_data.get('title', ''),
                        content=page_data.get('content', ''),
                        content_length=len(page_data.get('content', '')),
                        metadata={
                            'relevance_score': page_data.get('relevance_score', 0.5),
                            'source': 'web_discovery'
                        }
                    )
                    web_pages.append(page_content)
                except Exception as e:
                    logger.warning(f"Error converting page data to PageContent: {e}")
        
        # Store web_pages for evidence validation
        self.web_pages = web_pages
        
        # Intelligence processing steps - using existing methods
        intelligence_steps = [
            ("🔍 Depth Analysis", lambda a, d: self._analyze_theme_depth(a, d)),
            ("🏆 Authenticity Scoring", lambda a, d: self._analyze_authenticity(a, d)),
            ("✨ Emotional Profiling", lambda a, d: self._analyze_emotional_resonance(a, d)),
            ("⚡ Intensity Calibration", lambda a, d: self._analyze_experience_intensity(a, d)),
            ("🎯 Context Analysis", lambda a, d: self._analyze_context(a, d)),
            ("🌤️ Micro-Climate", lambda a, d: self._analyze_micro_climate(a, d)),
            ("🏛️ Cultural Sensitivity", lambda a, d: self._assess_cultural_sensitivity(a, d)),
            ("🔗 Theme Interconnections", lambda a, d: self._analyze_theme_interconnections(a, d)),
            ("💎 Hidden Gem Scoring", lambda a, d: self._calculate_hidden_gem_score(a, d)),
            ("💰 Price Analysis", lambda a, d: self._analyze_price_insights(a, d))
        ]
        
        enhanced = affinity.copy()
        
        # Process each intelligence layer
        for step_name, step_func in intelligence_steps:
            try:
                if "Depth" in step_name:
                    enhanced['depth_analysis'] = step_func(affinity, destination_name)
                elif "Authenticity" in step_name:
                    enhanced['authenticity_analysis'] = step_func(affinity, destination_name)
                elif "Emotional" in step_name:
                    enhanced['emotional_profile'] = step_func(affinity, destination_name)
                elif "Intensity" in step_name:
                    enhanced['experience_intensity'] = step_func(affinity, destination_name)
                elif "Context" in step_name:
                    enhanced['contextual_info'] = step_func(affinity, destination_name)
                elif "Micro-Climate" in step_name:
                    enhanced['micro_climate'] = step_func(affinity, destination_name)
                elif "Cultural" in step_name:
                    enhanced['cultural_sensitivity'] = step_func(affinity, destination_name)
                elif "Interconnections" in step_name:
                    enhanced['theme_interconnections'] = step_func(affinity, destination_name)
                elif "Hidden Gem" in step_name:
                    enhanced['hidden_gem_score'] = step_func(affinity, destination_name)
                elif "Price" in step_name:
                    enhanced['price_insights'] = step_func(affinity, destination_name)
                    
            except Exception as e:
                logger.warning(f"Error in {step_name} for {affinity.get('theme', 'unknown')}: {e}")
        
        # Validate ALL attributes with comprehensive evidence collection if web pages available
        if hasattr(self, 'evidence_validator') and web_pages:
            try:
                enhanced['comprehensive_attribute_evidence'] = self.evidence_validator.validate_all_theme_attributes(
                    enhanced, web_pages, destination_name
                )
                logger.info(f"Evidence validation completed for {affinity.get('theme', 'unknown')} with {len(web_pages)} pages")
            except Exception as e:
                logger.error(f"Error in evidence validation for {affinity.get('theme', 'unknown')}: {e}")
        
        return enhanced

    def _generate_session_summary(self, processed_files: Dict[str, str]):
        """Generate a summary of the processing session."""
        
        summary = {
            'session_info': {
                'timestamp': self.session_timestamp,
                'processing_date': datetime.now().isoformat(),
                'output_directory': self.session_output_dir,
                'destinations_processed': len(processed_files)
            },
            'processed_destinations': {},
            'session_statistics': {
                'total_themes_enhanced': 0,
                'total_hidden_gems_found': 0,
                'average_quality_score': 0,
                'quality_distribution': {
                    'excellent': 0,
                    'good': 0, 
                    'acceptable': 0,
                    'needs_improvement': 0
                }
            }
        }
        
        # Collect statistics from processed files
        total_quality_score = 0
        
        for dest_name, file_path in processed_files.items():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                theme_count = len(data.get('affinities', []))
                quality_score = data.get('quality_assessment', {}).get('overall_score', 0)
                hidden_gems = data.get('intelligence_insights', {}).get('hidden_gems_count', 0)
                
                summary['processed_destinations'][dest_name] = {
                    'file_path': file_path,
                    'theme_count': theme_count,
                    'quality_score': quality_score,
                    'hidden_gems_count': hidden_gems,
                    'quality_level': self._get_quality_level(quality_score)
                }
                
                # Update session statistics
                summary['session_statistics']['total_themes_enhanced'] += theme_count
                summary['session_statistics']['total_hidden_gems_found'] += hidden_gems
                total_quality_score += quality_score
                
                # Quality distribution
                quality_level = self._get_quality_level(quality_score).lower().replace(' ', '_')
                summary['session_statistics']['quality_distribution'][quality_level] += 1
                
            except Exception as e:
                logger.error(f"Error processing summary for {dest_name}: {e}")
        
        # Calculate average quality score
        if processed_files:
            summary['session_statistics']['average_quality_score'] = total_quality_score / len(processed_files)
        
        # Save session summary
        summary_file = os.path.join(self.session_output_dir, "session_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Session summary saved: {summary_file}")
        
        # Print summary to console
        print(f"\n📋 Session Summary:")
        print(f"   • Destinations processed: {len(processed_files)}")
        print(f"   • Total themes enhanced: {summary['session_statistics']['total_themes_enhanced']}")
        print(f"   • Hidden gems discovered: {summary['session_statistics']['total_hidden_gems_found']}")
        print(f"   • Average quality score: {summary['session_statistics']['average_quality_score']:.3f}")
        print(f"   • Quality distribution: {summary['session_statistics']['quality_distribution']}")

    def _get_quality_level(self, score: float) -> str:
        """Get quality level from score."""
        if score >= 0.85:
            return 'excellent'
        elif score >= 0.75:
            return 'good'
        elif score >= 0.65:
            return 'acceptable'
        else:
            return 'needs_improvement'

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize destination name for filename."""
        return "".join(c.lower() if c.isalnum() else '_' for c in name).strip('_')

    def get_session_output_dir(self) -> str:
        """Get the current session output directory."""
        return self.session_output_dir

    def get_latest_dashboard_url(self) -> str:
        """Get the URL to the latest generated dashboard."""
        dashboard_index = os.path.join(self.session_output_dir, "dashboard", "index.html")
        if os.path.exists(dashboard_index):
            return os.path.abspath(dashboard_index)
        return None

    async def enhance_and_save_affinities(self, affinities_data: Dict[str, Any], 
                                  destination: str, web_pages: List[PageContent] = None,
                                  output_file: str = None, llm_generator=None) -> Dict[str, Any]:
        """
        Enhance affinities with intelligence layers and comprehensive evidence collection.
        
        Args:
            affinities_data: Raw affinity data
            destination: Destination name
            web_pages: Web content for evidence collection
            output_file: Optional output file path
        
        Returns:
            Enhanced affinities data with intelligence layers and evidence
        """
        logger.info(f"Enhancing affinities for {destination}")
        
        # Store web_pages and LLM generator for evidence validation and content intelligence
        self.web_pages = web_pages or []
        self.llm_generator = llm_generator
        
        # Collect comprehensive evidence for all insights
        comprehensive_evidence = {}
        if web_pages:
            comprehensive_evidence = self._collect_comprehensive_evidence(web_pages, destination)
        
        # Enhance each affinity with intelligence layers
        enhanced_affinities = []
        if 'affinities' in affinities_data:
            for affinity in affinities_data['affinities']:
                enhanced_affinity = await self._enhance_single_affinity(affinity, destination, comprehensive_evidence)
                enhanced_affinities.append(enhanced_affinity)
        
        # Create enhanced dataset structure
        enhanced_data = {
            'destination_id': destination.lower().replace(' ', '_').replace(',', ''),
            'destination_name': destination,
            'affinities': enhanced_affinities,
            'comprehensive_evidence': comprehensive_evidence,  # Add all evidence
            'meta': {
                **affinities_data.get('meta', {}),
                'enhancement_timestamp': datetime.now().isoformat(),
                'total_affinities': len(enhanced_affinities),
                'enhancement_version': '2.0',
                'evidence_collection_enabled': bool(web_pages)
            }
        }
        
        # Calculate enhanced quality assessment
        enhanced_data['quality_assessment'] = self.scorer.score_affinity_set(
            {'affinities': enhanced_affinities}, destination
        )
        
        # Add intelligence insights
        enhanced_data['intelligence_insights'] = self._generate_intelligence_insights(enhanced_affinities)
        
        # Add composition analysis
        enhanced_data['composition_analysis'] = self._analyze_composition(enhanced_affinities)
        
        # Add QA workflow status
        enhanced_data['qa_workflow'] = self._generate_qa_workflow(enhanced_data['quality_assessment'])
        
        # Save to JSON
        if output_file:
            self._save_to_json(enhanced_data, output_file)
        
        logger.info(f"Enhanced {len(enhanced_affinities)} affinities for {destination}")
        return enhanced_data

    def _collect_comprehensive_evidence(self, web_pages: List[PageContent], destination: str) -> Dict[str, Any]:
        """Collect evidence for all types of insights."""
        logger.info(f"Collecting comprehensive evidence for {destination}")
        
        evidence_collection = {
            'price_evidence': None,
            'authenticity_evidence': None,
            'hidden_gem_evidence': None,
            'nano_themes_evidence': {},
            'collection_timestamp': datetime.now().isoformat(),
            'total_pages_analyzed': len(web_pages),
            'evidence_summary': {
                'total_evidence_pieces': 0,
                'unique_sources': 0,
                'evidence_types_collected': []
            }
        }
        
        try:
            # Collect price evidence
            price_evidence = self.evidence_validator.validate_price_evidence(web_pages, destination)
            evidence_collection['price_evidence'] = price_evidence.dict()
            if price_evidence.total_evidence_count > 0:
                evidence_collection['evidence_summary']['evidence_types_collected'].append('price')
            
            # Collect authenticity evidence
            auth_evidence = self.evidence_validator.validate_authenticity_evidence(web_pages, destination)
            evidence_collection['authenticity_evidence'] = auth_evidence.dict()
            if auth_evidence.total_evidence_count > 0:
                evidence_collection['evidence_summary']['evidence_types_collected'].append('authenticity')
            
            # Collect hidden gem evidence
            gem_evidence = self.evidence_validator.validate_hidden_gem_evidence(web_pages, destination)
            evidence_collection['hidden_gem_evidence'] = gem_evidence.dict()
            if gem_evidence.total_evidence_count > 0:
                evidence_collection['evidence_summary']['evidence_types_collected'].append('hidden_gems')
            
            # Calculate summary statistics
            all_evidence_pieces = []
            all_sources = set()
            
            for evidence_type in ['price_evidence', 'authenticity_evidence', 'hidden_gem_evidence']:
                evidence_data = evidence_collection[evidence_type]
                if evidence_data and evidence_data.get('evidence_pieces'):
                    all_evidence_pieces.extend(evidence_data['evidence_pieces'])
                    all_sources.update(ep['source_url'] for ep in evidence_data['evidence_pieces'])
            
            evidence_collection['evidence_summary']['total_evidence_pieces'] = len(all_evidence_pieces)
            evidence_collection['evidence_summary']['unique_sources'] = len(all_sources)
            
            logger.info(f"Collected {len(all_evidence_pieces)} evidence pieces from {len(all_sources)} sources")
            
        except Exception as e:
            logger.error(f"Error collecting comprehensive evidence: {e}")
            evidence_collection['error'] = str(e)
        
        return evidence_collection

    async def _enhance_single_affinity(self, affinity: Dict[str, Any], destination: str, 
                               comprehensive_evidence: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhance a single affinity with intelligence layers and evidence."""
        
        enhanced = affinity.copy()
        
        # Add depth analysis
        enhanced['depth_analysis'] = self._analyze_theme_depth(affinity, destination)
        
        # Add nano theme evidence if available
        nano_themes = enhanced['depth_analysis'].get('nano_themes', [])
        if nano_themes and comprehensive_evidence:
            # Note: For now, we'll add nano theme evidence collection in a future enhancement
            # This would require the web_pages to be passed to each affinity enhancement
            enhanced['nano_themes_evidence'] = self._get_nano_themes_evidence_summary(nano_themes, comprehensive_evidence)
        
        # Add authenticity scoring with evidence
        enhanced['authenticity_analysis'] = self._analyze_authenticity(affinity, destination, comprehensive_evidence)
        
        # Add emotional profiling
        enhanced['emotional_profile'] = self._analyze_emotional_resonance(affinity, destination)
        
        # Add experience intensity
        enhanced['experience_intensity'] = self._analyze_experience_intensity(affinity, destination)
        
        # Add contextual information
        enhanced['contextual_info'] = self._analyze_context(affinity, destination)
        
        # Add micro-climate insights
        enhanced['micro_climate'] = self._analyze_micro_climate(affinity, destination)
        
        # Add cultural sensitivity assessment
        enhanced['cultural_sensitivity'] = self._assess_cultural_sensitivity(affinity, destination)
        
        # Add theme interconnections
        enhanced['theme_interconnections'] = self._analyze_theme_interconnections(affinity, destination)
        
        # Add hidden gem potential with evidence
        enhanced['hidden_gem_score'] = self._calculate_hidden_gem_score(affinity, destination, comprehensive_evidence)
        
        # Add price insights with evidence
        enhanced['price_insights'] = self._analyze_price_insights(affinity, destination, comprehensive_evidence)
        
        # Add new content intelligence attributes (additive to existing framework)
        enhanced = await self._add_content_intelligence_attributes(enhanced, destination)
        
        # Validate ALL attributes with comprehensive evidence collection (including content intelligence)
        if hasattr(self, 'evidence_validator') and hasattr(self, 'web_pages') and self.web_pages:
            comprehensive_evidence = self.evidence_validator.validate_all_theme_attributes(
                enhanced, self.web_pages, destination
            )
            
            # Add the content intelligence attributes to the comprehensive evidence
            comprehensive_evidence['iconic_landmarks'] = enhanced.get('iconic_landmarks', {})
            comprehensive_evidence['practical_travel_intelligence'] = enhanced.get('practical_travel_intelligence', {})
            comprehensive_evidence['neighborhood_insights'] = enhanced.get('neighborhood_insights', {})
            comprehensive_evidence['content_discovery_intelligence'] = enhanced.get('content_discovery_intelligence', {})
            
            enhanced['comprehensive_attribute_evidence'] = comprehensive_evidence
        
        return enhanced

    def _get_nano_themes_evidence_summary(self, nano_themes: List[str], 
                                        comprehensive_evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Get evidence summary for nano themes."""
        nano_evidence_summary = {
            'nano_themes_with_evidence': [],
            'total_nano_evidence_pieces': 0,
            'evidence_quality_distribution': {}
        }
        
        # This would be enhanced with actual nano theme evidence collection
        # For now, we provide a placeholder structure
        for nano_theme in nano_themes:
            nano_evidence_summary['nano_themes_with_evidence'].append({
                'nano_theme': nano_theme,
                'evidence_status': 'collection_pending',
                'evidence_count': 0
            })
        
        return nano_evidence_summary

    def _analyze_authenticity(self, affinity: Dict[str, Any], 
                            destination: str,
                            comprehensive_evidence: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze authenticity level and characteristics with evidence support."""
        theme = affinity.get('theme', '')
        rationale = affinity.get('rationale', '')
        
        combined_text = f"{theme} {rationale}".lower()
        
        # Count authenticity indicators
        local_score = sum(1 for marker in self.authenticity_indicators['local_markers'] 
                         if marker in combined_text)
        tourist_score = sum(1 for marker in self.authenticity_indicators['tourist_markers'] 
                           if marker in combined_text)
        insider_score = sum(1 for marker in self.authenticity_indicators['insider_markers'] 
                           if marker in combined_text)
        commercial_score = sum(1 for marker in self.authenticity_indicators['commercial_markers'] 
                              if marker in combined_text)
        
        # Calculate authenticity score
        authenticity_score = (local_score + insider_score - tourist_score - commercial_score) / 10.0
        authenticity_score = max(0.0, min(1.0, authenticity_score + 0.5))  # Normalize to 0-1
        
        # Determine authenticity level
        if authenticity_score >= 0.8:
            authenticity_level = 'authentic_local'
        elif authenticity_score >= 0.6:
            authenticity_level = 'local_influenced'
        elif authenticity_score >= 0.4:
            authenticity_level = 'balanced'
        elif authenticity_score >= 0.2:
            authenticity_level = 'tourist_oriented'
        else:
            authenticity_level = 'commercialized'
        
        result = {
            'authenticity_level': authenticity_level,
            'authenticity_score': authenticity_score,
            'local_indicators': local_score,
            'tourist_indicators': tourist_score,
            'insider_indicators': insider_score,
            'commercial_indicators': commercial_score
        }
        
        # Add evidence support if available
        if comprehensive_evidence and comprehensive_evidence.get('authenticity_evidence'):
            auth_evidence = comprehensive_evidence['authenticity_evidence']
            result['evidence_support'] = {
                'evidence_pieces_count': auth_evidence.get('total_evidence_count', 0),
                'evidence_quality': auth_evidence.get('average_authority_score', 0),
                'validation_status': auth_evidence.get('validation_status', 'pending'),
                'strongest_evidence': self._get_strongest_evidence_text(auth_evidence)
            }
        
        return result

    def _calculate_hidden_gem_score(self, affinity: Dict[str, Any], 
                                  destination: str,
                                  comprehensive_evidence: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate hidden gem potential with evidence support."""
        theme = affinity.get('theme', '')
        rationale = affinity.get('rationale', '')
        
        combined_text = f"{theme} {rationale}".lower()
        
        # Hidden gem indicators
        hidden_indicators = ['hidden', 'secret', 'off the beaten path', 'locals only', 'undiscovered']
        crowd_indicators = ['crowded', 'tourist', 'popular', 'busy', 'packed', 'famous']
        unique_indicators = ['unique', 'rare', 'special', 'exclusive', 'distinctive']
        
        hidden_score = sum(1 for indicator in hidden_indicators if indicator in combined_text)
        crowd_penalty = sum(1 for indicator in crowd_indicators if indicator in combined_text)
        unique_score = sum(1 for indicator in unique_indicators if indicator in combined_text)
        
        # Calculate uniqueness score
        uniqueness_score = (hidden_score + unique_score - crowd_penalty) / 10.0
        uniqueness_score = max(0.0, min(1.0, uniqueness_score + 0.5))
        
        hidden_gem_level = self._classify_hidden_gem_level(uniqueness_score)
        
        result = {
            'hidden_gem_level': hidden_gem_level,
            'uniqueness_score': uniqueness_score,
            'hidden_indicators': hidden_score,
            'crowd_indicators': crowd_penalty,
            'unique_indicators': unique_score,
            'discovery_potential': 'high' if uniqueness_score > 0.7 else 'medium' if uniqueness_score > 0.4 else 'low'
        }
        
        # Add evidence support if available
        if comprehensive_evidence and comprehensive_evidence.get('hidden_gem_evidence'):
            gem_evidence = comprehensive_evidence['hidden_gem_evidence']
            result['evidence_support'] = {
                'evidence_pieces_count': gem_evidence.get('total_evidence_count', 0),
                'evidence_quality': gem_evidence.get('average_authority_score', 0),
                'validation_status': gem_evidence.get('validation_status', 'pending'),
                'strongest_evidence': self._get_strongest_evidence_text(gem_evidence)
            }
        
        return result

    def _analyze_price_insights(self, affinity: Dict[str, Any], 
                              destination: str,
                              comprehensive_evidence: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze price-related insights with evidence support."""
        theme = affinity.get('theme', '')
        rationale = affinity.get('rationale', '')
        
        combined_text = f"{theme} {rationale}".lower()
        
        # Price indicators
        expensive_indicators = ['expensive', 'costly', 'premium', 'luxury', 'high-end']
        budget_indicators = ['cheap', 'budget', 'affordable', 'inexpensive', 'free']
        
        expensive_score = sum(1 for indicator in expensive_indicators if indicator in combined_text)
        budget_score = sum(1 for indicator in budget_indicators if indicator in combined_text)
        
        # Determine price category
        if expensive_score > budget_score:
            price_category = 'expensive'
            price_confidence = expensive_score / (expensive_score + budget_score + 1)
        elif budget_score > expensive_score:
            price_category = 'budget'
            price_confidence = budget_score / (expensive_score + budget_score + 1)
        else:
            price_category = 'moderate'
            price_confidence = 0.5
        
        result = {
            'price_category': price_category,
            'price_confidence': price_confidence,
            'expensive_indicators': expensive_score,
            'budget_indicators': budget_score,
            'price_transparency': 'high' if (expensive_score + budget_score) > 2 else 'medium' if (expensive_score + budget_score) > 0 else 'low'
        }
        
        # Add evidence support if available
        if comprehensive_evidence and comprehensive_evidence.get('price_evidence'):
            price_evidence = comprehensive_evidence['price_evidence']
            result['evidence_support'] = {
                'evidence_pieces_count': price_evidence.get('total_evidence_count', 0),
                'evidence_quality': price_evidence.get('average_authority_score', 0),
                'validation_status': price_evidence.get('validation_status', 'pending'),
                'strongest_evidence': self._get_strongest_evidence_text(price_evidence),
                'price_mentions_found': price_evidence.get('total_evidence_count', 0) > 0
            }
        
        return result
    
    async def _add_content_intelligence_attributes(self, enhanced: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Add new content intelligence attributes to the enhanced affinity data"""
        
        theme = enhanced.get('theme', '')
        
        # Get web pages if available
        web_pages = getattr(self, 'web_pages', None)
        
        # Get LLM generator if available
        llm_generator = getattr(self, 'llm_generator', None)
        
        try:
            # Extract content intelligence using the new processor
            content_intelligence = await self.content_intelligence_processor.extract_content_intelligence(
                theme, destination, web_pages, llm_generator
            )
            
            # Add the new attributes to the enhanced data
            enhanced['iconic_landmarks'] = content_intelligence.get('iconic_landmarks', {})
            enhanced['practical_travel_intelligence'] = content_intelligence.get('practical_travel_intelligence', {})
            enhanced['neighborhood_insights'] = content_intelligence.get('neighborhood_insights', {})
            enhanced['content_discovery_intelligence'] = content_intelligence.get('content_discovery_intelligence', {})
            
            logger.debug(f"Added content intelligence attributes for theme: {theme}")
            
        except Exception as e:
            logger.warning(f"Content intelligence extraction failed for {theme}: {e}")
            
            # Add empty attributes as fallback
            enhanced['iconic_landmarks'] = {}
            enhanced['practical_travel_intelligence'] = {}
            enhanced['neighborhood_insights'] = {}
            enhanced['content_discovery_intelligence'] = {}
        
        return enhanced

    def _get_strongest_evidence_text(self, evidence_data: Dict[str, Any]) -> Optional[str]:
        """Extract the strongest evidence text from evidence data."""
        if not evidence_data or not evidence_data.get('evidence_pieces'):
            return None
        
        evidence_pieces = evidence_data['evidence_pieces']
        if not evidence_pieces:
            return None
        
        # Find the piece with highest authority score
        strongest = max(evidence_pieces, key=lambda x: x.get('authority_score', 0))
        return strongest.get('text_content', '')[:200] + '...' if len(strongest.get('text_content', '')) > 200 else strongest.get('text_content', '')

    def _analyze_theme_depth(self, affinity: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Analyze theme depth and granularity."""
        theme = affinity.get('theme', '')
        sub_themes = affinity.get('sub_themes', [])
        rationale = affinity.get('rationale', '')
        
        # Use nano themes from focused prompt processor (LLM-generated)
        nano_themes = affinity.get('nano_themes', [])
        if not nano_themes:
            # Fallback only for LLM failures or missing nano themes
            logger.debug(f"Using fallback nano themes for '{theme}' (LLM generation unavailable)")
            nano_themes = self._generate_nano_themes(theme, sub_themes, rationale)
        else:
            logger.debug(f"Using LLM-generated nano themes for '{theme}': {len(nano_themes)} themes")
        
        # Determine depth level
        if len(nano_themes) >= 3 and len(sub_themes) >= 2:
            depth_level = 'nano'
            depth_score = 1.0
        elif len(sub_themes) >= 2:
            depth_level = 'micro'
            depth_score = 0.7
        else:
            depth_level = 'macro'
            depth_score = 0.4
        
        return {
            'depth_level': depth_level,
            'depth_score': depth_score,
            'nano_themes': nano_themes,
            'theme_specificity': len(rationale.split()) / 50.0,  # Normalized by length
            'sub_theme_count': len(sub_themes)
        }

    def _generate_nano_themes(self, theme: str, sub_themes: List[str], rationale: str) -> List[str]:
        """
        FALLBACK: Generate basic nano-level themes using keyword matching.
        
        This is a fallback method used only when LLM-generated nano themes are unavailable
        due to processing failures. The primary nano theme generation should be done by
        the FocusedPromptProcessor using LLM for destination-specific themes.
        
        Args:
            theme: Main theme name
            sub_themes: List of sub-themes 
            rationale: Theme rationale text
            
        Returns:
            List of basic nano themes (max 4)
        """
        nano_themes = []
        theme_lower = theme.lower()
        rationale_lower = rationale.lower()
        
        # Theme-specific nano theme generation
        if 'food' in theme_lower or 'culinary' in theme_lower:
            nano_themes.extend(['street food markets', 'local family recipes', 'chef-owned restaurants', 'food tours'])
        
        if 'adventure' in theme_lower or 'outdoor' in theme_lower:
            nano_themes.extend(['sunrise hikes', 'technical climbing routes', 'wildlife photography', 'backcountry camping'])
        
        if 'culture' in theme_lower or 'art' in theme_lower:
            nano_themes.extend(['local artist studios', 'traditional craft workshops', 'underground music venues', 'neighborhood galleries'])
        
        if 'nightlife' in theme_lower or 'entertainment' in theme_lower:
            nano_themes.extend(['rooftop cocktail bars', 'jazz speakeasies', 'late-night food scenes', 'live music venues'])
        
        if 'shopping' in theme_lower:
            nano_themes.extend(['artisan markets', 'vintage boutiques', 'local designer shops', 'specialty bookstores'])
        
        # Extract specific mentions from rationale
        if 'museum' in rationale_lower:
            nano_themes.append('specialized museums')
        if 'beach' in rationale_lower:
            nano_themes.append('secluded beach coves')
        if 'mountain' in rationale_lower:
            nano_themes.append('alpine meadow trails')
        
        return list(set(nano_themes[:4]))  # Limit to 4 most relevant

    def _classify_hidden_gem_level(self, uniqueness_score: float) -> str:
        """Classify hidden gem level based on uniqueness score."""
        if uniqueness_score >= 0.8:
            return 'true hidden gem'
        elif uniqueness_score >= 0.6:
            return 'local favorite'
        elif uniqueness_score >= 0.4:
            return 'off the beaten path'
        else:
            return 'mainstream'

    def _analyze_emotional_resonance(self, affinity: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Analyze emotional resonance and appeal."""
        theme = affinity.get('theme', '')
        rationale = affinity.get('rationale', '')
        sub_themes = affinity.get('sub_themes', [])
        text = f"{theme} {rationale} {' '.join(sub_themes)}".lower()
        
        detected_emotions = []
        emotion_scores = {}
        
        for emotion, keywords in self.emotional_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > 0:
                detected_emotions.append(emotion)
                emotion_scores[emotion] = min(1.0, matches / 3.0)  # Normalize
        
        # Default emotion if none detected
        if not detected_emotions:
            theme_lower = theme.lower()
            if 'adventure' in theme_lower:
                detected_emotions.append('exhilarating')
                emotion_scores['exhilarating'] = 0.7
            elif 'culture' in theme_lower:
                detected_emotions.append('contemplative')
                emotion_scores['contemplative'] = 0.7
            elif 'nightlife' in theme_lower:
                detected_emotions.append('social')
                emotion_scores['social'] = 0.7
            elif 'spa' in theme_lower or 'wellness' in theme_lower:
                detected_emotions.append('peaceful')
                emotion_scores['peaceful'] = 0.7
            else:
                detected_emotions.append('inspiring')
                emotion_scores['inspiring'] = 0.5
        
        return {
            'primary_emotions': detected_emotions[:3],
            'emotion_scores': emotion_scores,
            'emotional_variety_score': min(1.0, len(detected_emotions) / 3.0),
            'emotional_intensity': max(emotion_scores.values()) if emotion_scores else 0.5
        }

    def _analyze_experience_intensity(self, affinity: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Analyze experience intensity across dimensions."""
        theme = affinity.get('theme', '')
        rationale = affinity.get('rationale', '')
        text = f"{theme} {rationale}".lower()
        
        # Physical intensity
        physical_intensity = 'low'
        if any(word in text for word in ['extreme', 'climbing', 'hiking', 'demanding']):
            physical_intensity = 'high'
        elif any(word in text for word in ['walking', 'strolling', 'gentle']):
            physical_intensity = 'low'
        elif any(word in text for word in ['active', 'moderate', 'biking']):
            physical_intensity = 'moderate'
        elif any(word in text for word in ['relaxing', 'spa', 'peaceful']):
            physical_intensity = 'minimal'
        
        # Cultural intensity
        cultural_intensity = 'moderate'
        if any(word in text for word in ['immersive', 'deep', 'traditional', 'authentic']):
            cultural_intensity = 'high'
        elif any(word in text for word in ['surface', 'casual', 'brief']):
            cultural_intensity = 'low'
        
        # Social intensity
        social_intensity = 'moderate'
        if any(word in text for word in ['party', 'festival', 'crowded', 'social']):
            social_intensity = 'high'
        elif any(word in text for word in ['solo', 'quiet', 'private', 'peaceful']):
            social_intensity = 'low'
        
        return {
            'physical': physical_intensity,
            'cultural': cultural_intensity,
            'social': social_intensity,
            'overall_intensity': self._calculate_overall_intensity(physical_intensity, cultural_intensity, social_intensity)
        }

    def _calculate_overall_intensity(self, physical: str, cultural: str, social: str) -> str:
        """Calculate overall intensity level."""
        intensity_values = {'minimal': 0, 'low': 1, 'moderate': 2, 'high': 3, 'extreme': 4}
        
        avg_intensity = (intensity_values[physical] + intensity_values[cultural] + intensity_values[social]) / 3
        
        if avg_intensity >= 3.5:
            return 'extreme'
        elif avg_intensity >= 2.5:
            return 'high'
        elif avg_intensity >= 1.5:
            return 'moderate'
        elif avg_intensity >= 0.5:
            return 'low'
        else:
            return 'minimal'

    def _analyze_context(self, affinity: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Analyze contextual information for the affinity."""
        theme = affinity.get('theme', '')
        traveler_types = affinity.get('traveler_types', [])
        
        # Get demographic mapping from config or use defaults
        demographic_config = self.config.get('demographic_mapping', {})
        default_mapping = {
            'family': ['families with children', 'multi-generational groups'],
            'solo': ['solo travelers'],
            'couple': ['couples'],
            'group': ['friend groups']
        }
        demographic_mapping = {**default_mapping, **demographic_config}
        
        # Demographic suitability based on traveler types
        demographics = []
        for traveler_type in traveler_types:
            if traveler_type in demographic_mapping:
                demographics.extend(demographic_mapping[traveler_type])
        
        # Experience level required
        experience_level = self._determine_experience_level(theme)
        
        # Accessibility level
        accessibility = self._determine_accessibility_level(theme)
        
        return {
            'demographic_suitability': demographics,
            'experience_level_required': experience_level,
            'accessibility_level': accessibility,
            'group_dynamics': self._determine_group_dynamics(theme),
            'time_commitment': self._estimate_time_commitment(theme)
        }

    def _determine_experience_level(self, theme: str) -> str:
        """Determine experience level required based on theme."""
        theme_lower = theme.lower()
        
        # Get experience level mapping from config or use defaults
        experience_config = self.config.get('experience_level_keywords', {
            'advanced': ['extreme', 'advanced', 'expert', 'professional'],
            'intermediate': ['intermediate', 'moderate', 'some experience'],
            'beginner': ['beginner', 'easy', 'introductory', 'basic']
        })
        
        for level, keywords in experience_config.items():
            if any(keyword in theme_lower for keyword in keywords):
                return level
        
        return 'beginner'  # Default
    
    def _determine_accessibility_level(self, theme: str) -> str:
        """Determine accessibility level based on theme."""
        theme_lower = theme.lower()
        
        # Get accessibility mapping from config or use defaults
        accessibility_config = self.config.get('accessibility_keywords', {
            'high physical demands': ['extreme', 'strenuous', 'challenging', 'demanding'],
            'requires mobility': ['hiking', 'climbing', 'walking', 'stairs', 'uneven terrain'],
            'accessible': ['accessible', 'wheelchair', 'easy access', 'level ground']
        })
        
        for level, keywords in accessibility_config.items():
            if any(keyword in theme_lower for keyword in keywords):
                return level
        
        return 'accessible'  # Default

    def _determine_group_dynamics(self, theme: str) -> List[str]:
        """Determine suitable group dynamics."""
        theme_lower = theme.lower()
        dynamics = []
        
        if 'nightlife' in theme_lower:
            dynamics.extend(['social groups', 'party atmosphere'])
        elif 'museum' in theme_lower:
            dynamics.extend(['quiet contemplation', 'educational discussions'])
        elif 'adventure' in theme_lower:
            dynamics.extend(['team building', 'shared challenges'])
        elif 'food' in theme_lower:
            dynamics.extend(['social dining', 'shared experiences'])
        else:
            dynamics.append('flexible')
        
        return dynamics

    def _estimate_time_commitment(self, theme: str) -> str:
        """Estimate time commitment for the theme."""
        theme_lower = theme.lower()
        
        if any(word in theme_lower for word in ['tour', 'day trip', 'excursion']):
            return 'full day'
        elif any(word in theme_lower for word in ['museum', 'gallery', 'show']):
            return '2-4 hours'
        elif any(word in theme_lower for word in ['dining', 'restaurant', 'bar']):
            return '1-3 hours'
        elif any(word in theme_lower for word in ['hiking', 'adventure']):
            return '3-8 hours'
        else:
            return 'flexible'

    def _analyze_micro_climate(self, affinity: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Analyze micro-climate and timing factors."""
        theme = affinity.get('theme', '')
        seasonality = affinity.get('seasonality', {})
        theme_lower = theme.lower()
        
        # Best times of day
        best_times = []
        if 'sunrise' in theme_lower or 'morning' in theme_lower:
            best_times.extend(['early morning', 'sunrise'])
        elif 'sunset' in theme_lower or 'evening' in theme_lower:
            best_times.extend(['evening', 'sunset'])
        elif 'nightlife' in theme_lower or 'night' in theme_lower:
            best_times.extend(['night', 'late evening'])
        elif 'photography' in theme_lower:
            best_times.extend(['golden hour', 'blue hour'])
        else:
            best_times.append('flexible')
        
        # Weather dependencies
        weather_deps = []
        if 'outdoor' in theme_lower or 'hiking' in theme_lower:
            weather_deps.extend(['clear weather', 'dry conditions'])
        elif 'beach' in theme_lower:
            weather_deps.extend(['sunny weather', 'calm seas'])
        elif 'snow' in theme_lower or 'skiing' in theme_lower:
            weather_deps.append('snow conditions')
        
        # Crowd patterns
        crowd_patterns = {}
        if 'museum' in theme_lower:
            crowd_patterns = {'weekday mornings': 'low', 'weekend afternoons': 'high'}
        elif 'restaurant' in theme_lower:
            crowd_patterns = {'lunch time': 'moderate', 'dinner time': 'high'}
        elif 'nightlife' in theme_lower:
            crowd_patterns = {'weeknights': 'moderate', 'weekends': 'high'}
        else:
            crowd_patterns = {'weekdays': 'moderate', 'weekends': 'high'}
        
        return {
            'best_time_of_day': best_times,
            'weather_dependencies': weather_deps,
            'crowd_patterns': crowd_patterns,
            'seasonal_variations': seasonality,
            'micro_season_timing': self._extract_micro_season(seasonality)
        }

    def _extract_micro_season(self, seasonality: Dict[str, List[str]]) -> Optional[str]:
        """Extract micro-season timing information."""
        if 'peak' in seasonality and seasonality['peak']:
            months = seasonality['peak']
            if len(months) <= 2:
                return f"Short season: {', '.join(months)}"
            elif 'March' in months and 'April' in months:
                return "Spring bloom period"
            elif 'September' in months and 'October' in months:
                return "Fall foliage season"
        return None

    def _assess_cultural_sensitivity(self, affinity: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Assess cultural sensitivity requirements."""
        theme = affinity.get('theme', '')
        rationale = affinity.get('rationale', '')
        text = f"{theme} {rationale}".lower()
        
        considerations = []
        religious_aware = True
        customs_respected = True
        language_req = None
        
        # Check for religious considerations
        if any(keyword in text for keyword in ['mosque', 'temple', 'church', 'shrine', 'sacred', 'holy']):
            considerations.append("Respect religious customs and dress codes")
            religious_aware = True
        
        # Check for dress code requirements
        if any(keyword in text for keyword in ['modest', 'covered', 'formal', 'traditional dress']):
            considerations.append("Modest dress required")
        
        # Check for custom awareness
        if any(keyword in text for keyword in ['tradition', 'custom', 'protocol', 'etiquette']):
            considerations.append("Learn local customs and etiquette")
        
        # Language requirements
        if any(keyword in text for keyword in ['language', 'translation', 'local language']):
            language_req = "Basic local language helpful"
        
        return {
            'appropriate': True,  # Default to appropriate
            'considerations': considerations,
            'religious_calendar_aware': religious_aware,
            'local_customs_respected': customs_respected,
            'language_requirements': language_req,
            'cultural_immersion_level': self._assess_cultural_immersion(text)
        }

    def _assess_cultural_immersion(self, text: str) -> str:
        """Assess level of cultural immersion required."""
        if any(word in text for word in ['deep', 'immersive', 'traditional', 'authentic']):
            return 'high'
        elif any(word in text for word in ['surface', 'casual', 'tourist']):
            return 'low'
        else:
            return 'moderate'

    def _analyze_theme_interconnections(self, affinity: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Analyze how this theme connects with others."""
        theme = affinity.get('theme', '')
        category = affinity.get('category', '')
        sub_themes = affinity.get('sub_themes', [])
        theme_lower = theme.lower()
        
        # Natural combinations
        combinations = []
        if 'food' in theme_lower:
            combinations.extend(['culture', 'nightlife', 'shopping'])
        elif 'adventure' in theme_lower:
            combinations.extend(['nature', 'photography', 'wellness'])
        elif 'culture' in theme_lower:
            combinations.extend(['food', 'art', 'history'])
        elif 'nightlife' in theme_lower:
            combinations.extend(['food', 'music', 'social'])
        
        # Sequential experiences
        sequences = []
        if 'morning' in theme_lower:
            sequences.append('afternoon relaxation')
        elif 'adventure' in theme_lower:
            sequences.extend(['post-activity dining', 'evening relaxation'])
        elif 'cultural' in theme_lower:
            sequences.append('reflective dining')
        
        # Energy flow
        energy_flow = 'balanced'
        if 'extreme' in theme_lower or 'adventure' in theme_lower:
            energy_flow = 'high-energy'
        elif 'spa' in theme_lower or 'meditation' in theme_lower:
            energy_flow = 'restorative'
        elif 'nightlife' in theme_lower:
            energy_flow = 'evening-peak'
        
        return {
            'natural_combinations': combinations,
            'sequential_experiences': sequences,
            'energy_flow': energy_flow,
            'complementary_activities': self._suggest_complementary_activities(theme_lower),
            'skill_progression': self._assess_skill_progression(theme_lower)
        }

    def _suggest_complementary_activities(self, theme_lower: str) -> List[str]:
        """Suggest complementary activities."""
        if 'food' in theme_lower:
            return ['cooking classes', 'market tours', 'wine tastings']
        elif 'adventure' in theme_lower:
            return ['photography workshops', 'nature walks', 'equipment rental']
        elif 'culture' in theme_lower:
            return ['guided tours', 'local workshops', 'historical walks']
        else:
            return []

    def _assess_skill_progression(self, theme_lower: str) -> Optional[str]:
        """Assess if theme offers skill progression opportunities."""
        if any(word in theme_lower for word in ['class', 'workshop', 'lesson', 'course']):
            return 'learning opportunity'
        elif any(word in theme_lower for word in ['beginner', 'intermediate', 'advanced']):
            return 'skill levels available'
        else:
            return None

    def _generate_intelligence_insights(self, enhanced_affinities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate high-level intelligence insights from enhanced affinities."""
        
        if not enhanced_affinities:
            return {}
        
        # Depth distribution
        depth_levels = [aff['depth_analysis']['depth_level'] for aff in enhanced_affinities]
        depth_distribution = {level: depth_levels.count(level) for level in set(depth_levels)}
        
        # Authenticity distribution
        auth_levels = [aff['authenticity_analysis']['authenticity_level'] for aff in enhanced_affinities]
        auth_distribution = {level: auth_levels.count(level) for level in set(auth_levels)}
        
        # Emotional variety
        all_emotions = set()
        for aff in enhanced_affinities:
            all_emotions.update(aff['emotional_profile']['primary_emotions'])
        
        # Intensity distribution
        intensity_levels = [aff['experience_intensity']['overall_intensity'] for aff in enhanced_affinities]
        intensity_distribution = {level: intensity_levels.count(level) for level in set(intensity_levels)}
        
        # Hidden gems count
        hidden_gems = sum(1 for aff in enhanced_affinities 
                         if aff['hidden_gem_score']['uniqueness_score'] > 0.6)
        
        return {
            'depth_distribution': depth_distribution,
            'authenticity_distribution': auth_distribution,
            'emotional_variety': {
                'total_emotions': len(all_emotions),
                'emotions_covered': list(all_emotions),
                'emotional_coverage_score': min(1.0, len(all_emotions) / 8)
            },
            'intensity_distribution': intensity_distribution,
            'hidden_gems_count': hidden_gems,
            'hidden_gems_ratio': round(hidden_gems / len(enhanced_affinities), 3),
            'average_depth_score': round(sum(aff['depth_analysis']['depth_score'] 
                                           for aff in enhanced_affinities) / len(enhanced_affinities), 3),
            'average_authenticity_score': round(sum(aff['authenticity_analysis']['authenticity_score'] 
                                                  for aff in enhanced_affinities) / len(enhanced_affinities), 3)
        }

    def _analyze_composition(self, enhanced_affinities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the overall composition of themes for balance and flow."""
        
        if not enhanced_affinities:
            return {}
        
        # Energy flow balance
        energy_flows = {}
        for aff in enhanced_affinities:
            flow = aff['theme_interconnections']['energy_flow']
            energy_flows[flow] = energy_flows.get(flow, 0) + 1
        
        total_themes = len(enhanced_affinities)
        energy_balance = {k: round(v / total_themes, 3) for k, v in energy_flows.items()}
        
        # Category diversity
        categories = [aff.get('category', 'unknown') for aff in enhanced_affinities]
        category_distribution = {cat: categories.count(cat) for cat in set(categories)}
        
        # Time commitment distribution
        time_commitments = [aff['contextual_info']['time_commitment'] for aff in enhanced_affinities]
        time_distribution = {time: time_commitments.count(time) for time in set(time_commitments)}
        
        # Social spectrum coverage
        social_coverage = {}
        for aff in enhanced_affinities:
            social_level = aff['experience_intensity']['social']
            social_coverage[social_level] = social_coverage.get(social_level, 0) + 1
        
        # Overall composition score
        composition_score = self._calculate_composition_score(
            energy_balance, category_distribution, time_distribution, social_coverage, total_themes
        )
        
        return {
            'energy_flow_balance': energy_balance,
            'category_distribution': category_distribution,
            'time_commitment_distribution': time_distribution,
            'social_intensity_distribution': social_coverage,
            'overall_composition_score': composition_score,
            'composition_quality': self._assess_composition_quality(composition_score),
            'balance_recommendations': self._generate_balance_recommendations(
                energy_balance, category_distribution, social_coverage
            )
        }

    def _calculate_composition_score(self, energy_balance: Dict[str, float], 
                                   category_distribution: Dict[str, int],
                                   time_distribution: Dict[str, int],
                                   social_coverage: Dict[str, int], 
                                   total_themes: int) -> float:
        """Calculate overall composition score."""
        
        # Energy variety (better if more balanced)
        energy_variety = 1.0 if len(energy_balance) > 1 else 0.5
        
        # Category variety (better with more categories)
        category_variety = min(1.0, len(category_distribution) / 6)  # Assuming 6 main categories
        
        # Time variety (better with different time commitments)
        time_variety = min(1.0, len(time_distribution) / 4)  # 4 main time categories
        
        # Social variety (better with different social levels)
        social_variety = min(1.0, len(social_coverage) / 4)  # 4 social intensity levels
        
        # Weighted combination
        composition_score = (
            energy_variety * 0.3 +
            category_variety * 0.3 +
            time_variety * 0.2 +
            social_variety * 0.2
        )
        
        return round(composition_score, 3)

    def _assess_composition_quality(self, score: float) -> str:
        """Assess composition quality level."""
        if score >= 0.8:
            return 'excellent'
        elif score >= 0.6:
            return 'good'
        elif score >= 0.4:
            return 'acceptable'
        else:
            return 'needs improvement'

    def _generate_balance_recommendations(self, energy_balance: Dict[str, float],
                                        category_distribution: Dict[str, int],
                                        social_coverage: Dict[str, int]) -> List[str]:
        """Generate recommendations for better balance."""
        recommendations = []
        
        # Check energy balance
        if len(energy_balance) == 1:
            recommendations.append("Add themes with different energy levels for better balance")
        
        # Check category diversity
        if len(category_distribution) < 4:
            recommendations.append("Include more diverse activity categories")
        
        # Check social coverage
        if len(social_coverage) < 3:
            recommendations.append("Add themes with varying social intensity levels")
        
        # Check for over-concentration
        max_category_count = max(category_distribution.values()) if category_distribution else 0
        if max_category_count > len(category_distribution) * 0.5:
            recommendations.append("Reduce concentration in dominant categories")
        
        return recommendations

    def _generate_qa_workflow(self, quality_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate QA workflow based on quality assessment."""
        
        overall_score = quality_assessment.get('overall_score', 0.0)
        quality_level = quality_assessment.get('quality_level', 'Unknown')
        
        # Determine workflow path
        if overall_score >= 0.85:
            workflow_path = 'auto_approve'
            review_required = False
            priority = 'low'
        elif overall_score >= 0.75:
            workflow_path = 'light_review'
            review_required = True
            priority = 'low'
        elif overall_score >= 0.65:
            workflow_path = 'standard_review'
            review_required = True
            priority = 'medium'
        else:
            workflow_path = 'detailed_review'
            review_required = True
            priority = 'high'
        
        return {
            'workflow_path': workflow_path,
            'review_required': review_required,
            'priority': priority,
            'quality_level': quality_level,
            'overall_score': overall_score,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending_review' if review_required else 'approved',
            'reviewer_notes': quality_assessment.get('recommendations', [])
        }

    def _save_to_json(self, data: Dict[str, Any], output_file: str) -> None:
        """Save enhanced data to JSON file."""
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Enhanced data saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving enhanced data to {output_path}: {e}")
            raise 