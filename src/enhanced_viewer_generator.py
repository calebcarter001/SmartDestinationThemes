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
        destination_name = data.get('destination_name', 'Unknown Destination')
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
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Set current file for evidence loading
                self._current_json_file = json_file
                
                destination_name = data.get('destination_name', 'Unknown Destination')
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
        
        destination_name = data.get('destination_name', 'Unknown Destination')
        affinities = data.get('affinities', [])
        
        # Merge evidence back into affinities for display
        theme_evidence = evidence_data.get('theme_evidence', {})
        for affinity in affinities:
            theme_name = affinity.get('theme', 'Unknown')
            if theme_name in theme_evidence:
                affinity['comprehensive_attribute_evidence'] = theme_evidence[theme_name]
        
        quality_assessment = data.get('quality_assessment', {})
        intelligence_insights = data.get('intelligence_insights', {})
        composition_analysis = data.get('composition_analysis', {})
        qa_workflow = data.get('qa_workflow', {})
        comprehensive_evidence = data.get('comprehensive_evidence', {})
        
        # Quality metrics
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
        
        # Generate intelligence insights cards
        insights_html = self._generate_intelligence_insights(intelligence_insights)
        
        # Generate composition analysis
        composition_html = self._generate_composition_analysis(composition_analysis)
        
        # Generate quality metrics
        quality_html = self._generate_quality_metrics(quality_assessment)
        
        # Generate comprehensive evidence display
        evidence_html = self._generate_comprehensive_evidence_display(comprehensive_evidence)
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{destination_name} - Enhanced Intelligence Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        {self._get_enhanced_css()}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Section -->
        <header class="destination-header">
            <div class="header-content">
                <h1 class="destination-title">{destination_name}</h1>
                <div class="quality-badge quality-{quality_level.lower().replace(' ', '-')}">
                    {quality_level} Quality ({quality_score:.3f})
                </div>
            </div>
            <div class="header-stats">
                <div class="stat-card">
                    <div class="stat-value">{len(affinities)}</div>
                    <div class="stat-label">Enhanced Themes</div>
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
            </div>
        </header>
        
        <!-- Intelligence Insights Section -->
        <section class="intelligence-insights">
            <h2><i class="fas fa-brain"></i> Intelligence Insights</h2>
            {insights_html}
        </section>
        
        <!-- Enhanced Themes Section -->
        <section class="enhanced-themes">
            <h2><i class="fas fa-sparkles"></i> Enhanced Themes ({len(affinities)})</h2>
            <div class="themes-grid">
                {themes_html}
            </div>
        </section>
        
        <!-- Composition Analysis Section -->
        <section class="composition-analysis">
            <h2><i class="fas fa-palette"></i> Composition Analysis</h2>
            {composition_html}
        </section>
        
        <!-- Quality Assessment Section -->
        <section class="quality-assessment">
            <h2><i class="fas fa-chart-line"></i> Quality Assessment</h2>
            {quality_html}
        </section>
        
        <!-- Comprehensive Evidence Section -->
        <section class="comprehensive-evidence">
            <h2><i class="fas fa-search"></i> Evidence Collection</h2>
            {evidence_html}
        </section>
        
        <!-- Footer -->
        <footer class="dashboard-footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | SmartDestinationThemes Enhanced Intelligence System</p>
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
        
        {self._get_enhanced_javascript()}
    </script>
</body>
</html>
        """
    
    def _generate_enhanced_themes(self, affinities: list) -> str:
        """Generate HTML for enhanced theme cards."""
        if not affinities:
            return '<p class="no-data">No enhanced themes available.</p>'
        
        themes_html = ""
        for theme in affinities:
            themes_html += self._generate_single_theme_card(theme)
        
        return themes_html
    
    def _generate_single_theme_card(self, theme: dict) -> str:
        """Generate HTML for a single enhanced theme card."""
        
        # Basic theme info
        theme_name = theme.get('theme', 'Unknown Theme')
        category = theme.get('category', 'general')
        confidence = theme.get('confidence', 0)
        rationale = theme.get('rationale', 'No rationale provided')
        
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
        
        confidence_color = self._get_confidence_color(confidence)
        
        return f"""
        <div class="theme-card enhanced-theme">
            <div class="theme-header">
                <div class="theme-title-section">
                    <h3 class="theme-title">{theme_name} {self._generate_evidence_paperclip(theme_name, theme)}</h3>
                    <span class="theme-category">{category}</span>
                </div>
                <div class="confidence-score" style="background: {confidence_color}">
                    {confidence:.2f}
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
        """Generate paperclip icon for evidence modal."""
        # Get evidence from comprehensive_attribute_evidence which contains the loaded evidence data
        comprehensive_evidence = theme_data.get('comprehensive_attribute_evidence', {})
        main_theme_evidence = comprehensive_evidence.get('main_theme', {})
        evidence_pieces = main_theme_evidence.get('evidence_pieces', [])
        
        # Collect all evidence types for this theme including new content intelligence attributes
        all_evidence = {
            'theme_evidence': evidence_pieces,
            'nano_themes': theme_data.get('nano_themes', []),
            'price_insights': theme_data.get('price_insights', {}),
            'authenticity_analysis': theme_data.get('authenticity_analysis', {}),
            'hidden_gem_score': theme_data.get('hidden_gem_score', {}),
            'depth_analysis': theme_data.get('depth_analysis', {}),
            # New content intelligence attributes
            'iconic_landmarks': theme_data.get('iconic_landmarks', {}),
            'practical_travel_intelligence': theme_data.get('practical_travel_intelligence', {}),
            'neighborhood_insights': theme_data.get('neighborhood_insights', {}),
            'content_discovery_intelligence': theme_data.get('content_discovery_intelligence', {}),
            'llm_generated': theme_data.get('llm_generated', True)  # Track if LLM generated
        }
        
        # Check if we have any evidence (including content intelligence data)
        has_evidence = (
            len(evidence_pieces) > 0 or 
            len(all_evidence['nano_themes']) > 0 or
            bool(all_evidence['price_insights']) or
            bool(all_evidence['authenticity_analysis']) or
            bool(all_evidence['hidden_gem_score']) or
            bool(all_evidence['depth_analysis']) or
            # Check content intelligence attributes
            bool(all_evidence['iconic_landmarks']) or
            bool(all_evidence['practical_travel_intelligence']) or
            bool(all_evidence['neighborhood_insights']) or
            bool(all_evidence['content_discovery_intelligence'])
        )
        
        if not has_evidence:
            return '<i class="fas fa-paperclip evidence-paperclip no-evidence" title="No evidence available"></i>'
        
        # Create unique ID for this evidence using deterministic hash
        import hashlib
        evidence_str = f"{theme_name}_theme_evidence_{str(sorted(str(all_evidence)))}"
        evidence_id = f"{theme_name.replace(' ', '_')}_theme_evidence_{hashlib.md5(evidence_str.encode()).hexdigest()[:8]}"
        
        # Store in evidence store instead of embedding in onclick
        if not hasattr(self, '_evidence_store'):
            self._evidence_store = {}
        self._evidence_store[evidence_id] = all_evidence
        
        return f'''<i class="fas fa-paperclip evidence-paperclip" 
                    onclick="showThemeEvidenceModal('{theme_name}', '{evidence_id}')" 
                    title="View evidence for {theme_name}"></i>'''
    
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
        # Check if we have evidence for this specific attribute
        attribute_evidence = comprehensive_evidence.get(attribute_name, {})
        
        if not attribute_evidence:
            return '<i class="fas fa-paperclip evidence-paperclip no-evidence" title="No evidence available for this attribute"></i>'
        
        # Create unique ID for this evidence using deterministic hash
        evidence_str = f"{theme_name}_{attribute_name}_{str(sorted(str(attribute_evidence)))}"
        evidence_id = f"{theme_name.replace(' ', '_')}_{attribute_name}_{hashlib.md5(evidence_str.encode()).hexdigest()[:8]}"
        
        # Create evidence data for modal
        evidence_data = {
            'attribute_name': attribute_name,
            'attribute_data': attribute_data,
            'evidence': attribute_evidence,
            'llm_generated': True  # Most attributes are LLM generated
        }
        
        # Store in evidence store
        if not hasattr(self, '_evidence_store'):
            self._evidence_store = {}
        self._evidence_store[evidence_id] = evidence_data
        
        return f'''<i class="fas fa-paperclip evidence-paperclip" 
                    onclick="showAttributeEvidenceModal('{theme_name}', '{attribute_name}', '{evidence_id}')" 
                    title="View evidence for {attribute_name.replace('_', ' ')}"></i>'''
    
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
    
    def _generate_quality_metrics(self, quality_assessment: dict) -> str:
        """Generate quality metrics section."""
        if not quality_assessment:
            return '<p class="no-data">No quality assessment available.</p>'
        
        metrics = quality_assessment.get('metrics', {})
        if not metrics:
            return '<p class="no-data">No quality metrics available.</p>'
        
        core_metrics = ['factual_accuracy', 'thematic_coverage', 'actionability', 'uniqueness', 'source_credibility']
        intelligence_metrics = ['theme_depth', 'authenticity', 'emotional_resonance']
        
        # Core metrics
        core_html = []
        for metric in core_metrics:
            if metric in metrics:
                value = metrics[metric]
                color = self._get_confidence_color(value)
                name = metric.replace('_', ' ').title()
                core_html.append(f"""
                <div class="metric-item">
                    <div class="metric-name">{name}</div>
                    <div class="metric-value" style="color: {color}">{value:.3f}</div>
                </div>
                """)
        
        # Intelligence metrics
        intel_html = []
        icons = {'theme_depth': '📊', 'authenticity': '🏆', 'emotional_resonance': '✨'}
        for metric in intelligence_metrics:
            if metric in metrics:
                value = metrics[metric]
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

    def _generate_comprehensive_evidence_display(self, comprehensive_evidence: dict) -> str:
        """Generate comprehensive evidence display showing all evidence types."""
        if not comprehensive_evidence:
            return '<div class="no-data">No comprehensive evidence data available</div>'
        
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
                <button class="view-evidence-btn" onclick="toggleEvidenceType(this, '{title.lower().replace(' ', '_')}')" style="background: {color}">
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
                <button class="view-evidence-btn" onclick="toggleContentIntelligence(this, '{title.lower().replace(' ', '_')}')" style="background: {color}">
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
            quality_score = data.get('quality_assessment', {}).get('overall_score', 0)
            quality_level = self._get_quality_level(quality_score)
            theme_count = len(data.get('affinities', []))
            hidden_gems = data.get('intelligence_insights', {}).get('hidden_gems_count', 0)
            
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
    <title>Enhanced Intelligence Dashboard - SmartDestinationThemes</title>
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
            <h1>🧠 Enhanced Intelligence Dashboard</h1>
            <p>SmartDestinationThemes with Advanced Intelligence Analysis</p>
        </div>
        
        <div class="destinations-index-grid">
            {"".join(destination_cards)}
        </div>
        
        <footer class="dashboard-footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | SmartDestinationThemes Enhanced Intelligence System</p>
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
            cursor: not-allowed;
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
            .themes-grid { grid-template-columns: 1fr; }
            .composition-content { grid-template-columns: 1fr; }
            .quality-content { grid-template-columns: 1fr; }
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
            console.log('Enhanced Intelligence Dashboard with Evidence loaded');
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
            
            // Show evidence if available
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
            } else {
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
            
            // Theme Evidence
            if (evidenceData.theme_evidence && evidenceData.theme_evidence.length > 0) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<h3>🔍 Theme Evidence</h3>';
                evidenceData.theme_evidence.forEach((piece, index) => {
                    modalContent += `
                    <div class="evidence-item">
                        <div class="evidence-type-tag">Web Evidence ${index + 1}</div>
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
            
            // LLM Generated indicator
            if (evidenceData.llm_generated) {
                modalContent += '<div class="evidence-section">';
                modalContent += '<div class="evidence-item">';
                modalContent += '<div class="llm-generated-tag">LLM Generated</div>';
                modalContent += '<p>This theme insight was generated by our AI system and may not have external web evidence.</p>';
                modalContent += '</div>';
                modalContent += '</div>';
            }
            
            if (!modalContent) {
                modalContent = '<p>No evidence data available for this theme.</p>';
            }
            
            modalBody.innerHTML = modalContent;
            modal.style.display = 'block';
        }
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