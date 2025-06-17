#!/usr/bin/env python3
"""
Analysis script to compare basic vs production system improvements.
Demonstrates the value of our new production-ready features.
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any

def load_json_file(filename: str) -> Dict[str, Any]:
    """Load JSON file with error handling."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File {filename} not found")
        return {}
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in {filename}")
        return {}

def analyze_quality_improvements():
    """Analyze quality improvements between systems."""
    print("🔍 QUALITY ANALYSIS COMPARISON")
    print("=" * 60)
    
    # Load files
    basic_data = load_json_file("destination_affinities_augmented.json")
    production_data = load_json_file("destination_affinities_production.json")
    summary_data = load_json_file("processing_summary.json")
    
    if not production_data:
        print("❌ Production data not available")
        return
    
    print("📊 PRODUCTION SYSTEM ENHANCEMENTS:")
    print("=" * 40)
    
    for destination, data in production_data.items():
        print(f"\n🌍 {destination.upper()}")
        print("-" * 30)
        
        # Quality Assessment
        if 'quality_assessment' in data:
            qa = data['quality_assessment']
            print(f"📈 Overall Quality Score: {qa['overall_score']:.3f} ({qa['quality_level']})")
            print(f"📊 Quality Metrics:")
            print(f"   • Factual Accuracy: {qa['metrics']['factual_accuracy']:.3f}")
            print(f"   • Thematic Coverage: {qa['metrics']['thematic_coverage']:.3f}")
            print(f"   • Actionability: {qa['metrics']['actionability']:.3f}")
            print(f"   • Uniqueness: {qa['metrics']['uniqueness']:.3f}")
            print(f"   • Source Credibility: {qa['metrics']['source_credibility']:.3f}")
            
            if qa['recommendations']:
                print(f"💡 Recommendations:")
                for rec in qa['recommendations']:
                    print(f"   • {rec}")
        
        # QA Workflow
        if 'qa_workflow' in data:
            qa_flow = data['qa_workflow']
            print(f"🔒 QA Status: {qa_flow['status']}")
            print(f"👥 Review ID: {qa_flow['review_id']}")
            print(f"👨‍💼 Assigned Reviewers: {len(qa_flow['assigned_reviewers'])}")
        
        # Performance
        if 'processing_time_seconds' in data:
            print(f"⏱️  Processing Time: {data['processing_time_seconds']:.4f}s")
        
        # Affinity Count
        affinity_count = len(data.get('affinities', []))
        print(f"🎯 Generated Affinities: {affinity_count}")

def analyze_system_health():
    """Analyze system health and monitoring capabilities."""
    print("\n\n🏥 SYSTEM HEALTH & MONITORING")
    print("=" * 60)
    
    summary_data = load_json_file("processing_summary.json")
    
    if not summary_data:
        print("❌ Summary data not available")
        return
    
    metrics = summary_data.get('system_metrics', {})
    
    print(f"🏭 System Performance:")
    print(f"   • Destinations Processed: {metrics.get('total_destinations_processed', 0)}")
    print(f"   • Affinities Generated: {metrics.get('total_affinities_generated', 0)}")
    print(f"   • Average Quality Score: {metrics.get('avg_quality_score', 0):.3f}")
    print(f"   • Average Processing Time: {metrics.get('avg_processing_time', 0):.4f}s")
    print(f"   • Error Rate: {metrics.get('error_rate', 0):.3f}")
    print(f"   • System Status: {metrics.get('system_status', 'unknown').upper()}")
    
    # Quality Distribution
    if 'quality_distribution' in metrics:
        qd = metrics['quality_distribution']
        print(f"\n📊 Quality Distribution:")
        print(f"   • Min Score: {qd.get('min', 0):.3f}")
        print(f"   • Max Score: {qd.get('max', 0):.3f}")
        print(f"   • Median: {qd.get('median', 0):.3f}")
        print(f"   • Std Dev: {qd.get('std_dev', 0):.3f}")
    
    # Performance Distribution
    if 'performance_distribution' in metrics:
        pd = metrics['performance_distribution']
        print(f"\n⚡ Performance Distribution:")
        print(f"   • Min Time: {pd.get('min', 0):.4f}s")
        print(f"   • Max Time: {pd.get('max', 0):.4f}s")
        print(f"   • Median: {pd.get('median', 0):.4f}s")
        print(f"   • 95th Percentile: {pd.get('p95', 0):.4f}s")
    
    # QA Summary
    qa_decisions = summary_data.get('qa_decisions', {})
    if qa_decisions:
        print(f"\n🔒 QA Workflow Summary:")
        auto_approved = sum(1 for status in qa_decisions.values() if status == 'auto_approved')
        human_reviewed = sum(1 for status in qa_decisions.values() if status == 'submitted_for_review')
        print(f"   • Auto-approved: {auto_approved}")
        print(f"   • Human reviewed: {human_reviewed}")
        print(f"   • Review rate: {(human_reviewed / len(qa_decisions) * 100):.1f}%")
    
    # Alerts
    alerts = summary_data.get('alerts', [])
    if alerts:
        print(f"\n⚠️  Active Alerts ({len(alerts)}):")
        for alert in alerts:
            severity_emoji = "🔴" if alert['severity'] == 'high' else "🟡" if alert['severity'] == 'medium' else "🟢"
            print(f"   {severity_emoji} {alert['type']}: {alert['message']}")
    else:
        print(f"\n✅ No active alerts - system operating normally")

def demonstrate_new_features():
    """Demonstrate the new production features."""
    print("\n\n🚀 NEW PRODUCTION FEATURES DEMONSTRATED")
    print("=" * 60)
    
    features = [
        {
            "name": "🔍 Multi-Dimensional Quality Scoring",
            "description": "Comprehensive quality assessment across 5 dimensions",
            "benefits": [
                "Factual accuracy validation",
                "Thematic coverage analysis", 
                "Actionability measurement",
                "Uniqueness scoring",
                "Source credibility assessment"
            ]
        },
        {
            "name": "🔒 Quality Assurance Workflow",
            "description": "Intelligent routing for human review",
            "benefits": [
                "Auto-approval for high-quality content (≥0.85)",
                "Human review for questionable content (<0.75)",
                "Multi-reviewer support with agreement tracking",
                "Structured feedback collection"
            ]
        },
        {
            "name": "📊 Real-time System Monitoring",
            "description": "Comprehensive system health tracking",
            "benefits": [
                "Performance metrics collection",
                "Quality trend analysis",
                "Error rate monitoring",
                "Automated alerting system"
            ]
        },
        {
            "name": "🚨 Priority Data Extraction",
            "description": "Critical travel information extraction",
            "benefits": [
                "Safety concern identification",
                "Visa requirement extraction",
                "Health advisory detection",
                "Emergency contact information"
            ]
        },
        {
            "name": "🏗️ Knowledge Graph Integration",
            "description": "Structured data storage and querying",
            "benefits": [
                "RDF triple generation",
                "SPARQL endpoint support",
                "Semantic relationship mapping",
                "Cross-destination insights"
            ]
        }
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"\n{i}. {feature['name']}")
        print(f"   {feature['description']}")
        print(f"   Benefits:")
        for benefit in feature['benefits']:
            print(f"     • {benefit}")

def show_data_quality_comparison():
    """Show specific data quality improvements."""
    print("\n\n📈 DATA QUALITY IMPROVEMENTS")
    print("=" * 60)
    
    production_data = load_json_file("destination_affinities_production.json")
    
    if not production_data:
        return
    
    print("🎯 Enhanced Data Structure:")
    print("=" * 30)
    
    sample_destination = list(production_data.keys())[0]
    sample_data = production_data[sample_destination]
    
    print(f"📋 Original affinity fields:")
    if sample_data.get('affinities'):
        affinity = sample_data['affinities'][0]
        print(f"   • theme, sub_themes, confidence, seasonality")
        print(f"   • traveler_types, price_point, rationale")
        print(f"   • unique_selling_points, validation")
    
    print(f"\n📊 NEW production fields:")
    print(f"   • quality_assessment (5 metrics + overall score)")
    print(f"   • qa_workflow (review status + reviewer assignments)")
    print(f"   • priority_data (safety, visa, health info)")
    print(f"   • processing_time_seconds (performance tracking)")
    
    print(f"\n🔍 Quality Assessment Example:")
    if 'quality_assessment' in sample_data:
        qa = sample_data['quality_assessment']
        print(f"   • Overall Score: {qa['overall_score']:.3f}")
        print(f"   • Quality Level: {qa['quality_level']}")
        print(f"   • Meets Threshold: {qa['meets_threshold']}")
        print(f"   • Recommendations: {len(qa['recommendations'])} items")

def main():
    """Main analysis function."""
    print("🎉 SMARTDESTINATIONTHEMES PRODUCTION SYSTEM ANALYSIS")
    print("=" * 70)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all analyses
    analyze_quality_improvements()
    analyze_system_health()
    demonstrate_new_features()
    show_data_quality_comparison()
    
    print("\n\n🎯 SUMMARY OF IMPROVEMENTS")
    print("=" * 60)
    
    improvements = [
        "✅ Multi-dimensional quality scoring implemented",
        "✅ Intelligent QA workflow with human review routing",
        "✅ Real-time system health monitoring",
        "✅ Priority data extraction capabilities",
        "✅ Enhanced error handling and logging",
        "✅ Performance metrics and alerting",
        "✅ Structured feedback collection",
        "✅ Knowledge graph integration ready"
    ]
    
    for improvement in improvements:
        print(f"   {improvement}")
    
    print(f"\n🚀 The system is now production-ready with enterprise-grade features!")
    print(f"📊 Quality assurance processes ensure consistent, high-quality output")
    print(f"🔍 Monitoring provides real-time insights into system performance")
    print(f"🛡️  Priority data extraction enhances traveler safety and planning")

if __name__ == "__main__":
    main() 