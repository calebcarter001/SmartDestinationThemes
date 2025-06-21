#!/usr/bin/env python3
"""
Enhanced Viewer Generator for SmartDestinationThemes
Creates individual HTML files for each destination with rich intelligence data display.
Much simpler and more modular than the original approach.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
import logging
import hashlib

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class EnhancedViewerGenerator:
    """Generates individual HTML files for enhanced destination intelligence data."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        
    def generate_destination_viewer(self, json_file: str, output_dir: str = "enhanced_dashboard"):
        """Generate HTML viewer for a single destination JSON file."""
        
        # Load the enhanced data
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"❌ JSON file {json_file} not found")
            return False
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in {json_file}")
            return False
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Set current file for evidence loading
        self._current_json_file = json_file
        
        # Generate HTML for this destination
        destination_name = data.get('destination', data.get('destination_name', 'Unknown Destination'))
        html_content = self._generate_destination_html(data)
        
        # Create filename
        safe_name = self._sanitize_filename(destination_name)
        html_file = os.path.join(output_dir, f"{safe_name}.html")
        
        try:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ Generated enhanced viewer: {html_file}")
            return html_file
        except Exception as e:
            print(f"❌ Error writing HTML file: {e}")
            return False
    
    def generate_multi_destination_viewer(self, json_files: list, output_dir: str = "enhanced_dashboard"):
        """Generate HTML viewers for multiple destination JSON files and create an index."""
        
        generated_files = []
        destination_data = {}
        
        # Generate individual destination files
        for json_file in json_files:
            try:
                # Skip evidence files (they contain lists, not destination data)
                if json_file.endswith('_evidence.json'):
                    print(f"⏭️ Skipping evidence file: {json_file}")
                    continue
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Skip if data is not a dictionary (safety check)
                if not isinstance(data, dict):
                    print(f"⏭️ Skipping non-dictionary data in: {json_file}")
                    continue
                
                # Set current file for evidence loading
                self._current_json_file = json_file
                
                destination_name = data.get('destination', data.get('destination_name', 'Unknown Destination'))
                sanitized_name = self._sanitize_filename(destination_name)
                
                # Generate destination HTML
                html_content = self._generate_destination_html(data)
                
                # Save HTML file
                html_filename = f"{sanitized_name}.html"
                html_filepath = os.path.join(output_dir, html_filename)
                
                with open(html_filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                generated_files.append(html_filepath)
                destination_data[destination_name] = {
                    'html_file': html_filename,
                    'data': data
                }
                
                print(f"✅ Generated enhanced viewer: {html_filepath}")
                
            except Exception as e:
                print(f"❌ Error processing {json_file}: {e}")
        
        # Generate index page
        if destination_data:
            index_html = self._generate_index_html(destination_data)
            index_file = os.path.join(output_dir, "index.html")
            
            try:
                with open(index_file, 'w', encoding='utf-8') as f:
                    f.write(index_html)
                print(f"✅ Generated index page: {index_file}")
            except Exception as e:
                print(f"❌ Error writing index file: {e}")
        
        return generated_files
    
    def _generate_destination_html(self, data: Dict[str, Any]) -> str:
        """Generate complete HTML for a destination."""
        
        # Load evidence data if separate evidence file exists
        evidence_data = {}
        evidence_file_ref = data.get('evidence_file_reference')
        if evidence_file_ref:
            # Try to load evidence file from same directory as main JSON
            try:
                import os
                json_dir = os.path.dirname(getattr(self, '_current_json_file', ''))
                evidence_file_path = os.path.join(json_dir, evidence_file_ref)
                if os.path.exists(evidence_file_path):
                    with open(evidence_file_path, 'r', encoding='utf-8') as f:
                        import json
                        evidence_data = json.load(f)
                        logger.info(f"Loaded evidence data from {evidence_file_path}")
            except Exception as e:
                logger.warning(f"Could not load evidence file {evidence_file_ref}: {e}")
        
        # Load destination nuances data (NEW) - prioritize 3-tier system
        nuances_data = {}
        try:
            import os
            json_dir = os.path.dirname(getattr(self, '_current_json_file', ''))
            # Extract base filename (without _enhanced.json) to construct nuances filename
            base_name = os.path.basename(getattr(self, '_current_json_file', ''))
            if base_name.endswith('_enhanced.json'):
                base_name = base_name[:-14]  # Remove '_enhanced.json'
                
                # Try 3-tier files first (prioritized)
                tier_files = [
                    f"{base_name}_nuances_3tier_updated.json",
                    f"{base_name}_nuances_3tier.json",
                    f"{base_name}_nuances.json"  # Legacy fallback
                ]
                
                for tier_file in tier_files:
                    nuances_file_path = os.path.join(json_dir, tier_file)
                    if os.path.exists(nuances_file_path):
                        with open(nuances_file_path, 'r', encoding='utf-8') as f:
                            import json
                            nuances_data = json.load(f)
                            logger.info(f"Loaded nuances data from {nuances_file_path}")
                            break
        except Exception as e:
            logger.warning(f"Could not load nuances file: {e}")
        
        # Load destination nuances if separate nuances file exists (NEW)
        nuances_evidence_data = {}
        try:
            import os
            json_dir = os.path.dirname(getattr(self, '_current_json_file', ''))
            
            # Try to find nuances file based on current JSON file name
            if hasattr(self, '_current_json_file'):
                base_name = os.path.basename(self._current_json_file)
                if base_name.endswith('_enhanced.json'):
                    base_name = base_name[:-14]  # Remove '_enhanced.json'
                    
                    # Try 3-tier evidence files first (prioritized)
                    evidence_files = [
                        f"{base_name}_nuances_3tier_updated_evidence.json",
                        f"{base_name}_nuances_3tier_evidence.json",
                        f"{base_name}_nuances_evidence.json"  # Legacy fallback
                    ]
                    
                    for evidence_file in evidence_files:
                        nuances_file_path = os.path.join(json_dir, evidence_file)
                        if os.path.exists(nuances_file_path):
                            with open(nuances_file_path, 'r', encoding='utf-8') as f:
                                nuances_evidence_data = json.load(f)
                                # Store for JavaScript access
                                self._nuances_evidence_data = nuances_evidence_data
                                logger.info(f"Loaded nuances evidence from {nuances_file_path}")
                                break
        except Exception as e:
            logger.warning(f"Could not load nuances files: {e}")
        
        destination_name = data.get('destination', data.get('destination_name', 'Unknown Destination'))
        affinities = data.get('affinities', [])
        
        # Merge evidence back into affinities for display
        theme_evidence = evidence_data.get('theme_evidence', {})
        for affinity in affinities:
            theme_name = affinity.get('theme', 'Unknown')
            if theme_name in theme_evidence:
                affinity['comprehensive_attribute_evidence'] = theme_evidence[theme_name]
        
        intelligence_insights = data.get('intelligence_insights', {})
        composition_analysis = data.get('composition_analysis', {})
        qa_workflow = data.get('qa_workflow', {})
        comprehensive_evidence = data.get('comprehensive_evidence', {})
        
        # If no top-level comprehensive evidence, aggregate from themes
        if not comprehensive_evidence and affinities:
            comprehensive_evidence = self._aggregate_evidence_from_themes(affinities)
        
        # Get destination nuances summary (NEW)
        nuances_summary = data.get('destination_nuances_summary', {})
        
        # Quality metrics - get from intelligence_insights.quality_assessment
        quality_assessment = intelligence_insights.get('quality_assessment', {})
        quality_score = quality_assessment.get('overall_score', 0)
        quality_level = quality_assessment.get('quality_level', 'Unknown')
        
        # Intelligence insights
        hidden_gems_count = intelligence_insights.get('hidden_gems_count', 0)
        hidden_gems_ratio = intelligence_insights.get('hidden_gems_ratio', 0)
        avg_authenticity = intelligence_insights.get('average_authenticity_score', 0)
        avg_depth = intelligence_insights.get('average_depth_score', 0)
        emotional_variety = intelligence_insights.get('emotional_variety', {})
        emotions_covered = emotional_variety.get('emotions_covered', [])
        
        # Generate enhanced theme cards
        themes_html = self._generate_enhanced_themes(affinities)
        
        # Generate destination nuances display (NEW)
        nuances_html = self._generate_destination_nuances(nuances_data, nuances_evidence_data, nuances_summary)
        
        # Generate intelligence insights cards
        insights_html = self._generate_intelligence_insights(intelligence_insights)
        
        # Generate nuance intelligence insights (NEW - separate from themes)
        nuance_insights_html = self._generate_nuance_intelligence_insights(nuances_data, nuances_evidence_data)
        
        # Generate composition analysis
        composition_html = self._generate_composition_analysis(composition_analysis)
        
        # Generate destination insight analysis for nuances (NEW - separate from themes)
        nuance_insight_analysis_html = self._generate_nuance_insight_analysis(nuances_data)
        
        # Generate quality metrics
        quality_html = self._generate_quality_metrics(quality_assessment, nuances_data)
        
        # Generate nuance quality assessment (NEW - separate from themes)
        nuance_quality_html = self._generate_nuance_quality_assessment(nuances_data)
        
        # Generate comprehensive evidence display
        # Check if we have nuances evidence data to display instead of theme evidence
        if nuances_evidence_data:
            # Handle both list and dict formats for nuances evidence
            if isinstance(nuances_evidence_data, list):
                # List format - check if it has content
                has_evidence = bool(nuances_evidence_data)
            else:
                # Dict format - check for evidence key or any values
                has_evidence = bool('evidence' in nuances_evidence_data or any(nuances_evidence_data.values()))
            
            if has_evidence:
                evidence_html = self._generate_comprehensive_evidence_display(nuances_evidence_data)
            else:
                evidence_html = self._generate_comprehensive_evidence_display(comprehensive_evidence)
        else:
            evidence_html = self._generate_comprehensive_evidence_display(comprehensive_evidence)
        
        # Add nuances count and quality to header stats (NEW) - supports all formats
        nuances_count = 0
        nuances_quality = 0
        if nuances_data:
            # Check for old 3-tier system first (separate arrays)
            if 'destination_nuances' in nuances_data or 'hotel_expectations' in nuances_data or 'vacation_rental_expectations' in nuances_data:
                nuances_count += len(nuances_data.get('destination_nuances', []))
                nuances_count += len(nuances_data.get('hotel_expectations', []))
                nuances_count += len(nuances_data.get('vacation_rental_expectations', []))
                nuances_quality = nuances_data.get('overall_nuance_quality_score', nuances_data.get('overall_quality_score', 0))
            # Check for current unified format (single array with categories)
            elif 'nuances' in nuances_data:
                nuances_list = nuances_data.get('nuances', [])
                nuances_count = len(nuances_list)
                # Get quality score from data structure or calculate from individual scores
                nuances_quality = nuances_data.get('quality_score', 0)
                if nuances_quality == 0:
                    nuances_quality = nuances_data.get('overall_quality_score', 0)
                if nuances_quality == 0 and nuances_list:
                    nuances_quality = sum(n.get('score', 0) for n in nuances_list) / len(nuances_list)
            # Also check enhanced JSON summary
            elif 'destination_nuances_summary' in data and data['destination_nuances_summary'].get('3_tier_system'):
                summary = data['destination_nuances_summary']
                nuances_count = summary.get('total_nuances_count', 0)
                nuances_quality = summary.get('overall_quality_score', 0)
        
        # Generate seasonal image carousel HTML
        seasonal_carousel_html = self._generate_seasonal_carousel(destination_name)

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{destination_name} - Destination Insights Discovery</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        {self._get_enhanced_css()}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Section -->
        <header class="destination-header">
            <div class="header-top">
                <a href="index.html" class="back-button">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </a>
            </div>
            
            <!-- Seasonal Image Carousel -->
            {seasonal_carousel_html}
            
            <div class="header-content">
                <h1 class="destination-title">{destination_name}</h1>
                <div class="quality-badge quality-{quality_level.lower().replace(' ', '-')}">
                    Destination Insights: {quality_level} ({quality_score:.3f})
                </div>
            </div>
            <div class="header-stats">
                <div class="stat-card">
                    <div class="stat-value">{len(affinities)}</div>
                    <div class="stat-label">Destination Themes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{hidden_gems_count}</div>
                    <div class="stat-label">Hidden Gems</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{avg_authenticity:.2f}</div>
                    <div class="stat-label">Authenticity</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(emotions_covered)}</div>
                    <div class="stat-label">Emotion Types</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{nuances_count}</div>
                    <div class="stat-label">Destination Nuances</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{nuances_quality:.3f}</div>
                    <div class="stat-label">Nuances Quality</div>
                </div>
            </div>
        </header>
        
        <!-- Intelligence Insights Section -->
        <section class="intelligence-insights">
            <h2><i class="fas fa-brain"></i> Intelligence Insights</h2>
            <div class="insights-tab-content">
                <div id="theme-insights" class="insights-content active">
                    {insights_html}
                </div>
                <div id="nuance-insights" class="insights-content">
                    {nuance_insights_html}
                </div>
            </div>
        </section>
        
        <!-- Tabbed Content Section for Themes and Nuances -->
        <section class="tabbed-content-section">
            <div class="tab-navigation">
                <button class="tab-button active" onclick="switchTab('themes')" id="themes-tab">
                    <i class="fas fa-sparkles"></i> Destination Themes ({len(affinities)})
                </button>
                <button class="tab-button" onclick="switchTab('nuances')" id="nuances-tab">
                    <i class="fas fa-star"></i> Destination Nuances ({nuances_count})
                </button>
            </div>
            
            <div class="tab-content">
                <div id="themes-pane" class="tab-pane active">
                    <div class="themes-container">
                        <div class="section-description">
                            <p>These are enhanced destination themes discovered through intelligent analysis. Each theme has been enhanced with depth analysis, authenticity scoring, and comprehensive evidence validation.</p>
                        </div>
                        {themes_html}
                    </div>
                </div>
                
                <div id="nuances-pane" class="tab-pane">
                    <div class="nuances-container">
                        <div class="section-description">
                            <p>Three distinct categories: Destination Nuances (fun experiences), Conventional Lodging Nuances (hotel/motel expectations), and Vacation Rental Nuances.</p>
                        </div>
                        {nuances_html}
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Destination Insight Analysis Section -->
        <section class="destination-insight-analysis">
            <h2><i class="fas fa-palette"></i> Destination Insight Analysis</h2>
            <div class="insights-tab-content">
                <div id="theme-composition" class="insights-content active">
                    {composition_html}
                </div>
                <div id="nuance-analysis" class="insights-content">
                    {nuance_insight_analysis_html}
                </div>
            </div>
        </section>
        
        <!-- Quality Assessment Section -->
        <section class="quality-assessment">
            <h2><i class="fas fa-chart-line"></i> Quality Assessment</h2>
            <div class="quality-tab-content">
                <div id="theme-quality" class="quality-content active">
                    {quality_html}
                </div>
                <div id="nuance-quality" class="quality-content">
                    {nuance_quality_html}
                </div>
            </div>
        </section>
        
        <!-- Comprehensive Evidence Section -->
        <section class="comprehensive-evidence">
            <h2><i class="fas fa-database"></i> Evidence Collection</h2>
            {evidence_html}
        </section>
        
        <!-- Footer -->
        <footer class="dashboard-footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Destination Insights Discovery</p>
        </footer>
    </div>
    
    <!-- Evidence Modal -->
    <div id="evidenceModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Evidence Details</h2>
                <span class="close" onclick="closeEvidenceModal()">&times;</span>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- Evidence content will be inserted here -->
            </div>
        </div>
    </div>
    
    <script>
        // Initialize global evidence store
        window.evidenceStore = {self._get_evidence_store_json()};
        console.log('Evidence store initialized with', Object.keys(window.evidenceStore).length, 'items');
        
        // Initialize nuances evidence data for enhanced modal support
        window.nuancesEvidenceData = {self._get_nuances_evidence_json()};
        console.log('Nuances evidence data initialized with', Object.keys(window.nuancesEvidenceData).length, 'evidence items');
        
        {self._get_enhanced_javascript()}
    </script>
</body>
</html>
        """
    
    def _generate_enhanced_themes(self, affinities: list) -> str:
        """Generate HTML for enhanced theme cards with proper grid layout."""
        if not affinities:
            return '<p class="no-data">No destination themes available.</p>'
        
        themes_html = ""
        for theme in affinities:
            themes_html += self._generate_single_theme_card(theme)
        
        return f'<div class="themes-grid">{themes_html}</div>'
    
    def _generate_single_theme_card(self, theme: dict) -> str:
        """Generate HTML for a single enhanced theme card."""
        
        # Basic theme info
        theme_name = theme.get('theme', 'Unknown Theme')
        category = theme.get('category', 'general')
        confidence = theme.get('confidence', 0)
        rationale = theme.get('rationale', 'No rationale provided')
        
        # Get theme quality from processing metadata
        processing_metadata = theme.get('processing_metadata', {})
        theme_quality_score = processing_metadata.get('quality_score', confidence)
        
        # Enhanced intelligence data
        depth_analysis = theme.get('depth_analysis', {})
        authenticity_analysis = theme.get('authenticity_analysis', {})
        emotional_profile = theme.get('emotional_profile', {})
        experience_intensity = theme.get('experience_intensity', {})
        contextual_info = theme.get('contextual_info', {})
        hidden_gem_score = theme.get('hidden_gem_score', {})
        
        # Generate intelligence badges
        badges_html = self._generate_intelligence_badges(
            depth_analysis, authenticity_analysis, emotional_profile, 
            experience_intensity, hidden_gem_score
        )
        
        # Generate evidence validation display
        # Check for content intelligence evidence first
        content_evidence_summary = self._create_content_intelligence_evidence_summary(theme)
        evidence_summary = theme.get('evidence_summary', content_evidence_summary)
        evidence_html = self._generate_evidence_validation_display(evidence_summary)
        
        # Generate enhanced details
        details_html = self._generate_theme_details(
            theme, depth_analysis, contextual_info, theme.get('micro_climate', {}),
            theme.get('cultural_sensitivity', {}), theme.get('theme_interconnections', {})
        )
        
        # Generate content intelligence display
        content_intelligence_html = self._generate_content_intelligence_display(theme)
        
        confidence_color = self._get_confidence_color(theme_quality_score)
        quality_level = self._get_quality_level(theme_quality_score)
        
        return f"""
        <div class="theme-card enhanced-theme">
            <div class="theme-header">
                <div class="theme-title-section">
                    <h3 class="theme-title">{theme_name} {self._generate_evidence_paperclip(theme_name, theme)}</h3>
                    <span class="theme-category">{category}</span>
                    <span class="theme-quality-badge quality-{quality_level.lower().replace(' ', '-')}">{quality_level}</span>
                </div>
                <div class="confidence-score" style="background: {confidence_color}">
                    {theme_quality_score:.3f}
                </div>
            </div>
            
            <div class="intelligence-badges">
                {badges_html}
            </div>
            
            <div class="evidence-validation">
                {evidence_html}
            </div>
            
            <div class="theme-rationale">
                <p>{rationale}</p>
            </div>
            
            <div class="theme-details">
                {details_html}
            </div>
            
            <div class="content-intelligence-section">
                {content_intelligence_html}
            </div>
        </div>
        """
    
    def _generate_intelligence_badges(self, depth_analysis, authenticity_analysis, 
                                    emotional_profile, experience_intensity, hidden_gem_score) -> str:
        """Generate intelligence badges for a theme."""
        badges = []
        
        # Depth badge
        depth_level = depth_analysis.get('depth_level', 'macro')
        depth_score = depth_analysis.get('depth_score', 0)
        depth_color = '#28a745' if depth_score > 0.8 else '#ffc107' if depth_score > 0.6 else '#6c757d'
        badges.append(f'<span class="badge" style="background: {depth_color}">📊 {depth_level.title()}</span>')
        
        # Authenticity badge
        auth_level = authenticity_analysis.get('authenticity_level', 'balanced')
        auth_score = authenticity_analysis.get('authenticity_score', 0)
        auth_color = '#28a745' if auth_score > 0.8 else '#17a2b8' if auth_score > 0.6 else '#6c757d'
        auth_icon = '🏆' if auth_level == 'authentic_local' else '🌟' if auth_level == 'local_influenced' else '⚖️'
        badges.append(f'<span class="badge" style="background: {auth_color}" title="{auth_score:.2f}">{auth_icon} {auth_level.replace("_", " ").title()}</span>')
        
        # Hidden gem badge
        gem_level = hidden_gem_score.get('hidden_gem_level', 'mainstream')
        if gem_level == 'true hidden gem':
            badges.append('<span class="badge" style="background: #dc3545">💎 Hidden Gem</span>')
        elif gem_level == 'local favorite':
            badges.append('<span class="badge" style="background: #fd7e14">⭐ Local Favorite</span>')
        elif gem_level == 'off the beaten path':
            badges.append('<span class="badge" style="background: #20c997">🗺️ Off Beaten Path</span>')
        
        # Experience intensity badge
        intensity = experience_intensity.get('overall_intensity', 'moderate')
        intensity_colors = {'extreme': '#dc3545', 'high': '#fd7e14', 'moderate': '#ffc107', 'low': '#28a745', 'minimal': '#6c757d'}
        intensity_icons = {'extreme': '🔥', 'high': '🔥', 'moderate': '⚡', 'low': '🌱', 'minimal': '🌱'}
        color = intensity_colors.get(intensity, '#6c757d')
        icon = intensity_icons.get(intensity, '⚡')
        badges.append(f'<span class="badge" style="background: {color}">{icon} {intensity.title()}</span>')
        
        # Emotional badges
        emotions = emotional_profile.get('primary_emotions', [])
        if emotions:
            emotion_icons = {'peaceful': '😊', 'exhilarating': '🎯', 'contemplative': '🧘', 'inspiring': '✨', 'social': '👥', 'challenging': '💪'}
            for emotion in emotions[:2]:  # Show max 2 emotions
                icon = emotion_icons.get(emotion, '✨')
                badges.append(f'<span class="badge" style="background: #6f42c1">{icon} {emotion.title()}</span>')
        
        return ''.join(badges)
    
    def _generate_content_intelligence_display(self, theme: dict) -> str:
        """Generate display for new content intelligence attributes."""
        
        # Get the new content intelligence attributes
        iconic_landmarks = theme.get('iconic_landmarks', {})
        practical_intelligence = theme.get('practical_travel_intelligence', {})
        neighborhood_insights = theme.get('neighborhood_insights', {})
        content_discovery = theme.get('content_discovery_intelligence', {})
        
        # Only show if we have some content intelligence data
        if not any([iconic_landmarks, practical_intelligence, neighborhood_insights, content_discovery]):
            return ""
        
        sections = []
        
        # Iconic Landmarks Section
        if iconic_landmarks and iconic_landmarks.get('specific_locations'):
            landmarks_html = self._generate_landmarks_section(iconic_landmarks)
            sections.append(landmarks_html)
        
        # Practical Intelligence Section
        if practical_intelligence and (practical_intelligence.get('specific_costs') or practical_intelligence.get('timing_intelligence')):
            practical_html = self._generate_practical_section(practical_intelligence)
            sections.append(practical_html)
        
        # Neighborhood Insights Section
        if neighborhood_insights and neighborhood_insights.get('neighborhood_names'):
            neighborhood_html = self._generate_neighborhood_section(neighborhood_insights)
            sections.append(neighborhood_html)
        
        # Content Discovery Section
        if content_discovery and content_discovery.get('high_quality_sources'):
            discovery_html = self._generate_discovery_section(content_discovery)
            sections.append(discovery_html)
        
        if not sections:
            return ""
        
        return f"""
        <div class="content-intelligence">
            <div class="ci-toggle" onclick="toggleContentIntelligence(this)">
                <span class="toggle-icon">▼</span> Content Intelligence
                <span class="ci-badge">{len(sections)} insights</span>
            </div>
            <div class="ci-content" style="display: none;">
                {''.join(sections)}
            </div>
        </div>
        """
    
    def _create_content_intelligence_evidence_summary(self, theme: dict) -> dict:
        """Create evidence summary for content intelligence attributes."""
        # Get content intelligence attributes
        iconic_landmarks = theme.get('iconic_landmarks', {})
        practical_intelligence = theme.get('practical_travel_intelligence', {})
        neighborhood_insights = theme.get('neighborhood_insights', {})
        content_discovery = theme.get('content_discovery_intelligence', {})
        
        # Check if we have any content intelligence data
        has_landmarks = bool(iconic_landmarks and iconic_landmarks.get('specific_locations'))
        has_practical = bool(practical_intelligence and (practical_intelligence.get('specific_costs') or practical_intelligence.get('timing_intelligence')))
        has_neighborhoods = bool(neighborhood_insights and neighborhood_insights.get('neighborhood_names'))
        has_discovery = bool(content_discovery and content_discovery.get('high_quality_sources'))
        
        if not any([has_landmarks, has_practical, has_neighborhoods, has_discovery]):
            return {}
        
        # Count evidence pieces
        evidence_count = 0
        unique_sources = 0
        
        # Count from landmarks
        if has_landmarks:
            evidence_count += len(iconic_landmarks.get('specific_locations', []))
            evidence_count += len(iconic_landmarks.get('what_makes_them_special', []))
        
        # Count from practical intelligence
        if has_practical:
            evidence_count += len(practical_intelligence.get('specific_costs', {}))
            evidence_count += len(practical_intelligence.get('timing_intelligence', {}))
            evidence_count += len(practical_intelligence.get('practical_tips', []))
        
        # Count from neighborhoods
        if has_neighborhoods:
            evidence_count += len(neighborhood_insights.get('neighborhood_names', []))
            evidence_count += len(neighborhood_insights.get('area_personalities', {}))
        
        # Count from content discovery
        if has_discovery:
            sources = content_discovery.get('high_quality_sources', [])
            evidence_count += len(sources)
            unique_sources = len(set(sources))  # Unique sources
        
        # Create evidence pieces for display
        evidence_pieces = []
        
        # Add landmark evidence
        if has_landmarks:
            for location in iconic_landmarks.get('specific_locations', [])[:2]:
                description = iconic_landmarks.get('landmark_descriptions', {}).get(location, '')
                evidence_pieces.append({
                    'text_content': f"Iconic landmark: {location}. {description}",
                    'source_url': '#',
                    'source_title': 'Content Intelligence',
                    'authority_score': 0.8,
                    'quality_rating': 'good',
                    'source_type': 'content_intelligence'
                })
        
        # Add practical evidence
        if has_practical:
            for category, cost in list(practical_intelligence.get('specific_costs', {}).items())[:2]:
                evidence_pieces.append({
                    'text_content': f"Cost insight: {category} - {cost}",
                    'source_url': '#',
                    'source_title': 'Content Intelligence',
                    'authority_score': 0.9,
                    'quality_rating': 'excellent',
                    'source_type': 'content_intelligence'
                })
        
        # Add neighborhood evidence
        if has_neighborhoods:
            for neighborhood in neighborhood_insights.get('neighborhood_names', [])[:2]:
                personality = neighborhood_insights.get('area_personalities', {}).get(neighborhood, '')
                evidence_pieces.append({
                    'text_content': f"Neighborhood insight: {neighborhood}. {personality}",
                    'source_url': '#',
                    'source_title': 'Content Intelligence',
                    'authority_score': 0.7,
                    'quality_rating': 'good',
                    'source_type': 'content_intelligence'
                })
        
        # Calculate summary metrics
        total_attributes = sum([has_landmarks, has_practical, has_neighborhoods, has_discovery])
        average_authority = 0.8  # Default authority for content intelligence
        validation_confidence = min(1.0, total_attributes / 4.0)  # Based on completeness
        
        # Determine validation status
        if total_attributes >= 3:
            validation_status = 'validated'
        elif total_attributes >= 2:
            validation_status = 'partially_validated'
        else:
            validation_status = 'pending'
        
        return {
            'validation_status': validation_status,
            'evidence_count': evidence_count,
            'unique_sources': max(unique_sources, 1),  # At least 1 for content intelligence
            'average_authority': average_authority,
            'validation_confidence': validation_confidence,
            'evidence_gaps': [],
            'evidence_pieces': evidence_pieces
        }
    
    def _generate_landmarks_section(self, landmarks: dict) -> str:
        """Generate landmarks section HTML."""
        locations = landmarks.get('specific_locations', [])
        descriptions = landmarks.get('landmark_descriptions', {})
        special_features = landmarks.get('what_makes_them_special', [])
        
        landmarks_html = []
        for location in locations[:3]:  # Show top 3 landmarks
            description = descriptions.get(location, "")
            landmarks_html.append(f"""
            <div class="landmark-item">
                <div class="landmark-name">🏛️ {location}</div>
                {f'<div class="landmark-description">{description}</div>' if description else ''}
            </div>
            """)
        
        special_html = ""
        if special_features:
            special_items = [f"<li>{feature}</li>" for feature in special_features[:3]]
            special_html = f"""
            <div class="special-features">
                <strong>What makes them special:</strong>
                <ul>{''.join(special_items)}</ul>
            </div>
            """
        
        return f"""
        <div class="ci-section landmarks-section">
            <h5><i class="fas fa-landmark"></i> Iconic Landmarks</h5>
            {''.join(landmarks_html)}
            {special_html}
        </div>
        """
    
    def _generate_practical_section(self, practical: dict) -> str:
        """Generate practical intelligence section HTML."""
        costs = practical.get('specific_costs', {})
        timing = practical.get('timing_intelligence', {})
        booking = practical.get('booking_specifics', [])
        tips = practical.get('practical_tips', [])
        
        content_parts = []
        
        # Costs
        if costs:
            cost_items = [f"<li><strong>{category}:</strong> {cost}</li>" for category, cost in costs.items()]
            content_parts.append(f"""
            <div class="practical-costs">
                <strong>💰 Costs:</strong>
                <ul>{''.join(cost_items)}</ul>
            </div>
            """)
        
        # Timing
        if timing:
            timing_items = []
            for season, advice_list in timing.items():
                advice = ', '.join(advice_list) if isinstance(advice_list, list) else str(advice_list)
                timing_items.append(f"<li><strong>{season.replace('_', ' ').title()}:</strong> {advice}</li>")
            content_parts.append(f"""
            <div class="practical-timing">
                <strong>⏰ Timing:</strong>
                <ul>{''.join(timing_items)}</ul>
            </div>
            """)
        
        # Tips
        if tips:
            tip_items = [f"<li>{tip}</li>" for tip in tips[:3]]
            content_parts.append(f"""
            <div class="practical-tips">
                <strong>💡 Tips:</strong>
                <ul>{''.join(tip_items)}</ul>
            </div>
            """)
        
        return f"""
        <div class="ci-section practical-section">
            <h5><i class="fas fa-info-circle"></i> Practical Intelligence</h5>
            {''.join(content_parts)}
        </div>
        """
    
    def _generate_neighborhood_section(self, neighborhoods: dict) -> str:
        """Generate neighborhood insights section HTML."""
        names = neighborhoods.get('neighborhood_names', [])
        personalities = neighborhoods.get('area_personalities', {})
        specialties = neighborhoods.get('neighborhood_specialties', {})
        stay_advice = neighborhoods.get('stay_recommendations', {})
        
        neighborhood_items = []
        for name in names[:3]:  # Show top 3 neighborhoods
            personality = personalities.get(name, "")
            specialty_list = specialties.get(name, [])
            stay = stay_advice.get(name, "")
            
            specialty_html = ""
            if specialty_list:
                specialty_html = f"<div class='specialty'>Known for: {', '.join(specialty_list[:2])}</div>"
            
            neighborhood_items.append(f"""
            <div class="neighborhood-item">
                <div class="neighborhood-name">🏘️ {name}</div>
                {f'<div class="neighborhood-personality">{personality}</div>' if personality else ''}
                {specialty_html}
                {f'<div class="stay-advice"><strong>Stay:</strong> {stay}</div>' if stay else ''}
            </div>
            """)
        
        return f"""
        <div class="ci-section neighborhoods-section">
            <h5><i class="fas fa-map-marker-alt"></i> Neighborhood Insights</h5>
            {''.join(neighborhood_items)}
        </div>
        """
    
    def _generate_discovery_section(self, discovery: dict) -> str:
        """Generate content discovery section HTML."""
        sources = discovery.get('high_quality_sources', [])
        phrases = discovery.get('extracted_phrases', [])
        validation = discovery.get('authority_validation', {})
        
        content_parts = []
        
        # Authority validation
        if validation:
            quality_score = validation.get('content_quality_score', 0)
            total_sources = validation.get('total_sources', 0)
            quality_color = '#28a745' if quality_score > 0.7 else '#ffc107' if quality_score > 0.4 else '#dc3545'
            
            content_parts.append(f"""
            <div class="discovery-validation">
                <div class="validation-item">
                    <span class="validation-label">Sources:</span>
                    <span class="validation-value">{total_sources}</span>
                </div>
                <div class="validation-item">
                    <span class="validation-label">Quality:</span>
                    <span class="validation-value" style="color: {quality_color}">{quality_score:.2f}</span>
                </div>
            </div>
            """)
        
        # Compelling phrases
        if phrases:
            phrase_items = [f"<li>\"{phrase}\"</li>" for phrase in phrases[:3]]
            content_parts.append(f"""
            <div class="discovery-phrases">
                <strong>📝 Compelling Language:</strong>
                <ul>{''.join(phrase_items)}</ul>
            </div>
            """)
        
        return f"""
        <div class="ci-section discovery-section">
            <h5><i class="fas fa-search"></i> Content Discovery</h5>
            {''.join(content_parts)}
        </div>
        """
    
    def _generate_evidence_validation_display(self, evidence_summary: dict) -> str:
        """Generate enhanced evidence validation display with clickable URLs and comprehensive source information."""
        if not evidence_summary:
            return '<div class="evidence-status validated"><span class="evidence-icon">✅</span> Enhanced theme analysis complete</div>'
        
        validation_status = evidence_summary.get('validation_status', 'pending')
        evidence_count = evidence_summary.get('evidence_count', 0)
        unique_sources = evidence_summary.get('unique_sources', 0)
        average_authority = evidence_summary.get('average_authority', 0)
        validation_confidence = evidence_summary.get('validation_confidence', 0)
        evidence_gaps = evidence_summary.get('evidence_gaps', [])
        evidence_pieces = evidence_summary.get('evidence_pieces', [])
        
        # Status icons and colors
        status_config = {
            'validated': {'icon': '✅', 'color': '#28a745', 'label': 'Validated'},
            'partially_validated': {'icon': '⚠️', 'color': '#ffc107', 'label': 'Partial'},
            'unvalidated': {'icon': '❌', 'color': '#dc3545', 'label': 'Unvalidated'},
            'conflicting': {'icon': '⚡', 'color': '#fd7e14', 'label': 'Conflicting'},
            'pending': {'icon': '⏳', 'color': '#6c757d', 'label': 'Pending'}
        }
        
        config = status_config.get(validation_status, status_config['pending'])
        
        # Enhanced evidence metrics
        metrics_html = ""
        if evidence_count > 0:
            authority_bar = f'<div class="authority-bar"><div class="authority-fill" style="width: {average_authority*100}%; background: {config["color"]}"></div></div>'
            metrics_html = f"""
            <div class="evidence-metrics">
                <div class="evidence-metric">
                    <span class="metric-label">Sources:</span>
                    <span class="metric-value">{unique_sources}</span>
                </div>
                <div class="evidence-metric">
                    <span class="metric-label">Evidence:</span>
                    <span class="metric-value">{evidence_count}</span>
                </div>
                <div class="evidence-metric">
                    <span class="metric-label">Authority:</span>
                    <span class="metric-value">{average_authority:.2f}</span>
                    {authority_bar}
                </div>
                <div class="evidence-metric">
                    <span class="metric-label">Confidence:</span>
                    <span class="metric-value">{validation_confidence:.2f}</span>
                </div>
            </div>
            """
        
        # Evidence pieces display
        evidence_pieces_html = ""
        if evidence_pieces:
            evidence_items = []
            for i, piece in enumerate(evidence_pieces[:3]):  # Show top 3 evidence pieces
                source_type_icon = self._get_source_type_icon(piece.get('source_type', 'unknown'))
                quality_color = self._get_quality_color(piece.get('quality_rating', 'poor'))
                authority_score = piece.get('authority_score', 0)
                
                evidence_items.append(f"""
                <div class="evidence-piece" style="border-left-color: {quality_color}">
                    <div class="evidence-header">
                        <span class="source-icon">{source_type_icon}</span>
                        <span class="authority-score" style="background: {quality_color}">{authority_score:.2f}</span>
                    </div>
                    <div class="evidence-text">"{piece.get('text_content', '')}"</div>
                    <div class="evidence-source">
                        <a href="{piece.get('source_url', '#')}" target="_blank" title="{piece.get('source_title', 'Source')}">
                            {self._truncate_url(piece.get('source_url', ''))}
                        </a>
                    </div>
                </div>
                """)
            
            evidence_pieces_html = f"""
            <div class="evidence-pieces">
                <div class="evidence-toggle" onclick="toggleEvidence(this)">
                    <span class="toggle-icon">▼</span> View Evidence ({len(evidence_pieces)} pieces)
                </div>
                <div class="evidence-content" style="display: none;">
                    {''.join(evidence_items)}
                    {f'<div class="evidence-more">... and {len(evidence_pieces) - 3} more pieces</div>' if len(evidence_pieces) > 3 else ''}
                </div>
            </div>
            """
        
        # Evidence gaps
        gaps_html = ""
        if evidence_gaps:
            gap_tags = ''.join(f'<span class="gap-tag">{gap}</span>' for gap in evidence_gaps[:3])
            gaps_html = f'<div class="evidence-gaps"><strong>Gaps:</strong> {gap_tags}</div>'
        
        return f"""
        <div class="evidence-status {validation_status}" style="border-left-color: {config['color']}">
            <div class="evidence-header">
                <span class="evidence-icon">{config['icon']}</span>
                <span class="evidence-label">{config['label']}</span>
            </div>
            {metrics_html}
            {evidence_pieces_html}
            {gaps_html}
        </div>
        """

    def _get_source_type_icon(self, source_type: str) -> str:
        """Get icon for source type."""
        icons = {
            'government': '🏛️',
            'education': '🎓',
            'major_travel': '✈️',
            'news_media': '📰',
            'tourism_board': '🗺️',
            'travel_blog': '📝',
            'local_business': '🏪',
            'social_media': '📱',
            'unknown': '❓'
        }
        return icons.get(source_type, '❓')
    
    def _get_quality_color(self, quality_rating: str) -> str:
        """Get color for quality rating."""
        colors = {
            'excellent': '#28a745',
            'good': '#20c997',
            'acceptable': '#ffc107',
            'poor': '#fd7e14',
            'rejected': '#dc3545'
        }
        return colors.get(quality_rating, '#6c757d')
    
    def _truncate_url(self, url: str) -> str:
        """Truncate URL for display."""
        if len(url) > 40:
            return url[:37] + '...'
        return url

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for display."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return "unknown"

    def _get_relevance_color(self, relevance_score: float) -> str:
        """Get color for relevance score."""
        if relevance_score >= 0.8:
            return '#28a745'  # Green
        elif relevance_score >= 0.6:
            return '#20c997'  # Teal
        elif relevance_score >= 0.4:
            return '#ffc107'  # Yellow
        elif relevance_score >= 0.2:
            return '#fd7e14'  # Orange
        else:
            return '#dc3545'  # Red

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + '...'

    def _format_gap_name(self, gap: str) -> str:
        """Format evidence gap name for display."""
        gap_names = {
            'insufficient_evidence_count': 'Not Enough Evidence',
            'low_source_diversity': 'Limited Sources',
            'low_authority_sources': 'Low Authority',
            'low_relevance_scores': 'Low Relevance'
        }
        return gap_names.get(gap, gap.replace('_', ' ').title())

    def _generate_evidence_paperclip(self, theme_name: str, theme_data: dict) -> str:
        """Generate evidence paperclip for themes."""
        evidence_id = f"theme_{self._sanitize_filename(theme_name)}"
        
        # Store evidence data for modal
        if not hasattr(self, '_evidence_store'):
            self._evidence_store = {}
        
        self._evidence_store[evidence_id] = {
            'theme_evidence': theme_data.get('comprehensive_attribute_evidence', {}).get('theme_evidence', []),
            'nano_themes': theme_data.get('nano_themes', []),
            'price_insights': theme_data.get('price_insights', {}),
            'authenticity_analysis': theme_data.get('authenticity_analysis', {}),
            'hidden_gem_score': theme_data.get('hidden_gem_score', {}),
            'llm_generated': not bool(theme_data.get('comprehensive_attribute_evidence', {}).get('theme_evidence', []))
        }
        
        return f'<i class="fas fa-paperclip evidence-paperclip" onclick="showThemeEvidenceModal(\'{theme_name}\', \'{evidence_id}\')" title="View evidence for {theme_name}"></i>'
    
    def _generate_nuance_evidence_paperclip(self, nuance_phrase: str, nuance_data: dict) -> str:
        """Generate evidence paperclip for nuances."""
        evidence_id = f"nuance_{self._sanitize_filename(nuance_phrase)}"
        
        # Store evidence data for modal
        if not hasattr(self, '_evidence_store'):
            self._evidence_store = {}
        
        # Get validation data and evidence
        validation_data = nuance_data.get('validation_data', {})
        evidence_sources = nuance_data.get('evidence_sources', [])
        
        self._evidence_store[evidence_id] = {
            'nuance_phrase': nuance_phrase,
            'score': nuance_data.get('score', 0),
            'search_hits': validation_data.get('destination_hits', 0),
            'uniqueness_ratio': validation_data.get('uniqueness_ratio', 0),
            'evidence_sources': evidence_sources,
            'validation_metadata': validation_data,
            'source_models': nuance_data.get('source_models', []),
            'category': nuance_data.get('category', ''),
            'confidence': nuance_data.get('confidence', 0),
            'nuance_evidence': True  # Flag to indicate this is nuance evidence
        }
        
        return f'<i class="fas fa-paperclip evidence-paperclip" onclick="showNuanceEvidenceModal(\'{nuance_phrase}\', \'{evidence_id}\')" title="View evidence for {nuance_phrase}"></i>'

    def _generate_theme_details(self, theme, depth_analysis, contextual_info, micro_climate, cultural_sensitivity, interconnections) -> str:
        """Generate detailed theme information with evidence paperclips for each attribute."""
        details = []
        theme_name = theme.get('theme', 'Unknown Theme')
        
        # Get comprehensive evidence for all attributes
        comprehensive_evidence = theme.get('comprehensive_attribute_evidence', {})
        
        # Sub-themes
        sub_themes = theme.get('sub_themes', [])
        if sub_themes:
            sub_theme_tags = ''.join(f'<span class="sub-theme-tag">{st}</span>' for st in sub_themes)
            sub_themes_paperclip = self._generate_attribute_paperclip(theme_name, 'sub_themes', sub_themes, comprehensive_evidence)
            details.append(f'<div class="detail-row"><strong>🎯 Sub-themes: {sub_themes_paperclip}</strong> <div class="sub-themes">{sub_theme_tags}</div></div>')
        
        # Nano themes
        nano_themes = depth_analysis.get('nano_themes', [])
        if nano_themes:
            nano_tags = ''.join(f'<span class="nano-theme-tag">{nt}</span>' for nt in nano_themes[:4])
            nano_paperclip = self._generate_attribute_paperclip(theme_name, 'nano_themes', nano_themes, comprehensive_evidence)
            details.append(f'<div class="detail-row"><strong>🔬 Nano Themes: {nano_paperclip}</strong> <div class="nano-themes">{nano_tags}</div></div>')
        
        # Demographics
        demographics = contextual_info.get('demographic_suitability', [])
        if demographics:
            demo_paperclip = self._generate_attribute_paperclip(theme_name, 'demographic_suitability', demographics, comprehensive_evidence)
            details.append(f'<div class="detail-row"><strong>👥 Best For: {demo_paperclip}</strong> {", ".join(demographics)}</div>')
        
        # Time commitment
        time_commit = contextual_info.get('time_commitment', '')
        if time_commit:
            time_paperclip = self._generate_attribute_paperclip(theme_name, 'time_commitment', time_commit, comprehensive_evidence)
            details.append(f'<div class="detail-row"><strong>⏰ Time Needed: {time_paperclip}</strong> {time_commit.title()}</div>')
        
        # Experience Intensity
        experience_intensity = theme.get('experience_intensity', {})
        if experience_intensity:
            intensity_paperclip = self._generate_attribute_paperclip(theme_name, 'experience_intensity', experience_intensity, comprehensive_evidence)
            overall_intensity = experience_intensity.get('overall_intensity', 'moderate')
            details.append(f'<div class="detail-row"><strong>⚡ Intensity: {intensity_paperclip}</strong> {overall_intensity.title()}</div>')
        
        # Emotional Profile
        emotional_profile = theme.get('emotional_profile', {})
        emotions = emotional_profile.get('primary_emotions', [])
        if emotions:
            emotion_paperclip = self._generate_attribute_paperclip(theme_name, 'emotional_profile', emotions, comprehensive_evidence)
            details.append(f'<div class="detail-row"><strong>✨ Emotions: {emotion_paperclip}</strong> {", ".join(emotions[:3])}</div>')
        
        # Best timing
        best_time = micro_climate.get('best_time_of_day', [])
        if best_time and best_time != ['flexible']:
            timing_paperclip = self._generate_attribute_paperclip(theme_name, 'micro_climate', best_time, comprehensive_evidence)
            details.append(f'<div class="detail-row"><strong>🕐 Best Time: {timing_paperclip}</strong> {", ".join(best_time)}</div>')
        
        # Weather needs
        weather_deps = micro_climate.get('weather_dependencies', [])
        if weather_deps:
            weather_paperclip = self._generate_attribute_paperclip(theme_name, 'weather_dependencies', weather_deps, comprehensive_evidence)
            details.append(f'<div class="detail-row"><strong>🌤️ Weather: {weather_paperclip}</strong> {", ".join(weather_deps)}</div>')
        
        # Cultural notes
        cultural_notes = cultural_sensitivity.get('considerations', [])
        if cultural_notes:
            cultural_paperclip = self._generate_attribute_paperclip(theme_name, 'cultural_sensitivity', cultural_notes, comprehensive_evidence)
            details.append(f'<div class="detail-row"><strong>🏛️ Cultural: {cultural_paperclip}</strong> {", ".join(cultural_notes[:2])}</div>')
        
        # Combinations
        combinations = interconnections.get('natural_combinations', [])
        if combinations:
            combo_paperclip = self._generate_attribute_paperclip(theme_name, 'theme_interconnections', combinations, comprehensive_evidence)
            details.append(f'<div class="detail-row"><strong>🔗 Combines With: {combo_paperclip}</strong> {", ".join(combinations[:3])}</div>')
        
        # Price insights
        price_insights = theme.get('price_insights', {})
        if price_insights:
            price_category = price_insights.get('price_category', 'N/A')
            price_paperclip = self._generate_attribute_paperclip(theme_name, 'price_insights', price_category, comprehensive_evidence)
            details.append(f'<div class="detail-row"><strong>💰 Price: {price_paperclip}</strong> {price_category.title()}</div>')
        
        return ''.join(details)

    def _generate_attribute_paperclip(self, theme_name: str, attribute_name: str, 
                                    attribute_data: Any, comprehensive_evidence: Dict[str, Any]) -> str:
        """Generate paperclip icon for specific attribute with evidence."""
        import hashlib
        
        # Always show paperclip since we have the attribute data (even if LLM generated)
        # Check if we have specific web evidence for this attribute OR theme-level evidence
        attribute_evidence = comprehensive_evidence.get(attribute_name, {})
        
        # Also check for theme-level evidence (main_theme.evidence_pieces)
        theme_evidence = comprehensive_evidence.get('main_theme', {})
        theme_evidence_pieces = theme_evidence.get('evidence_pieces', []) if isinstance(theme_evidence, dict) else []
        
        # Determine if we have any web evidence (attribute-specific OR theme-level)
        has_web_evidence = len(attribute_evidence) > 0 or len(theme_evidence_pieces) > 0
        
        # Create unique ID for this evidence using deterministic hash
        evidence_str = f"{theme_name}_{attribute_name}_{str(attribute_data)}"
        evidence_id = f"{theme_name.replace(' ', '_')}_{attribute_name}_{hashlib.md5(evidence_str.encode()).hexdigest()[:8]}"
        
        # Create evidence data for modal - include both attribute and theme evidence
        evidence_data = {
            'attribute_name': attribute_name,
            'attribute_data': attribute_data,
            'evidence': attribute_evidence,
            'theme_evidence': theme_evidence_pieces,  # Include theme-level evidence
            'llm_generated': not has_web_evidence,  # True if no web evidence at all
            'has_web_evidence': has_web_evidence
        }
        
        # Store in evidence store
        if not hasattr(self, '_evidence_store'):
            self._evidence_store = {}
        self._evidence_store[evidence_id] = evidence_data
        
        # Paperclip color based on evidence availability (attribute-specific OR theme-level)
        paperclip_class = "evidence-paperclip" if has_web_evidence else "evidence-paperclip no-evidence"
        title_text = f"View evidence for {attribute_name.replace('_', ' ')}" if has_web_evidence else f"View data for {attribute_name.replace('_', ' ')} (AI generated)"
        
        return f'''<i class="fas fa-paperclip {paperclip_class}" 
                    onclick="showAttributeEvidenceModal('{theme_name}', '{attribute_name}', '{evidence_id}')" 
                    title="{title_text}"></i>'''
    
    def _generate_intelligence_insights(self, intelligence_insights: dict) -> str:
        """Generate intelligence insights cards."""
        if not intelligence_insights:
            return '<p class="no-data">No intelligence insights available.</p>'
        
        insights_cards = []
        
        # Hidden gems insight
        hidden_gems_count = intelligence_insights.get('hidden_gems_count', 0)
        hidden_gems_ratio = intelligence_insights.get('hidden_gems_ratio', 0)
        if hidden_gems_count > 0:
            insights_cards.append(f"""
            <div class="insight-card hidden-gems">
                <div class="insight-icon">💎</div>
                <div class="insight-content">
                    <h3>Hidden Gems</h3>
                    <div class="insight-value">{hidden_gems_count} gems ({hidden_gems_ratio*100:.1f}%)</div>
                    <p>Unique experiences off the beaten path</p>
                </div>
            </div>
            """)
        
        # Authenticity insight
        avg_auth = intelligence_insights.get('average_authenticity_score', 0)
        if avg_auth > 0:
            auth_level = "Excellent" if avg_auth > 0.8 else "Good" if avg_auth > 0.6 else "Moderate"
            insights_cards.append(f"""
            <div class="insight-card authenticity">
                <div class="insight-icon">🏆</div>
                <div class="insight-content">
                    <h3>Authenticity</h3>
                    <div class="insight-value">{avg_auth:.2f} ({auth_level})</div>
                    <p>Focus on local and authentic experiences</p>
                </div>
            </div>
            """)
        
        # Depth insight
        avg_depth = intelligence_insights.get('average_depth_score', 0)
        if avg_depth > 0:
            depth_level = "Nano-level" if avg_depth > 0.8 else "Micro-level" if avg_depth > 0.6 else "Macro-level"
            insights_cards.append(f"""
            <div class="insight-card depth">
                <div class="insight-icon">📊</div>
                <div class="insight-content">
                    <h3>Theme Depth</h3>
                    <div class="insight-value">{avg_depth:.2f} ({depth_level})</div>
                    <p>Detailed, specific experience granularity</p>
                </div>
            </div>
            """)
        
        # Emotional variety
        emotional_variety = intelligence_insights.get('emotional_variety', {})
        emotions_covered = emotional_variety.get('emotions_covered', [])
        if emotions_covered:
            insights_cards.append(f"""
            <div class="insight-card emotions">
                <div class="insight-icon">✨</div>
                <div class="insight-content">
                    <h3>Emotional Range</h3>
                    <div class="insight-value">{len(emotions_covered)} emotion types</div>
                    <p>{", ".join(emotions_covered)}</p>
                </div>
            </div>
            """)
        
        return f'<div class="insights-grid">{"".join(insights_cards)}</div>'
    
    def _generate_composition_analysis(self, composition_analysis: dict) -> str:
        """Generate composition analysis section."""
        if not composition_analysis:
            return '<p class="no-data">No composition analysis available.</p>'
        
        comp_score = composition_analysis.get('overall_composition_score', 0)
        category_dist = composition_analysis.get('category_distribution', {})
        
        # Category distribution
        category_cards = []
        if category_dist:
            for category, count in category_dist.items():
                category_cards.append(f"""
                <div class="category-card">
                    <div class="category-name">{category.title()}</div>
                    <div class="category-count">{count}</div>
                </div>
                """)
        
        return f"""
        <div class="composition-content">
            <div class="composition-score">
                <h3>Overall Composition Score</h3>
                <div class="score-value">{comp_score:.2f}</div>
            </div>
            <div class="category-distribution">
                <h3>Category Distribution</h3>
                <div class="category-grid">
                    {"".join(category_cards)}
                </div>
            </div>
        </div>
        """
    
    def _generate_quality_metrics(self, quality_assessment: dict, nuances_data: dict = None) -> str:
        """Generate combined quality metrics section for both themes and nuances."""
        if not quality_assessment:
            return '<p class="no-data">No quality assessment available.</p>'
        
        # Theme quality metrics
        theme_metrics = quality_assessment.get('metrics', {})
        theme_overall_score = quality_assessment.get('overall_score', 0)
        
        # Nuance quality metrics
        nuance_overall_score = 0
        nuance_count = 0
        if nuances_data:
            # Check for 3-tier system first
            if 'destination_nuances' in nuances_data or 'hotel_expectations' in nuances_data or 'vacation_rental_expectations' in nuances_data:
                nuance_overall_score = nuances_data.get('overall_nuance_quality_score', nuances_data.get('overall_quality_score', 0))
                nuance_count += len(nuances_data.get('destination_nuances', []))
                nuance_count += len(nuances_data.get('hotel_expectations', []))
                nuance_count += len(nuances_data.get('vacation_rental_expectations', []))
            # Fall back to legacy format
            elif 'nuances' in nuances_data:
                nuances_list = nuances_data.get('nuances', [])
                if nuances_list:
                    nuance_overall_score = sum(n.get('score', 0) for n in nuances_list) / len(nuances_list)
                    nuance_count = len(nuances_list)
        
        # Calculate combined discovery quality score
        combined_score = 0
        if theme_overall_score > 0 and nuance_overall_score > 0:
            # Weight: 60% theme quality, 40% nuance quality
            combined_score = (theme_overall_score * 0.6) + (nuance_overall_score * 0.4)
        elif theme_overall_score > 0:
            combined_score = theme_overall_score
        elif nuance_overall_score > 0:
            combined_score = nuance_overall_score
        
        # Generate combined quality overview
        combined_quality_level = self._get_quality_level(combined_score)
        combined_color = self._get_confidence_color(combined_score)
        
        # Core theme metrics
        core_metrics = ['factual_accuracy', 'thematic_coverage', 'actionability', 'uniqueness', 'source_credibility']
        intelligence_metrics = ['theme_depth', 'authenticity', 'emotional_resonance']
        
        # Core metrics HTML
        core_html = []
        for metric in core_metrics:
            if metric in theme_metrics:
                value = theme_metrics[metric]
                color = self._get_confidence_color(value)
                name = metric.replace('_', ' ').title()
                core_html.append(f"""
                <div class="metric-item">
                    <div class="metric-name">{name}</div>
                    <div class="metric-value" style="color: {color}">{value:.3f}</div>
                </div>
                """)
        
        # Intelligence metrics HTML
        intel_html = []
        icons = {'theme_depth': '📊', 'authenticity': '🏆', 'emotional_resonance': '✨'}
        for metric in intelligence_metrics:
            if metric in theme_metrics:
                value = theme_metrics[metric]
                color = self._get_confidence_color(value)
                name = metric.replace('_', ' ').title()
                icon = icons.get(metric, '📈')
                intel_html.append(f"""
                <div class="metric-item">
                    <div class="metric-name">{icon} {name}</div>
                    <div class="metric-value" style="color: {color}">{value:.3f}</div>
                </div>
                """)
        
        return f"""
        <div class="combined-quality-overview">
            <div class="quality-summary-card">
                <div class="quality-summary-icon">🏆</div>
                <div class="quality-summary-content">
                    <h3>Combined Discovery Quality</h3>
                    <div class="combined-score" style="color: {combined_color}">{combined_score:.3f}</div>
                    <div class="quality-level-badge quality-{combined_quality_level.lower().replace(' ', '-')}">{combined_quality_level}</div>
                </div>
                <div class="quality-breakdown">
                    <div class="breakdown-item">
                        <span class="breakdown-label">Theme Quality:</span>
                        <span class="breakdown-value" style="color: {self._get_confidence_color(theme_overall_score)}">{theme_overall_score:.3f}</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="breakdown-label">Nuance Quality:</span>
                        <span class="breakdown-value" style="color: {self._get_confidence_color(nuance_overall_score)}">{nuance_overall_score:.3f}</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="breakdown-label">Total Features:</span>
                        <span class="breakdown-value">{len(theme_metrics)} themes + {nuance_count} nuances</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="quality-content">
            <div class="metrics-section">
                <h3>Core Quality Metrics</h3>
                <div class="metrics-grid">
                    {"".join(core_html)}
                </div>
            </div>
            <div class="metrics-section">
                <h3>Intelligence Metrics</h3>
                <div class="metrics-grid">
                    {"".join(intel_html)}
                </div>
            </div>
        </div>
        """

    def _generate_comprehensive_evidence_display(self, comprehensive_evidence) -> str:
        """Generate comprehensive evidence display showing all evidence types."""
        if not comprehensive_evidence:
            return '<div class="no-data">No comprehensive evidence data available</div>'
        
        # Handle list format (nuances evidence as list)
        if isinstance(comprehensive_evidence, list):
            # Convert list format to dict format for nuance evidence display
            nuances_evidence_dict = {'evidence': comprehensive_evidence}
            return self._generate_nuance_evidence_display(nuances_evidence_dict)
        
        # Handle dict format
        if not isinstance(comprehensive_evidence, dict):
            return '<div class="no-data">Invalid evidence data format</div>'
        
        # Check if this is nuance evidence data (different structure)
        if 'nuances_evidence' in comprehensive_evidence:
            return self._generate_nuance_evidence_display(comprehensive_evidence)
        
        # Check if this is evidence in list format within a dict
        if 'evidence' in comprehensive_evidence:
            return self._generate_nuance_evidence_display(comprehensive_evidence)
        
        evidence_summary = comprehensive_evidence.get('evidence_summary', {})
        total_pieces = evidence_summary.get('total_evidence_pieces', 0)
        unique_sources = evidence_summary.get('unique_sources', 0)
        evidence_types = evidence_summary.get('evidence_types_collected', [])
        
        # Evidence type cards
        evidence_cards = []
        
        # Price evidence
        if comprehensive_evidence.get('price_evidence'):
            price_evidence = comprehensive_evidence['price_evidence']
            evidence_cards.append(self._generate_evidence_type_card(
                'Price Information', '💰', price_evidence, '#28a745'
            ))
        
        # Authenticity evidence
        if comprehensive_evidence.get('authenticity_evidence'):
            auth_evidence = comprehensive_evidence['authenticity_evidence']
            evidence_cards.append(self._generate_evidence_type_card(
                'Authenticity Markers', '🏛️', auth_evidence, '#17a2b8'
            ))
        
        # Hidden gem evidence
        if comprehensive_evidence.get('hidden_gem_evidence'):
            gem_evidence = comprehensive_evidence['hidden_gem_evidence']
            evidence_cards.append(self._generate_evidence_type_card(
                'Hidden Gem Indicators', '💎', gem_evidence, '#6f42c1'
            ))
        
        # Content Intelligence Evidence Cards
        # Note: For content intelligence, we'll show the extracted data as "evidence"
        if comprehensive_evidence.get('iconic_landmarks'):
            landmarks_data = comprehensive_evidence['iconic_landmarks']
            evidence_cards.append(self._generate_content_intelligence_card(
                'Iconic Landmarks', '🏛️', landmarks_data, '#dc3545'
            ))
        
        if comprehensive_evidence.get('practical_travel_intelligence'):
            practical_data = comprehensive_evidence['practical_travel_intelligence']
            evidence_cards.append(self._generate_content_intelligence_card(
                'Practical Intelligence', '💡', practical_data, '#fd7e14'
            ))
        
        if comprehensive_evidence.get('neighborhood_insights'):
            neighborhood_data = comprehensive_evidence['neighborhood_insights']
            evidence_cards.append(self._generate_content_intelligence_card(
                'Neighborhood Insights', '🏘️', neighborhood_data, '#20c997'
            ))
        
        if comprehensive_evidence.get('content_discovery_intelligence'):
            discovery_data = comprehensive_evidence['content_discovery_intelligence']
            evidence_cards.append(self._generate_content_intelligence_card(
                'Content Discovery', '🔍', discovery_data, '#6610f2'
            ))
        
        return f"""
        <div class="evidence-overview">
            <div class="evidence-summary-stats">
                <div class="evidence-stat">
                    <div class="stat-value">{total_pieces}</div>
                    <div class="stat-label">Total Evidence Pieces</div>
                </div>
                <div class="evidence-stat">
                    <div class="stat-value">{unique_sources}</div>
                    <div class="stat-label">Unique Sources</div>
                </div>
                <div class="evidence-stat">
                    <div class="stat-value">{len(evidence_types)}</div>
                    <div class="stat-label">Evidence Types</div>
                </div>
            </div>
        </div>
        
        <div class="evidence-types-grid">
            {''.join(evidence_cards)}
        </div>
        """

    def _generate_nuance_evidence_display(self, nuances_evidence: dict) -> str:
        """Generate evidence display specifically for nuances data."""
        # Handle the actual evidence structure from the JSON file
        evidence_list = nuances_evidence.get('evidence', [])
        
        if not evidence_list:
            return '<div class="no-data">No nuance evidence data available</div>'
        
        # Calculate summary statistics from the actual evidence list
        total_evidence = len(evidence_list)
        unique_sources = set()
        evidence_types = set()
        
        for item in evidence_list:
            # Get unique domains from authority_sources URLs
            authority_sources = item.get('authority_sources', [])
            for url in authority_sources:
                if url and not url.startswith('https://fallback-evidence'):
                    # Extract domain from URL
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(url).netloc
                        if domain:
                            unique_sources.add(domain)
                    except:
                        pass
            
            # Detect evidence types from metadata
            metadata = item.get('metadata', {})
            if metadata.get('authority_validated', False):
                evidence_types.add('search_validation')
            elif metadata.get('evidence_type') == 'fallback_generated':
                evidence_types.add('fallback_scoring')
            elif 'search_results_count' in metadata:
                evidence_types.add('search_validation')
            else:
                evidence_types.add('fallback_scoring')
        
        # Ensure we have at least one evidence type
        if not evidence_types:
            evidence_types.add('search_validation')
        
        # Generate summary stats with actual data
        summary_html = f"""
        <div class="evidence-overview">
            <div class="evidence-summary-stats">
                <div class="evidence-stat">
                    <div class="stat-value">{total_evidence}</div>
                    <div class="stat-label">Total Evidence Pieces</div>
                </div>
                <div class="evidence-stat">
                    <div class="stat-value">{len(unique_sources)}</div>
                    <div class="stat-label">Unique Sources</div>
                </div>
                <div class="evidence-stat">
                    <div class="stat-value">{len(evidence_types)}</div>
                    <div class="stat-label">Evidence Types</div>
                </div>
            </div>
        </div>
        """
        
        # Generate evidence type cards based on actual data
        evidence_cards_html = """
        <div class="evidence-types-grid">
        """
        
        # Group evidence by source type
        fallback_scoring_items = []
        search_validation_items = []
        
        for item in evidence_list:
            sources = item.get('evidence_sources', [])
            if 'fallback_scoring' in sources:
                fallback_scoring_items.append(item)
            else:
                search_validation_items.append(item)
        
        # Generate Search Validation Evidence card (if any)
        if search_validation_items:
            total_hits = sum(item.get('search_hits', 0) for item in search_validation_items)
            avg_uniqueness = sum(item.get('uniqueness_ratio', 0) for item in search_validation_items) / len(search_validation_items)
            
            evidence_cards_html += f"""
            <div class="evidence-type-card" style="border-left-color: #28a745">
                <div class="evidence-type-header">
                    <div class="evidence-type-title">
                        <span class="evidence-type-icon">🔍</span>
                        <span class="evidence-type-name">Search Validation Evidence</span>
                    </div>
                    <div class="evidence-type-status">
                        <span class="status-icon">✅</span>
                        <span class="evidence-count">{len(search_validation_items)}</span>
                    </div>
                </div>
                
                <div class="evidence-type-metrics">
                    <div class="authority-metric">
                        <span class="metric-label">Avg Uniqueness:</span>
                        <span class="metric-value">{avg_uniqueness:.1f}x</span>
                        <div class="authority-bar">
                            <div class="authority-fill" style="width: {min(avg_uniqueness * 20, 100)}%; background: #28a745"></div>
                        </div>
                    </div>
                </div>
                
                <div class="evidence-preview">
                    <div class="evidence-preview-item">
                        <div class="evidence-preview-text">📊 {total_hits:,} total search hits collected</div>
                        <div class="evidence-preview-source">🌐 Real search engine validation</div>
                    </div>
                </div>
                
                <div class="evidence-type-actions">
                    <button class="view-evidence-btn" onclick="toggleEvidenceType(this, 'search_validation')" style="background: #28a745">
                        View Search Evidence
                    </button>
                </div>
            </div>
            """
        
        # Generate Fallback Scoring Evidence card (if any)
        if fallback_scoring_items:
            total_hits = sum(item.get('search_hits', 0) for item in fallback_scoring_items)
            avg_uniqueness = sum(item.get('uniqueness_ratio', 0) for item in fallback_scoring_items) / len(fallback_scoring_items)
            
            evidence_cards_html += f"""
            <div class="evidence-type-card" style="border-left-color: #ffc107">
                <div class="evidence-type-header">
                    <div class="evidence-type-title">
                        <span class="evidence-type-icon">📊</span>
                        <span class="evidence-type-name">Fallback Scoring Evidence</span>
                    </div>
                    <div class="evidence-type-status">
                        <span class="status-icon">⚠️</span>
                        <span class="evidence-count">{len(fallback_scoring_items)}</span>
                    </div>
                </div>
                
                <div class="evidence-type-metrics">
                    <div class="authority-metric">
                        <span class="metric-label">Avg Uniqueness:</span>
                        <span class="metric-value">{avg_uniqueness:.1f}x</span>
                        <div class="authority-bar">
                            <div class="authority-fill" style="width: {min(avg_uniqueness * 20, 100)}%; background: #ffc107"></div>
                        </div>
                    </div>
                </div>
                
                <div class="evidence-preview">
                    <div class="evidence-preview-item">
                        <div class="evidence-preview-text">🔄 {total_hits:,} estimated search hits</div>
                        <div class="evidence-preview-source">⚡ Fallback validation mode (was using wrong API key)</div>
                    </div>
                </div>
                
                <div class="evidence-type-actions">
                    <button class="view-evidence-btn" onclick="toggleEvidenceType(this, 'fallback_scoring')" style="background: #ffc107">
                        View Fallback Evidence
                    </button>
                </div>
            </div>
            """
        
        # Generate Nuance Details card
        evidence_cards_html += f"""
        <div class="evidence-type-card" style="border-left-color: #667eea">
            <div class="evidence-type-header">
                <div class="evidence-type-title">
                    <span class="evidence-type-icon">🎯</span>
                    <span class="evidence-type-name">Nuance Details</span>
                </div>
                <div class="evidence-type-status">
                    <span class="status-icon">📋</span>
                    <span class="evidence-count">{total_evidence}</span>
                </div>
            </div>
            
            <div class="evidence-type-metrics">
                <div class="authority-metric">
                    <span class="metric-label">Coverage:</span>
                    <span class="metric-value">{min(total_evidence / 8.0, 1.0):.1%}</span>
                    <div class="authority-bar">
                        <div class="authority-fill" style="width: {min(total_evidence / 8.0 * 100, 100)}%; background: #667eea"></div>
                    </div>
                </div>
            </div>
            
            <div class="evidence-preview">
        """
        
        # Add top 3 nuances as preview
        for i, item in enumerate(evidence_list[:3]):
            phrase = item.get('phrase', 'Unknown')
            # Get search hits from metadata or use relevance_score as indicator
            metadata = item.get('metadata', {})
            hits = metadata.get('search_results_count', 0)
            if hits == 0:
                # If no search hits, show relevance score as percentage
                relevance = item.get('relevance_score', 0)
                display_text = f"{relevance:.1%} relevance"
            else:
                display_text = f"{hits:,} hits"
            
            evidence_cards_html += f"""
                <div class="evidence-preview-item">
                    <div class="evidence-preview-text">"{phrase}"</div>
                    <div class="evidence-preview-source">🔍 {display_text}</div>
                </div>
            """
        
        evidence_cards_html += f"""
            </div>
            
            <div class="evidence-type-actions">
                <button class="view-evidence-btn" onclick="toggleEvidenceType(this, 'nuance_details')" style="background: #667eea">
                    View All Nuances
                </button>
            </div>
        </div>
        """
        
        evidence_cards_html += """
        </div>
        """
        
        return summary_html + evidence_cards_html

    def _generate_nuance_evidence_type_card(self, title: str, icon: str, nuances_evidence: dict, color: str) -> str:
        """Generate a card for nuance evidence types."""
        evidence_count = 0
        authority_scores = []
        evidence_preview = ""
        
        # Aggregate data from all nuances
        for nuance_phrase, evidence_data in nuances_evidence.items():
            if isinstance(evidence_data, dict):
                pieces = evidence_data.get('evidence_pieces', [])
                evidence_count += len(pieces)
                
                for piece in pieces:
                    if isinstance(piece, dict):
                        authority_scores.append(piece.get('authority_score', 0))
        
        avg_authority = sum(authority_scores) / len(authority_scores) if authority_scores else 0
        
        # Generate preview based on card type
        if title == 'Nuance Validation Evidence':
            validated_count = sum(1 for _, data in nuances_evidence.items() 
                                if isinstance(data, dict) and data.get('validation_status') == 'validated')
            evidence_preview = f"""
            <div class="evidence-preview-item">
                <div class="evidence-preview-text">✅ {validated_count} nuances successfully validated</div>
                <div class="evidence-preview-source">🔍 Search validation enabled</div>
            </div>
            """
        elif title == 'Search Validation Results':
            total_hits = sum(data.get('search_hits', 0) for data in nuances_evidence.values() 
                           if isinstance(data, dict))
            evidence_preview = f"""
            <div class="evidence-preview-item">
                <div class="evidence-preview-text">📊 {total_hits:,} total search hits collected</div>
                <div class="evidence-preview-source">🌐 Multiple search engines</div>
            </div>
            """
        elif title == 'Source Authority Analysis':
            high_authority = sum(1 for score in authority_scores if score >= 0.7)
            evidence_preview = f"""
            <div class="evidence-preview-item">
                <div class="evidence-preview-text">🏛️ {high_authority} high-authority sources</div>
                <div class="evidence-preview-source">⭐ Avg authority: {avg_authority:.2f}</div>
            </div>
            """
        
        status_icon = "✅" if evidence_count > 0 else "❓"
        
        return f"""
        <div class="evidence-type-card" style="border-left-color: {color}">
            <div class="evidence-type-header">
                <div class="evidence-type-title">
                    <span class="evidence-type-icon">{icon}</span>
                    <span class="evidence-type-name">{title}</span>
                </div>
                <div class="evidence-type-status">
                    <span class="status-icon">{status_icon}</span>
                    <span class="evidence-count">{evidence_count}</span>
                </div>
            </div>
            
            <div class="evidence-type-metrics">
                <div class="authority-metric">
                    <span class="metric-label">Authority:</span>
                    <span class="metric-value">{avg_authority:.2f}</span>
                    <div class="authority-bar">
                        <div class="authority-fill" style="width: {avg_authority*100}%; background: {color}"></div>
                    </div>
                </div>
            </div>
            
            {f'<div class="evidence-preview">{evidence_preview}</div>' if evidence_preview else '<div class="no-evidence-preview">No evidence available</div>'}
            
            <div class="evidence-type-actions">
                <button class="view-evidence-btn" onclick="toggleEvidenceType(this, \'{title.lower().replace(' ', '_')}\')" style="background: {color}">
                    View All Evidence
                </button>
            </div>
        </div>
        """

    def _generate_evidence_type_card(self, title: str, icon: str, evidence_data: dict, color: str) -> str:
        """Generate a card for a specific evidence type."""
        evidence_count = evidence_data.get('total_evidence_count', 0)
        validation_status = evidence_data.get('validation_status', 'pending')
        authority_score = evidence_data.get('average_authority_score', 0)
        evidence_pieces = evidence_data.get('evidence_pieces', [])
        
        # Status indicator
        status_icons = {
            'validated': '✅',
            'partially_validated': '⚠️', 
            'unvalidated': '❌',
            'pending': '⏳'
        }
        status_icon = status_icons.get(validation_status, '❓')
        
        # Top evidence pieces
        evidence_preview = ""
        if evidence_pieces:
            top_pieces = evidence_pieces[:2]  # Show top 2
            for piece in top_pieces:
                evidence_preview += f"""
                <div class="evidence-preview-item">
                    <div class="evidence-preview-text">"{piece.get('text_content', '')[:100]}..."</div>
                    <div class="evidence-preview-source">{self._get_source_type_icon(piece.get('source_type', 'unknown'))} {piece.get('authority_score', 0):.2f}</div>
                </div>
                """
        
        return f"""
        <div class="evidence-type-card" style="border-left-color: {color}">
            <div class="evidence-type-header">
                <div class="evidence-type-title">
                    <span class="evidence-type-icon">{icon}</span>
                    <span class="evidence-type-name">{title}</span>
                </div>
                <div class="evidence-type-status">
                    <span class="status-icon">{status_icon}</span>
                    <span class="evidence-count">{evidence_count}</span>
                </div>
            </div>
            
            <div class="evidence-type-metrics">
                <div class="authority-metric">
                    <span class="metric-label">Authority:</span>
                    <span class="metric-value">{authority_score:.2f}</span>
                    <div class="authority-bar">
                        <div class="authority-fill" style="width: {authority_score*100}%; background: {color}"></div>
                    </div>
                </div>
            </div>
            
            {f'<div class="evidence-preview">{evidence_preview}</div>' if evidence_preview else '<div class="no-evidence-preview">No evidence available</div>'}
            
            <div class="evidence-type-actions">
                <button class="view-evidence-btn" onclick="toggleEvidenceType(this, \'{title.lower().replace(' ', '_')}\')" style="background: {color}">
                    View All Evidence
                </button>
            </div>
        </div>
        """

    def _generate_content_intelligence_card(self, title: str, icon: str, intelligence_data: dict, color: str) -> str:
        """Generate a card for content intelligence attributes."""
        
        # Count the number of data items in the intelligence
        data_count = 0
        preview_items = []
        
        if title == 'Iconic Landmarks':
            locations = intelligence_data.get('specific_locations', [])
            descriptions = intelligence_data.get('landmark_descriptions', {})
            data_count = len(locations)
            for location in locations[:2]:
                desc = descriptions.get(location, "")[:60] + "..." if descriptions.get(location, "") else ""
                preview_items.append(f"🏛️ {location}: {desc}")
        
        elif title == 'Practical Intelligence':
            costs = intelligence_data.get('specific_costs', {})
            timing = intelligence_data.get('timing_intelligence', {})
            tips = intelligence_data.get('practical_tips', [])
            data_count = len(costs) + len(timing) + len(tips)
            for category, cost in list(costs.items())[:2]:
                preview_items.append(f"💰 {category}: {cost}")
        
        elif title == 'Neighborhood Insights':
            neighborhoods = intelligence_data.get('neighborhood_names', [])
            personalities = intelligence_data.get('area_personalities', {})
            data_count = len(neighborhoods)
            for neighborhood in neighborhoods[:2]:
                personality = personalities.get(neighborhood, "")[:50] + "..." if personalities.get(neighborhood, "") else ""
                preview_items.append(f"🏘️ {neighborhood}: {personality}")
        
        elif title == 'Content Discovery':
            sources = intelligence_data.get('high_quality_sources', [])
            phrases = intelligence_data.get('extracted_phrases', [])
            data_count = len(sources) + len(phrases)
            for phrase in phrases[:2]:
                preview_items.append(f"📝 \"{phrase[:50]}...\"")
        
        # Generate preview HTML
        preview_html = ""
        if preview_items:
            preview_html = "".join([f'<div class="intelligence-preview-item">{item}</div>' for item in preview_items])
        
        # Determine status based on data availability
        status_icon = "✅" if data_count > 0 else "❓"
        data_quality = min(1.0, data_count / 3.0) if data_count > 0 else 0.0
        
        return f"""
        <div class="evidence-type-card" style="border-left-color: {color}">
            <div class="evidence-type-header">
                <div class="evidence-type-title">
                    <span class="evidence-type-icon">{icon}</span>
                    <span class="evidence-type-name">{title}</span>
                </div>
                <div class="evidence-type-status">
                    <span class="status-icon">{status_icon}</span>
                    <span class="evidence-count">{data_count}</span>
                </div>
            </div>
            
            <div class="evidence-type-metrics">
                <div class="authority-metric">
                    <span class="metric-label">Data Quality:</span>
                    <span class="metric-value">{data_quality:.2f}</span>
                    <div class="authority-bar">
                        <div class="authority-fill" style="width: {data_quality*100}%; background: {color}"></div>
                    </div>
                </div>
            </div>
            
            {f'<div class="evidence-preview">{preview_html}</div>' if preview_html else '<div class="no-evidence-preview">No data extracted</div>'}
            
            <div class="evidence-type-actions">
                <button class="view-evidence-btn" onclick="toggleContentIntelligence(this, \'{title.lower().replace(' ', '_')}\')" style="background: {color}">
                    View Intelligence Data
                </button>
            </div>
        </div>
        """
    
    def _generate_index_html(self, destination_data: dict) -> str:
        """Generate index page for multiple destinations."""
        
        destination_cards = []
        for dest_name, dest_info in destination_data.items():
            data = dest_info['data']
            # Get quality assessment from intelligence_insights.quality_assessment
            intelligence_insights = data.get('intelligence_insights', {})
            quality_assessment = intelligence_insights.get('quality_assessment', {})
            quality_score = quality_assessment.get('overall_score', 0)
            quality_level = quality_assessment.get('quality_level', self._get_quality_level(quality_score))
            theme_count = len(data.get('affinities', []))
            hidden_gems = intelligence_insights.get('hidden_gems_count', 0)
            
            destination_cards.append(f"""
            <div class="destination-index-card">
                <div class="dest-card-header">
                    <h3>{dest_name}</h3>
                    <span class="quality-badge quality-{quality_level.lower().replace(' ', '-')}">{quality_level}</span>
                </div>
                <div class="dest-card-stats">
                    <div class="stat"><strong>{theme_count}</strong> themes</div>
                    <div class="stat"><strong>{hidden_gems}</strong> hidden gems</div>
                    <div class="stat"><strong>{quality_score:.3f}</strong> quality score</div>
                </div>
                <a href="{dest_info['html_file']}" class="view-button">View Details</a>
            </div>
            """)
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Destination Insights Discovery - Multi-Destination Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        {self._get_enhanced_css()}
        
        .index-header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        
        .destinations-index-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .destination-index-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }}
        
        .destination-index-card:hover {{
            transform: translateY(-5px);
        }}
        
        .dest-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .dest-card-stats {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            font-size: 0.9rem;
            color: #666;
        }}
        
        .view-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 600;
            transition: transform 0.2s ease;
        }}
        
        .view-button:hover {{
            transform: scale(1.05);
            text-decoration: none;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
                    <div class="index-header">
                <h1>🧠 Destination Insights Discovery</h1>
                <p>Advanced Travel Intelligence & Destination Analysis</p>
            </div>
        
        <div class="destinations-index-grid">
            {"".join(destination_cards)}
        </div>
        
        <footer class="dashboard-footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Destination Insights Discovery</p>
        </footer>
    </div>
</body>
</html>
        """
    
    def _get_enhanced_css(self) -> str:
        """Get enhanced CSS styles for the viewer."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .destination-header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .header-top {
            margin-bottom: 1rem;
        }
        
        .back-button {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: #667eea;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            background: rgba(102, 126, 234, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.2);
            transition: all 0.3s ease;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .back-button:hover {
            background: rgba(102, 126, 234, 0.2);
            color: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        }
        
        .back-button i {
            font-size: 0.8rem;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .destination-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .quality-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .quality-excellent { background: #d4edda; color: #155724; }
        .quality-good { background: #cce5ff; color: #004085; }
        .quality-acceptable { background: #fff3cd; color: #856404; }
        .quality-needs-improvement { background: #f8d7da; color: #721c24; }
        .quality-unknown { background: #e2e3e5; color: #6c757d; }
        
        .header-stats {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.7);
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            min-width: 100px;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #333;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #666;
        }
        
        section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        section h2 {
            font-size: 1.8rem;
            margin-bottom: 20px;
            color: #333;
        }
        
        .themes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        
        .theme-card {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 15px;
            padding: 25px;
            border-left: 5px solid #667eea;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .theme-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
        }
        
        .theme-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        
        .theme-title-section {
            flex: 1;
        }
        
        .theme-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .theme-category {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .theme-quality-badge {
            background: #6c757d;
            color: white;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.7rem;
            font-weight: bold;
            margin-left: 8px;
        }
        
        .theme-quality-badge.quality-excellent { background: #28a745; }
        .theme-quality-badge.quality-good { background: #17a2b8; }
        .theme-quality-badge.quality-acceptable { background: #ffc107; color: #000; }
        .theme-quality-badge.quality-poor { background: #dc3545; }
        .theme-quality-badge.quality-unknown { background: #6c757d; }
        
        .confidence-score {
            background: #667eea;
            color: white;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .intelligence-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }
        
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            color: white;
            font-weight: 600;
            white-space: nowrap;
        }
        
        .theme-rationale {
            margin-bottom: 15px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 10px;
            font-style: italic;
        }
        
        /* Evidence validation styles */
        .evidence-validation {
            margin: 12px 0;
        }
        
        .evidence-status {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-left: 4px solid #6c757d;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 0.85rem;
        }
        
        .evidence-header {
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        /* Content Intelligence Styles */
        .content-intelligence-section {
            margin-top: 20px;
            border-top: 1px solid rgba(0, 0, 0, 0.1);
            padding-top: 20px;
        }
        
        .content-intelligence {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            overflow: hidden;
        }
        
        .ci-toggle {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 15px 20px;
            background: linear-gradient(135deg, #00355F, #004080);
            color: white;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s ease;
        }
        
        .ci-toggle:hover {
            background: linear-gradient(135deg, #004080, #0050A0);
        }
        
        .toggle-icon {
            transition: transform 0.3s ease;
            margin-right: 8px;
        }
        
        .ci-toggle.active .toggle-icon {
            transform: rotate(180deg);
        }
        
        .ci-badge {
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
        }
        
        .ci-content {
            padding: 0;
            background: rgba(255, 255, 255, 0.95);
        }
        
        .ci-section {
            padding: 20px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        .ci-section:last-child {
            border-bottom: none;
        }
        
        .ci-section h5 {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 15px;
            color: #00355F;
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        /* Landmarks Section */
        .landmark-item {
            margin-bottom: 15px;
            padding: 12px;
            background: rgba(0, 53, 95, 0.05);
            border-radius: 8px;
            border-left: 3px solid #00355F;
        }
        
        .landmark-name {
            font-weight: 600;
            color: #00355F;
            margin-bottom: 5px;
        }
        
        .landmark-description {
            font-size: 0.9rem;
            color: #666;
            line-height: 1.4;
        }
        
        .special-features {
            margin-top: 15px;
            padding: 12px;
            background: rgba(0, 53, 95, 0.03);
            border-radius: 8px;
        }
        
        .special-features ul {
            margin: 8px 0 0 20px;
        }
        
        /* Practical Section */
        .practical-costs, .practical-timing, .practical-tips {
            margin-bottom: 15px;
        }
        
        .practical-costs ul, .practical-timing ul, .practical-tips ul {
            margin: 8px 0 0 20px;
        }
        
        .practical-costs li, .practical-timing li, .practical-tips li {
            margin-bottom: 6px;
            color: #444;
        }
        
        /* Neighborhood Section */
        .neighborhood-item {
            margin-bottom: 15px;
            padding: 12px;
            background: rgba(0, 53, 95, 0.05);
            border-radius: 8px;
            border-left: 3px solid #00355F;
        }
        
        .neighborhood-name {
            font-weight: 600;
            color: #00355F;
            margin-bottom: 5px;
        }
        
        .neighborhood-personality {
            font-size: 0.9rem;
            color: #555;
            margin-bottom: 5px;
            font-style: italic;
        }
        
        .specialty {
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 5px;
        }
        
        .stay-advice {
            font-size: 0.85rem;
            color: #444;
            background: rgba(255, 255, 255, 0.5);
            padding: 6px 10px;
            border-radius: 5px;
            margin-top: 8px;
        }
        
        /* Discovery Section */
        .discovery-validation {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
        }
        
        .validation-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 10px;
            background: rgba(0, 53, 95, 0.05);
            border-radius: 8px;
            min-width: 80px;
        }
        
        .validation-label {
            font-size: 0.8rem;
            color: #666;
            margin-bottom: 3px;
        }
        
        .validation-value {
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .discovery-phrases ul {
            margin: 8px 0 0 20px;
        }
        
        .discovery-phrases li {
            margin-bottom: 6px;
            color: #444;
            font-style: italic;
        }
        
        .evidence-icon {
            font-size: 1rem;
        }
        
        .evidence-metrics {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 6px;
            margin-top: 6px;
        }
        
        .evidence-metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
        }
        
        .metric-label {
            color: #6c757d;
            font-weight: 500;
        }
        
        .metric-value {
            font-weight: 600;
            color: #212529;
        }
        
        .authority-bar {
            width: 40px;
            height: 4px;
            background: #e9ecef;
            border-radius: 2px;
            overflow: hidden;
            margin-left: 4px;
        }
        
        .authority-fill {
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .evidence-gaps {
            margin-top: 6px;
            font-size: 0.8rem;
        }
        
        .gap-tag {
            display: inline-block;
            background: #f8d7da;
            color: #721c24;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.75rem;
            margin: 0 2px;
        }
        
        .evidence-status.validated {
            background: #d4edda;
            border-color: #c3e6cb;
        }
        
        .evidence-status.partially_validated {
            background: #fff3cd;
            border-color: #ffeaa7;
        }
        
        .evidence-status.unvalidated {
            background: #f8d7da;
            border-color: #f5c6cb;
        }
        
        .evidence-status.no-evidence {
            background: #e2e3e5;
            border-color: #d6d8db;
        }
        
        /* Evidence pieces display */
        .evidence-pieces {
            margin-top: 15px;
        }
        
        .evidence-toggle {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 600;
            color: #495057;
            transition: all 0.3s ease;
        }
        
        .evidence-toggle:hover {
            background: #e9ecef;
        }
        
        .toggle-icon {
            transition: transform 0.3s ease;
            margin-right: 5px;
        }
        
        .evidence-toggle.expanded .toggle-icon {
            transform: rotate(180deg);
        }
        
        .evidence-content {
            margin-top: 10px;
        }
        
        .evidence-piece {
            background: #f8f9fa;
            border-left: 3px solid #dee2e6;
            border-radius: 6px;
            padding: 12px;
            margin: 8px 0;
        }
        
        .evidence-piece .evidence-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .source-icon {
            font-size: 1.1em;
            margin-right: 8px;
        }
        
        .authority-score {
            background: #6c757d;
            color: white;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.8em;
            font-weight: 600;
            margin-left: auto;
        }
        
        .evidence-text {
            font-style: italic;
            color: #495057;
            margin: 8px 0;
            line-height: 1.4;
        }
        
        .evidence-source {
            font-size: 0.8em;
            margin-top: 8px;
        }
        
        .evidence-source a {
            color: #007bff;
            text-decoration: none;
        }
        
        .evidence-source a:hover {
            text-decoration: underline;
        }
        
        .evidence-more {
            text-align: center;
            color: #6c757d;
            font-style: italic;
            margin-top: 10px;
            padding: 8px;
        }

        /* Evidence paperclip styling */
        .evidence-paperclip {
            margin-left: 8px;
            color: #007bff;
            cursor: pointer;
            font-size: 14px;
            transition: color 0.3s;
        }

        .evidence-paperclip:hover {
            color: #0056b3;
        }

        .evidence-paperclip.no-evidence {
            color: #6c757d;
            cursor: pointer;
        }
        
        .evidence-paperclip.no-evidence:hover {
            color: #495057;
        }

        /* Modal styling */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.4);
        }

        .modal-content {
            background-color: #fefefe;
            margin: 5% auto;
            padding: 0;
            border: none;
            border-radius: 8px;
            width: 80%;
            max-width: 800px;
            max-height: 80vh;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }

        .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .modal-header h2 {
            margin: 0;
            font-size: 20px;
        }

        .close {
            color: white;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            line-height: 1;
        }

        .close:hover {
            opacity: 0.7;
        }

        .modal-body {
            padding: 20px;
            max-height: 60vh;
            overflow-y: auto;
        }

        .evidence-section {
            margin-bottom: 20px;
        }

        .evidence-section h3 {
            color: #495057;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 8px;
            margin-bottom: 15px;
        }

        .evidence-item {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 12px;
        }

        .evidence-type-tag {
            background: #007bff;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            margin-bottom: 8px;
            display: inline-block;
        }

        .llm-generated-tag {
            background: #6f42c1;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 8px;
        }
        
        /* Comprehensive evidence section */
        .comprehensive-evidence {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin: 30px 0;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        
        .evidence-overview {
            margin-bottom: 30px;
        }
        
        .evidence-summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .evidence-stat {
            text-align: center;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
        }
        
        .evidence-stat .stat-value {
            font-size: 2em;
            font-weight: 700;
            color: #495057;
            margin-bottom: 5px;
        }
        
        .evidence-stat .stat-label {
            font-size: 0.9em;
            color: #6c757d;
            font-weight: 500;
        }
        
        .evidence-types-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
        }
        
        .evidence-type-card {
            background: rgba(255, 255, 255, 0.95);
            border-left: 4px solid #dee2e6;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .evidence-type-card:hover {
            transform: translateY(-2px);
        }
        
        .evidence-type-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .evidence-type-title {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .evidence-type-icon {
            font-size: 1.5em;
        }
        
        .evidence-type-name {
            font-weight: 600;
            color: #333;
            font-size: 1.1em;
        }
        
        .evidence-type-status {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .status-icon {
            font-size: 1.2em;
        }
        
        .evidence-count {
            background: #e9ecef;
            color: #495057;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.9em;
            font-weight: 600;
        }
        
        .evidence-type-metrics {
            margin: 15px 0;
        }
        
        .authority-metric {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .evidence-preview {
            margin: 15px 0;
        }
        
        .evidence-preview-item {
            background: #f8f9fa;
            border-radius: 6px;
            padding: 10px;
            margin: 8px 0;
            border-left: 3px solid #dee2e6;
        }
        
        .evidence-preview-text {
            font-style: italic;
            color: #495057;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .evidence-preview-source {
            font-size: 0.8em;
            color: #6c757d;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .no-evidence-preview {
            text-align: center;
            color: #6c757d;
            font-style: italic;
            padding: 15px;
        }
        
        .evidence-type-actions {
            margin-top: 15px;
        }
        
        .view-evidence-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 0.9em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .view-evidence-btn:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
        
        .theme-details {
            font-size: 0.9rem;
        }
        
        .detail-row {
            margin-bottom: 8px;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .sub-themes, .nano-themes {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }
        
        .sub-theme-tag {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 3px 8px;
            border-radius: 8px;
            font-size: 0.75rem;
        }
        
        .nano-theme-tag {
            background: rgba(220, 53, 69, 0.1);
            color: #dc3545;
            padding: 3px 8px;
            border-radius: 8px;
            font-size: 0.75rem;
        }
        
        .insights-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .insight-card {
            background: rgba(255, 255, 255, 0.7);
            border-radius: 15px;
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .insight-icon {
            font-size: 2rem;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(102, 126, 234, 0.1);
        }
        
        .insight-content h3 {
            margin: 0 0 5px 0;
            font-size: 1.1rem;
        }
        
        .insight-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #667eea;
        }
        
        .composition-content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
        }
        
        .composition-score {
            text-align: center;
            background: rgba(255, 255, 255, 0.5);
            padding: 20px;
            border-radius: 15px;
        }
        
        .score-value {
            font-size: 3rem;
            font-weight: 700;
            color: #667eea;
        }
        
        .category-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
        }
        
        .category-card {
            background: rgba(255, 255, 255, 0.5);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .category-name {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .category-count {
            font-size: 1.5rem;
            font-weight: 700;
            color: #667eea;
        }
        
        .quality-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .metrics-section h3 {
            margin-bottom: 15px;
            color: #495057;
        }
        
        .metrics-grid {
            display: grid;
            gap: 10px;
        }
        
        .metric-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 15px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 10px;
        }
        
        .metric-name {
            font-weight: 600;
        }
        
        .metric-value {
            font-weight: 700;
            font-size: 1.1rem;
        }
        
        .dashboard-footer {
            text-align: center;
            padding: 20px;
            color: rgba(255, 255, 255, 0.8);
            background: rgba(0, 0, 0, 0.1);
            border-radius: 15px;
            margin-top: 30px;
        }
        
        .no-data {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 40px;
        }
        
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .destination-title { font-size: 2rem; }
            .header-content { flex-direction: column; gap: 15px; }
            .header-stats { justify-content: center; }
            .themes-grid { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
            .composition-content { grid-template-columns: 1fr; }
            .quality-content { grid-template-columns: 1fr; }
        }
        
        /* Destination Nuances Styles */
        .destination-nuances {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
        }
        
        /* Destination Nuances Layout */
        .nuances-container-3tier {
            padding: 20px;
        }
        
        .nuances-summary {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .nuances-summary h2 {
            margin: 0 0 20px 0;
            color: #333;
            font-size: 1.8rem;
        }
        
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
        }
        
        .summary-stats .stat-card {
            background: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .stat-number {
            display: block;
            font-size: 1.8rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-label {
            display: block;
            font-size: 0.85rem;
            color: #666;
            font-weight: 500;
        }
        
        /* Main Destination Section (full width) */
        .main-destination-section {
            margin-bottom: 30px;
        }
        
        .main-destination-section .section-header {
            margin-bottom: 25px;
        }
        
        .main-destination-section h2 {
            color: #333;
            font-size: 1.6rem;
            margin: 0 0 10px 0;
        }
        
        /* Side-by-side Accommodation Sections */
        .accommodation-sections {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .accommodation-section {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(102, 126, 234, 0.1);
        }
        
        .accommodation-section h3 {
            color: #333;
            font-size: 1.4rem;
            margin: 0 0 10px 0;
        }
        
        .accommodation-section .section-description {
            background: rgba(102, 126, 234, 0.05);
            border-left: 4px solid #667eea;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        /* Feature Cards for all categories */
        .features-grid {
            display: grid;
            gap: 15px;
        }
        
        .destination-grid {
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }
        
        .hotel-grid, .vacation-rental-grid {
            grid-template-columns: 1fr;
        }
        
        .feature-card {
            background: linear-gradient(135deg, #fff, #f8f9fa);
            border-radius: 12px;
            padding: 18px;
            border-left: 4px solid #667eea;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
        }
        
        .feature-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }
        
        .feature-rank {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.8rem;
            flex-shrink: 0;
        }
        
        .feature-phrase {
            font-size: 1.1rem;
            font-weight: 600;
            color: #333;
            flex: 1;
        }
        
        .evidence-btn {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .evidence-btn:hover {
            background: rgba(102, 126, 234, 0.2);
            transform: translateY(-1px);
        }
        
        .feature-metrics {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .feature-score {
            font-size: 0.85rem;
        }
        
        .score-label {
            color: #666;
            font-weight: 500;
        }
        
        .score-value {
            font-weight: 600;
            margin: 0 5px;
        }
        
        .score-level {
            color: #888;
            font-style: italic;
        }
        
        .feature-category {
            font-size: 0.85rem;
        }
        
        .category-label {
            color: #666;
            font-weight: 500;
        }
        
        .category-value {
            color: #667eea;
            font-weight: 600;
            margin-left: 5px;
        }
        
        .feature-sources, .feature-validation {
            padding: 8px 12px;
            border-radius: 6px;
            margin-top: 8px;
        }
        
        .feature-sources {
            background: rgba(102, 126, 234, 0.05);
            border-left: 3px solid #667eea;
        }
        
        .feature-validation {
            background: rgba(40, 167, 69, 0.05);
            border-left: 3px solid #28a745;
        }
        
        .feature-sources small, .feature-validation small {
            font-size: 0.8rem;
            color: #666;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .accommodation-sections {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .destination-grid {
                grid-template-columns: 1fr;
            }
            
            .summary-stats {
                grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            }
        }
        
        .nuances-container {
            max-width: 100%;
        }
        
        .section-description {
            background: rgba(102, 126, 234, 0.05);
            border-left: 4px solid #667eea;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 25px;
        }
        
        .section-description p {
            margin: 0;
            color: #555;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        .nuances-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .nuances-stats .stat-item {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            border-left: 4px solid #667eea;
            transition: transform 0.2s ease;
        }
        
        .nuances-stats .stat-item:hover {
            transform: translateY(-2px);
        }
        
        .nuances-stats .stat-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #333;
            display: block;
        }
        
        .nuances-stats .stat-label {
            font-size: 0.85rem;
            color: #666;
            margin-top: 5px;
            display: block;
        }
        
        .nuances-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .nuance-card {
            background: linear-gradient(135deg, #fff, #f8f9fa);
            border-radius: 15px;
            padding: 20px;
            border-left: 5px solid #667eea;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            position: relative;
        }
        
        .nuance-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
        }
        
        .nuance-header {
            display: flex;
            align-items: flex-start;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .nuance-rank {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.9rem;
            flex-shrink: 0;
        }
        
        .nuance-content {
            flex: 1;
        }
        
        .nuance-phrase {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin: 0 0 8px 0;
            line-height: 1.3;
        }
        
        .nuance-meta {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .nuance-category {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .nuance-score {
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .nuance-sources {
            margin-top: 10px;
            padding: 8px 12px;
            background: rgba(102, 126, 234, 0.05);
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }
        
        .nuance-sources small {
            color: #666;
            font-size: 0.8rem;
        }
        
        .nuance-validation {
            margin-top: 8px;
            padding: 6px 10px;
            background: rgba(40, 167, 69, 0.05);
            border-radius: 8px;
            border-left: 3px solid #28a745;
        }
        
        .nuance-validation small {
            color: #28a745;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .nuances-metadata {
            background: rgba(102, 126, 234, 0.05);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }
        
        .processing-status {
            font-size: 1.1rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        
        .processing-details {
            color: #666;
        }
        
        .processing-details small {
            font-size: 0.9rem;
            line-height: 1.4;
        }
        
        /* Tabbed Interface Styles */
        .tabbed-content-section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .tab-navigation {
            display: flex;
            background: rgba(255, 255, 255, 0.9);
            border-bottom: 1px solid rgba(102, 126, 234, 0.1);
            padding: 8px;
            gap: 8px;
        }
        
        .tab-button {
            flex: 1;
            padding: 16px 24px;
            background: transparent;
            border: 2px solid transparent;
            color: #667eea;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            border-radius: 12px;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .tab-button:hover {
            background: rgba(102, 126, 234, 0.05);
            border-color: rgba(102, 126, 234, 0.2);
            transform: translateY(-1px);
        }
        
        .tab-button.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-color: transparent;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .tab-button.active:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
        }
        
        .tab-content {
            padding: 30px;
        }
        
        .tab-pane {
            display: none;
        }
        
        .tab-pane.active {
            display: block;
            animation: slideIn 0.4s ease-out;
        }
        
        @keyframes slideIn {
            from { 
                opacity: 0; 
                transform: translateY(20px); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0); 
            }
        }

        .analysis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        /* Seasonal Carousel Styles */
        .seasonal-carousel {
            margin: 20px 0;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            background: #fff;
        }

        .carousel-container {
            position: relative;
            height: 300px;
            overflow: hidden;
        }

        .carousel-slides {
            position: relative;
            width: 100%;
            height: 100%;
        }

        .carousel-item {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
        }

        .carousel-item.active {
            opacity: 1;
        }

        .carousel-item img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }

        .carousel-caption {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 10px 16px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
        }

        .season-icon {
            font-size: 18px;
        }

        .season-name {
            font-size: 14px;
        }

        .carousel-controls {
            position: absolute;
            bottom: 20px;
            right: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(255,255,255,0.9);
            padding: 8px 12px;
            border-radius: 25px;
            backdrop-filter: blur(10px);
        }

        .carousel-btn {
            background: none;
            border: none;
            color: #333;
            font-size: 16px;
            cursor: pointer;
            padding: 8px;
            border-radius: 50%;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
        }

        .carousel-btn:hover {
            background: rgba(0,0,0,0.1);
            transform: scale(1.1);
        }

        .carousel-indicators {
            display: flex;
            gap: 4px;
            margin: 0 8px;
        }

        .carousel-indicator {
            background: none;
            border: none;
            font-size: 16px;
            cursor: pointer;
            padding: 4px;
            border-radius: 50%;
            transition: all 0.2s ease;
            opacity: 0.6;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
        }

        .carousel-indicator:hover {
            opacity: 0.8;
            transform: scale(1.1);
        }

        .carousel-indicator.active {
            opacity: 1;
            background: rgba(0,0,0,0.1);
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .carousel-container {
                height: 250px;
            }
            
            .carousel-caption {
                bottom: 15px;
                left: 15px;
                padding: 8px 12px;
                font-size: 12px;
            }
            
            .carousel-controls {
                bottom: 15px;
                right: 15px;
                padding: 6px 8px;
            }
            
            .carousel-btn {
                width: 28px;
                height: 28px;
                font-size: 14px;
            }
            
            .carousel-indicator {
                width: 24px;
                height: 24px;
                font-size: 14px;
            }
        }
        
        /* Combined Quality Overview Styles */
        .combined-quality-overview {
            margin-bottom: 30px;
        }
        
        .quality-summary-card {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 15px;
            padding: 25px;
            border-left: 5px solid #667eea;
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .quality-summary-icon {
            font-size: 2.5rem;
            opacity: 0.8;
        }
        
        .quality-summary-content {
            flex: 1;
        }
        
        .quality-summary-content h3 {
            margin: 0 0 10px 0;
            color: #333;
            font-size: 1.2rem;
        }
        
        .combined-score {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .quality-level-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .quality-breakdown {
            display: flex;
            flex-direction: column;
            gap: 8px;
            min-width: 200px;
        }
        
        .breakdown-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9rem;
        }
        
        .breakdown-label {
            color: #666;
        }
        
        .breakdown-value {
            font-weight: 600;
        }
        
        /* Nuance Description Styles */
        .nuance-description {
            margin: 15px 0;
            padding: 12px;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }
        
        .description-preview {
            color: #555;
            line-height: 1.5;
            font-size: 0.9rem;
        }
        
        .description-full {
            color: #555;
            line-height: 1.5;
            font-size: 0.9rem;
            margin-top: 10px;
        }
        
        .expand-btn {
            background: none;
            border: none;
            color: #667eea;
            cursor: pointer;
            font-size: 0.8rem;
            margin-top: 8px;
            text-decoration: underline;
            padding: 0;
        }
        
        .expand-btn:hover {
            color: #764ba2;
        }
        
        /* Smaller quality score styles */
        .score-value-small {
            font-size: 0.9rem;
            font-weight: 600;
        }
        """
    
    def _get_enhanced_javascript(self) -> str:
        """Get enhanced JavaScript for interactivity."""
        return """
        // Evidence toggle functionality
        function toggleEvidence(element) {
            const content = element.nextElementSibling;
            const icon = element.querySelector('.toggle-icon');
            
            if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
                element.classList.add('expanded');
            } else {
                content.style.display = 'none';
                element.classList.remove('expanded');
            }
        }
        
        function toggleEvidenceType(button, evidenceType) {
            // This would expand detailed evidence view for each type
            console.log('Viewing evidence for:', evidenceType);
            // Future enhancement: show modal or expanded view
            button.textContent = button.textContent === 'View All Evidence' ? 'Hide Evidence' : 'View All Evidence';
        }
        
        // Content Intelligence toggle functionality
        function toggleContentIntelligence(element) {
            const content = element.nextElementSibling;
            const icon = element.querySelector('.toggle-icon');
            
            if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
                icon.textContent = '▲';
                element.classList.add('active');
            } else {
                content.style.display = 'none';
                icon.textContent = '▼';
                element.classList.remove('active');
            }
        }
        
        // Tab switching functionality
        function switchTab(tabName) {
            // Remove active class from all tabs and panes
            document.querySelectorAll('.tab-button').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            
            // Add active class to selected tab and pane
            document.getElementById(tabName + '-tab').classList.add('active');
            document.getElementById(tabName + '-pane').classList.add('active');
            
            // Also switch intelligence insights, destination insight analysis, and quality assessment
            const insightsSections = document.querySelectorAll('.insights-content, .quality-content');
            insightsSections.forEach(section => section.classList.remove('active'));
            
            if (tabName === 'themes') {
                // Show theme-related insights
                const themeInsights = document.getElementById('theme-insights');
                const themeComposition = document.getElementById('theme-composition');
                if (themeInsights) themeInsights.classList.add('active');
                if (themeComposition) themeComposition.classList.add('active');
            } else if (tabName === 'nuances') {
                // Show nuance-related insights
                const nuanceInsights = document.getElementById('nuance-insights');
                const nuanceAnalysis = document.getElementById('nuance-analysis');
                if (nuanceInsights) nuanceInsights.classList.add('active');
                if (nuanceAnalysis) nuanceAnalysis.classList.add('active');
            }
        }
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
        
        // Add loading animation
        document.addEventListener('DOMContentLoaded', function() {
            document.body.style.opacity = '0';
            document.body.style.transition = 'opacity 0.5s ease-in-out';
            setTimeout(() => {
                document.body.style.opacity = '1';
            }, 100);
            
            // Initialize evidence toggles
            console.log('Destination Insights Discovery loaded');
        });
        
        // Hover effects for theme cards
        document.querySelectorAll('.theme-card').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
        
        // Evidence modal functions
        function showEvidenceModal(themeName, evidenceData) {
            const modal = document.getElementById('evidenceModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalBody = document.getElementById('modalBody');
            
            modalTitle.textContent = 'Evidence for: ' + themeName;
            
            // Parse evidence data if it's a string
            let evidence;
            try {
                evidence = typeof evidenceData === 'string' ? JSON.parse(evidenceData) : evidenceData;
            } catch (e) {
                console.error('Error parsing evidence data:', e);
                modalBody.innerHTML = '<p>Error loading evidence data.</p>';
                modal.style.display = 'block';
                return;
            }
            
            // Generate modal content
            let modalContent = '';
            
            // Theme Evidence
            if (evidence.theme_evidence && evidence.theme_evidence.length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>🔍 Theme Evidence</h3>';
                evidence.theme_evidence.forEach(piece => {
                                            modalContent += `
                        <div class="evidence-item">
                            <div class="evidence-type-tag">Web Evidence</div>
                            <p><strong>Text:</strong> "${piece.text_content || 'No text available'}"</p>
                            <p><strong>Source:</strong> <a href="${piece.source_url || '#'}" target="_blank" style="color: #007bff; text-decoration: underline;">${piece.source_title || 'Unknown Source'}</a></p>
                            <p><strong>URL:</strong> <a href="${piece.source_url || '#'}" target="_blank" style="color: #007bff; text-decoration: underline; font-family: monospace; font-size: 0.9em;">${piece.source_url || 'No URL'}</a></p>
                            <p><strong>Authority Score:</strong> ${(piece.authority_score || 0).toFixed(2)}</p>
                            <p><strong>Quality:</strong> ${piece.quality_rating || 'Unknown'}</p>
                        </div>`;
                });
                modalContent += '</div>';
            }
            
            // Nano Themes
            if (evidence.nano_themes && evidence.nano_themes.length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>🔬 Nano Themes</h3>';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="evidence-type-tag">Detailed Insights</div>';
                modalContent += '<p>' + evidence.nano_themes.join(', ') + '</p>';
                modalContent += '</div>';
                modalContent += '</div>';
            }
            
            // Price Insights
            if (evidence.price_insights && Object.keys(evidence.price_insights).length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>💰 Price Information</h3>';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="evidence-type-tag">Price Analysis</div>';
                Object.entries(evidence.price_insights).forEach(([key, value]) => {
                    modalContent += `<p><strong>${key.replace('_', ' ').toUpperCase()}:</strong> ${value}</p>`;
                });
                modalContent += '</div>';
                modalContent += '</div>';
            }
            
            // Authenticity Analysis
            if (evidence.authenticity_analysis && Object.keys(evidence.authenticity_analysis).length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>🏛️ Authenticity Analysis</h3>';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="evidence-type-tag">Authenticity Metrics</div>';
                Object.entries(evidence.authenticity_analysis).forEach(([key, value]) => {
                    modalContent += `<p><strong>${key.replace('_', ' ').toUpperCase()}:</strong> ${value}</p>`;
                });
                modalContent += '</div>';
                modalContent += '</div>';
            }
            
            // Hidden Gem Score
            if (evidence.hidden_gem_score && Object.keys(evidence.hidden_gem_score).length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>💎 Hidden Gem Analysis</h3>';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="evidence-type-tag">Uniqueness Metrics</div>';
                Object.entries(evidence.hidden_gem_score).forEach(([key, value]) => {
                    modalContent += `<p><strong>${key.replace('_', ' ').toUpperCase()}:</strong> ${value}</p>`;
                });
                modalContent += '</div>';
                modalContent += '</div>';
            }
            
            // LLM Generated indicator
            if (evidence.llm_generated) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="llm-generated-tag">LLM Generated</div>';
                modalContent += '<p>This insight was generated by our AI system and may not have external web evidence.</p>';
                modalContent += '</div>';
                modalContent += '</div>';
            }
            
            if (!modalContent) {
                modalContent = '<p>No evidence data available for this theme.</p>';
            }
            
            modalBody.innerHTML = modalContent;
            modal.style.display = 'block';
        }
        
        function closeEvidenceModal() {
            const modal = document.getElementById('evidenceModal');
            modal.style.display = 'none';
        }
        
        // Close modal when clicking outside of it
        window.onclick = function(event) {
            const modal = document.getElementById('evidenceModal');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
        
        // Attribute-specific evidence modal
        function showAttributeEvidenceModal(themeName, attributeName, evidenceId) {
            console.log('Modal called with:', {themeName, attributeName, evidenceId});
            
            const modal = document.getElementById('evidenceModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalBody = document.getElementById('modalBody');
            
            if (!modal || !modalTitle || !modalBody) {
                console.error('Modal elements not found');
                return;
            }
            
            modalTitle.textContent = `Evidence for: ${themeName} - ${attributeName.replace('_', ' ')}`;
            
            // Get evidence data from global store
            const evidenceData = window.evidenceStore && window.evidenceStore[evidenceId];
            if (!evidenceData) {
                console.error('Evidence not found for ID:', evidenceId);
                console.log('Available evidence IDs:', Object.keys(window.evidenceStore || {}));
                modalBody.innerHTML = '<div class="alert alert-warning">Evidence data not available for this attribute.</div>';
                modal.style.display = 'block';
                return;
            }
            
            console.log('Evidence data found:', evidenceData);
            
            // Generate modal content for attribute evidence
            let modalContent = '';
            
            // Show the attribute data
            modalContent += '<div class="evidence-section">';
            modalContent += `<h3>📊 ${attributeName.replace('_', ' ').toUpperCase()} Data</h3>`;
            modalContent += '<div class="evidence-item">';
            modalContent += '<div class="evidence-type-tag">LLM Generated</div>';
            modalContent += `<p><strong>Value:</strong> ${JSON.stringify(evidenceData.attribute_data, null, 2)}</p>`;
            modalContent += '</div>';
            modalContent += '</div>';
            
            // Show theme evidence first (web evidence that supports the theme)
            if (evidenceData.theme_evidence && evidenceData.theme_evidence.length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>🔍 Theme Web Evidence</h3>';
                modalContent += '<p style="color: #666; font-style: italic; margin-bottom: 15px;">Web evidence supporting the overall theme (this attribute is part of this theme)</p>';
                
                evidenceData.theme_evidence.forEach((piece, index) => {
                    const hasUrl = piece.source_url && piece.source_url !== '#' && piece.source_url !== '';
                    modalContent += `
                    <div class="evidence-item">
                        <div class="evidence-type-tag">${hasUrl ? 'Web Evidence' : 'Content Evidence'} ${index + 1}</div>
                        <p><strong>Text:</strong> "${piece.text_content || 'No text available'}"</p>
                        ${hasUrl ? `<p><strong>Source:</strong> <a href="${piece.source_url}" target="_blank" style="color: #007bff; text-decoration: underline;">${piece.source_title || 'View Source'}</a></p>` : `<p><strong>Source:</strong> ${piece.source_title || 'AI Generated'}</p>`}
                        ${hasUrl ? `<p><strong>URL:</strong> <a href="${piece.source_url}" target="_blank" style="color: #007bff; text-decoration: underline; font-family: monospace; font-size: 0.9em; word-break: break-all;">${piece.source_url}</a></p>` : ''}
                        <p><strong>Authority Score:</strong> ${(piece.authority_score || 0).toFixed(2)}</p>
                        <p><strong>Quality:</strong> ${piece.quality_rating || 'Unknown'}</p>
                        <p><strong>Source Type:</strong> ${piece.source_type || 'web'}</p>
                    </div>`;
                });
                modalContent += '</div>';
            }
            
            // Show attribute-specific evidence if available
            if (evidenceData.evidence && Object.keys(evidenceData.evidence).length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>🔍 Supporting Evidence</h3>';
                
                const evidenceObj = evidenceData.evidence;
                let evidencePieces = [];
                
                // Handle direct evidence structure: evidenceData.evidence.evidence_pieces
                if (evidenceObj.evidence_pieces && evidenceObj.evidence_pieces.length > 0) {
                    evidencePieces = evidenceObj.evidence_pieces;
                } 
                // Handle nested sub-theme structure: evidenceData.evidence["Sub Theme Name"].evidence_pieces
                else {
                    // Look for nested sub-themes or other structures
                    Object.values(evidenceObj).forEach(subEvidence => {
                        if (subEvidence && subEvidence.evidence_pieces && subEvidence.evidence_pieces.length > 0) {
                            evidencePieces = evidencePieces.concat(subEvidence.evidence_pieces);
                        }
                    });
                }
                
                if (evidencePieces.length > 0) {
                    evidencePieces.forEach(piece => {
                        modalContent += `
                        <div class="evidence-item">
                            <div class="evidence-type-tag">Web Evidence</div>
                            <p><strong>Text:</strong> "${piece.text_content || 'No text available'}"</p>
                            <p><strong>Source:</strong> <a href="${piece.source_url || '#'}" target="_blank" style="color: #007bff; text-decoration: underline;">${piece.source_title || 'Unknown Source'}</a></p>
                            <p><strong>URL:</strong> <a href="${piece.source_url || '#'}" target="_blank" style="color: #007bff; text-decoration: underline; font-family: monospace; font-size: 0.9em;">${piece.source_url || 'No URL'}</a></p>
                            <p><strong>Authority Score:</strong> ${(piece.authority_score || 0).toFixed(2)}</p>
                            <p><strong>Quality:</strong> ${piece.quality_rating || 'Unknown'}</p>
                        </div>`;
                    });
                } else {
                    modalContent += '<div class="evidence-item">';
                    modalContent += '<div class="evidence-type-tag">No Evidence</div>';
                    modalContent += '<p>No web evidence found to support this attribute. This data was generated by the AI system.</p>';
                    modalContent += '</div>';
                }
                
                modalContent += '</div>';
            } else if (!evidenceData.theme_evidence || evidenceData.theme_evidence.length === 0) {
                // Only show "no evidence" if there's no theme evidence either
                modalContent += '<div class="evidence-section">';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="llm-generated-tag">LLM Generated</div>';
                modalContent += '<p>This attribute was generated by our AI system and does not have external web evidence.</p>';
                modalContent += '</div>';
                modalContent += '</div>';
            }
            
            modalBody.innerHTML = modalContent;
            modal.style.display = 'block';
        }
        
        // Theme-level evidence modal
        function showThemeEvidenceModal(themeName, evidenceId) {
            console.log('Theme modal called with:', {themeName, evidenceId});
            
            const modal = document.getElementById('evidenceModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalBody = document.getElementById('modalBody');
            
            if (!modal || !modalTitle || !modalBody) {
                console.error('Modal elements not found');
                return;
            }
            
            modalTitle.textContent = `Evidence for: ${themeName}`;
            
            // Get evidence data from global store
            const evidenceData = window.evidenceStore && window.evidenceStore[evidenceId];
            if (!evidenceData) {
                console.error('Evidence not found for ID:', evidenceId);
                console.log('Available evidence IDs:', Object.keys(window.evidenceStore || {}));
                modalBody.innerHTML = '<div class="alert alert-warning">Evidence data not available for this theme.</div>';
                modal.style.display = 'block';
                return;
            }
            
            console.log('Theme evidence data found:', evidenceData);
            
            // Generate modal content for theme evidence
            let modalContent = '';
            
            // Theme Evidence - check both theme_evidence and main_theme.evidence_pieces
            let themeEvidencePieces = [];
            if (evidenceData.theme_evidence && evidenceData.theme_evidence.length > 0) {
                themeEvidencePieces = evidenceData.theme_evidence;
            } else if (evidenceData.main_theme && evidenceData.main_theme.evidence_pieces && evidenceData.main_theme.evidence_pieces.length > 0) {
                themeEvidencePieces = evidenceData.main_theme.evidence_pieces;
            }
            
            if (themeEvidencePieces.length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>🔍 Web Evidence Sources</h3>';
                themeEvidencePieces.forEach((piece, index) => {
                    const hasUrl = piece.source_url && piece.source_url !== '#' && piece.source_url !== '';
                    modalContent += `
                    <div class="evidence-item">
                        <div class="evidence-type-tag">${hasUrl ? 'Web Evidence' : 'Content Evidence'} ${index + 1}</div>
                        <p><strong>Text:</strong> "${piece.text_content || 'No text available'}"</p>
                        ${hasUrl ? `<p><strong>Source:</strong> <a href="${piece.source_url}" target="_blank" style="color: #007bff; text-decoration: underline;">${piece.source_title || 'View Source'}</a></p>` : `<p><strong>Source:</strong> ${piece.source_title || 'AI Generated'}</p>`}
                        ${hasUrl ? `<p><strong>URL:</strong> <a href="${piece.source_url}" target="_blank" style="color: #007bff; text-decoration: underline; font-family: monospace; font-size: 0.9em; word-break: break-all;">${piece.source_url}</a></p>` : ''}
                        <p><strong>Authority Score:</strong> ${(piece.authority_score || 0).toFixed(2)}</p>
                        <p><strong>Quality:</strong> ${piece.quality_rating || 'Unknown'}</p>
                        <p><strong>Source Type:</strong> ${piece.source_type || 'web'}</p>
                    </div>`;
                });
                modalContent += '</div>';
            }
            
            // Nano Themes
            if (evidenceData.nano_themes && evidenceData.nano_themes.length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>🔬 Nano Themes</h3>';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="evidence-type-tag">Detailed Insights</div>';
                modalContent += '<p>' + evidenceData.nano_themes.join(', ') + '</p>';
                modalContent += '</div>';
                modalContent += '</div>';
            }
            
            // Price Insights
            if (evidenceData.price_insights && Object.keys(evidenceData.price_insights).length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>💰 Price Information</h3>';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="evidence-type-tag">Price Analysis</div>';
                Object.entries(evidenceData.price_insights).forEach(([key, value]) => {
                    modalContent += `<p><strong>${key.replace('_', ' ').toUpperCase()}:</strong> ${value}</p>`;
                });
                modalContent += '</div>';
                modalContent += '</div>';
            }
            
            // Authenticity Analysis
            if (evidenceData.authenticity_analysis && Object.keys(evidenceData.authenticity_analysis).length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>🏛️ Authenticity Analysis</h3>';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="evidence-type-tag">Authenticity Metrics</div>';
                Object.entries(evidenceData.authenticity_analysis).forEach(([key, value]) => {
                    modalContent += `<p><strong>${key.replace('_', ' ').toUpperCase()}:</strong> ${value}</p>`;
                });
                modalContent += '</div>';
                modalContent += '</div>';
            }
            
            // Hidden Gem Score
            if (evidenceData.hidden_gem_score && Object.keys(evidenceData.hidden_gem_score).length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>💎 Hidden Gem Analysis</h3>';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="evidence-type-tag">Uniqueness Metrics</div>';
                Object.entries(evidenceData.hidden_gem_score).forEach(([key, value]) => {
                    modalContent += `<p><strong>${key.replace('_', ' ').toUpperCase()}:</strong> ${value}</p>`;
                });
                modalContent += '</div>';
                modalContent += '</div>';
            }
            
            // Show comprehensive evidence methodology for themes
            const themeEvidenceSources = evidenceData.evidence_sources || [];
            const themeSourceModels = evidenceData.source_models || [];
            const isThemeSearchValidated = themeEvidenceSources.includes('search_validation');
            const isThemeFallbackValidated = themeEvidenceSources.includes('fallback_validation');
            
            modalContent += '<div class="evidence-section">';
            modalContent += '<h3>🔬 Evidence Methodology</h3>';
            modalContent += '<div class="evidence-item">';
            
            if (isThemeSearchValidated && themeSourceModels.length > 0) {
                modalContent += '<div class="evidence-type-tag">LLM + Search Validation</div>';
                modalContent += `<p><strong>Content Generation:</strong> LLM-generated by ${themeSourceModels.join(', ')}</p>`;
                modalContent += `<p><strong>Validation Method:</strong> Web search confirmed this theme exists in real travel content</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> LLM Generated theme validated through search_validation</p>`;
            } else if (isThemeSearchValidated) {
                modalContent += '<div class="evidence-type-tag">Search Validation</div>';
                modalContent += `<p><strong>Content Generation:</strong> LLM-generated (source models not recorded)</p>`;
                modalContent += `<p><strong>Validation Method:</strong> Web search confirmed this theme exists in real travel content</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> LLM Generated theme validated through search_validation</p>`;
            } else if (isThemeFallbackValidated && themeSourceModels.length > 0) {
                modalContent += '<div class="evidence-type-tag">LLM + Confidence Scoring</div>';
                modalContent += `<p><strong>Content Generation:</strong> LLM-generated by ${themeSourceModels.join(', ')}</p>`;
                modalContent += `<p><strong>Validation Method:</strong> Confidence-based scoring (no web search results found)</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> LLM Generated theme with fallback_validation</p>`;
            } else if (isThemeFallbackValidated) {
                modalContent += '<div class="evidence-type-tag">Confidence Scoring</div>';
                modalContent += `<p><strong>Content Generation:</strong> LLM-generated (source models not recorded)</p>`;
                modalContent += `<p><strong>Validation Method:</strong> Confidence-based scoring (no web search results found)</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> LLM Generated theme with fallback_validation</p>`;
            } else if (themeSourceModels.length > 0) {
                modalContent += '<div class="evidence-type-tag">LLM Generation</div>';
                modalContent += `<p><strong>Content Generation:</strong> LLM-generated by ${themeSourceModels.join(', ')}</p>`;
                modalContent += `<p><strong>Validation Method:</strong> No validation method recorded</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> LLM Generated theme (validation method unknown)</p>`;
            } else if (themeEvidenceSources.length > 0) {
                modalContent += '<div class="evidence-type-tag">Recorded Methodology</div>';
                modalContent += `<p><strong>Content Generation:</strong> Source not recorded</p>`;
                modalContent += `<p><strong>Validation Method:</strong> ${themeEvidenceSources.join(', ')}</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> Evidence methodology: ${themeEvidenceSources.join(', ')}</p>`;
            } else if (evidenceData.llm_generated) {
                modalContent += '<div class="evidence-type-tag">LLM Generation</div>';
                modalContent += `<p><strong>Content Generation:</strong> LLM-generated (models not specified)</p>`;
                modalContent += `<p><strong>Validation Method:</strong> No validation method recorded</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> LLM Generated theme (validation method unknown)</p>`;
            } else {
                modalContent += '<div class="evidence-type-tag">Unknown Methodology</div>';
                modalContent += `<p><strong>Content Generation:</strong> Method not recorded</p>`;
                modalContent += `<p><strong>Validation Method:</strong> Method not recorded</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> Methodology information incomplete</p>`;
            }
            
            modalContent += '</div>';
            modalContent += '</div>';
            
            if (!modalContent) {
                modalContent = '<p>No evidence data available for this theme.</p>';
            }
            
            modalBody.innerHTML = modalContent;
            modal.style.display = 'block';
        }
        
        // Nuance evidence modal
        function showNuanceEvidenceModal(nuancePhrase, evidenceId) {
            console.log('Nuance modal called with:', {nuancePhrase, evidenceId});
            
            const modal = document.getElementById('evidenceModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalBody = document.getElementById('modalBody');
            
            if (!modal || !modalTitle || !modalBody) {
                console.error('Modal elements not found');
                return;
            }
            
            modalTitle.textContent = `Evidence for: ${nuancePhrase}`;
            
            // Get evidence data from global store
            const evidenceData = window.evidenceStore && window.evidenceStore[evidenceId];
            if (!evidenceData) {
                console.error('Evidence not found for ID:', evidenceId);
                console.log('Available evidence IDs:', Object.keys(window.evidenceStore || {}));
                modalBody.innerHTML = '<div class="alert alert-warning">Evidence data not available for this nuance.</div>';
                modal.style.display = 'block';
                return;
            }
            
            console.log('Nuance evidence data found:', evidenceData);
            
            // Generate modal content for nuance evidence
            let modalContent = '';
            
            // Show nuance details
            modalContent += '<div class="evidence-section">';
            modalContent += '<h3>🎯 Nuance Details</h3>';
            modalContent += '<div class="evidence-item">';
            modalContent += '<div class="evidence-type-tag">Destination Feature</div>';
            modalContent += `<p><strong>Phrase:</strong> "${evidenceData.nuance_phrase}"</p>`;
            modalContent += `<p><strong>Category:</strong> ${evidenceData.category || 'general'}</p>`;
            modalContent += `<p><strong>Quality Score:</strong> ${(evidenceData.score || 0).toFixed(3)}</p>`;
            modalContent += `<p><strong>Confidence:</strong> ${(evidenceData.confidence || 0).toFixed(2)}</p>`;
            modalContent += '</div>';
            modalContent += '</div>';
            
            // Show validation data based on actual validation method
            const evidenceSources = evidenceData.evidence_sources || [];
            const validationData = evidenceData.validation_metadata || {};
            const isSearchValidated = evidenceSources.includes('search_validation') && validationData.authority_validated !== false;
            const isFallbackValidated = evidenceSources.includes('fallback_validation') || validationData.validation_method === 'fallback_confidence';
            
            if (isSearchValidated) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>🔍 Web Validation Results</h3>';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="evidence-type-tag">Search Confirmation</div>';
                modalContent += `<p><strong>Search Hits:</strong> ${evidenceData.search_hits.toLocaleString()}</p>`;
                modalContent += `<p><strong>Uniqueness Ratio:</strong> ${(evidenceData.uniqueness_ratio || 0).toFixed(2)}x</p>`;
                modalContent += '<p><strong>Validation Result:</strong> Web search confirmed this LLM-generated nuance appears in real travel content</p>';
                modalContent += '</div>';
                modalContent += '</div>';
            } else if (isFallbackValidated) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>⚠️ Confidence-Based Validation</h3>';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="llm-generated-tag">Fallback Scoring</div>';
                modalContent += `<p><strong>Confidence Score:</strong> ${(validationData.confidence_score || evidenceData.confidence || 0).toFixed(3)}</p>`;
                modalContent += `<p><strong>Validation Result:</strong> This LLM-generated nuance was scored using confidence-based methods when web search found no results</p>`;
                const fallbackReason = validationData.search_fallback_reason || 'unknown';
                const reasonText = fallbackReason === 'no_search_results_found' ? 'No web search results found for this specific phrase' : 
                                 fallbackReason === 'rate_limit_or_api_issue' ? 'Search API rate limits or issues' : fallbackReason;
                modalContent += `<p><strong>Reason:</strong> ${reasonText}</p>`;
                modalContent += '</div>';
                modalContent += '</div>';
            } else {
                modalContent += '<div class="evidence-section">';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="llm-generated-tag">Unknown Validation</div>';
                modalContent += '<p>Validation method could not be determined for this nuance.</p>';
                modalContent += '</div>';
                modalContent += '</div>';
            }
            
            // Show source URLs from evidence store or nuances evidence data
            let sourceUrls = [];
            
            // First try to get URLs from the evidence store
            if (evidenceData.source_urls && evidenceData.source_urls.length > 0) {
                sourceUrls = evidenceData.source_urls;
            }
            
            // Also check the nuances evidence data for authority sources
            if (window.nuancesEvidenceData && window.nuancesEvidenceData[evidenceData.nuance_phrase]) {
                const nuanceEvidence = window.nuancesEvidenceData[evidenceData.nuance_phrase];
                if (nuanceEvidence.authority_sources && nuanceEvidence.authority_sources.length > 0) {
                    // Combine with existing URLs, avoiding duplicates
                    nuanceEvidence.authority_sources.forEach(url => {
                        if (url && !sourceUrls.includes(url)) {
                            sourceUrls.push(url);
                        }
                    });
                }
            }
            
            if (sourceUrls.length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>🌐 Validation URLs</h3>';
                modalContent += '<p style="font-size: 0.9em; color: #666; margin-bottom: 15px;"><em>Web sources that confirm this LLM-generated nuance exists in real travel content:</em></p>';
                
                sourceUrls.forEach((url, index) => {
                    // Skip fallback URLs that are just placeholders
                    if (url && !url.includes('fallback-evidence') && url !== 'https://search.brave.com/') {
                        modalContent += '<div class="evidence-item">';
                        modalContent += '<div class="evidence-type-tag">Validation Source</div>';
                        modalContent += `<p><strong>Validation URL ${index + 1}:</strong></p>`;
                        modalContent += `<p><a href="${url}" target="_blank" style="color: #007bff; text-decoration: underline; word-break: break-all;">${url}</a></p>`;
                        modalContent += '</div>';
                    }
                });
                
                modalContent += '</div>';
            }
            
                        // Show comprehensive evidence methodology
            const methodologyEvidenceSources = evidenceData.evidence_sources || [];
            const sourceModels = evidenceData.source_models || [];
            const isMethodologySearchValidated = methodologyEvidenceSources.includes('search_validation');
            const isMethodologyFallbackValidated = methodologyEvidenceSources.includes('fallback_validation');
            
            modalContent += '<div class="evidence-section">';
            modalContent += '<h3>🔬 Evidence Methodology</h3>';
            modalContent += '<div class="evidence-item">';
            
            if (isMethodologySearchValidated && sourceModels.length > 0) {
                modalContent += '<div class="evidence-type-tag">LLM + Search Validation</div>';
                modalContent += `<p><strong>Content Generation:</strong> LLM-generated by ${sourceModels.join(', ')}</p>`;
                modalContent += `<p><strong>Validation Method:</strong> Web search confirmed this nuance exists in real travel content</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> LLM Generated content validated through search_validation</p>`;
            } else if (isMethodologySearchValidated) {
                modalContent += '<div class="evidence-type-tag">Search Validation</div>';
                modalContent += `<p><strong>Content Generation:</strong> LLM-generated (source models not recorded)</p>`;
                modalContent += `<p><strong>Validation Method:</strong> Web search confirmed this nuance exists in real travel content</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> LLM Generated content validated through search_validation</p>`;
            } else if (isMethodologyFallbackValidated && sourceModels.length > 0) {
                modalContent += '<div class="evidence-type-tag">LLM + Confidence Scoring</div>';
                modalContent += `<p><strong>Content Generation:</strong> LLM-generated by ${sourceModels.join(', ')}</p>`;
                modalContent += `<p><strong>Validation Method:</strong> Confidence-based scoring (no web search results found)</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> LLM Generated content with fallback_validation</p>`;
            } else if (isMethodologyFallbackValidated) {
                modalContent += '<div class="evidence-type-tag">Confidence Scoring</div>';
                modalContent += `<p><strong>Content Generation:</strong> LLM-generated (source models not recorded)</p>`;
                modalContent += `<p><strong>Validation Method:</strong> Confidence-based scoring (no web search results found)</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> LLM Generated content with fallback_validation</p>`;
            } else if (sourceModels.length > 0) {
                modalContent += '<div class="evidence-type-tag">LLM Generation</div>';
                modalContent += `<p><strong>Content Generation:</strong> LLM-generated by ${sourceModels.join(', ')}</p>`;
                modalContent += `<p><strong>Validation Method:</strong> No validation method recorded</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> LLM Generated content (validation method unknown)</p>`;
            } else if (methodologyEvidenceSources.length > 0) {
                modalContent += '<div class="evidence-type-tag">Recorded Methodology</div>';
                modalContent += `<p><strong>Content Generation:</strong> Source not recorded</p>`;
                modalContent += `<p><strong>Validation Method:</strong> ${methodologyEvidenceSources.join(', ')}</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> Evidence methodology: ${methodologyEvidenceSources.join(', ')}</p>`;
            } else {
                modalContent += '<div class="evidence-type-tag">Unknown Methodology</div>';
                modalContent += `<p><strong>Content Generation:</strong> Method not recorded</p>`;
                modalContent += `<p><strong>Validation Method:</strong> Method not recorded</p>`;
                modalContent += `<p><strong>Evidence Type:</strong> Methodology information incomplete</p>`;
            }
            
            modalContent += '</div>';
            modalContent += '</div>';
            
            if (!modalContent) {
                modalContent = '<p>No evidence data available for this nuance.</p>';
            }
            
            modalBody.innerHTML = modalContent;
            modal.style.display = 'block';
        }

        // Seasonal Carousel Functions
        let currentSeasonIndex = 0;
        const totalSeasons = 4;

        function changeSeasonalImage(direction) {
            currentSeasonIndex += direction;
            
            if (currentSeasonIndex >= totalSeasons) {
                currentSeasonIndex = 0;
            } else if (currentSeasonIndex < 0) {
                currentSeasonIndex = totalSeasons - 1;
            }
            
            showSeasonalImage(currentSeasonIndex);
        }

        function showSeasonalImage(index) {
            currentSeasonIndex = index;
            
            // Update carousel items
            const carouselItems = document.querySelectorAll('.carousel-item');
            const indicators = document.querySelectorAll('.carousel-indicator');
            
            carouselItems.forEach((item, i) => {
                if (i === index) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
            
            indicators.forEach((indicator, i) => {
                if (i === index) {
                    indicator.classList.add('active');
                } else {
                    indicator.classList.remove('active');
                }
            });
        }

        // Auto-advance carousel every 5 seconds
        setInterval(() => {
            changeSeasonalImage(1);
        }, 5000);

        // Keyboard navigation for carousel
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                changeSeasonalImage(-1);
            } else if (e.key === 'ArrowRight') {
                changeSeasonalImage(1);
            }
        });
    </script>
</body>
</html>
        """
    
    def _get_confidence_color(self, confidence: float) -> str:
        """Get color based on confidence score."""
        if confidence >= 0.8:
            return '#28a745'  # Green
        elif confidence >= 0.6:
            return '#ffc107'  # Yellow
        elif confidence >= 0.4:
            return '#fd7e14'  # Orange
        else:
            return '#dc3545'  # Red
    
    def _get_quality_level(self, score: float) -> str:
        """Get quality level from score."""
        if score >= 0.85:
            return 'Excellent'
        elif score >= 0.75:
            return 'Good'
        elif score >= 0.65:
            return 'Acceptable'
        else:
            return 'Needs Improvement'
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize destination name for filename."""
        return "".join(c.lower() if c.isalnum() else '_' for c in name).strip('_')
    
    def _get_evidence_store_json(self) -> str:
        """Get the evidence store as JSON string for JavaScript."""
        if not hasattr(self, '_evidence_store') or not self._evidence_store:
            return '{}'
        
        import json
        try:
            return json.dumps(self._evidence_store, default=str)
        except Exception as e:
            logger.warning(f"Error serializing evidence store: {e}")
            return '{}'
    
    def _get_nuances_evidence_json(self) -> str:
        """Get nuances evidence data as JSON string for JavaScript."""
        if not hasattr(self, '_nuances_evidence_data') or not self._nuances_evidence_data:
            return '{}'
        
        import json
        try:
            # Convert evidence list to phrase-keyed dictionary for easy lookup
            evidence_dict = {}
            
            # Handle both list and dict formats for nuances evidence data
            if isinstance(self._nuances_evidence_data, dict):
                evidence_list = self._nuances_evidence_data.get('evidence', [])
            elif isinstance(self._nuances_evidence_data, list):
                evidence_list = self._nuances_evidence_data
            else:
                evidence_list = []
            
            for evidence_item in evidence_list:
                if isinstance(evidence_item, dict):
                    phrase = evidence_item.get('phrase', '')
                    if phrase:
                        evidence_dict[phrase] = evidence_item
            
            return json.dumps(evidence_dict, default=str)
        except Exception as e:
            logger.warning(f"Error serializing nuances evidence data: {e}")
            return '{}'
    
    def _generate_destination_nuances(self, nuances_data: dict, nuances_evidence_data: dict = None, nuances_summary: dict = None) -> str:
        """Generate HTML for destination nuances display - supports all formats."""
        # Check for old 3-tier format with separate arrays
        has_destination_nuances = 'destination_nuances' in nuances_data
        has_hotel_expectations = 'hotel_expectations' in nuances_data  
        has_vacation_rental = 'vacation_rental_expectations' in nuances_data
        
        if has_destination_nuances or has_hotel_expectations or has_vacation_rental:
            return self._generate_3_tier_nuances_display(nuances_data, nuances_evidence_data)
        
        # Check for current unified format (single array with category fields)
        unified_nuances = nuances_data.get('nuances', [])
        if unified_nuances and any(nuance.get('category') for nuance in unified_nuances):
            # Convert unified format to 3-tier format for display
            converted_data = self._convert_unified_to_3tier(nuances_data)
            return self._generate_3_tier_nuances_display(converted_data, nuances_evidence_data)
        
        # Check for legacy nuances format (no categories)
        elif unified_nuances:
            return self._generate_legacy_nuances_display(nuances_data, nuances_evidence_data)
        
        else:
            return '''
            <p class="no-data">No destination insights available.</p>
            <p class="suggestion">Run the nuance generation to get destination nuances, hotel expectations, and vacation rental expectations.</p>
            '''
    
    def _convert_unified_to_3tier(self, nuances_data: dict) -> dict:
        """Convert unified format (single array with categories) to 3-tier format for display."""
        unified_nuances = nuances_data.get('nuances', [])
        
        # Separate nuances by category
        destination_nuances = []
        hotel_expectations = []
        vacation_rental_expectations = []
        
        for nuance in unified_nuances:
            category = nuance.get('category', 'destination')
            
            if category == 'destination':
                destination_nuances.append(nuance)
            elif category == 'hotel':
                hotel_expectations.append(nuance)
            elif category == 'vacation_rental':
                vacation_rental_expectations.append(nuance)
            else:
                # Default unknown categories to destination
                destination_nuances.append(nuance)
        
        # Create converted data structure
        converted_data = nuances_data.copy()
        converted_data['destination_nuances'] = destination_nuances
        converted_data['hotel_expectations'] = hotel_expectations
        converted_data['vacation_rental_expectations'] = vacation_rental_expectations
        
        # Preserve original quality score if available
        if 'quality_score' not in converted_data and unified_nuances:
            # Calculate quality score from individual nuance scores
            scores = [n.get('score', 0) for n in unified_nuances if n.get('score', 0) > 0]
            if scores:
                converted_data['quality_score'] = sum(scores) / len(scores)
        
        return converted_data
    
    def _generate_3_tier_nuances_display(self, nuances_data: dict, nuances_evidence_data: dict = None) -> str:
        """Generate display for 3-tier nuance system with proper layout."""
        
        # Generate summary statistics first
        destination_nuances = nuances_data.get('destination_nuances', [])
        hotel_expectations = nuances_data.get('hotel_expectations', [])
        vacation_rental_expectations = nuances_data.get('vacation_rental_expectations', [])
        
        total_insights = len(destination_nuances) + len(hotel_expectations) + len(vacation_rental_expectations)
        quality_scores = nuances_data.get('nuance_quality_scores', {})
        
        # Calculate overall quality score from actual data structure
        overall_score = nuances_data.get('quality_score', 0)
        if overall_score == 0:
            # Try alternative field names for backward compatibility
            overall_score = nuances_data.get('overall_quality_score', 0)
            if overall_score == 0:
                # Try statistics section
                statistics = nuances_data.get('statistics', {})
                overall_score = statistics.get('overall_quality_score', 0)
                if overall_score == 0:
                    # Calculate from individual nuance scores as fallback
                    all_nuances = destination_nuances + hotel_expectations + vacation_rental_expectations
                    if all_nuances:
                        scores = [n.get('score', 0) for n in all_nuances]
                        overall_score = sum(scores) / len(scores) if scores else 0
        
        summary_html = f'''
        <div class="nuances-summary">
            <h2>🧠 3-Tier Destination Insights</h2>
            <div class="summary-stats">
                <div class="stat-card">
                    <span class="stat-number">{total_insights}</span>
                    <span class="stat-label">Total Insights</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{len(destination_nuances)}</span>
                    <span class="stat-label">Destination Nuances</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{len(hotel_expectations)}</span>
                    <span class="stat-label">Conventional Lodging</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{len(vacation_rental_expectations)}</span>
                    <span class="stat-label">Vacation Rentals</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{overall_score:.3f}</span>
                    <span class="stat-label">Overall Quality</span>
                </div>
            </div>
        </div>
        '''
        
        # Main Destination Nuances Section (full width)
        destination_section = ""
        if destination_nuances:
            destination_section = f'''
            <div class="main-destination-section">
                <div class="section-header">
                    <h2>🎯 Destination Nuances</h2>
                    <p class="section-description">Fun experiences, activities, entertainment, and unique aspects that make this destination special for travelers.</p>
                </div>
                <div class="features-grid destination-grid">
                    {self._generate_nuance_feature_cards(destination_nuances, "destination")}
                </div>
            </div>
            '''
        
        # Side-by-side Accommodation Sections
        accommodation_sections = ""
        if hotel_expectations or vacation_rental_expectations:
            hotel_section = ""
            if hotel_expectations:
                hotel_section = f'''
                <div class="accommodation-section hotel-section">
                    <div class="section-header">
                        <h3>🏨 Conventional Lodging Nuances</h3>
                        <p class="section-description">What travelers expect from hotels, motels, and conventional accommodations in this destination.</p>
                    </div>
                    <div class="features-grid hotel-grid">
                        {self._generate_nuance_feature_cards(hotel_expectations, "hotel")}
                    </div>
                </div>
                '''
            
            vacation_rental_section = ""
            if vacation_rental_expectations:
                vacation_rental_section = f'''
                <div class="accommodation-section vacation-rental-section">
                    <div class="section-header">
                        <h3>🏡 Vacation Rental Nuances</h3>
                        <p class="section-description">What travelers expect to see and experience in vacation rentals in this destination.</p>
                    </div>
                    <div class="features-grid vacation-rental-grid">
                        {self._generate_nuance_feature_cards(vacation_rental_expectations, "vacation_rental")}
                    </div>
                </div>
                '''
            
            accommodation_sections = f'''
            <div class="accommodation-sections">
                {hotel_section}
                {vacation_rental_section}
            </div>
            '''
        
        return f'''
        <div class="nuances-container-3tier">
            {summary_html}
            {destination_section}
            {accommodation_sections}
        </div>
        '''
    
    def _generate_nuance_feature_cards(self, nuances_list: list, category: str) -> str:
        """Generate feature cards for a list of nuances."""
        feature_cards = []
        
        for i, nuance in enumerate(nuances_list, 1):
            phrase = nuance.get('phrase', 'Unknown Feature')
            score = nuance.get('score', 0)
            confidence = nuance.get('confidence', 0.8)
            source_models = nuance.get('source_models', [])
            validation_data = nuance.get('validation_data', {})
            
            # Generate description for the nuance
            description = self._generate_nuance_description(phrase, category)
            
            # Categorize destination nuances by lodging focus
            if category == "destination":
                nuance_category = self._categorize_destination_nuance(phrase)
            else:
                nuance_category = category.replace('_', ' ').title()
            
            # Get quality color and level
            quality_color = self._get_confidence_color(score)
            quality_level = self._get_quality_level(score)
            
            # Create evidence button with proper evidence ID
            evidence_id = f"nuance_{self._sanitize_filename(phrase)}"
            
            # Store evidence data for modal (ensure it's in the evidence store)
            if not hasattr(self, '_evidence_store'):
                self._evidence_store = {}
            
            # Store the evidence data if not already stored
            if evidence_id not in self._evidence_store:
                validation_data = nuance.get('validation_data', {})
                evidence_sources = nuance.get('evidence_sources', [])
                
                self._evidence_store[evidence_id] = {
                    'nuance_phrase': phrase,
                    'score': nuance.get('score', 0),
                    'search_hits': validation_data.get('search_hits', nuance.get('search_hits', 0)),
                    'uniqueness_ratio': validation_data.get('uniqueness_ratio', nuance.get('uniqueness_ratio', 0)),
                    'evidence_sources': evidence_sources,
                    'validation_metadata': validation_data,
                    'source_models': nuance.get('source_models', []),
                    'category': nuance.get('category', category),
                    'confidence': nuance.get('confidence', 0),
                    'source_urls': nuance.get('source_urls', []),
                    'nuance_evidence': True  # Flag to indicate this is nuance evidence
                }
            
            evidence_button = f'''
            <button class="evidence-btn" onclick="showNuanceEvidenceModal('{phrase}', '{evidence_id}')">
                📎 Evidence
            </button>
            '''
            
            # Create expandable description
            description_html = f'''
            <div class="nuance-description">
                <div class="description-preview">{description[:120]}{'...' if len(description) > 120 else ''}</div>
                {f'<div class="description-full" style="display: none;">{description}</div>' if len(description) > 120 else ''}
                {f'<button class="expand-btn" onclick="toggleDescription(this)">Read more</button>' if len(description) > 120 else ''}
            </div>
            '''
            
            # Create source models display
            models_html = ""
            if source_models:
                models_html = f'<div class="feature-sources"><small>Generated by: {", ".join(source_models[:3])}</small></div>'
            
            # Create validation display
            validation_html = ""
            if validation_data:
                search_hits = validation_data.get('search_hits', 0)
                uniqueness = validation_data.get('uniqueness_ratio', 0)
                if search_hits > 0:
                    validation_html = f'<div class="feature-validation"><small>🔍 {search_hits:,} hits • 📊 {uniqueness:.2f}x unique</small></div>'
            
            feature_card = f'''
            <div class="feature-card {category}-card">
                <div class="feature-header">
                    <div class="feature-rank">#{i}</div>
                    <div class="feature-phrase">"{phrase}"</div>
                    {evidence_button}
                </div>
                {description_html}
                <div class="feature-metrics">
                    <div class="feature-score">
                        <span class="score-label">Quality:</span>
                        <span class="score-value-small" style="color: {quality_color}">{score:.3f}</span>
                        <span class="score-level">({quality_level})</span>
                    </div>
                    <div class="feature-category">
                        <span class="category-label">Category:</span>
                        <span class="category-value">{nuance_category}</span>
                    </div>
                </div>
                {models_html}
                {validation_html}
            </div>
            '''
            
            feature_cards.append(feature_card)
        
        return "".join(feature_cards)
    
    def _generate_nuance_description(self, phrase: str, category: str) -> str:
        """Generate a descriptive explanation for a nuance phrase."""
        phrase_lower = phrase.lower()
        
        # Common description patterns based on category and phrase content
        if category == "destination":
            if "shrine" in phrase_lower or "temple" in phrase_lower:
                return f"Understanding proper {phrase} helps travelers respectfully participate in Japan's spiritual traditions and avoid cultural missteps during religious site visits."
            elif "etiquette" in phrase_lower:
                return f"Mastering {phrase} is essential for travelers to blend in with local customs and show respect for Japanese social norms."
            elif "experience" in phrase_lower or "tradition" in phrase_lower:
                return f"Participating in {phrase} offers travelers authentic cultural immersion and deeper connection to local heritage."
            elif "protocol" in phrase_lower or "importance" in phrase_lower:
                return f"Following {phrase} ensures travelers navigate social situations appropriately and gain local acceptance."
            elif "efficiency" in phrase_lower or "system" in phrase_lower:
                return f"Appreciating {phrase} helps travelers understand and utilize Japan's advanced infrastructure effectively."
            elif "preparedness" in phrase_lower or "safety" in phrase_lower:
                return f"Being aware of {phrase} keeps travelers informed about local safety considerations and emergency procedures."
            else:
                return f"Understanding {phrase} enhances the travel experience by providing insight into unique aspects of Japanese culture and daily life."
        
        elif category == "hotel":
            if "tech" in phrase_lower or "automated" in phrase_lower:
                return f"Hotels featuring {phrase} showcase Japan's technological advancement and provide guests with innovative convenience features."
            elif "traditional" in phrase_lower or "ceremony" in phrase_lower:
                return f"Hotels offering {phrase} allow guests to experience authentic Japanese culture without leaving their accommodation."
            elif "dining" in phrase_lower or "restaurant" in phrase_lower:
                return f"Hotels with {phrase} provide guests access to high-quality culinary experiences reflecting local food culture."
            elif "staff" in phrase_lower or "service" in phrase_lower:
                return f"Hotels emphasizing {phrase} ensure international guests receive appropriate support and communication assistance."
            elif "room" in phrase_lower or "accommodation" in phrase_lower:
                return f"Hotels providing {phrase} offer guests authentic Japanese living experiences and cultural immersion."
            else:
                return f"Hotels featuring {phrase} cater to travelers seeking distinctive accommodations that reflect local character and preferences."
        
        elif category == "vacation_rental":
            if "kitchen" in phrase_lower or "cooking" in phrase_lower:
                return f"Vacation rentals with {phrase} enable guests to prepare local ingredients and experience Japanese home cooking culture."
            elif "traditional" in phrase_lower or "authentic" in phrase_lower:
                return f"Vacation rentals offering {phrase} provide immersive living experiences in genuine Japanese residential settings."
            elif "space" in phrase_lower or "room" in phrase_lower:
                return f"Vacation rentals featuring {phrase} give guests insight into Japanese residential design and lifestyle preferences."
            elif "amenity" in phrase_lower or "feature" in phrase_lower:
                return f"Vacation rentals including {phrase} offer practical conveniences that enhance the local living experience."
            else:
                return f"Vacation rentals with {phrase} provide authentic residential experiences that hotels typically cannot offer."
        
        else:
            return f"This feature represents an important aspect of the local travel experience that visitors should be aware of when planning their stay."
    
    def _generate_legacy_nuances_display(self, nuances_data: dict, nuances_evidence_data: dict = None) -> str:
        """Generate display for legacy single-category nuance format."""
        if not nuances_data or not nuances_data.get('nuances'):
            return '<p class="no-data">No destination hotel features available.</p>'
        
        nuances_list = nuances_data.get('nuances', [])
        
        # Generate hotel features grid
        hotel_features_html = self._generate_hotel_features_grid(nuances_list)
        
        # Generate intelligence insights
        intelligence_insights_html = self._generate_nuance_intelligence_insights(nuances_data, nuances_evidence_data)
        
        return f'''
        <div class="nuances-container">
            <div class="section-header">
                <h2>🏨 Hotel Features (Legacy)</h2>
                <p class="section-description">Legacy single-category hotel features. Upgrade to 3-tier system for full insights.</p>
            </div>
            {hotel_features_html}
            
            <div class="section-header">
                <h2>🧠 Discovery Intelligence</h2>
                <p class="section-description">Analytics and insights from the hotel feature discovery process.</p>
            </div>
            {intelligence_insights_html}
        </div>
        '''

    def _generate_hotel_features_grid(self, nuances_list: list) -> str:
        """Generate a grid of hotel feature cards."""
        feature_cards = []
        
        for i, nuance in enumerate(nuances_list, 1):
            phrase = nuance.get('phrase', 'Unknown Feature')
            score = nuance.get('score', 0)
            category = nuance.get('category', 'general')
            confidence = nuance.get('confidence', 0.8)
            source_models = nuance.get('source_models', [])
            validation_data = nuance.get('validation_data', {})
            
            # Get quality color and level
            quality_color = self._get_confidence_color(score)
            quality_level = self._get_quality_level(score)
            
            # Create evidence button
            evidence_button = f'''
            <button class="evidence-btn" onclick="showNuanceEvidenceModal('{phrase}', {i})">
                📎 Evidence
            </button>
            ''' if nuances_list else ''
            
            # Create source models display
            models_html = ""
            if source_models:
                models_html = f'<div class="feature-sources"><small>Generated by: {", ".join(source_models[:3])}</small></div>'
            
            # Create validation display
            validation_html = ""
            if validation_data:
                search_hits = validation_data.get('search_hits', 0)
                uniqueness = validation_data.get('uniqueness_ratio', 0)
                if search_hits > 0:
                    validation_html = f'<div class="feature-validation"><small>🔍 {search_hits:,} hits • 📊 {uniqueness:.2f}x unique</small></div>'
            
            feature_card = f'''
            <div class="feature-card">
                <div class="feature-header">
                    <div class="feature-rank">#{i}</div>
                    <div class="feature-phrase">"{phrase}"</div>
                    {evidence_button}
                </div>
                <div class="feature-metrics">
                    <div class="feature-score">
                        <span class="score-label">Quality Score:</span>
                        <span class="score-value" style="color: {quality_color}">{score:.3f}</span>
                        <span class="score-level">({quality_level})</span>
                    </div>
                    <div class="feature-category">
                        <span class="category-label">Category:</span>
                        <span class="category-value">{category.title()}</span>
                    </div>
                </div>
                {models_html}
                {validation_html}
            </div>
            '''
            
            feature_cards.append(feature_card)
        
        return f'<div class="features-grid">{"".join(feature_cards)}</div>'

    def _generate_nuance_intelligence_insights(self, nuances_data: dict, nuances_evidence_data: dict = None) -> str:
        """Generate HTML for nuance intelligence insights - supports both 3-tier and legacy formats."""
        # Check for 3-tier system first
        if 'destination_nuances' in nuances_data or 'hotel_expectations' in nuances_data or 'vacation_rental_expectations' in nuances_data:
            return self._generate_3_tier_intelligence_insights(nuances_data, nuances_evidence_data)
        elif 'nuances' in nuances_data:
            return self._generate_legacy_intelligence_insights(nuances_data, nuances_evidence_data)
        else:
            return '<p class="no-data">No nuances data available for intelligence insights.</p>'

    def _generate_3_tier_intelligence_insights(self, nuances_data: dict, nuances_evidence_data: dict = None) -> str:
        """Generate intelligence insights for 3-tier nuance system."""
        destination_nuances = nuances_data.get('destination_nuances', [])
        hotel_expectations = nuances_data.get('hotel_expectations', [])
        vacation_rental_expectations = nuances_data.get('vacation_rental_expectations', [])
        
        # Get overall quality scores from actual data structure
        quality_scores = nuances_data.get('quality_scores', {})
        overall_quality = nuances_data.get('quality_score', 0)
        if overall_quality == 0:
            # Try alternative field names
            overall_quality = nuances_data.get('overall_quality_score', 0)
            if overall_quality == 0:
                statistics = nuances_data.get('statistics', {})
                overall_quality = statistics.get('overall_quality_score', 0)
        
        # Calculate aggregate statistics
        all_nuances = destination_nuances + hotel_expectations + vacation_rental_expectations
        total_nuances = len(all_nuances)
        
        if total_nuances == 0:
            return '<p class="no-data">No nuances available for intelligence insights.</p>'
        
        # Calculate quality distribution
        quality_distribution = {'excellent': 0, 'good': 0, 'needs_improvement': 0}
        for nuance in all_nuances:
            score = nuance.get('score', 0)
            if score >= 0.8:
                quality_distribution['excellent'] += 1
            elif score >= 0.6:
                quality_distribution['good'] += 1
            else:
                quality_distribution['needs_improvement'] += 1
        
        insights_cards = []
        
        # 3-Tier System Overview
        insights_cards.append(f"""
        <div class="insight-card tier-overview">
            <div class="insight-icon">🎯</div>
            <div class="insight-content">
                <h3>3-Tier System Coverage</h3>
                <div class="insight-value">{total_nuances} insights</div>
                <p>Comprehensive destination intelligence</p>
            </div>
            <div class="tier-breakdown">
                <small><strong>Destination:</strong> {len(destination_nuances)} | <strong>Hotels:</strong> {len(hotel_expectations)} | <strong>Rentals:</strong> {len(vacation_rental_expectations)}</small>
            </div>
        </div>
        """)
        
        # Overall Quality Score
        quality_level = self._get_quality_level(overall_quality)
        quality_color = self._get_confidence_color(overall_quality)
        insights_cards.append(f"""
        <div class="insight-card quality-overview">
            <div class="insight-icon">📊</div>
            <div class="insight-content">
                <h3>Overall Quality Score</h3>
                <div class="insight-value" style="color: {quality_color}">{overall_quality:.3f}</div>
                <p>{quality_level} nuance quality</p>
            </div>
            <div class="quality-breakdown">
                <small><strong>Excellent:</strong> {quality_distribution['excellent']} | <strong>Good:</strong> {quality_distribution['good']} | <strong>Needs Work:</strong> {quality_distribution['needs_improvement']}</small>
            </div>
        </div>
        """)
        
        # Tier Quality Comparison
        tier_qualities = []
        if destination_nuances:
            dest_avg = sum(n.get('score', 0) for n in destination_nuances) / len(destination_nuances)
            tier_qualities.append(f"Destination: {dest_avg:.3f}")
        if hotel_expectations:
            hotel_avg = sum(n.get('score', 0) for n in hotel_expectations) / len(hotel_expectations)
            tier_qualities.append(f"Hotels: {hotel_avg:.3f}")
        if vacation_rental_expectations:
            rental_avg = sum(n.get('score', 0) for n in vacation_rental_expectations) / len(vacation_rental_expectations)
            tier_qualities.append(f"Rentals: {rental_avg:.3f}")
        
        insights_cards.append(f"""
        <div class="insight-card tier-quality">
            <div class="insight-icon">⚖️</div>
            <div class="insight-content">
                <h3>Tier Quality Balance</h3>
                <div class="insight-value">{len(tier_qualities)}/3 tiers</div>
                <p>Quality across accommodation types</p>
            </div>
            <div class="tier-details">
                <small>{' | '.join(tier_qualities)}</small>
            </div>
        </div>
        """)
        
        return f'<div class="insights-grid">{"".join(insights_cards)}</div>'

    def _generate_legacy_intelligence_insights(self, nuances_data: dict, nuances_evidence_data: dict = None) -> str:
        """Generate intelligence insights for legacy nuance format."""
        nuances_list = nuances_data.get('nuances', [])
        statistics = nuances_data.get('statistics', {})
        
        # Calculate hotel feature statistics
        total_features = len(nuances_list)
        avg_score = sum(n.get('score', 0) for n in nuances_list) / total_features if total_features > 0 else 0
        feature_categories = {}
        
        for nuance in nuances_list:
            category = nuance.get('category', 'general')
            feature_categories[category] = feature_categories.get(category, 0) + 1
        
        # Quality distribution
        quality_distribution = {'excellent': 0, 'good': 0, 'needs_improvement': 0}
        for nuance in nuances_list:
            score = nuance.get('score', 0)
            if score >= 0.8:
                quality_distribution['excellent'] += 1
            elif score >= 0.6:
                quality_distribution['good'] += 1
            else:
                quality_distribution['needs_improvement'] += 1
        
        insights_cards = []
        
        # Hotel Features Discovery Stats
        insights_cards.append(f"""
        <div class="insight-card hotel-features">
            <div class="insight-icon">🏨</div>
            <div class="insight-content">
                <h3>Hotel Features Discovered</h3>
                <div class="insight-value">{total_features} features</div>
                <p>Destination-specific hotel amenities and services</p>
            </div>
            <div class="feature-breakdown">
                <small><strong>Categories:</strong> {', '.join(feature_categories.keys())}</small>
            </div>
        </div>
        """)
        
        # Average Quality Score
        quality_level = self._get_quality_level(avg_score)
        quality_color = self._get_confidence_color(avg_score)
        insights_cards.append(f"""
        <div class="insight-card quality-overview">
            <div class="insight-icon">📊</div>
            <div class="insight-content">
                <h3>Feature Quality Score</h3>
                <div class="insight-value" style="color: {quality_color}">{avg_score:.3f}</div>
                <p>{quality_level} hotel feature quality</p>
            </div>
            <div class="quality-breakdown">
                <small><strong>Excellent:</strong> {quality_distribution['excellent']} | <strong>Good:</strong> {quality_distribution['good']} | <strong>Needs Work:</strong> {quality_distribution['needs_improvement']}</small>
            </div>
        </div>
        """)
        
        # Feature Uniqueness (if we have search validation data)
        if statistics.get('search_validation_enabled', False):
            validation_rate = statistics.get('validation_success_rate', 0) * 100
            insights_cards.append(f"""
            <div class="insight-card validation-stats">
                <div class="insight-icon">🔍</div>
                <div class="insight-content">
                    <h3>Feature Validation</h3>
                    <div class="insight-value">{validation_rate:.1f}%</div>
                    <p>Search-validated hotel features</p>
                </div>
                <div class="validation-breakdown">
                    <small><strong>Validated:</strong> {statistics.get('phrases_validated', 0)} | <strong>Failed:</strong> {statistics.get('phrases_failed', 0)}</small>
                </div>
            </div>
            """)
        else:
            insights_cards.append(f"""
            <div class="insight-card fallback-mode">
                <div class="insight-icon">⚡</div>
                <div class="insight-content">
                    <h3>Generation Mode</h3>
                    <div class="insight-value">Fallback</div>
                    <p>Multi-LLM consensus scoring</p>
                </div>
                <div class="mode-info">
                    <small><strong>Models Used:</strong> {statistics.get('phrases_attempted', 0)} attempted</small>
                </div>
            </div>
            """)
        
        return f'<div class="insights-grid">{"".join(insights_cards)}</div>'

    def _generate_nuance_insight_analysis(self, nuances_data: dict) -> str:
        """Generate HTML for nuance insight analysis - supports both 3-tier and legacy formats."""
        # Check for 3-tier system first
        if 'destination_nuances' in nuances_data or 'hotel_expectations' in nuances_data or 'vacation_rental_expectations' in nuances_data:
            return self._generate_3_tier_insight_analysis(nuances_data)
        elif 'nuances' in nuances_data:
            return self._generate_legacy_insight_analysis(nuances_data)
        else:
            return '<p class="no-data">No nuances data available for insight analysis.</p>'

    def _generate_3_tier_insight_analysis(self, nuances_data: dict) -> str:
        """Generate insight analysis for 3-tier nuance system."""
        destination_nuances = nuances_data.get('destination_nuances', [])
        hotel_expectations = nuances_data.get('hotel_expectations', [])
        vacation_rental_expectations = nuances_data.get('vacation_rental_expectations', [])
        
        # Analyze all nuances together
        all_nuances = destination_nuances + hotel_expectations + vacation_rental_expectations
        total_nuances = len(all_nuances)
        
        if total_nuances == 0:
            return '<p class="no-data">No nuances available for insight analysis.</p>'
        
        # Categorize by lodging focus across all tiers
        lodging_categories = {'🏨 Lodging': 0, '🍽️ Food & Dining': 0, '🎯 Activities': 0, '⚙️ Amenities': 0, '✨ Experience': 0}
        price_segments = {'budget': 0, 'mid_range': 0, 'luxury': 0}
        
        for nuance in all_nuances:
            phrase = nuance.get('phrase', '')
            score = nuance.get('score', 0)
            
            # Categorize by lodging focus
            category = self._categorize_destination_nuance(phrase)
            if category in lodging_categories:
                lodging_categories[category] += 1
            
            # Estimate price segment based on keywords
            phrase_lower = phrase.lower()
            if any(word in phrase_lower for word in ['luxury', 'premium', 'exclusive', 'private', 'high-end']):
                price_segments['luxury'] += 1
            elif any(word in phrase_lower for word in ['budget', 'basic', 'simple', 'affordable']):
                price_segments['budget'] += 1
            else:
                price_segments['mid_range'] += 1
        
        # Calculate tier balance
        tier_balance = {
            'destination': len(destination_nuances),
            'hotel': len(hotel_expectations),
            'vacation_rental': len(vacation_rental_expectations)
        }
        
        # Calculate quality metrics
        avg_score = sum(n.get('score', 0) for n in all_nuances) / total_nuances if total_nuances > 0 else 0
        
        analysis_cards = []
        
        # Lodging Category Distribution
        active_categories = len([k for k, v in lodging_categories.items() if v > 0])
        analysis_cards.append(f"""
        <div class="analysis-card category-distribution">
            <div class="analysis-icon">🏨</div>
            <div class="analysis-content">
                <h3>Lodging Category Coverage</h3>
                <div class="analysis-value">{active_categories}/5 categories</div>
                <p>Breadth of lodging-focused insights</p>
            </div>
            <div class="distribution-breakdown">
                {chr(10).join([f'<div class="breakdown-item"><span class="category-label">{cat}:</span><span class="category-count">{count}</span></div>' for cat, count in lodging_categories.items() if count > 0])}
            </div>
        </div>
        """)
        
        # 3-Tier Balance Analysis
        max_tier = max(tier_balance.values()) if tier_balance.values() else 0
        min_tier = min(tier_balance.values()) if tier_balance.values() else 0
        balance_ratio = (min_tier / max_tier * 100) if max_tier > 0 else 0
        
        analysis_cards.append(f"""
        <div class="analysis-card tier-balance">
            <div class="analysis-icon">⚖️</div>
            <div class="analysis-content">
                <h3>3-Tier Balance</h3>
                <div class="analysis-value">{balance_ratio:.0f}% balanced</div>
                <p>Distribution across accommodation types</p>
            </div>
            <div class="tier-breakdown">
                <div class="tier-item">
                    <span class="tier-label">Destination Nuances:</span>
                    <span class="tier-count">{tier_balance['destination']} insights</span>
                </div>
                <div class="tier-item">
                    <span class="tier-label">Hotel Expectations:</span>
                    <span class="tier-count">{tier_balance['hotel']} features</span>
                </div>
                <div class="tier-item">
                    <span class="tier-label">Rental Expectations:</span>
                    <span class="tier-count">{tier_balance['vacation_rental']} features</span>
                </div>
            </div>
        </div>
        """)
        
        # Price Segment Analysis
        luxury_percentage = (price_segments['luxury'] / total_nuances * 100) if total_nuances > 0 else 0
        analysis_cards.append(f"""
        <div class="analysis-card price-analysis">
            <div class="analysis-icon">💰</div>
            <div class="analysis-content">
                <h3>Price Segment Analysis</h3>
                <div class="analysis-value">{luxury_percentage:.0f}% luxury</div>
                <p>Market positioning insights</p>
            </div>
            <div class="price-breakdown">
                <div class="price-segment">
                    <span class="segment-label">Luxury:</span>
                    <span class="segment-count">{price_segments['luxury']} features</span>
                    <div class="segment-bar">
                        <div class="segment-fill luxury" style="width: {(price_segments['luxury'] / total_nuances * 100) if total_nuances > 0 else 0}%; background: #dc3545;"></div>
                    </div>
                </div>
                <div class="price-segment">
                    <span class="segment-label">Mid-Range:</span>
                    <span class="segment-count">{price_segments['mid_range']} features</span>
                    <div class="segment-bar">
                        <div class="segment-fill mid-range" style="width: {(price_segments['mid_range'] / total_nuances * 100) if total_nuances > 0 else 0}%; background: #ffc107;"></div>
                    </div>
                </div>
                <div class="price-segment">
                    <span class="segment-label">Budget:</span>
                    <span class="segment-count">{price_segments['budget']} features</span>
                    <div class="segment-bar">
                        <div class="segment-fill budget" style="width: {(price_segments['budget'] / total_nuances * 100) if total_nuances > 0 else 0}%; background: #28a745;"></div>
                    </div>
                </div>
            </div>
        </div>
        """)
        
        return f'<div class="analysis-grid">{"".join(analysis_cards)}</div>'

    def _generate_legacy_insight_analysis(self, nuances_data: dict) -> str:
        """Generate insight analysis for legacy nuance format."""
        nuances_list = nuances_data.get('nuances', [])
        
        # Analyze hotel feature patterns
        feature_categories = {}
        price_segments = {'budget': 0, 'mid_range': 0, 'luxury': 0}
        service_types = {'amenities': 0, 'services': 0, 'accommodations': 0, 'dining': 0}
        
        for nuance in nuances_list:
            phrase = nuance.get('phrase', '')
            category = nuance.get('category', 'general')
            score = nuance.get('score', 0)
            
            # Categorize features
            feature_categories[category] = feature_categories.get(category, 0) + 1
            
            # Analyze service types based on keywords
            phrase_lower = phrase.lower()
            if any(word in phrase_lower for word in ['pool', 'spa', 'gym', 'wifi', 'parking']):
                service_types['amenities'] += 1
            elif any(word in phrase_lower for word in ['concierge', 'service', 'valet', 'butler']):
                service_types['services'] += 1
            elif any(word in phrase_lower for word in ['room', 'suite', 'accommodation', 'lodging']):
                service_types['accommodations'] += 1
            elif any(word in phrase_lower for word in ['dining', 'restaurant', 'bar', 'breakfast']):
                service_types['dining'] += 1
            
            # Estimate price segment based on keywords
            if any(word in phrase_lower for word in ['luxury', 'premium', 'exclusive', 'private']):
                price_segments['luxury'] += 1
            elif any(word in phrase_lower for word in ['budget', 'basic', 'simple']):
                price_segments['budget'] += 1
            else:
                price_segments['mid_range'] += 1
        
        # Calculate coverage metrics
        total_features = len(nuances_list)
        service_coverage = len([k for k, v in service_types.items() if v > 0])
        avg_score = sum(n.get('score', 0) for n in nuances_list) / total_features if total_features > 0 else 0
        
        analysis_cards = []
        
        # Hotel Feature Distribution
        analysis_cards.append(f"""
        <div class="analysis-card feature-distribution">
            <div class="analysis-icon">🏨</div>
            <div class="analysis-content">
                <h3>Hotel Feature Distribution</h3>
                <div class="analysis-value">{service_coverage}/4 service types</div>
                <p>Coverage of hotel service categories</p>
            </div>
            <div class="distribution-breakdown">
                <div class="breakdown-item">
                    <span class="category-label">Amenities:</span>
                    <span class="category-count">{service_types['amenities']}</span>
                </div>
                <div class="breakdown-item">
                    <span class="category-label">Services:</span>
                    <span class="category-count">{service_types['services']}</span>
                </div>
                <div class="breakdown-item">
                    <span class="category-label">Accommodations:</span>
                    <span class="category-count">{service_types['accommodations']}</span>
                </div>
                <div class="breakdown-item">
                    <span class="category-label">Dining:</span>
                    <span class="category-count">{service_types['dining']}</span>
                </div>
            </div>
        </div>
        """)
        
        # Price Segment Analysis
        luxury_percentage = (price_segments['luxury'] / total_features * 100) if total_features > 0 else 0
        analysis_cards.append(f"""
        <div class="analysis-card price-analysis">
            <div class="analysis-icon">💰</div>
            <div class="analysis-content">
                <h3>Price Segment Analysis</h3>
                <div class="analysis-value">{luxury_percentage:.0f}% luxury</div>
                <p>Hotel market positioning insights</p>
            </div>
            <div class="price-breakdown">
                <div class="price-segment">
                    <span class="segment-label">Luxury:</span>
                    <span class="segment-count">{price_segments['luxury']} features</span>
                    <div class="segment-bar">
                        <div class="segment-fill luxury" style="width: {(price_segments['luxury'] / total_features * 100) if total_features > 0 else 0}%; background: #dc3545;"></div>
                    </div>
                </div>
                <div class="price-segment">
                    <span class="segment-label">Mid-Range:</span>
                    <span class="segment-count">{price_segments['mid_range']} features</span>
                    <div class="segment-bar">
                        <div class="segment-fill mid-range" style="width: {(price_segments['mid_range'] / total_features * 100) if total_features > 0 else 0}%; background: #ffc107;"></div>
                    </div>
                </div>
                <div class="price-segment">
                    <span class="segment-label">Budget:</span>
                    <span class="segment-count">{price_segments['budget']} features</span>
                    <div class="segment-bar">
                        <div class="segment-fill budget" style="width: {(price_segments['budget'] / total_features * 100) if total_features > 0 else 0}%; background: #28a745;"></div>
                    </div>
                </div>
            </div>
        </div>
        """)
        
        # Feature Quality Overview
        excellent_count = sum(1 for n in nuances_list if n.get('score', 0) >= 0.8)
        quality_percentage = (excellent_count / total_features * 100) if total_features > 0 else 0
        analysis_cards.append(f"""
        <div class="analysis-card quality-analysis">
            <div class="analysis-icon">⭐</div>
            <div class="analysis-content">
                <h3>Feature Quality Overview</h3>
                <div class="analysis-value">{quality_percentage:.0f}% excellent</div>
                <p>High-quality hotel feature ratio</p>
            </div>
            <div class="quality-metrics">
                <div class="metric-item">
                    <span class="metric-label">Average Score:</span>
                    <span class="metric-value" style="color: {self._get_confidence_color(avg_score)}">{avg_score:.3f}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Quality Level:</span>
                    <span class="metric-value">{self._get_quality_level(avg_score)}</span>
                </div>
            </div>
        </div>
        """)
        
        return f'<div class="analysis-grid">{"".join(analysis_cards)}</div>'

    def _generate_nuance_quality_assessment(self, nuances_data: dict) -> str:
        """Generate HTML for nuance quality assessment - supports both 3-tier and legacy formats."""
        # Check for 3-tier system first
        if 'destination_nuances' in nuances_data or 'hotel_expectations' in nuances_data or 'vacation_rental_expectations' in nuances_data:
            return self._generate_3_tier_quality_assessment(nuances_data)
        elif 'nuances' in nuances_data:
            return self._generate_legacy_quality_assessment(nuances_data)
        else:
            return '<p class="no-data">No nuances data available for quality assessment.</p>'

    def _generate_3_tier_quality_assessment(self, nuances_data: dict) -> str:
        """Generate quality assessment for 3-tier nuance system."""
        destination_nuances = nuances_data.get('destination_nuances', [])
        hotel_expectations = nuances_data.get('hotel_expectations', [])
        vacation_rental_expectations = nuances_data.get('vacation_rental_expectations', [])
        
        # Get overall quality scores from actual data structure
        quality_scores = nuances_data.get('quality_scores', {})
        overall_quality = nuances_data.get('quality_score', 0)
        if overall_quality == 0:
            # Try alternative field names
            overall_quality = nuances_data.get('overall_quality_score', 0)  
            if overall_quality == 0:
                statistics = nuances_data.get('statistics', {})
                overall_quality = statistics.get('overall_quality_score', 0)
        
        # Calculate aggregate statistics
        all_nuances = destination_nuances + hotel_expectations + vacation_rental_expectations
        total_nuances = len(all_nuances)
        
        if total_nuances == 0:
            return '<p class="no-data">No nuances available for quality assessment.</p>'
        
        # Calculate quality distribution across all tiers
        scores = [n.get('score', 0) for n in all_nuances]
        avg_score = sum(scores) / total_nuances if total_nuances > 0 else 0
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 0
        
        # Quality level distribution
        quality_levels = {'excellent': 0, 'good': 0, 'acceptable': 0, 'needs_improvement': 0}
        for score in scores:
            if score >= 0.85:
                quality_levels['excellent'] += 1
            elif score >= 0.75:
                quality_levels['good'] += 1
            elif score >= 0.65:
                quality_levels['acceptable'] += 1
            else:
                quality_levels['needs_improvement'] += 1
        
        assessment_cards = []
        
        # Overall 3-Tier Quality Score
        overall_quality_level = self._get_quality_level(overall_quality)
        assessment_cards.append(f"""
        <div class="assessment-card overall-quality">
            <div class="assessment-icon">🏆</div>
            <div class="assessment-content">
                <h3>Overall 3-Tier Quality</h3>
                <div class="assessment-value" style="color: {self._get_confidence_color(overall_quality)}">{overall_quality:.3f}</div>
                <p>{overall_quality_level} quality level</p>
            </div>
            <div class="quality-details">
                <div class="score-range">
                    <span class="range-label">Score Range:</span>
                    <span class="range-value">{min_score:.3f} - {max_score:.3f}</span>
                </div>
                <div class="quality-trend">
                    <span class="trend-label">Consistency:</span>
                    <span class="trend-value">{'High' if (max_score - min_score) < 0.2 else 'Medium' if (max_score - min_score) < 0.4 else 'Low'}</span>
                </div>
            </div>
        </div>
        """)
        
        # Tier-by-Tier Quality Breakdown
        tier_breakdown = []
        if destination_nuances:
            dest_avg = sum(n.get('score', 0) for n in destination_nuances) / len(destination_nuances)
            tier_breakdown.append(f"Destination: {dest_avg:.3f}")
        if hotel_expectations:
            hotel_avg = sum(n.get('score', 0) for n in hotel_expectations) / len(hotel_expectations)
            tier_breakdown.append(f"Hotels: {hotel_avg:.3f}")
        if vacation_rental_expectations:
            rental_avg = sum(n.get('score', 0) for n in vacation_rental_expectations) / len(vacation_rental_expectations)
            tier_breakdown.append(f"Rentals: {rental_avg:.3f}")
        
        assessment_cards.append(f"""
        <div class="assessment-card tier-breakdown">
            <div class="assessment-icon">📊</div>
            <div class="assessment-content">
                <h3>Tier Quality Breakdown</h3>
                <div class="assessment-value">{len([t for t in [destination_nuances, hotel_expectations, vacation_rental_expectations] if t])}/3 tiers</div>
                <p>Quality across accommodation types</p>
            </div>
            <div class="tier-details">
                {'<br>'.join(tier_breakdown)}
            </div>
        </div>
        """)
        
        # Quality Distribution Chart
        excellent_percentage = (quality_levels['excellent'] / total_nuances * 100) if total_nuances > 0 else 0
        assessment_cards.append(f"""
        <div class="assessment-card quality-distribution">
            <div class="assessment-icon">📈</div>
            <div class="assessment-content">
                <h3>Quality Distribution</h3>
                <div class="assessment-value">{excellent_percentage:.0f}% excellent</div>
                <p>Nuance quality breakdown</p>
            </div>
            <div class="distribution-chart">
                <div class="quality-bar excellent">
                    <span class="bar-label">Excellent:</span>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: {(quality_levels['excellent'] / total_nuances * 100) if total_nuances > 0 else 0}%; background: #28a745;"></div>
                        <span class="bar-count">{quality_levels['excellent']}</span>
                    </div>
                </div>
                <div class="quality-bar good">
                    <span class="bar-label">Good:</span>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: {(quality_levels['good'] / total_nuances * 100) if total_nuances > 0 else 0}%; background: #28a745;"></div>
                        <span class="bar-count">{quality_levels['good']}</span>
                    </div>
                </div>
                <div class="quality-bar acceptable">
                    <span class="bar-label">Acceptable:</span>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: {(quality_levels['acceptable'] / total_nuances * 100) if total_nuances > 0 else 0}%; background: #ffc107;"></div>
                        <span class="bar-count">{quality_levels['acceptable']}</span>
                    </div>
                </div>
                <div class="quality-bar needs-improvement">
                    <span class="bar-label">Needs Work:</span>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: {(quality_levels['needs_improvement'] / total_nuances * 100) if total_nuances > 0 else 0}%; background: #dc3545;"></div>
                        <span class="bar-count">{quality_levels['needs_improvement']}</span>
                    </div>
                </div>
            </div>
        </div>
        """)
        
        # Coverage Assessment
        coverage_score = len([t for t in [destination_nuances, hotel_expectations, vacation_rental_expectations] if t]) / 3 * 100
        assessment_cards.append(f"""
        <div class="assessment-card coverage-assessment">
            <div class="assessment-icon">🎯</div>
            <div class="assessment-content">
                <h3>System Coverage</h3>
                <div class="assessment-value">{coverage_score:.0f}%</div>
                <p>3-tier system completeness</p>
            </div>
            <div class="coverage-details">
                <div class="coverage-item">
                    <span class="coverage-label">Destination Nuances:</span>
                    <span class="coverage-value">{len(destination_nuances)} insights</span>
                </div>
                <div class="coverage-item">
                    <span class="coverage-label">Hotel Expectations:</span>
                    <span class="coverage-value">{len(hotel_expectations)} features</span>
                </div>
                <div class="coverage-item">
                    <span class="coverage-label">Rental Expectations:</span>
                    <span class="coverage-value">{len(vacation_rental_expectations)} features</span>
                </div>
            </div>
        </div>
        """)
        
        return f'<div class="assessment-grid">{"".join(assessment_cards)}</div>'

    def _generate_legacy_quality_assessment(self, nuances_data: dict) -> str:
        """Generate quality assessment for legacy nuance format."""
        nuances_list = nuances_data.get('nuances', [])
        statistics = nuances_data.get('statistics', {})
        
        # Calculate hotel feature quality metrics
        total_features = len(nuances_list)
        scores = [n.get('score', 0) for n in nuances_list]
        avg_score = sum(scores) / total_features if total_features > 0 else 0
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 0
        
        # Quality distribution
        quality_levels = {'excellent': 0, 'good': 0, 'acceptable': 0, 'needs_improvement': 0}
        for score in scores:
            if score >= 0.85:
                quality_levels['excellent'] += 1
            elif score >= 0.75:
                quality_levels['good'] += 1
            elif score >= 0.65:
                quality_levels['acceptable'] += 1
            else:
                quality_levels['needs_improvement'] += 1
        
        # Feature completeness assessment
        feature_categories = set(n.get('category', 'general') for n in nuances_list)
        completeness_score = min(1.0, len(feature_categories) / 4)  # Assuming 4 main categories
        
        # Validation quality
        validation_enabled = statistics.get('search_validation_enabled', False)
        validation_rate = statistics.get('validation_success_rate', 0) if validation_enabled else 0
        
        assessment_cards = []
        
        # Overall Quality Score
        overall_quality_level = self._get_quality_level(avg_score)
        assessment_cards.append(f"""
        <div class="assessment-card overall-quality">
            <div class="assessment-icon">🏆</div>
            <div class="assessment-content">
                <h3>Overall Hotel Feature Quality</h3>
                <div class="assessment-value" style="color: {self._get_confidence_color(avg_score)}">{avg_score:.3f}</div>
                <p>{overall_quality_level} quality level</p>
            </div>
            <div class="quality-details">
                <div class="score-range">
                    <span class="range-label">Score Range:</span>
                    <span class="range-value">{min_score:.3f} - {max_score:.3f}</span>
                </div>
                <div class="quality-trend">
                    <span class="trend-label">Consistency:</span>
                    <span class="trend-value">{'High' if (max_score - min_score) < 0.2 else 'Medium' if (max_score - min_score) < 0.4 else 'Low'}</span>
                </div>
            </div>
        </div>
        """)
        
        # Quality Distribution
        excellent_percentage = (quality_levels['excellent'] / total_features * 100) if total_features > 0 else 0
        assessment_cards.append(f"""
        <div class="assessment-card quality-distribution">
            <div class="assessment-icon">📊</div>
            <div class="assessment-content">
                <h3>Quality Distribution</h3>
                <div class="assessment-value">{excellent_percentage:.0f}% excellent</div>
                <p>Hotel feature quality breakdown</p>
            </div>
            <div class="distribution-chart">
                <div class="quality-bar excellent">
                    <span class="bar-label">Excellent:</span>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: {(quality_levels['excellent'] / total_features * 100) if total_features > 0 else 0}%; background: #28a745;"></div>
                        <span class="bar-count">{quality_levels['excellent']}</span>
                    </div>
                </div>
                <div class="quality-bar good">
                    <span class="bar-label">Good:</span>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: {(quality_levels['good'] / total_features * 100) if total_features > 0 else 0}%; background: #28a745;"></div>
                        <span class="bar-count">{quality_levels['good']}</span>
                    </div>
                </div>
                <div class="quality-bar acceptable">
                    <span class="bar-label">Acceptable:</span>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: {(quality_levels['acceptable'] / total_features * 100) if total_features > 0 else 0}%; background: #ffc107;"></div>
                        <span class="bar-count">{quality_levels['acceptable']}</span>
                    </div>
                </div>
                <div class="quality-bar needs-improvement">
                    <span class="bar-label">Needs Work:</span>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: {(quality_levels['needs_improvement'] / total_features * 100) if total_features > 0 else 0}%; background: #dc3545;"></div>
                        <span class="bar-count">{quality_levels['needs_improvement']}</span>
                    </div>
                </div>
            </div>
        </div>
        """)
        
        # Feature Coverage Assessment
        coverage_percentage = completeness_score * 100
        assessment_cards.append(f"""
        <div class="assessment-card feature-coverage">
            <div class="assessment-icon">🎯</div>
            <div class="assessment-content">
                <h3>Feature Coverage</h3>
                <div class="assessment-value">{coverage_percentage:.0f}%</div>
                <p>Hotel service category coverage</p>
            </div>
            <div class="coverage-details">
                <div class="coverage-item">
                    <span class="coverage-label">Categories Covered:</span>
                    <span class="coverage-value">{len(feature_categories)}/4</span>
                </div>
                <div class="coverage-item">
                    <span class="coverage-label">Total Features:</span>
                    <span class="coverage-value">{total_features}</span>
                </div>
                <div class="coverage-recommendation">
                    <small>{'✅ Good coverage' if coverage_percentage >= 75 else '⚠️ Consider more categories' if coverage_percentage >= 50 else '❌ Needs more coverage'}</small>
                </div>
            </div>
        </div>
        """)
        
        # Validation Quality (if applicable)
        if validation_enabled:
            validation_percentage = validation_rate * 100
            assessment_cards.append(f"""
            <div class="assessment-card validation-quality">
                <div class="assessment-icon">🔍</div>
                <div class="assessment-content">
                    <h3>Validation Quality</h3>
                    <div class="assessment-value">{validation_percentage:.0f}%</div>
                    <p>Search-validated features</p>
                </div>
                <div class="validation-details">
                    <div class="validation-item">
                        <span class="validation-label">Validated:</span>
                        <span class="validation-value">{statistics.get('phrases_validated', 0)}</span>
                    </div>
                    <div class="validation-item">
                        <span class="validation-label">Failed:</span>
                        <span class="validation-value">{statistics.get('phrases_failed', 0)}</span>
                    </div>
                </div>
            </div>
            """)
        else:
            assessment_cards.append(f"""
            <div class="assessment-card fallback-quality">
                <div class="assessment-icon">⚡</div>
                <div class="assessment-content">
                    <h3>Assessment Mode</h3>
                    <div class="assessment-value">Consensus</div>
                    <p>Multi-LLM generated scores</p>
                </div>
                <div class="mode-details">
                    <div class="mode-item">
                        <span class="mode-label">Models Used:</span>
                        <span class="mode-value">{len(set().union(*[n.get('source_models', []) for n in nuances_list]))}</span>
                    </div>
                    <div class="mode-item">
                        <span class="mode-label">Quality:</span>
                        <span class="mode-value">{'High confidence' if avg_score >= 0.7 else 'Medium confidence' if avg_score >= 0.5 else 'Low confidence'}</span>
                    </div>
                </div>
            </div>
            """)
        
        return f'<div class="assessment-grid">{"".join(assessment_cards)}</div>'

    def _aggregate_evidence_from_themes(self, affinities: list) -> dict:
        """Aggregate evidence from themes for comprehensive evidence display."""
        aggregated_evidence = {}
        for theme in affinities:
            theme_name = theme.get('theme', 'Unknown Theme')
            theme_data = theme.get('comprehensive_attribute_evidence', {})
            for evidence_type, evidence_data in theme_data.items():
                if evidence_type not in aggregated_evidence:
                    aggregated_evidence[evidence_type] = []
                aggregated_evidence[evidence_type].extend(evidence_data)
        return aggregated_evidence

    def _generate_seasonal_carousel(self, destination_name: str) -> str:
        """Generate seasonal image carousel HTML."""
        import os
        
        # Convert destination name to file format
        dest_filename = destination_name.lower().replace(', ', '_').replace(' ', '_').replace(',', '')
        
        # Check for seasonal images
        images_base_path = "../images"  # Relative path from dashboard subdirectory to images
        image_dir = f"{images_base_path}/{dest_filename}"
        
        # Define seasons and their display info
        seasons = [
            {"name": "spring", "display": "Spring", "icon": "🌸"},
            {"name": "summer", "display": "Summer", "icon": "☀️"},
            {"name": "autumn", "display": "Autumn", "icon": "🍂"},
            {"name": "winter", "display": "Winter", "icon": "❄️"}
        ]
        
        # Check if images exist (we'll assume they do since we generated them)
        carousel_items = []
        for i, season in enumerate(seasons):
            image_path = f"{image_dir}/{season['name']}.jpg"
            active_class = "active" if i == 0 else ""
            
            carousel_items.append(f"""
            <div class="carousel-item {active_class}">
                <img src="{image_path}" alt="{destination_name} in {season['display']}" 
                     onerror="this.style.display='none'">
                <div class="carousel-caption">
                    <span class="season-icon">{season['icon']}</span>
                    <span class="season-name">{season['display']}</span>
                </div>
            </div>
            """)
        
        # Generate carousel indicators
        indicators = []
        for i, season in enumerate(seasons):
            active_class = "active" if i == 0 else ""
            indicators.append(f"""
            <button class="carousel-indicator {active_class}" 
                    onclick="showSeasonalImage({i})"
                    title="{season['display']}">
                {season['icon']}
            </button>
            """)
        
        return f"""
        <div class="seasonal-carousel">
            <div class="carousel-container">
                <div class="carousel-slides">
                    {''.join(carousel_items)}
                </div>
                <div class="carousel-controls">
                    <button class="carousel-btn prev" onclick="changeSeasonalImage(-1)">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <div class="carousel-indicators">
                        {''.join(indicators)}
                    </div>
                    <button class="carousel-btn next" onclick="changeSeasonalImage(1)">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
            </div>
        </div>
        """
    
    def _categorize_destination_nuance(self, phrase: str) -> str:
        """Categorize destination nuances by lodging focus."""
        phrase_lower = phrase.lower()
        
        # Lodging & Accommodation
        if any(word in phrase_lower for word in [
            'room', 'suite', 'lodge', 'stay', 'accommodation', 'hotel', 'resort', 'inn', 
            'villa', 'cabin', 'chalet', 'bungalow', 'ryokan', 'riad', 'pension', 'guesthouse',
            'view', 'balcony', 'terrace', 'window', 'bathroom', 'toilet', 'shower', 'bath',
            'bed', 'sleeping', 'tatami', 'futon', 'check-in', 'checkout'
        ]):
            return "🏨 Lodging"
        
        # Food & Dining
        elif any(word in phrase_lower for word in [
            'food', 'dining', 'restaurant', 'cuisine', 'meal', 'breakfast', 'lunch', 'dinner',
            'tea', 'coffee', 'drink', 'bar', 'cafe', 'kitchen', 'cooking', 'chef', 'menu',
            'taste', 'flavor', 'recipe', 'market', 'street food', 'local dish', 'specialty'
        ]):
            return "🍽️ Food & Dining"
        
        # Activities & Experiences  
        elif any(word in phrase_lower for word in [
            'activity', 'experience', 'tour', 'visit', 'explore', 'adventure', 'excursion',
            'ceremony', 'festival', 'show', 'performance', 'museum', 'temple', 'shrine',
            'park', 'garden', 'hiking', 'walking', 'cycling', 'sport', 'game', 'lesson',
            'class', 'workshop', 'cultural', 'tradition', 'custom', 'ritual', 'celebration'
        ]):
            return "🎯 Activities"
        
        # Amenities & Services
        elif any(word in phrase_lower for word in [
            'service', 'amenity', 'facility', 'spa', 'wellness', 'massage', 'gym', 'fitness',
            'pool', 'beach', 'wifi', 'internet', 'transport', 'taxi', 'train', 'subway',
            'station', 'airport', 'parking', 'concierge', 'staff', 'guide', 'assistance',
            'help', 'support', 'convenience', 'access', 'proximity', 'location'
        ]):
            return "⚙️ Amenities"
        
        # Default to Experience for cultural/unique aspects
        else:
            return "✨ Experience"