#!/usr/bin/env python3
"""
HTML Viewer Generator for SmartDestinationThemes
Creates a modern, interactive dashboard showing all destination themes and metadata.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
import base64

class ThemeViewerGenerator:
    """Generates modern HTML dashboard for destination themes."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        
    def generate_html_viewer(self, data_file: str, output_dir: str = "dashboard"):
        """Generate modular HTML dashboard with separate pages for each destination."""
        
        # Load the data
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Data file {data_file} not found")
            return False
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in {data_file}")
            return False
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate individual destination pages
        destination_files = {}
        for destination in data.keys():
            dest_filename = self._sanitize_filename(destination) + ".html"
            dest_filepath = os.path.join(output_dir, dest_filename)
            
            # Generate individual destination page
            dest_html = self._generate_destination_page(destination, data[destination], data_file)
            
            try:
                with open(dest_filepath, 'w', encoding='utf-8') as f:
                    f.write(dest_html)
                destination_files[destination] = dest_filename
                print(f"✅ Generated destination page: {dest_filepath}")
            except Exception as e:
                print(f"❌ Error writing destination file {dest_filepath}: {e}")
                continue
        
        # Generate main index page
        index_html = self._generate_index_page(data, data_file, destination_files)
        index_filepath = os.path.join(output_dir, "index.html")
        
        try:
            with open(index_filepath, 'w', encoding='utf-8') as f:
                f.write(index_html)
            print(f"✅ Generated main dashboard: {index_filepath}")
            
            # Also create a top-level link for convenience
            with open("themes_dashboard.html", 'w', encoding='utf-8') as f:
                f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url=dashboard/index.html">
    <title>Redirecting to Dashboard...</title>
</head>
<body>
    <p>Redirecting to <a href="dashboard/index.html">SmartDestinationThemes Dashboard</a>...</p>
</body>
</html>
                """)
            
            return True
        except Exception as e:
            print(f"❌ Error writing index file: {e}")
            return False
    
    def _generate_html_content(self, data: Dict[str, Any], source_file: str) -> str:
        """Generate the complete HTML content."""
        
        # Extract summary statistics
        stats = self._calculate_statistics(data)
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartDestinationThemes Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="dashboard">
        {self._generate_header(source_file, stats)}
        {self._generate_summary_cards(stats)}
        {self._generate_destinations_grid(data)}
        {self._generate_analytics_section(data, stats)}
        {self._generate_footer()}
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>
"""
        return html
    
    def _get_css_styles(self) -> str:
        """Return modern CSS styles."""
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
        }
        
        .dashboard {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            color: #666;
            font-size: 1.1rem;
            margin-bottom: 20px;
        }
        
        .header .meta-info {
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
            font-size: 0.9rem;
            color: #888;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .card-icon {
            font-size: 2rem;
            margin-right: 15px;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
        }
        
        .card-icon.destinations { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
        .card-icon.themes { background: linear-gradient(135deg, #f093fb, #f5576c); color: white; }
        .card-icon.quality { background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; }
        .card-icon.performance { background: linear-gradient(135deg, #43e97b, #38f9d7); color: white; }
        
        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #333;
        }
        
        .card-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 5px;
        }
        
        .card-subtitle {
            color: #666;
            font-size: 0.9rem;
        }
        
        .destinations-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .destination-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .destination-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .destination-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #333;
        }
        
        .destination-meta {
            display: flex;
            gap: 15px;
            font-size: 0.9rem;
            color: #666;
        }
        
        .quality-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
        }
        
        .quality-excellent { background: #d4edda; color: #155724; }
        .quality-good { background: #cce5ff; color: #004085; }
        .quality-acceptable { background: #fff3cd; color: #856404; }
        .quality-poor { background: #f8d7da; color: #721c24; }
        
        .themes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .theme-card {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s ease;
        }
        
        .theme-card:hover {
            transform: scale(1.02);
        }
        
        .theme-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .theme-title {
            font-weight: 600;
            color: #333;
            font-size: 1.1rem;
        }
        
        .confidence-score {
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: auto;
        }
        
        .theme-category {
            display: inline-block;
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-bottom: 10px;
        }
        
        .theme-details {
            font-size: 0.9rem;
            color: #666;
            line-height: 1.4;
        }
        
        .sub-themes {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin: 8px 0;
        }
        
        .sub-theme {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.75rem;
        }
        
        .intelligence-badges-container {
            margin: 10px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        
        .intelligence-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            color: white;
            font-weight: 600;
            white-space: nowrap;
        }
        
        .enhanced-theme-card {
            position: relative;
        }
        
        .enhanced-theme-card::before {
            content: '🧠';
            position: absolute;
            top: 15px;
            right: 15px;
            font-size: 1.2rem;
            opacity: 0.3;
        }
        
        .analytics-section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .analytics-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .analytics-header h2 {
            font-size: 2rem;
            color: #333;
            margin-bottom: 10px;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
        }
        
        .chart-container {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            height: 300px;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }
        
        .expandable {
            cursor: pointer;
            user-select: none;
        }
        
        .expandable-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }
        
        .expandable-content.expanded {
            max-height: 1000px;
        }
        
        .expand-icon {
            transition: transform 0.3s ease;
        }
        
        .expand-icon.rotated {
            transform: rotate(180deg);
        }
        
        @media (max-width: 768px) {
            .dashboard {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .destinations-grid {
                grid-template-columns: 1fr;
            }
            
            .themes-grid {
                grid-template-columns: 1fr;
            }
            
            .charts-grid {
                grid-template-columns: 1fr;
            }
        }
        """
    
    def _generate_header(self, source_file: str, stats: Dict[str, Any]) -> str:
        """Generate the dashboard header."""
        return f"""
        <div class="header">
            <h1><i class="fas fa-globe-americas"></i> SmartDestinationThemes Dashboard</h1>
            <div class="subtitle">Intelligent Destination Affinity Analysis & Recommendations</div>
            <div class="meta-info">
                <div><i class="fas fa-file-alt"></i> Source: {source_file}</div>
                <div><i class="fas fa-clock"></i> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div><i class="fas fa-chart-line"></i> System: Production Mode</div>
            </div>
        </div>
        """
    
    def _generate_summary_cards(self, stats: Dict[str, Any]) -> str:
        """Generate summary statistics cards."""
        return f"""
        <div class="summary-cards">
            <div class="card">
                <div class="card-header">
                    <div class="card-icon destinations">
                        <i class="fas fa-map-marked-alt"></i>
                    </div>
                    <div class="card-title">Destinations</div>
                </div>
                <div class="card-value">{stats['total_destinations']}</div>
                <div class="card-subtitle">Analyzed destinations</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon themes">
                        <i class="fas fa-lightbulb"></i>
                    </div>
                    <div class="card-title">Total Themes</div>
                </div>
                <div class="card-value">{stats['total_themes']}</div>
                <div class="card-subtitle">Generated affinities</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon quality">
                        <i class="fas fa-star"></i>
                    </div>
                    <div class="card-title">Avg Quality</div>
                </div>
                <div class="card-value">{stats['avg_quality']:.2f}</div>
                <div class="card-subtitle">Quality score (0-1)</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon performance">
                        <i class="fas fa-tachometer-alt"></i>
                    </div>
                    <div class="card-title">Performance</div>
                </div>
                <div class="card-value">{stats['avg_processing_time']:.1f}s</div>
                <div class="card-subtitle">Avg processing time</div>
            </div>
        </div>
        """
    
    def _generate_destinations_grid(self, data: Dict[str, Any]) -> str:
        """Generate the destinations grid with themes."""
        destinations_html = ""
        
        for destination, dest_data in data.items():
            affinities = dest_data.get('affinities', [])
            quality_assessment = dest_data.get('quality_assessment', {})
            qa_workflow = dest_data.get('qa_workflow', {})
            processing_time = dest_data.get('processing_time_seconds', 0)
            
            # Quality badge
            quality_score = quality_assessment.get('overall_score', 0)
            quality_level = quality_assessment.get('quality_level', 'Unknown')
            quality_class = f"quality-{quality_level.lower()}"
            
            # Generate themes HTML
            themes_html = ""
            for theme in affinities:
                sub_themes_html = ""
                for sub_theme in theme.get('sub_themes', []):
                    sub_themes_html += f'<span class="sub-theme">{sub_theme}</span>'
                
                confidence_color = self._get_confidence_color(theme.get('confidence', 0))
                
                themes_html += f"""
                <div class="theme-card">
                    <div class="theme-header">
                        <div class="theme-title">{theme.get('theme', 'Unknown')}</div>
                        <div class="confidence-score" style="background: {confidence_color}">
                            {theme.get('confidence', 0):.2f}
                        </div>
                    </div>
                    <div class="theme-category">{theme.get('category', 'general')}</div>
                    <div class="sub-themes">{sub_themes_html}</div>
                    <div class="theme-details">
                        <strong>Rationale:</strong> {theme.get('rationale', 'N/A')}<br>
                        <strong>Price Point:</strong> {theme.get('price_point', 'N/A').title()}<br>
                        <strong>Validation:</strong> {theme.get('validation', 'N/A')}
                    </div>
                </div>
                """
            
            # Quality metrics
            quality_metrics_html = ""
            if quality_assessment.get('metrics'):
                for metric, value in quality_assessment['metrics'].items():
                    metric_name = metric.replace('_', ' ').title()
                    quality_metrics_html += f"""
                    <div style="margin: 5px 0;">
                        <strong>{metric_name}:</strong> {value:.3f}
                    </div>
                    """
            
            # QA workflow info
            qa_status = qa_workflow.get('status', 'N/A')
            qa_score = qa_workflow.get('quality_score', 0)
            
            destinations_html += f"""
            <div class="destination-card">
                <div class="destination-header">
                    <div>
                        <div class="destination-title">{destination}</div>
                        <div class="destination-meta">
                            <span><i class="fas fa-clock"></i> {processing_time:.2f}s</span>
                            <span><i class="fas fa-lightbulb"></i> {len(affinities)} themes</span>
                        </div>
                    </div>
                    <div class="quality-badge {quality_class}">
                        {quality_level} ({quality_score:.3f})
                    </div>
                </div>
                
                <div class="expandable" onclick="toggleExpand(this)">
                    <h3 style="margin-bottom: 15px;">
                        <i class="fas fa-lightbulb"></i> Generated Themes 
                        <i class="fas fa-chevron-down expand-icon" style="float: right;"></i>
                    </h3>
                </div>
                <div class="expandable-content">
                    <div class="themes-grid">
                        {themes_html}
                    </div>
                </div>
                
                <div class="expandable" onclick="toggleExpand(this)" style="margin-top: 20px;">
                    <h3 style="margin-bottom: 15px;">
                        <i class="fas fa-chart-bar"></i> Quality Assessment 
                        <i class="fas fa-chevron-down expand-icon" style="float: right;"></i>
                    </h3>
                </div>
                <div class="expandable-content">
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 10px;">
                        <div style="margin-bottom: 10px;"><strong>Overall Score:</strong> {quality_score:.3f}</div>
                        <div style="margin-bottom: 10px;"><strong>QA Status:</strong> {qa_status}</div>
                        {quality_metrics_html}
                    </div>
                </div>
            </div>
            """
        
        return f'<div class="destinations-grid">{destinations_html}</div>'
    
    def _generate_analytics_section(self, data: Dict[str, Any], stats: Dict[str, Any]) -> str:
        """Generate analytics charts section."""
        
        # Prepare data for charts
        quality_data = []
        category_counts = {}
        confidence_distribution = []
        
        for destination, dest_data in data.items():
            # Quality scores
            quality_assessment = dest_data.get('quality_assessment', {})
            if quality_assessment.get('overall_score'):
                quality_data.append({
                    'destination': destination,
                    'score': quality_assessment['overall_score']
                })
            
            # Category counts
            for theme in dest_data.get('affinities', []):
                category = theme.get('category', 'other')
                category_counts[category] = category_counts.get(category, 0) + 1
                
                # Confidence distribution
                confidence = theme.get('confidence', 0)
                confidence_distribution.append(confidence)
        
        return f"""
        <div class="analytics-section">
            <div class="analytics-header">
                <h2><i class="fas fa-chart-line"></i> Analytics & Insights</h2>
                <p>Comprehensive analysis of destination themes and quality metrics</p>
            </div>
            <div class="charts-grid">
                <div class="chart-container">
                    <canvas id="qualityChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="categoryChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="confidenceChart"></canvas>
                </div>
            </div>
        </div>
        
        <script>
            // Quality Scores Chart
            const qualityCtx = document.getElementById('qualityChart').getContext('2d');
            new Chart(qualityCtx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps([item['destination'] for item in quality_data])},
                    datasets: [{{
                        label: 'Quality Score',
                        data: {json.dumps([item['score'] for item in quality_data])},
                        backgroundColor: 'rgba(102, 126, 234, 0.8)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Quality Scores by Destination'
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 1
                        }}
                    }}
                }}
            }});
            
            // Category Distribution Chart
            const categoryCtx = document.getElementById('categoryChart').getContext('2d');
            new Chart(categoryCtx, {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(list(category_counts.keys()))},
                    datasets: [{{
                        data: {json.dumps(list(category_counts.values()))},
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.8)',
                            'rgba(240, 147, 251, 0.8)',
                            'rgba(79, 172, 254, 0.8)',
                            'rgba(67, 233, 123, 0.8)',
                            'rgba(245, 87, 108, 0.8)',
                            'rgba(56, 249, 215, 0.8)'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Theme Categories Distribution'
                        }}
                    }}
                }}
            }});
            
            // Confidence Distribution Chart
            const confidenceCtx = document.getElementById('confidenceChart').getContext('2d');
            const confidenceBins = [0, 0.2, 0.4, 0.6, 0.8, 1.0];
            const confidenceHistogram = new Array(confidenceBins.length - 1).fill(0);
            
            {json.dumps(confidence_distribution)}.forEach(conf => {{
                for (let i = 0; i < confidenceBins.length - 1; i++) {{
                    if (conf >= confidenceBins[i] && conf < confidenceBins[i + 1]) {{
                        confidenceHistogram[i]++;
                        break;
                    }}
                }}
            }});
            
            new Chart(confidenceCtx, {{
                type: 'bar',
                data: {{
                    labels: ['0.0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0'],
                    datasets: [{{
                        label: 'Number of Themes',
                        data: confidenceHistogram,
                        backgroundColor: 'rgba(67, 233, 123, 0.8)',
                        borderColor: 'rgba(67, 233, 123, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Confidence Score Distribution'
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        </script>
        """
    
    def _generate_footer(self) -> str:
        """Generate the dashboard footer."""
        return f"""
        <div class="footer">
            <p><i class="fas fa-robot"></i> Generated by SmartDestinationThemes Production System</p>
            <p>© {datetime.now().year} - Intelligent Travel Affinity Analysis Platform</p>
        </div>
        """
    
    def _get_javascript(self) -> str:
        """Return JavaScript for interactive features."""
        return """
        function toggleExpand(element) {
            const content = element.nextElementSibling;
            const icon = element.querySelector('.expand-icon');
            
            if (content.classList.contains('expanded')) {
                content.classList.remove('expanded');
                icon.classList.remove('rotated');
            } else {
                content.classList.add('expanded');
                icon.classList.add('rotated');
            }
        }
        
        // Auto-expand first destination on load
        document.addEventListener('DOMContentLoaded', function() {
            const firstExpandable = document.querySelector('.expandable');
            if (firstExpandable) {
                toggleExpand(firstExpandable);
            }
        });
        """
    
    def _calculate_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics from the data."""
        stats = {
            'total_destinations': len(data),
            'total_themes': 0,
            'avg_quality': 0,
            'avg_processing_time': 0,
            'quality_scores': [],
            'processing_times': []
        }
        
        for destination, dest_data in data.items():
            # Count themes
            affinities = dest_data.get('affinities', [])
            stats['total_themes'] += len(affinities)
            
            # Quality scores
            quality_assessment = dest_data.get('quality_assessment', {})
            if quality_assessment.get('overall_score'):
                stats['quality_scores'].append(quality_assessment['overall_score'])
            
            # Processing times
            processing_time = dest_data.get('processing_time_seconds', 0)
            if processing_time > 0:
                stats['processing_times'].append(processing_time)
        
        # Calculate averages
        if stats['quality_scores']:
            stats['avg_quality'] = sum(stats['quality_scores']) / len(stats['quality_scores'])
        
        if stats['processing_times']:
            stats['avg_processing_time'] = sum(stats['processing_times']) / len(stats['processing_times'])
        
        return stats
    
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
    
    def _sanitize_filename(self, destination: str) -> str:
        """Convert destination name to safe filename."""
        import re
        # Remove special characters and replace spaces with underscores
        safe_name = re.sub(r'[^\w\s-]', '', destination)
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        return safe_name.lower()
    
    def _generate_index_page(self, data: Dict[str, Any], source_file: str, destination_files: Dict[str, str]) -> str:
        """Generate the main index page with destination overview."""
        stats = self._calculate_statistics(data)
        
        # Generate destination cards for index
        destination_cards_html = ""
        for destination, dest_data in data.items():
            dest_filename = destination_files.get(destination, "#")
            affinities = dest_data.get('affinities', [])
            quality_assessment = dest_data.get('quality_assessment', {})
            processing_time = dest_data.get('processing_time_seconds', 0)
            
            quality_score = quality_assessment.get('overall_score', 0)
            quality_level = quality_assessment.get('quality_level', 'Unknown')
            quality_class = f"quality-{quality_level.lower()}"
            
            # Top themes preview
            top_themes = affinities[:3]  # Show top 3 themes
            themes_preview = ""
            for theme in top_themes:
                confidence_color = self._get_confidence_color(theme.get('confidence', 0))
                themes_preview += f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin: 5px 0; padding: 8px; background: #f8f9fa; border-radius: 8px;">
                    <span style="font-weight: 500;">{theme.get('theme', 'Unknown')}</span>
                    <span style="background: {confidence_color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem;">
                        {theme.get('confidence', 0):.2f}
                    </span>
                </div>
                """
            
            destination_cards_html += f"""
            <div class="destination-overview-card">
                <div class="destination-overview-header">
                    <h3>{destination}</h3>
                    <div class="quality-badge {quality_class}">
                        {quality_level} ({quality_score:.3f})
                    </div>
                </div>
                <div class="destination-overview-meta">
                    <span><i class="fas fa-lightbulb"></i> {len(affinities)} themes</span>
                    <span><i class="fas fa-clock"></i> {processing_time:.2f}s</span>
                </div>
                <div class="themes-preview">
                    <h4>Top Themes:</h4>
                    {themes_preview}
                    {f'<div style="text-align: center; color: #666; font-size: 0.9rem; margin-top: 10px;">+{len(affinities) - 3} more themes</div>' if len(affinities) > 3 else ''}
                </div>
                <div class="destination-actions">
                    <a href="{dest_filename}" class="view-button">
                        <i class="fas fa-eye"></i> View Full Analysis
                    </a>
                </div>
            </div>
            """
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartDestinationThemes Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_css_styles()}
        
        .destination-overview-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .destination-overview-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        }}
        
        .destination-overview-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .destination-overview-header h3 {{
            margin: 0;
            color: #333;
            font-size: 1.4rem;
        }}
        
        .destination-overview-meta {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            font-size: 0.9rem;
            color: #666;
        }}
        
        .themes-preview {{
            margin-bottom: 20px;
        }}
        
        .themes-preview h4 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 1rem;
        }}
        
        .destination-actions {{
            text-align: center;
        }}
        
        .view-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .view-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
            text-decoration: none;
            color: white;
        }}
        
        .destinations-overview-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        {self._generate_header(source_file, stats)}
        {self._generate_summary_cards(stats)}
        
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: white; font-size: 2rem; margin-bottom: 10px;">
                <i class="fas fa-map-marked-alt"></i> Destination Overview
            </h2>
            <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.1rem;">
                Click on any destination to view detailed analysis and themes
            </p>
        </div>
        
        <div class="destinations-overview-grid">
            {destination_cards_html}
        </div>
        
        {self._generate_analytics_section(data, stats)}
        {self._generate_footer()}
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>
        """
    
    def _generate_destination_page(self, destination: str, dest_data: Dict[str, Any], source_file: str) -> str:
        """Generate individual destination page."""
        affinities = dest_data.get('affinities', [])
        quality_assessment = dest_data.get('quality_assessment', {})
        qa_workflow = dest_data.get('qa_workflow', {})
        priority_data = dest_data.get('priority_data', [])
        processing_time = dest_data.get('processing_time_seconds', 0)
        
        # Enhanced intelligence data
        intelligence_insights = dest_data.get('intelligence_insights', {})
        composition_analysis = dest_data.get('composition_analysis', {})
        
        # Quality info
        quality_score = quality_assessment.get('overall_score', 0)
        quality_level = quality_assessment.get('quality_level', 'Unknown')
        quality_class = f"quality-{quality_level.lower()}"
        
        # Generate enhanced themes HTML
        themes_html = ""
        for theme in affinities:
            sub_themes_html = ""
            for sub_theme in theme.get('sub_themes', []):
                sub_themes_html += f'<span class="sub-theme">{sub_theme}</span>'
            
            confidence_color = self._get_confidence_color(theme.get('confidence', 0))
            
            # Seasonality info
            seasonality = theme.get('seasonality', {})
            peak_months = ", ".join(seasonality.get('peak', []))
            avoid_months = ", ".join(seasonality.get('avoid', []))
            
            # Enhanced intelligence data
            depth_analysis = theme.get('depth_analysis', {})
            authenticity_analysis = theme.get('authenticity_analysis', {})
            emotional_profile = theme.get('emotional_profile', {})
            experience_intensity = theme.get('experience_intensity', {})
            contextual_info = theme.get('contextual_info', {})
            hidden_gem_score = theme.get('hidden_gem_score', {})
            micro_climate = theme.get('micro_climate', {})
            cultural_sensitivity = theme.get('cultural_sensitivity', {})
            theme_interconnections = theme.get('theme_interconnections', {})
            
            # Intelligence badges
            intelligence_badges = ""
            
            # Depth badge
            depth_level = depth_analysis.get('depth_level', 'macro')
            depth_score = depth_analysis.get('depth_score', 0)
            depth_color = '#28a745' if depth_score > 0.8 else '#ffc107' if depth_score > 0.6 else '#6c757d'
            intelligence_badges += f'<span class="intelligence-badge" style="background: {depth_color};" title="Theme Depth: {depth_score:.2f}">📊 {depth_level.title()}</span>'
            
            # Authenticity badge  
            auth_level = authenticity_analysis.get('authenticity_level', 'balanced')
            auth_score = authenticity_analysis.get('authenticity_score', 0)
            auth_color = '#28a745' if auth_score > 0.8 else '#17a2b8' if auth_score > 0.6 else '#6c757d'
            auth_icon = '🏆' if auth_level == 'authentic_local' else '🌟' if auth_level == 'local_influenced' else '⚖️'
            intelligence_badges += f'<span class="intelligence-badge" style="background: {auth_color};" title="Authenticity: {auth_score:.2f}">{auth_icon} {auth_level.replace("_", " ").title()}</span>'
            
            # Hidden gem badge
            gem_level = hidden_gem_score.get('hidden_gem_level', 'mainstream')
            gem_score = hidden_gem_score.get('uniqueness_score', 0)
            if gem_level == 'true hidden gem':
                intelligence_badges += f'<span class="intelligence-badge" style="background: #dc3545;" title="Hidden Gem Score: {gem_score:.2f}">💎 Hidden Gem</span>'
            elif gem_level == 'local favorite':
                intelligence_badges += f'<span class="intelligence-badge" style="background: #fd7e14;" title="Hidden Gem Score: {gem_score:.2f}">⭐ Local Favorite</span>'
            elif gem_level == 'off the beaten path':
                intelligence_badges += f'<span class="intelligence-badge" style="background: #20c997;" title="Hidden Gem Score: {gem_score:.2f}">🗺️ Off Beaten Path</span>'
            
            # Experience intensity badge
            intensity = experience_intensity.get('overall_intensity', 'moderate')
            intensity_color = '#dc3545' if intensity == 'extreme' else '#fd7e14' if intensity == 'high' else '#ffc107' if intensity == 'moderate' else '#28a745'
            intensity_icon = '🔥' if intensity in ['extreme', 'high'] else '⚡' if intensity == 'moderate' else '🌱'
            intelligence_badges += f'<span class="intelligence-badge" style="background: {intensity_color};" title="Experience Intensity">{intensity_icon} {intensity.title()}</span>'
            
            # Emotional profile badge
            emotions = emotional_profile.get('primary_emotions', [])
            if emotions:
                emotion_text = ', '.join(emotions[:2])
                emotion_icon = '😊' if 'peaceful' in emotions else '🎯' if 'exhilarating' in emotions else '🧘' if 'contemplative' in emotions else '✨'
                intelligence_badges += f'<span class="intelligence-badge" style="background: #6f42c1;" title="Primary Emotions">{emotion_icon} {emotion_text.title()}</span>'
            
            # Enhanced details section
            enhanced_details = ""
            
            # Nano themes if available
            nano_themes = depth_analysis.get('nano_themes', [])
            if nano_themes:
                nano_html = ', '.join(nano_themes)
                enhanced_details += f'<div style="margin-bottom: 8px;"><strong>🔬 Nano Themes:</strong> {nano_html}</div>'
            
            # Demographics and context
            demographics = contextual_info.get('demographic_suitability', [])
            if demographics:
                demo_text = ', '.join(demographics)
                enhanced_details += f'<div style="margin-bottom: 8px;"><strong>👥 Best For:</strong> {demo_text}</div>'
            
            # Time commitment
            time_commit = contextual_info.get('time_commitment', '')
            if time_commit:
                enhanced_details += f'<div style="margin-bottom: 8px;"><strong>⏰ Time Needed:</strong> {time_commit.title()}</div>'
            
            # Best timing
            best_time = micro_climate.get('best_time_of_day', [])
            if best_time and best_time != ['flexible']:
                time_text = ', '.join(best_time)
                enhanced_details += f'<div style="margin-bottom: 8px;"><strong>🕐 Best Time:</strong> {time_text}</div>'
            
            # Weather dependencies
            weather_deps = micro_climate.get('weather_dependencies', [])
            if weather_deps:
                weather_text = ', '.join(weather_deps)
                enhanced_details += f'<div style="margin-bottom: 8px;"><strong>🌤️ Weather Needs:</strong> {weather_text}</div>'
            
            # Cultural considerations
            cultural_notes = cultural_sensitivity.get('considerations', [])
            if cultural_notes:
                cultural_text = ', '.join(cultural_notes[:2])
                enhanced_details += f'<div style="margin-bottom: 8px;"><strong>🏛️ Cultural Notes:</strong> {cultural_text}</div>'
            
            # Theme combinations
            combinations = theme_interconnections.get('natural_combinations', [])
            if combinations:
                combo_text = ', '.join(combinations[:3])
                enhanced_details += f'<div style="margin-bottom: 8px;"><strong>🔗 Pairs Well With:</strong> {combo_text}</div>'
            
            themes_html += f"""
            <div class="theme-card enhanced-theme-card">
                <div class="theme-header">
                    <div class="theme-title">{theme.get('theme', 'Unknown')}</div>
                    <div class="confidence-score" style="background: {confidence_color}">
                        {theme.get('confidence', 0):.2f}
                    </div>
                </div>
                <div class="theme-category">{theme.get('category', 'general')}</div>
                <div class="intelligence-badges-container">
                    {intelligence_badges}
                </div>
                <div class="sub-themes">{sub_themes_html}</div>
                <div class="theme-details">
                    <div style="margin-bottom: 12px;"><strong>💭 Rationale:</strong> {theme.get('rationale', 'N/A')}</div>
                    <div style="margin-bottom: 8px;"><strong>💰 Price Point:</strong> {theme.get('price_point', 'N/A').title()}</div>
                    <div style="margin-bottom: 8px;"><strong>🎯 Traveler Types:</strong> {', '.join(theme.get('traveler_types', []))}</div>
                    <div style="margin-bottom: 8px;"><strong>✅ Validation:</strong> {theme.get('validation', 'N/A')}</div>
                    {f'<div style="margin-bottom: 8px;"><strong>🌸 Peak Season:</strong> {peak_months}</div>' if peak_months else ''}
                    {f'<div style="margin-bottom: 8px;"><strong>🚫 Avoid:</strong> {avoid_months}</div>' if avoid_months else ''}
                    {enhanced_details}
                </div>
            </div>
            """
        
        # Quality metrics with enhanced intelligence metrics
        quality_metrics_html = ""
        if quality_assessment.get('metrics'):
            core_metrics = ['factual_accuracy', 'thematic_coverage', 'actionability', 'uniqueness', 'source_credibility']
            intelligence_metrics = ['theme_depth', 'authenticity', 'emotional_resonance']
            
            # Core metrics
            quality_metrics_html += "<h5 style='margin: 15px 0 10px 0; color: #495057;'>📋 Core Quality Metrics</h5>"
            for metric, value in quality_assessment['metrics'].items():
                if metric in core_metrics:
                    metric_name = metric.replace('_', ' ').title()
                    quality_metrics_html += f"""
                    <div style="margin: 8px 0; display: flex; justify-content: space-between;">
                        <strong>{metric_name}:</strong> 
                        <span style="color: {self._get_confidence_color(value)}; font-weight: 600;">{value:.3f}</span>
                    </div>
                    """
            
            # Intelligence metrics
            quality_metrics_html += "<h5 style='margin: 15px 0 10px 0; color: #495057;'>🧠 Intelligence Metrics</h5>"
            for metric, value in quality_assessment['metrics'].items():
                if metric in intelligence_metrics:
                    metric_name = metric.replace('_', ' ').title()
                    metric_icon = '📊' if metric == 'theme_depth' else '🏆' if metric == 'authenticity' else '✨'
                    quality_metrics_html += f"""
                    <div style="margin: 8px 0; display: flex; justify-content: space-between;">
                        <strong>{metric_icon} {metric_name}:</strong> 
                        <span style="color: {self._get_confidence_color(value)}; font-weight: 600;">{value:.3f}</span>
                    </div>
                    """
        
        # Intelligence insights section
        intelligence_insights_html = ""
        if intelligence_insights:
            insights_sections = []
            
            # Hidden gems insights
            hidden_gems_count = intelligence_insights.get('hidden_gems_count', 0)
            hidden_gems_ratio = intelligence_insights.get('hidden_gems_ratio', 0)
            if hidden_gems_count > 0:
                insights_sections.append(f"""
                <div style="background: #fff3cd; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #ffc107;">
                    <h5 style="margin: 0 0 8px 0; color: #856404;">💎 Hidden Gems Discovery</h5>
                    <div><strong>Count:</strong> {hidden_gems_count} hidden gems identified</div>
                    <div><strong>Ratio:</strong> {hidden_gems_ratio*100:.1f}% of themes are unique experiences</div>
                </div>
                """)
            
            # Authenticity insights
            avg_auth_score = intelligence_insights.get('average_authenticity_score', 0)
            if avg_auth_score > 0:
                auth_level_text = "Excellent" if avg_auth_score > 0.8 else "Good" if avg_auth_score > 0.6 else "Moderate"
                insights_sections.append(f"""
                <div style="background: #d4edda; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #28a745;">
                    <h5 style="margin: 0 0 8px 0; color: #155724;">🏆 Authenticity Analysis</h5>
                    <div><strong>Average Score:</strong> {avg_auth_score:.2f} ({auth_level_text})</div>
                    <div><strong>Focus:</strong> Strong emphasis on local and authentic experiences</div>
                </div>
                """)
            
            # Theme depth insights
            avg_depth_score = intelligence_insights.get('average_depth_score', 0)
            if avg_depth_score > 0:
                depth_level_text = "Nano-level" if avg_depth_score > 0.8 else "Micro-level" if avg_depth_score > 0.6 else "Macro-level"
                insights_sections.append(f"""
                <div style="background: #d1ecf1; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #17a2b8;">
                    <h5 style="margin: 0 0 8px 0; color: #0c5460;">📊 Theme Depth Analysis</h5>
                    <div><strong>Average Depth:</strong> {avg_depth_score:.2f} ({depth_level_text})</div>
                    <div><strong>Granularity:</strong> Themes provide detailed, specific experiences</div>
                </div>
                """)
            
            # Emotional variety insights
            emotional_variety = intelligence_insights.get('emotional_variety', {})
            emotions_covered = emotional_variety.get('emotions_covered', [])
            if emotions_covered:
                emotion_text = ', '.join(emotions_covered)
                insights_sections.append(f"""
                <div style="background: #f8d7da; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #dc3545;">
                    <h5 style="margin: 0 0 8px 0; color: #721c24;">✨ Emotional Resonance</h5>
                    <div><strong>Coverage:</strong> {len(emotions_covered)} emotional types</div>
                    <div><strong>Emotions:</strong> {emotion_text}</div>
                </div>
                """)
            
            intelligence_insights_html = ''.join(insights_sections)
        
        # Composition analysis
        composition_analysis_html = ""
        if composition_analysis:
            comp_score = composition_analysis.get('overall_composition_score', 0)
            category_dist = composition_analysis.get('category_distribution', {})
            
            # Category distribution chart data
            if category_dist:
                categories = list(category_dist.keys())
                counts = list(category_dist.values())
                
                composition_analysis_html = f"""
                <div style="background: #e7e3ff; padding: 20px; border-radius: 15px; margin: 15px 0; border-left: 4px solid #6f42c1;">
                    <h5 style="margin: 0 0 15px 0; color: #4a148c;">🎨 Composition Intelligence</h5>
                    <div style="margin-bottom: 10px;"><strong>Overall Score:</strong> {comp_score:.2f}</div>
                    <div style="margin-bottom: 15px;"><strong>Category Distribution:</strong></div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                        {''.join(f'<div style="background: rgba(255,255,255,0.7); padding: 10px; border-radius: 8px; text-align: center;"><strong>{cat.title()}</strong><br>{count} themes</div>' for cat, count in category_dist.items())}
                    </div>
                </div>
                """
        
        # QA workflow info
        qa_status = qa_workflow.get('status', 'N/A')
        qa_score = qa_workflow.get('quality_score', 0)
        
        # Priority data
        priority_data_html = ""
        if priority_data:
            for pd in priority_data[:3]:  # Show first 3
                safety_count = len(pd.get('safety_concerns', []))
                health_count = len(pd.get('health_advisories', []))
                emergency_count = len(pd.get('emergency_contacts', []))
                
                priority_data_html += f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <div><strong>Source:</strong> {pd.get('source_url', 'Unknown')}</div>
                    <div><strong>Confidence:</strong> {pd.get('extraction_confidence', 0):.2f}</div>
                    <div><strong>Data:</strong> {safety_count} safety, {health_count} health, {emergency_count} emergency</div>
                </div>
                """
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{destination} - SmartDestinationThemes</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        {self._get_css_styles()}
        
        .back-button {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            text-decoration: none;
            margin-bottom: 20px;
            transition: background 0.3s ease;
        }}
        
        .back-button:hover {{
            background: rgba(255, 255, 255, 0.3);
            text-decoration: none;
            color: white;
        }}
        
        .destination-hero {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .destination-hero h1 {{
            font-size: 3rem;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .hero-stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}
        
        .hero-stat {{
            text-align: center;
        }}
        
        .hero-stat-value {{
            font-size: 2rem;
            font-weight: 700;
            color: #333;
        }}
        
        .hero-stat-label {{
            color: #666;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <a href="index.html" class="back-button">
            <i class="fas fa-arrow-left"></i> Back to Dashboard
        </a>
        
        <div class="destination-hero">
            <h1>{destination}</h1>
            <div class="quality-badge {quality_class}" style="font-size: 1.1rem; padding: 8px 16px;">
                {quality_level} Quality ({quality_score:.3f})
            </div>
            <div class="hero-stats">
                <div class="hero-stat">
                    <div class="hero-stat-value">{len(affinities)}</div>
                    <div class="hero-stat-label">Themes Generated</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-value">{processing_time:.2f}s</div>
                    <div class="hero-stat-label">Processing Time</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-value">{qa_status.replace('_', ' ').title()}</div>
                    <div class="hero-stat-label">QA Status</div>
                </div>
            </div>
        </div>
        
        <div class="destination-card">
            <div class="expandable" onclick="toggleExpand(this)">
                <h3 style="margin-bottom: 15px;">
                    <i class="fas fa-lightbulb"></i> Generated Themes ({len(affinities)})
                    <i class="fas fa-chevron-down expand-icon" style="float: right;"></i>
                </h3>
            </div>
            <div class="expandable-content expanded">
                <div class="themes-grid">
                    {themes_html}
                </div>
            </div>
            
            <div class="expandable" onclick="toggleExpand(this)" style="margin-top: 30px;">
                <h3 style="margin-bottom: 15px;">
                    <i class="fas fa-chart-bar"></i> Quality Assessment
                    <i class="fas fa-chevron-down expand-icon" style="float: right;"></i>
                </h3>
            </div>
            <div class="expandable-content">
                <div style="background: #f8f9fa; padding: 20px; border-radius: 15px;">
                    <div style="margin-bottom: 15px;"><strong>Overall Score:</strong> {quality_score:.3f}</div>
                    <div style="margin-bottom: 15px;"><strong>QA Status:</strong> {qa_status}</div>
                    <div style="margin-bottom: 15px;"><strong>QA Score:</strong> {qa_score:.3f}</div>
                    <h4 style="margin: 15px 0 10px 0;">Detailed Metrics:</h4>
                    {quality_metrics_html}
                    {f'<h4 style="margin: 15px 0 10px 0;">Recommendations:</h4>' if quality_assessment.get('recommendations') else ''}
                    {f'<ul>{"".join(f"<li>{rec}</li>" for rec in quality_assessment.get("recommendations", []))}</ul>' if quality_assessment.get('recommendations') else ''}
                </div>
            </div>
            
            {f'''
            <div class="expandable" onclick="toggleExpand(this)" style="margin-top: 30px;">
                <h3 style="margin-bottom: 15px;">
                    <i class="fas fa-brain"></i> Intelligence Insights
                    <i class="fas fa-chevron-down expand-icon" style="float: right;"></i>
                </h3>
            </div>
            <div class="expandable-content">
                {intelligence_insights_html}
            </div>
            ''' if intelligence_insights_html else ''}
            
            {f'''
            <div class="expandable" onclick="toggleExpand(this)" style="margin-top: 30px;">
                <h3 style="margin-bottom: 15px;">
                    <i class="fas fa-palette"></i> Composition Analysis
                    <i class="fas fa-chevron-down expand-icon" style="float: right;"></i>
                </h3>
            </div>
            <div class="expandable-content">
                {composition_analysis_html}
            </div>
            ''' if composition_analysis_html else ''}
            
            {f'''
            <div class="expandable" onclick="toggleExpand(this)" style="margin-top: 30px;">
                <h3 style="margin-bottom: 15px;">
                    <i class="fas fa-shield-alt"></i> Priority Travel Data ({len(priority_data)})
                    <i class="fas fa-chevron-down expand-icon" style="float: right;"></i>
                </h3>
            </div>
            <div class="expandable-content">
                {priority_data_html}
            </div>
            ''' if priority_data else ''}
        </div>
        
        {self._generate_footer()}
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>
        """ 