# 🌍 Destination Insights Discovery

**AI-Powered Multi-Agent Travel Intelligence System**

A sophisticated multi-agent system that discovers, analyzes, and curates comprehensive travel insights for destinations worldwide. Powered by advanced LLM orchestration, intelligent web discovery, and **cutting-edge citation enhancement technology**.

## ✨ **Latest Features**

### 🎨 **AI-Powered Seasonal Image Generation** *(NEW)*
- **DALL-E 3 Integration**: Professional travel photography for all 4 seasons per destination
- **Dual Entry Points**: Standalone script for manual generation + integrated Phase 3.5 workflow
- **Seasonal Visual Themes**: Spring blooms, summer festivals, autumn colors, winter atmospheres
- **Automatic Collages**: Beautiful 2x2 seasonal grids combining all seasonal images
- **Smart Caching**: Detects existing images to avoid unnecessary regeneration
- **Graceful Degradation**: System continues processing even if image generation fails

### 🔗 **LLM Citation Enhancement System**
- **Structured Citation Processing**: LLMs now provide direct URL citations in their responses
- **Dual Evidence Pipeline**: Combines web-discovered evidence with LLM-cited sources
- **Intelligent Evidence Fusion**: Smart merging of citation streams with deduplication and quality scoring
- **Citation Content Mining**: Automated extraction and analysis of cited source content
- **Authority Boosting**: Enhanced scoring for government, academic, and tourism sources
- **Graceful Fallback**: Robust system maintains functionality even when citations aren't available

### 🤖 **Multi-Agent Intelligence System**
- **6-Agent Orchestration**: Web Discovery, LLM Orchestration, Intelligence Enhancement, Evidence Validation, Seasonal Images, Quality Assurance
- **Adaptive Processing**: Context-aware theme discovery and content optimization
- **Parallel Processing**: Concurrent agent execution for maximum efficiency
- **Quality-Driven**: Comprehensive validation and scoring at every stage

## 🏗️ **System Architecture**

### **Enhanced Evidence Pipeline**
```
🔍 Web Discovery Agent
├── Authority-filtered source discovery
├── Multi-query search strategies  
└── Content quality validation

🧠 LLM Orchestration Agent
├── Structured citation requests
├── Theme-specific URL generation
└── Enhanced JSON response parsing

🔗 Citation Enhancement Coordinator
├── URL extraction and validation
├── Citation content mining
├── Evidence stream fusion
└── Quality-weighted ranking

📊 Evidence Validation Agent
├── Cross-source validation
├── Authority scoring
└── Comprehensive reporting
```

## ✨ Key Features

- **🤖 Multi-Agent Orchestration**: 6 intelligent agents working in harmony for comprehensive destination analysis
- **🧠 Advanced Intelligence Processing**: 18 validation attributes with 4-phase decomposed LLM processing
- **🔍 Evidence-Based Validation**: Real-time web evidence with travel authority scoring and cross-source verification
- **📊 Professional Interactive Dashboard**: Clean design with evidence modals, back navigation, and quality indicators
- **⚡ High-Performance Architecture**: Agent-based parallel processing with intelligent fallback systems
- **🌍 Global Coverage**: Ready to process 25 of the world's top travel destinations
- **🎨 Modern UI/UX**: Professional Expedia-inspired interface with responsive design

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone and setup
git clone https://github.com/calebcarter001/SmartDestinationThemes.git
cd SmartDestinationThemes
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys
Create a `.env` file in the project root:
```bash
# LLM APIs (required - choose one or both)
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key  # Required for seasonal image generation

# Web Discovery APIs (optional, fallbacks available)
BRAVE_SEARCH_API_KEY=your_brave_search_api_key
JINA_API_KEY=your_jina_api_key
```

### 3. Run the Application
```bash
# Clean previous runs and start fresh processing
python cleanup_for_fresh_run.py
python main.py

# Or start server for existing results
python start_server.py
```

### 4. Access Dashboard
Navigate to: **http://localhost:8000**
- 📊 **Main Dashboard**: Overview of all destinations
- 🎯 **Individual Pages**: Detailed analysis per destination
- 🔙 **Back Navigation**: Easy navigation between pages
- 📎 **Evidence Modals**: Click paperclips to view web evidence

## 🏗️ System Architecture

### High-Level System Overview
📊 **[View System Architecture](docs/architecture-overview.md)**

The Destination Insights Discovery system features a sophisticated **multi-agent orchestration architecture** that coordinates intelligent agents for comprehensive destination processing.

### Agent Workflow Sequence
🔄 **[View Agent Workflow](docs/agent-workflow.md)**

The system processes destinations through a **4-phase intelligent workflow** with parallel processing and quality assurance at every step.

### Data Flow Architecture
🌊 **[View Data Flow](docs/data-flow.md)**

Evidence and intelligence flow through **multiple validation layers** ensuring high-quality, authoritative destination insights.

### Agent Communication Pattern
📡 **[View Agent Communication](docs/agent-communication.md)**

Agents communicate through an **asynchronous message bus** with intelligent task coordination and resource management.

## 🤖 Multi-Agent System

### 🎭 Orchestrator Agent
**Central Command & Coordination**
- **Workflow Management**: Coordinates all agent activities and task distribution
- **State Tracking**: Maintains comprehensive workflow state across all phases
- **Resource Allocation**: Intelligent resource management and load balancing
- **Quality Monitoring**: Real-time performance tracking and optimization

### 🕷️ Web Discovery Agent
**Intelligent Content Discovery**
- **Smart Query Generation**: Context-aware search query optimization for travel content
- **Authority Filtering**: Prioritizes high-authority travel sources (Lonely Planet, government tourism sites)
- **Content Validation**: Quality-based content selection with relevance scoring
- **Source Verification**: Travel authority validation and credibility assessment

**Performance**: ~11.6 seconds per destination, 9 high-quality sources average

### 🧠 LLM Orchestration Agent
**Resource Management & Processing**
- **Adaptive Resource Allocation**: Intelligent LLM connection pooling and optimization
- **4-Phase Processing**: Theme discovery → Analysis → Enhancement → Quality assessment
- **Performance Optimization**: Intelligent batching and caching for efficiency
- **Quality Control**: Continuous monitoring and result optimization

**Performance**: ~0.01 seconds per destination (cached), 23 themes average

### 💡 Intelligence Enhancement Agent
**Advanced Attribute Processing**
- **18 Intelligence Attributes**: Core intelligence (14) + Content intelligence (4)
- **Dependency-Aware Processing**: Optimized processing order based on attribute relationships
- **Context-Aware Enhancement**: Destination-specific intelligence optimization
- **Quality-Driven Optimization**: Continuous improvement of enhancement quality

**Core Attributes**: nano_themes, price_insights, seasonality, traveler_types, accessibility, authenticity_analysis, hidden_gem_score, depth_analysis, cultural_sensitivity, experience_intensity, time_commitment, local_transportation, accommodation_types, booking_considerations

**Content Attributes**: iconic_landmarks, practical_travel_intelligence, neighborhood_insights, content_discovery_intelligence

### 🔍 Evidence Validation Agent
**Cross-Source Verification & Authority Scoring**
- **Multi-Source Validation**: Cross-references evidence across multiple travel authorities
- **Authority Scoring**: Weights sources by domain authority and travel relevance
- **Conflict Resolution**: Intelligent resolution of conflicting evidence
- **Evidence Synthesis**: Aggregates evidence into comprehensive theme support

**Performance**: ~0.11 seconds per destination, 38 evidence pieces average across themes

### ✅ Quality Assurance Agent
**Continuous Monitoring & Adaptive Intervention**
- **Real-Time Quality Assessment**: Monitors quality throughout the entire workflow
- **Adaptive Interventions**: Automatic quality improvements and error correction
- **Performance Analytics**: Comprehensive quality metrics and trend analysis
- **Optimization Recommendations**: Intelligent suggestions for workflow improvements

### 🎨 Seasonal Image Agent *(NEW)*
**AI-Powered Visual Enhancement**
- **DALL-E 3 Integration**: Professional-quality seasonal travel photography
- **4-Season Generation**: Spring, summer, autumn, winter imagery for each destination
- **Intelligent Prompting**: Context-aware seasonal themes and landmark integration
- **Collage Creation**: Automatic 2x2 seasonal grid generation
- **Smart Caching**: Existing image detection and selective regeneration
- **Graceful Integration**: Phase 3.5 workflow integration with fallback capability

**Performance**: ~55-60 seconds per destination (4 images + collage)

## 🌍 Ready-to-Process Destinations

The system is pre-configured with **25 of the world's top travel destinations**:

### 🏛️ Historic & Cultural Sites
- **Athens, Greece** - Ancient wonders and archaeological treasures
- **Rome, Italy** - Eternal city with millennia of history
- **Cairo, Egypt** - Pyramids and ancient Egyptian civilization
- **Agra, India** - Taj Mahal and Mughal architecture
- **Beijing, China** - Great Wall and imperial heritage
- **Stonehenge, England** - Prehistoric monument and mystery
- **Siem Reap, Cambodia** - Gateway to Angkor Wat temples
- **Chichen Itza, Mexico** - Mayan archaeological wonder
- **Machu Picchu, Peru** - Lost city of the Incas
- **Bagan, Myanmar** - Ancient temple complex

### 🏞️ Natural Wonders
- **Grand Canyon, Arizona, USA** - Iconic geological marvel
- **Reykjavik, Iceland** - Northern Lights gateway
- **Giant's Causeway, Northern Ireland** - Volcanic basalt formations
- **Bryce Canyon, Utah, USA** - Stunning red rock formations
- **Antelope Canyon, Arizona, USA** - Slot canyon photography paradise
- **Reynisfjara Beach, Iceland** - Dramatic black sand volcanic beach
- **Yosemite National Park, California, USA** - Granite cliffs and waterfalls
- **Dead Sea, Jordan** - Unique salt lake experience
- **Ha Long Bay, Vietnam** - Emerald waters and limestone islands
- **Jeita Grotto, Lebanon** - Stunning limestone cave system

### 🏙️ World-Class Cities
- **Tokyo, Japan** - Modern metropolis meets ancient tradition
- **London, UK** - Historic capital with royal heritage
- **Paris, France** - City of light and romance
- **Florence, Italy** - Renaissance art and architecture capital
- **Vienna, Austria** - Imperial elegance and classical music

## 📊 Dashboard Features

### Professional Theme Cards
- **Clean Design**: Modern, responsive layout with professional typography
- **Evidence Integration**: Blue paperclip icons (📎) for themes with web evidence
- **Quality Indicators**: Visual badges showing theme completeness and authority
- **Expandable Content**: Click to reveal detailed intelligence attributes

### Evidence Modal System
- **Real Web URLs**: Clickable links to authoritative travel sources
- **Authority Scoring**: Source credibility and relevance ratings
- **Cross-Source Validation**: Evidence verified across multiple sources
- **Quality Ratings**: Excellent, good, and acceptable quality indicators

### Navigation & User Experience
- **Back Navigation**: Easy return to main dashboard from any destination
- **Responsive Design**: Optimized for desktop and mobile viewing
- **Loading Indicators**: Real-time progress tracking during processing
- **Professional Styling**: Consistent branding and visual hierarchy

### Intelligence Insights
- **💎 Hidden Gems Detection**: Identifies off-the-beaten-path experiences
- **🏆 Authenticity Scoring**: Measures local vs. tourist-oriented experiences
- **📈 Quality Metrics**: Comprehensive quality assessment with confidence scoring
- **🎨 Composition Analysis**: Theme distribution and diversity analysis

## ⚙️ Configuration

### Core Settings (`config/config.yaml`)
```yaml
# Application name and branding
app_name: "Destination Insights Discovery"

# Server configuration with auto-detection
server:
  default_port: 8000
  auto_port_detection: true
  max_port_attempts: 10

# LLM configuration
llm_settings:
  provider: "gemini"  # or "openai"
  gemini_model_name: "gemini-2.0-flash"
  openai_model_name: "o4-mini"

# Agent system configuration
agents:
  enabled: true
  migration_mode: "fallback"  # Try agents first, fallback to legacy
  
  orchestrator:
    max_parallel_destinations: 3
    quality_threshold: 0.75
    
  web_discovery:
    enabled: true
    max_sources_per_destination: 12
    adaptive_query_generation: true
    
  intelligence_enhancement:
    enabled: true
    adaptive_attribute_processing: true
    
  evidence_validation:
    enabled: true
    cross_source_validation: true

# Seasonal image generation
seasonal_imagery:
  enabled: true  # Enable AI-powered seasonal image generation
  model: "dall-e-3"  # DALL-E model version
  image_size: "1024x1024"  # Image dimensions
  quality: "standard"  # 'standard' or 'hd'
  timeout_seconds: 60  # API timeout
  max_retries: 2  # Retry attempts for failed generations
  graceful_degradation: true  # Continue processing if image generation fails
    
# Pre-configured with 25 top destinations
destinations:
  - "Tokyo, Japan"
  - "Grand Canyon, Arizona, USA"
  - "Reykjavik, Iceland"
  # ... 22 more destinations
```

### Agent-Specific Configuration (`config/agent_config.yaml`)
```yaml
# Detailed agent behavior configuration
agents:
  orchestrator:
    workflow_timeout: 300
    enable_performance_monitoring: true
    
  web_discovery:
    content_quality_threshold: 0.6
    authority_filtering: true
    
  llm_orchestration:
    adaptive_resource_allocation: true
    max_concurrent_requests: 8
    
  intelligence_enhancement:
    dependency_aware_processing: true
    quality_driven_optimization: true
    
  evidence_validation:
    evidence_sufficiency_threshold: 0.7
    conflict_resolution: true
    
  quality_assurance:
    continuous_monitoring: true
    intervention_threshold: 0.5
```

## 🚀 Advanced Usage

### Processing Modes

#### Agent Mode (Recommended)
```bash
# Uses intelligent multi-agent orchestration
python main.py
```

#### Legacy Mode (Fallback)
```bash
# Traditional processing (automatically used if agents fail)
# Configured in config.yaml with migration_mode: "fallback"
```

### Command Line Options

#### Data Processing
```bash
# Process all configured destinations
python main.py

# Process specific destinations
python main.py --destinations "Bali, Indonesia" "Santorini, Greece"

# Clean run without browser instructions
python main.py --no-browser

# Process with seasonal image generation
python main.py --seasonal-images

# Process specific destinations with seasonal images
python main.py --destinations "Tokyo, Japan" "Paris, France" --seasonal-images

# Force regenerate seasonal images during processing
python main.py --seasonal-images --force-seasonal-images

# Generate ONLY seasonal images (skip main processing)
python main.py --seasonal-images-only

# Disable seasonal images (override config)
python main.py --no-seasonal-images
```

#### Standalone Seasonal Image Generation
```bash
# Generate images for a single destination
python generate_seasonal_images.py --destination "Tokyo, Japan"

# Generate for multiple destinations
python generate_seasonal_images.py --destination "Tokyo, Japan" "Paris, France"

# Generate for all configured destinations
python generate_seasonal_images.py --all

# Force regenerate existing images
python generate_seasonal_images.py --all --force

# Custom output directory
python generate_seasonal_images.py --destination "Rome, Italy" --output custom_images/

# List available destinations
python generate_seasonal_images.py --list

# Check API status and configuration
python generate_seasonal_images.py --check-api
```

#### Server Management
```bash
# Start server for latest results
python start_server.py

# Custom port and options
python start_server.py --port 8080 --no-browser

# List available sessions
python start_server.py --list-sessions
```