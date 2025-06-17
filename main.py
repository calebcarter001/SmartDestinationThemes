import sys
import os
import json
import logging
import asyncio
import time
from datetime import datetime

# --- Force venv site-packages into path ---
# This is a workaround for stubborn environment issues.
venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.10', 'site-packages')
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)
# -----------------------------------------

from src.affinity_pipeline import AffinityPipeline
from src.scorer import AffinityQualityScorer
from src.monitoring import AffinityMonitoring
from src.qa_flow import QualityAssuranceFlow
from src.html_viewer_generator import ThemeViewerGenerator
from tools.priority_data_extraction_tool import PriorityDataExtractor
from tools.config_loader import load_app_config

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    """
    Enhanced asynchronous main function with production-ready features:
    - Quality scoring and assessment
    - System health monitoring
    - Quality assurance workflow
    - Priority data extraction
    """
    print("--- Starting Grade A Destination Affinity System (Production Mode) ---")
    
    # Load configuration using the new loader
    config = load_app_config()
    
    # Initialize production components
    pipeline = AffinityPipeline(config=config)
    quality_scorer = AffinityQualityScorer(config=config)
    monitoring = AffinityMonitoring(config=config)
    qa_flow = QualityAssuranceFlow(config=config)
    priority_extractor = PriorityDataExtractor(config=config)
    html_generator = ThemeViewerGenerator(config=config)
    
    # Start monitoring
    monitoring.track_system_health()
    
    # Get destinations from config.yaml
    destinations_to_process = config.get("destinations", [])
    
    if not destinations_to_process:
        logging.warning("No destinations found in config.yaml. Exiting.")
        return

    all_results = {}
    processing_summary = {
        "total_destinations": len(destinations_to_process),
        "quality_scores": {},
        "qa_decisions": {},
        "priority_data": {},
        "system_metrics": {},
        "processing_times": {}
    }
    
    # Process destinations sequentially for now to avoid overwhelming APIs
    for destination in destinations_to_process:
        destination_start_time = time.time()
        
        logging.info(f"Processing destination: {destination}")
        print("="*60)
        print(f"🌍 DESTINATION: {destination}")
        print("="*60)
        
        try:
            # 1. Run core affinity generation pipeline
            print("📊 Generating affinities...")
            result = await pipeline.process_destination(destination)
            
            if "error" in result:
                print(f"❌ Error processing {destination}: {result['error']}")
                continue
                
            # 2. Quality Assessment
            print("🔍 Evaluating affinity quality...")
            quality_assessment = quality_scorer.score_affinity_set(
                result, destination, web_signals=result.get('web_augmentation_results', {})
            )
            
            print(f"📈 Quality Score: {quality_assessment['overall_score']:.3f} ({quality_assessment['quality_level']})")
            print(f"📋 Core Metrics: Factual: {quality_assessment['metrics']['factual_accuracy']:.2f}, "
                  f"Coverage: {quality_assessment['metrics']['thematic_coverage']:.2f}, "
                  f"Actionability: {quality_assessment['metrics']['actionability']:.2f}")
            print(f"🧠 Intelligence Metrics: Depth: {quality_assessment['metrics']['theme_depth']:.2f}, "
                  f"Authenticity: {quality_assessment['metrics']['authenticity']:.2f}, "
                  f"Emotional: {quality_assessment['metrics']['emotional_resonance']:.2f}")
            
            # Display intelligence insights
            if 'intelligence_insights' in result:
                insights = result['intelligence_insights']
                print(f"💡 Intelligence Insights:")
                print(f"   • Hidden gems: {insights.get('hidden_gems_count', 0)} "
                      f"({insights.get('hidden_gems_ratio', 0)*100:.1f}%)")
                print(f"   • Avg depth score: {insights.get('average_depth_score', 0):.2f}")
                print(f"   • Avg authenticity: {insights.get('average_authenticity_score', 0):.2f}")
                
                if 'emotional_variety' in insights:
                    emotions = insights['emotional_variety'].get('emotions_covered', [])
                    print(f"   • Emotional coverage: {len(emotions)} types ({', '.join(emotions[:3])}...)")
            
            # 3. Quality Assurance Workflow
            print("🔒 Processing through QA workflow...")
            qa_result = qa_flow.submit_for_review(
                result, 
                quality_assessment['overall_score'], 
                destination,
                priority="normal"
            )
            
            print(f"✅ QA Status: {qa_result['status']}")
            if qa_result['status'] == 'auto_approved':
                print(f"🚀 Auto-approved with quality score {qa_result['quality_score']:.3f}")
            elif qa_result['status'] == 'submitted_for_review':
                print(f"👥 Submitted for human review (ID: {qa_result['review_id']})")
                print(f"👨‍💼 Assigned reviewers: {len(qa_result['assigned_reviewers'])}")
                
                # Simulate quick reviewer feedback for demo
                if len(qa_result['assigned_reviewers']) > 0:
                    reviewer_id = qa_result['assigned_reviewers'][0]
                    mock_feedback = {
                        'decision': 'approved',
                        'factual_accuracy_score': 0.85,
                        'completeness_score': 0.80,
                        'actionability_score': 0.88,
                        'local_relevance_score': 0.82,
                        'comments': 'Good quality affinities with solid evidence backing',
                        'review_time_minutes': 25
                    }
                    
                    feedback_result = qa_flow.submit_reviewer_feedback(
                        qa_result['review_id'], reviewer_id, mock_feedback
                    )
                    
                    if feedback_result['status'] == 'review_completed':
                        print(f"✅ Review completed: {feedback_result['final_decision']['status']}")
                        print(f"📊 Reviewer agreement: {feedback_result['final_decision']['confidence']:.2f}")
            
            # 4. Priority Data Extraction
            print("🚨 Extracting priority travel data...")
            priority_data_results = []
            
            # Extract from web content if available
            web_signals = result.get('web_augmentation_results', {})
            if web_signals and 'pages' in web_signals:
                for page_data in web_signals['pages'][:3]:  # Limit to first 3 pages for demo
                    if page_data.get('content'):
                        priority_data = priority_extractor.extract_all_priority_data(
                            page_data['content'], 
                            page_data.get('url', 'unknown'),
                            destination
                        )
                        if priority_data['extraction_confidence'] > 0.1:
                            priority_data_results.append(priority_data)
            
            if priority_data_results:
                avg_confidence = sum(pd['extraction_confidence'] for pd in priority_data_results) / len(priority_data_results)
                avg_completeness = sum(pd['data_completeness'] for pd in priority_data_results) / len(priority_data_results)
                print(f"🛡️  Priority data extracted from {len(priority_data_results)} sources")
                print(f"📊 Avg confidence: {avg_confidence:.2f}, completeness: {avg_completeness:.2f}")
                
                # Show sample safety/visa info
                for pd in priority_data_results[:1]:  # Show first result
                    if pd['safety_concerns']:
                        print(f"⚠️  Safety concerns found: {len(pd['safety_concerns'])} items")
                    if pd['visa_requirements'] != "No information found.":
                        print(f"📋 Visa info available (confidence: {pd['visa_confidence']:.2f})")
            else:
                print("ℹ️  No significant priority data extracted")
            
            # 5. Performance Tracking
            destination_processing_time = time.time() - destination_start_time
            
            monitoring.track_destination_processing(
                destination, 
                destination_processing_time,
                quality_assessment['overall_score'],
                len(result.get('affinities', [])),
                errors=[]
            )
            
            # Store enhanced results
            enhanced_result = result.copy()
            enhanced_result['quality_assessment'] = quality_assessment
            enhanced_result['qa_workflow'] = qa_result
            enhanced_result['priority_data'] = priority_data_results
            enhanced_result['processing_time_seconds'] = round(destination_processing_time, 2)
            
            all_results[destination] = enhanced_result
            
            # Update summary
            processing_summary['quality_scores'][destination] = quality_assessment['overall_score']
            processing_summary['qa_decisions'][destination] = qa_result['status']
            processing_summary['priority_data'][destination] = len(priority_data_results)
            processing_summary['processing_times'][destination] = destination_processing_time
            
            print(f"⏱️  Processing completed in {destination_processing_time:.2f} seconds")
            print("✅ Destination processing complete!\n")
            
        except Exception as e:
            logging.error(f"Error processing {destination}: {e}", exc_info=True)
            monitoring.track_destination_processing(
                destination, 0, 0, 0, errors=[str(e)]
            )

    print("="*60)
    print("🎯 PROCESSING COMPLETE - PRODUCTION SUMMARY")
    print("="*60)
    
    # System Health Summary
    health_summary = monitoring.track_system_health()
    system_metrics = monitoring.get_system_metrics(hours=1)
    
    print(f"📊 System Health: {health_summary['system_state']['status'].upper()}")
    print(f"🏭 Destinations Processed: {system_metrics['total_destinations_processed']}")
    print(f"🎯 Affinities Generated: {system_metrics['total_affinities_generated']}")
    print(f"📈 Average Quality Score: {system_metrics['avg_quality_score']:.3f}")
    print(f"⏱️  Average Processing Time: {system_metrics['avg_processing_time']:.2f}s")
    print(f"🚨 Active Alerts: {system_metrics['active_alerts_count']}")
    
    # Quality Distribution
    if processing_summary['quality_scores']:
        quality_scores = list(processing_summary['quality_scores'].values())
        print(f"\n📊 Quality Score Distribution:")
        print(f"   • Excellent (≥0.85): {sum(1 for q in quality_scores if q >= 0.85)}")
        print(f"   • Good (0.75-0.84): {sum(1 for q in quality_scores if 0.75 <= q < 0.85)}")
        print(f"   • Acceptable (0.65-0.74): {sum(1 for q in quality_scores if 0.65 <= q < 0.75)}")
        print(f"   • Needs Improvement (<0.65): {sum(1 for q in quality_scores if q < 0.65)}")
    
    # QA Summary
    qa_decisions = list(processing_summary['qa_decisions'].values())
    print(f"\n🔒 QA Workflow Summary:")
    print(f"   • Auto-approved: {qa_decisions.count('auto_approved')}")
    print(f"   • Human reviewed: {qa_decisions.count('submitted_for_review')}")
    
    # Priority Data Summary
    total_priority_extractions = sum(processing_summary['priority_data'].values())
    print(f"\n🚨 Priority Data Extraction:")
    print(f"   • Total extractions: {total_priority_extractions}")
    print(f"   • Avg per destination: {total_priority_extractions / len(destinations_to_process):.1f}")
    
    # Check for alerts
    alerts = monitoring.check_for_alerts()
    if alerts:
        print(f"\n⚠️  SYSTEM ALERTS ({len(alerts)}):")
        for alert in alerts:
            severity_emoji = "🔴" if alert['severity'] == 'high' else "🟡" if alert['severity'] == 'medium' else "🟢"
            print(f"   {severity_emoji} {alert['type']}: {alert['message']}")
    else:
        print("\n✅ No system alerts - all metrics within thresholds")
    
    processing_summary['system_metrics'] = system_metrics
    processing_summary['alerts'] = alerts
    processing_summary['timestamp'] = datetime.now().isoformat()

    print("\n📄 Detailed Results:")
    print(json.dumps(all_results, indent=2, default=lambda o: o.dict() if hasattr(o, 'dict') else str(o)))

    # Save enhanced results
    output_filename = "destination_affinities_production.json"
    summary_filename = "processing_summary.json"
    
    with open(output_filename, "w") as f:
        json.dump(all_results, f, indent=2, default=lambda o: o.dict() if hasattr(o, 'dict') else str(o))
    
    with open(summary_filename, "w") as f:
        json.dump(processing_summary, f, indent=2, default=str)
    
    logging.info(f"Enhanced results saved to {output_filename}")
    logging.info(f"Processing summary saved to {summary_filename}")

    # Generate HTML dashboard
    print(f"\n🎨 Generating modular HTML dashboard...")
    html_success = html_generator.generate_html_viewer(output_filename)
    
    if html_success:
        dashboard_path = os.path.abspath("dashboard/index.html")
        print(f"✨ Modular dashboard generated!")
        print(f"🌐 Main dashboard: file://{dashboard_path}")
        print(f"📁 Individual pages in dashboard/ directory")

    print(f"\n💾 Files saved:")
    print(f"   • Enhanced results: {output_filename}")
    print(f"   • Processing summary: {summary_filename}")
    if html_success:
        print(f"   • Modular dashboard: dashboard/ directory")
        print(f"   • Legacy redirect: themes_dashboard.html")
    print("\n🎉 Production system test complete!")


if __name__ == "__main__":
    asyncio.run(main()) 