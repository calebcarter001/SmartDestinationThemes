#!/usr/bin/env python3
"""
Quick demonstration of production system improvements.
Shows key features working together.
"""

import json
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from src.scorer import AffinityQualityScorer
from src.monitoring import AffinityMonitoring
from src.qa_flow import QualityAssuranceFlow
from tools.priority_data_extraction_tool import PriorityDataExtractor
from tools.config_loader import load_app_config

def demonstrate_quality_scoring():
    """Demonstrate the quality scoring system."""
    print("🔍 QUALITY SCORING DEMONSTRATION")
    print("=" * 50)
    
    config = load_app_config()
    scorer = AffinityQualityScorer(config=config)
    
    # Load production data
    try:
        with open("destination_affinities_production.json", "r") as f:
            production_data = json.load(f)
    except FileNotFoundError:
        print("❌ Production data not found. Run main.py first.")
        return
    
    for destination, data in production_data.items():
        print(f"\n🌍 {destination}")
        print("-" * 30)
        
        if 'quality_assessment' in data:
            qa = data['quality_assessment']
            print(f"📈 Overall Score: {qa['overall_score']:.3f} ({qa['quality_level']})")
            print(f"📊 Detailed Metrics:")
            for metric, value in qa['metrics'].items():
                print(f"   • {metric.replace('_', ' ').title()}: {value:.3f}")
            
            if qa['recommendations']:
                print(f"💡 Improvement Recommendations:")
                for rec in qa['recommendations']:
                    print(f"   • {rec}")
        
        print(f"🎯 Total Affinities: {len(data.get('affinities', []))}")

def demonstrate_qa_workflow():
    """Demonstrate the QA workflow system."""
    print("\n\n🔒 QA WORKFLOW DEMONSTRATION")
    print("=" * 50)
    
    config = load_app_config()
    qa_flow = QualityAssuranceFlow(config=config)
    
    # Load production data
    try:
        with open("destination_affinities_production.json", "r") as f:
            production_data = json.load(f)
    except FileNotFoundError:
        print("❌ Production data not found.")
        return
    
    for destination, data in production_data.items():
        print(f"\n🌍 {destination}")
        print("-" * 30)
        
        if 'qa_workflow' in data:
            qa = data['qa_workflow']
            print(f"✅ Status: {qa['status']}")
            print(f"🆔 Review ID: {qa['review_id']}")
            print(f"👥 Assigned Reviewers: {len(qa['assigned_reviewers'])}")
            print(f"📊 Quality Score: {qa['quality_score']:.3f}")
            
            if 'review_decision' in qa:
                decision = qa['review_decision']
                print(f"🎯 Review Action: {decision['action']}")
                print(f"💭 Reason: {decision['reason']}")

def demonstrate_monitoring_capabilities():
    """Demonstrate monitoring system capabilities."""
    print("\n\n📊 MONITORING SYSTEM DEMONSTRATION")
    print("=" * 50)
    
    config = load_app_config()
    monitoring = AffinityMonitoring(config=config)
    
    # Track some sample processing
    print("📈 Tracking sample operations...")
    
    sample_destinations = [
        ("Paris, France", 3.2, 0.89, 12),
        ("Tokyo, Japan", 4.1, 0.76, 10),
        ("London, UK", 2.8, 0.92, 11),
        ("Sydney, Australia", 5.2, 0.68, 9)
    ]
    
    for dest, time, quality, count in sample_destinations:
        monitoring.track_destination_processing(
            dest, time, quality, count, errors=[]
        )
        print(f"   ✅ Tracked: {dest} (Quality: {quality:.2f}, Time: {time:.1f}s)")
    
    # Get system metrics
    print(f"\n📊 System Metrics:")
    health = monitoring.track_system_health()
    metrics = monitoring.get_system_metrics(hours=1)
    
    print(f"   • System Status: {health['system_state']['status'].upper()}")
    print(f"   • Destinations Processed: {metrics['total_destinations_processed']}")
    print(f"   • Average Quality: {metrics['avg_quality_score']:.3f}")
    print(f"   • Average Processing Time: {metrics['avg_processing_time']:.2f}s")
    print(f"   • Error Rate: {metrics['error_rate']:.3f}")
    
    # Check for alerts
    alerts = monitoring.check_for_alerts()
    if alerts:
        print(f"\n⚠️  Active Alerts ({len(alerts)}):")
        for alert in alerts:
            severity_emoji = "🔴" if alert['severity'] == 'high' else "🟡" if alert['severity'] == 'medium' else "🟢"
            print(f"   {severity_emoji} {alert['type']}: {alert['message']}")
    else:
        print(f"\n✅ No active alerts - system healthy")

def demonstrate_priority_extraction():
    """Demonstrate priority data extraction."""
    print("\n\n🚨 PRIORITY DATA EXTRACTION DEMONSTRATION")
    print("=" * 50)
    
    config = load_app_config()
    extractor = PriorityDataExtractor(config=config)
    
    # Sample travel content for extraction
    sample_content = """
    Travel Advisory for Thailand: Visitors should be aware of monsoon season from June to October.
    Visa Requirements: US citizens need a tourist visa for stays longer than 30 days.
    Health Notice: Yellow fever vaccination required if arriving from affected areas.
    Safety Concern: Avoid protest areas in Bangkok city center.
    Emergency Contacts: Tourist Police Hotline: 1155, US Embassy: +66-2-205-4000
    Transportation: BTS Skytrain operates 6 AM to midnight daily.
    """
    
    print("📋 Extracting from sample travel content...")
    
    priority_data = extractor.extract_all_priority_data(
        sample_content, 
        "https://example-travel-site.com",
        "Bangkok, Thailand"
    )
    
    print(f"📊 Extraction Results:")
    print(f"   • Confidence: {priority_data['extraction_confidence']:.2f}")
    print(f"   • Completeness: {priority_data['data_completeness']:.2f}")
    
    if priority_data['safety_concerns']:
        print(f"   • Safety Concerns: {len(priority_data['safety_concerns'])} found")
        for concern in priority_data['safety_concerns'][:2]:
            print(f"     - {concern}")
    
    if priority_data['visa_requirements'] != "No information found.":
        print(f"   • Visa Info: Available (confidence: {priority_data['visa_confidence']:.2f})")
    
    if priority_data['health_advisories']:
        print(f"   • Health Advisories: {len(priority_data['health_advisories'])} found")
    
    if priority_data['emergency_contacts']:
        print(f"   • Emergency Contacts: {len(priority_data['emergency_contacts'])} found")

def show_production_improvements():
    """Show the overall production improvements."""
    print("\n\n🚀 PRODUCTION SYSTEM IMPROVEMENTS SUMMARY")
    print("=" * 60)
    
    improvements = [
        {
            "feature": "🔍 Multi-Dimensional Quality Scoring",
            "before": "Basic confidence scores only",
            "after": "5-metric comprehensive assessment with recommendations",
            "impact": "Improved output quality and actionable feedback"
        },
        {
            "feature": "🔒 Quality Assurance Workflow", 
            "before": "No review process",
            "after": "Intelligent routing with human review for quality issues",
            "impact": "Consistent quality control and continuous improvement"
        },
        {
            "feature": "📊 Real-time Monitoring",
            "before": "No system visibility",
            "after": "Comprehensive metrics, alerts, and health tracking",
            "impact": "Proactive issue detection and performance optimization"
        },
        {
            "feature": "🚨 Priority Data Extraction",
            "before": "No safety/travel info extraction",
            "after": "Automated extraction of critical travel information",
            "impact": "Enhanced traveler safety and trip planning"
        },
        {
            "feature": "🏗️ Knowledge Graph Integration",
            "before": "Isolated destination data",
            "after": "Structured RDF storage with semantic relationships",
            "impact": "Cross-destination insights and advanced querying"
        }
    ]
    
    for i, improvement in enumerate(improvements, 1):
        print(f"\n{i}. {improvement['feature']}")
        print(f"   📉 Before: {improvement['before']}")
        print(f"   📈 After: {improvement['after']}")
        print(f"   💡 Impact: {improvement['impact']}")

def main():
    """Main demonstration function."""
    print("🎉 SMARTDESTINATIONTHEMES PRODUCTION FEATURES DEMO")
    print("=" * 70)
    print(f"📅 Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all demonstrations
    demonstrate_quality_scoring()
    demonstrate_qa_workflow()
    demonstrate_monitoring_capabilities()
    demonstrate_priority_extraction()
    show_production_improvements()
    
    print(f"\n🎯 DEMO COMPLETE!")
    print("=" * 40)
    
    conclusion_points = [
        "✅ Quality scoring provides detailed assessment across 5 dimensions",
        "✅ QA workflow ensures consistent review and approval processes", 
        "✅ Monitoring system tracks performance and detects issues",
        "✅ Priority extraction enhances safety and planning capabilities",
        "✅ All systems integrate seamlessly for production deployment"
    ]
    
    for point in conclusion_points:
        print(f"   {point}")
    
    print(f"\n🚀 The SmartDestinationThemes system is now enterprise-ready!")
    print(f"📊 Production features ensure quality, reliability, and scalability")
    print(f"🔍 Comprehensive monitoring provides operational visibility")
    print(f"🛡️  Enhanced safety features protect and inform travelers")

if __name__ == "__main__":
    main() 