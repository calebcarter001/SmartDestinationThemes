#!/usr/bin/env python3
"""
Demo Script for Enhanced Intelligence Features
Shows the new theme intelligence capabilities on existing data
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from src.enhanced_data_processor import EnhancedDataProcessor
from tools.config_loader import load_app_config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def demo_enhanced_intelligence():
    """Demonstrate enhanced intelligence features on existing data"""
    
    print("🧠 Enhanced Intelligence Demo - Smart Destination Themes")
    print("="*70)
    
    # Load configuration
    config = load_app_config()
    
    # Initialize enhanced processor
    processor = EnhancedDataProcessor(config)
    
    # Sample destination data for demo
    sample_destinations = {
        "Las Vegas, Nevada": {
            "affinities": [
                {
                    "category": "adventure",
                    "theme": "Thrill seeking",
                    "sub_themes": ["High roller", "Off-roading", "Extreme sports"],
                    "confidence": 0.95,
                    "seasonality": {"peak": ["March", "April", "October", "November"], "avoid": ["July", "August"]},
                    "traveler_types": ["solo", "couple", "group"],
                    "price_point": "mid",
                    "rationale": "Las Vegas offers a wide array of adventurous activities, from gambling to desert excursions with authentic local experiences and hidden gems.",
                    "unique_selling_points": ["Variety of high-adrenaline activities", "Accessibility to desert landscapes", "Nightlife"],
                    "validation": "Evidence found in web content"
                },
                {
                    "category": "culture",
                    "theme": "Local art scene exploration",
                    "sub_themes": ["Underground galleries", "Street art", "Local artist studios"],
                    "confidence": 0.85,
                    "seasonality": {"peak": ["March", "April", "October", "November"], "avoid": ["July", "August"]},
                    "traveler_types": ["solo", "couple"],
                    "price_point": "budget",
                    "rationale": "Hidden neighborhood galleries and authentic local artist studios offer peaceful contemplative experiences away from tourist crowds.",
                    "unique_selling_points": ["Off the beaten path", "Local authentic culture", "Inspiring artistic community"],
                    "validation": "Evidence found in web content"
                },
                {
                    "category": "culture",
                    "theme": "Culinary adventures",
                    "sub_themes": ["Street food markets", "Local family recipes", "Chef-owned restaurants"],
                    "confidence": 0.8,
                    "seasonality": {"peak": ["March", "April", "October", "November"], "avoid": ["July", "August"]},
                    "traveler_types": ["couple", "group", "solo"],
                    "price_point": "mid",
                    "rationale": "Explore traditional family-owned restaurants and challenging culinary experiences that locals frequent, offering social and exciting adventures.",
                    "unique_selling_points": ["Authentic flavors", "Local family traditions", "Hidden culinary gems"],
                    "validation": "Evidence found in web content"
                }
            ],
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "model_consensus": 0.87
            }
        },
        "New York, New York": {
            "affinities": [
                {
                    "category": "culture", 
                    "theme": "Underground music venues",
                    "sub_themes": ["Jazz speakeasies", "Indie rock clubs", "Live music venues"],
                    "confidence": 0.9,
                    "seasonality": {"peak": ["September", "October", "November", "December"], "avoid": ["July", "August"]},
                    "traveler_types": ["solo", "couple", "group"],
                    "price_point": "mid",
                    "rationale": "Hidden jazz speakeasies and secret locals-only venues offer inspiring and social experiences with authentic neighborhood culture.",
                    "unique_selling_points": ["Secret venues", "Local music scene", "Intimate settings"],
                    "validation": "Evidence found in web content"
                },
                {
                    "category": "adventure",
                    "theme": "Rooftop exploration",
                    "sub_themes": ["Secret rooftops", "Urban photography", "Sunset views"],
                    "confidence": 0.75,
                    "seasonality": {"peak": ["May", "June", "September", "October"], "avoid": ["January", "February"]},
                    "traveler_types": ["solo", "couple"],
                    "price_point": "budget",
                    "rationale": "Challenging urban exploration of hidden rooftops offers thrilling and peaceful contemplative moments with unique city perspectives.",
                    "unique_selling_points": ["Unique perspectives", "Photography opportunities", "Off the beaten path"],
                    "validation": "Evidence found in web content"
                }
            ],
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "model_consensus": 0.82
            }
        }
    }
    
    # Process each destination with enhanced intelligence
    for destination_name, destination_data in sample_destinations.items():
        print(f"\n🌍 Processing: {destination_name}")
        print("-" * 50)
        
        # Apply enhanced intelligence processing
        enhanced_data = processor.enhance_and_save_affinities(
            destination_data,
            destination_name,
            output_file=f"outputs/{destination_name.lower().replace(' ', '_').replace(',', '')}_enhanced_demo.json"
        )
        
        # Display enhanced intelligence insights
        print(f"📊 Enhanced Quality Assessment:")
        qa = enhanced_data['quality_assessment']
        print(f"   • Overall Score: {qa['overall_score']:.3f} ({qa['quality_level']})")
        print(f"   • Core Metrics: Factual: {qa['metrics']['factual_accuracy']:.2f}, Coverage: {qa['metrics']['thematic_coverage']:.2f}")
        print(f"   • Intelligence Metrics: Depth: {qa['metrics']['theme_depth']:.2f}, Authenticity: {qa['metrics']['authenticity']:.2f}, Emotional: {qa['metrics']['emotional_resonance']:.2f}")
        
        print(f"\n💡 Intelligence Insights:")
        insights = enhanced_data['intelligence_insights']
        print(f"   • Hidden gems: {insights['hidden_gems_count']} ({insights['hidden_gems_ratio']*100:.1f}%)")
        print(f"   • Average depth score: {insights['average_depth_score']:.2f}")
        print(f"   • Average authenticity: {insights['average_authenticity_score']:.2f}")
        
        if 'emotional_variety' in insights:
            emotions = insights['emotional_variety']['emotions_covered']
            print(f"   • Emotional coverage: {len(emotions)} types - {', '.join(emotions)}")
        
        print(f"\n🎨 Composition Analysis:")
        comp = enhanced_data['composition_analysis']
        print(f"   • Overall composition score: {comp.get('overall_composition_score', 0.0):.2f}")
        print(f"   • Category distribution: {dict(list(comp.get('category_distribution', {}).items())[:3])}")
        if 'intensity_distribution' in comp:
            print(f"   • Intensity distribution: {comp['intensity_distribution']}")
        else:
            print(f"   • Intensity analysis: Processing complete")
        
        print(f"\n🔍 Sample Enhanced Affinity Analysis:")
        if enhanced_data['affinities']:
            sample_affinity = enhanced_data['affinities'][0]
            print(f"   • Theme: {sample_affinity['theme']}")
            print(f"   • Depth Level: {sample_affinity['depth_analysis']['depth_level']} (score: {sample_affinity['depth_analysis']['depth_score']:.2f})")
            print(f"   • Authenticity: {sample_affinity['authenticity_analysis']['authenticity_level']} (score: {sample_affinity['authenticity_analysis']['authenticity_score']:.2f})")
            print(f"   • Primary Emotions: {', '.join(sample_affinity['emotional_profile']['primary_emotions'])}")
            print(f"   • Experience Intensity: {sample_affinity['experience_intensity']['overall_intensity']}")
            print(f"   • Hidden Gem Score: {sample_affinity['hidden_gem_score']['uniqueness_score']:.2f} ({sample_affinity['hidden_gem_score']['hidden_gem_level']})")
            
            if 'nano_themes' in sample_affinity['depth_analysis']:
                nano_themes = sample_affinity['depth_analysis'].get('nano_themes', [])
                if nano_themes:
                    print(f"   • Nano Themes: {', '.join(nano_themes)}")
            
            # Show contextual info
            context = sample_affinity['contextual_info']
            print(f"   • Target Demographics: {', '.join(context['demographic_suitability'])}")
            print(f"   • Time Commitment: {context['time_commitment']}")
        
        print(f"\n🔒 QA Workflow:")
        qa_workflow = enhanced_data['qa_workflow']
        print(f"   • Status: {qa_workflow['workflow_path']}")
        print(f"   • Review Required: {qa_workflow['review_required']}")
        print(f"   • Overall Score: {qa_workflow['overall_score']:.3f}")
    
    print(f"\n" + "="*70)
    print("🎉 Enhanced Intelligence Demo Complete!")
    print(f"📁 Enhanced JSON files saved in outputs/ directory")
    print(f"🧠 Key Features Demonstrated:")
    print("   • Theme Depth Analysis (Macro → Micro → Nano levels)")
    print("   • Authenticity Scoring (Local vs Tourist orientation)")
    print("   • Emotional Resonance Profiling (8 emotional categories)")
    print("   • Experience Intensity Analysis (Physical, Cultural, Social)")
    print("   • Hidden Gem Discovery (Uniqueness scoring)")
    print("   • Contextual Intelligence (Demographics, timing, accessibility)")
    print("   • Composition Analysis (Balance and flow optimization)")
    print("   • Enhanced Quality Assessment (8 comprehensive metrics)")
    print("   • Intelligent QA Workflow (Automated decision paths)")
    
    # Show file locations
    print(f"\n📄 Generated Files:")
    for dest in sample_destinations.keys():
        filename = f"outputs/{dest.lower().replace(' ', '_').replace(',', '')}_enhanced_demo.json"
        if Path(filename).exists():
            print(f"   • {filename}")

if __name__ == "__main__":
    demo_enhanced_intelligence() 