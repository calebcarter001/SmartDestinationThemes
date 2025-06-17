#!/usr/bin/env python3
"""
Enhanced Data Processor with Progress Tracking
Adds tqdm progress bars and timestamped output organization to the intelligence processing pipeline.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from tqdm import tqdm

from src.enhanced_data_processor import EnhancedDataProcessor
from src.enhanced_viewer_generator import EnhancedViewerGenerator

logger = logging.getLogger(__name__)

class EnhancedDataProcessorWithProgress(EnhancedDataProcessor):
    """Enhanced data processor with progress tracking and organized output management."""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_output_dir = "outputs"
        self.session_output_dir = os.path.join(self.base_output_dir, f"session_{self.session_timestamp}")
        
        # Create session output directory
        os.makedirs(self.session_output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.session_output_dir, "json"), exist_ok=True)
        os.makedirs(os.path.join(self.session_output_dir, "dashboard"), exist_ok=True)
        
        logger.info(f"Session output directory: {self.session_output_dir}")
    
    def process_destinations_with_progress(self, destinations_data: Dict[str, Any], 
                                         generate_dashboard: bool = True) -> Dict[str, str]:
        """
        Process multiple destinations with progress tracking and organized output.
        
        Args:
            destinations_data: Dictionary of destination name -> destination data
            generate_dashboard: Whether to generate HTML dashboard
            
        Returns:
            Dictionary of destination name -> output file path
        """
        
        print(f"\n🚀 Processing {len(destinations_data)} destinations with Enhanced Intelligence")
        print(f"📁 Session output directory: {self.session_output_dir}")
        print("="*70)
        
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
                # Process single destination with progress
                enhanced_data = self._process_single_destination_with_progress(
                    destination_data, destination_name
                )
                
                # Save enhanced JSON
                json_filename = f"{self._sanitize_filename(destination_name)}_enhanced.json"
                json_filepath = os.path.join(self.session_output_dir, "json", json_filename)
                
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
                                                destination_name: str) -> Dict[str, Any]:
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
                    affinity, destination_name, affinity_progress
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
        enhanced_destination_data['qa_workflow'] = self._generate_qa_workflow(enhanced_destination_data)
        
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
                                             parent_progress: tqdm) -> Dict[str, Any]:
        """Enhance a single affinity with detailed progress tracking."""
        
        # Intelligence processing steps - using parent class methods
        intelligence_steps = [
            ("🔍 Depth Analysis", lambda a, d: self._analyze_theme_depth(a)),
            ("🏆 Authenticity Scoring", lambda a, d: self._analyze_authenticity(a)),
            ("✨ Emotional Profiling", lambda a, d: self._analyze_emotional_resonance(a)),
            ("⚡ Intensity Calibration", lambda a, d: self._analyze_experience_intensity(a)),
            ("🎯 Context Analysis", lambda a, d: self._analyze_context(a, d)),
            ("🌤️ Micro-Climate", lambda a, d: self._analyze_micro_climate(a, d)),
            ("🏛️ Cultural Sensitivity", lambda a, d: self._assess_cultural_sensitivity(a, d)),
            ("🔗 Interconnections", lambda a, d: self._analyze_theme_interconnections(a)),
            ("💎 Hidden Gem Detection", lambda a, d: self._calculate_hidden_gem_score(a))
        ]
        
        enhanced_affinity = affinity.copy()
        
        # Process each intelligence layer
        for step_name, step_function in intelligence_steps:
            try:
                parent_progress.set_postfix_str(step_name)
                result = step_function(affinity, destination_name)
                
                # Map results to affinity fields
                if "Depth" in step_name:
                    enhanced_affinity['depth_analysis'] = result
                elif "Authenticity" in step_name:
                    enhanced_affinity['authenticity_analysis'] = result
                elif "Emotional" in step_name:
                    enhanced_affinity['emotional_profile'] = result
                elif "Intensity" in step_name:
                    enhanced_affinity['experience_intensity'] = result
                elif "Context" in step_name:
                    enhanced_affinity['contextual_info'] = result
                elif "Micro-Climate" in step_name:
                    enhanced_affinity['micro_climate'] = result
                elif "Cultural" in step_name:
                    enhanced_affinity['cultural_sensitivity'] = result
                elif "Interconnections" in step_name:
                    enhanced_affinity['theme_interconnections'] = result
                elif "Hidden Gem" in step_name:
                    enhanced_affinity['hidden_gem_score'] = result
                    
            except Exception as e:
                logger.error(f"Error in {step_name} for {affinity.get('theme', 'Unknown')}: {e}")
        
        # Clear postfix
        parent_progress.set_postfix_str("")
        
        return enhanced_affinity
    
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