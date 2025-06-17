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
            result = self.generate_destination_viewer(json_file, output_dir)
            if result:
                generated_files.append(result)
                
                # Load data for index
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        destination_name = data.get('destination_name', 'Unknown')
                        destination_data[destination_name] = {
                            'file': os.path.basename(result),
                            'quality_score': data.get('quality_assessment', {}).get('overall_score', 0),
                            'hidden_gems': data.get('intelligence_insights', {}).get('hidden_gems_count', 0),
                            'theme_count': len(data.get('affinities', []))
                        }
                except:
                    continue
        
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
        """Generate HTML content for a single destination."""
        
        destination_name = data.get('destination_name', 'Unknown Destination')
        affinities = data.get('affinities', [])
        quality_assessment = data.get('quality_assessment', {})
        intelligence_insights = data.get('intelligence_insights', {})
        composition_analysis = data.get('composition_analysis', {})
        qa_workflow = data.get('qa_workflow', {})
        
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
        
        <!-- Footer -->
        <footer class="dashboard-footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | SmartDestinationThemes Enhanced Intelligence System</p>
        </footer>
    </div>
    
    <script>
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
        
        # Generate enhanced details
        details_html = self._generate_theme_details(
            theme, depth_analysis, contextual_info, theme.get('micro_climate', {}),
            theme.get('cultural_sensitivity', {}), theme.get('theme_interconnections', {})
        )
        
        confidence_color = self._get_confidence_color(confidence)
        
        return f"""
        <div class="theme-card enhanced-theme">
            <div class="theme-header">
                <div class="theme-title-section">
                    <h3 class="theme-title">{theme_name}</h3>
                    <span class="theme-category">{category}</span>
                </div>
                <div class="confidence-score" style="background: {confidence_color}">
                    {confidence:.2f}
                </div>
            </div>
            
            <div class="intelligence-badges">
                {badges_html}
            </div>
            
            <div class="theme-rationale">
                <p>{rationale}</p>
            </div>
            
            <div class="theme-details">
                {details_html}
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
    
    def _generate_theme_details(self, theme, depth_analysis, contextual_info, micro_climate, cultural_sensitivity, interconnections) -> str:
        """Generate detailed theme information."""
        details = []
        
        # Sub-themes
        sub_themes = theme.get('sub_themes', [])
        if sub_themes:
            sub_theme_tags = ''.join(f'<span class="sub-theme-tag">{st}</span>' for st in sub_themes)
            details.append(f'<div class="detail-row"><strong>🎯 Sub-themes:</strong> <div class="sub-themes">{sub_theme_tags}</div></div>')
        
        # Nano themes
        nano_themes = depth_analysis.get('nano_themes', [])
        if nano_themes:
            nano_tags = ''.join(f'<span class="nano-theme-tag">{nt}</span>' for nt in nano_themes[:4])
            details.append(f'<div class="detail-row"><strong>🔬 Nano Themes:</strong> <div class="nano-themes">{nano_tags}</div></div>')
        
        # Demographics
        demographics = contextual_info.get('demographic_suitability', [])
        if demographics:
            details.append(f'<div class="detail-row"><strong>👥 Best For:</strong> {", ".join(demographics)}</div>')
        
        # Time commitment
        time_commit = contextual_info.get('time_commitment', '')
        if time_commit:
            details.append(f'<div class="detail-row"><strong>⏰ Time Needed:</strong> {time_commit.title()}</div>')
        
        # Best timing
        best_time = micro_climate.get('best_time_of_day', [])
        if best_time and best_time != ['flexible']:
            details.append(f'<div class="detail-row"><strong>🕐 Best Time:</strong> {", ".join(best_time)}</div>')
        
        # Weather needs
        weather_deps = micro_climate.get('weather_dependencies', [])
        if weather_deps:
            details.append(f'<div class="detail-row"><strong>🌤️ Weather:</strong> {", ".join(weather_deps)}</div>')
        
        # Cultural notes
        cultural_notes = cultural_sensitivity.get('considerations', [])
        if cultural_notes:
            details.append(f'<div class="detail-row"><strong>🏛️ Cultural:</strong> {", ".join(cultural_notes[:2])}</div>')
        
        # Combinations
        combinations = interconnections.get('natural_combinations', [])
        if combinations:
            details.append(f'<div class="detail-row"><strong>🔗 Combines With:</strong> {", ".join(combinations[:3])}</div>')
        
        # Price and validation
        details.append(f'<div class="detail-row"><strong>💰 Price:</strong> {theme.get("price_point", "N/A").title()}</div>')
        details.append(f'<div class="detail-row"><strong>✅ Status:</strong> {theme.get("validation", "N/A")}</div>')
        
        return ''.join(details)
    
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
    
    def _generate_index_html(self, destination_data: dict) -> str:
        """Generate index page for multiple destinations."""
        
        destination_cards = []
        for dest_name, dest_info in destination_data.items():
            quality_score = dest_info['quality_score']
            quality_level = self._get_quality_level(quality_score)
            
            destination_cards.append(f"""
            <div class="destination-index-card">
                <div class="dest-card-header">
                    <h3>{dest_name}</h3>
                    <span class="quality-badge quality-{quality_level.lower().replace(' ', '-')}">{quality_level}</span>
                </div>
                <div class="dest-card-stats">
                    <div class="stat"><strong>{dest_info['theme_count']}</strong> themes</div>
                    <div class="stat"><strong>{dest_info['hidden_gems']}</strong> hidden gems</div>
                    <div class="stat"><strong>{quality_score:.3f}</strong> quality score</div>
                </div>
                <a href="{dest_info['file']}" class="view-button">View Details</a>
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