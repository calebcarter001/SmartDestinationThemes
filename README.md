# 🌍 SmartDestinationThemes

An intelligent destination analysis system that discovers, analyzes, and validates travel themes using advanced prompt processing, web discovery, and evidence-based validation. Built as an internal tool for content strategists and product managers, featuring an interactive dashboard with comprehensive theme analysis and professional Expedia-inspired design.

## ✨ Key Features

- **🤖 Agentic Workflow System**: Multi-agent orchestration with intelligent task coordination and autonomous processing
- **🧠 Enhanced Intelligence Processing**: 4-phase decomposed prompt system with 18 validation attributes
- **🎯 Content Intelligence**: 4 specialized attributes for factual content extraction and source validation
- **🔍 Evidence-Based Validation**: Real-time web evidence collection with travel authority scoring  
- **📊 Interactive Dashboard**: Professional HTML interface with expandable content sections
- **🌐 Smart Server Management**: Automatic port detection and conflict resolution
- **⚡ Performance Optimized**: Parallel processing, intelligent caching, and connection pooling
- **🎨 Professional Design**: Clean Expedia-inspired UI with brand colors (#00355F)

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
# LLM APIs (required - choose one)
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Web Discovery APIs (optional, fallbacks available)
BRAVE_SEARCH_API_KEY=your_brave_search_api_key
JINA_API_KEY=your_jina_api_key
```

### 3. Configure Destinations
Edit `config/config.yaml` to specify destinations:
```yaml
destinations:
  - "Paris, France"
  - "Tokyo, Japan"
  - "New York, USA"
```

### 4. Run the Application
```bash
# Clean previous runs and start fresh processing
python cleanup_for_fresh_run.py
python main.py

# Or start server for existing results
python start_server.py
```

## 🤖 Agentic Workflow System

### Multi-Agent Architecture

The SmartDestinationThemes application now features an **intelligent multi-agent orchestration system** that coordinates autonomous agents for comprehensive destination processing:

#### 🎭 Agent Orchestrator
- **Central Command Center**: Coordinates all agent activities and workflow execution
- **Task Distribution**: Intelligent task routing based on agent capabilities and workload
- **State Management**: Maintains workflow state and ensures processing continuity
- **Performance Monitoring**: Real-time tracking of agent performance and resource utilization

#### 🕷️ Web Discovery Agent
- **Intelligent Web Crawling**: Adaptive content discovery from travel authority sources
- **Smart Query Generation**: Context-aware search query optimization
- **Content Filtering**: Quality-based content selection and relevance scoring
- **Source Verification**: Travel authority validation and credibility assessment

#### 🧠 LLM Orchestration Agent
- **Resource Management**: Intelligent LLM resource allocation and optimization
- **Processing Strategy**: Adaptive processing approaches based on content complexity
- **Quality Control**: Performance monitoring and result optimization
- **Cache Management**: Intelligent caching for improved efficiency

#### 💡 Intelligence Enhancement Agent
- **Attribute Processing**: 18 specialized intelligence attributes with adaptive selection
- **Context-Aware Enhancement**: Destination-specific intelligence optimization
- **Dependency Management**: Intelligent processing order based on attribute dependencies
- **Quality Optimization**: Continuous improvement of enhancement quality

#### 🔍 Evidence Validation Agent
- **Cross-Source Verification**: Multi-source evidence validation and conflict resolution
- **Authority Scoring**: Source credibility assessment and authority ranking
- **Fact Checking**: Real-time validation against authoritative travel sources
- **Evidence Synthesis**: Intelligent evidence aggregation and consensus building

#### ✅ Quality Assurance Agent
- **Continuous Monitoring**: Real-time quality assessment throughout the workflow
- **Adaptive Interventions**: Dynamic quality improvements and error correction
- **Performance Analytics**: Comprehensive quality metrics and reporting
- **Optimization Recommendations**: Intelligent suggestions for workflow improvements

### Agent Communication & Coordination

- **Message-Based Architecture**: Asynchronous inter-agent communication with message routing
- **Workflow Orchestration**: Sequential and parallel task execution with dependency management
- **Error Handling & Recovery**: Robust error handling with automatic retries and fallback strategies
- **Performance Optimization**: Dynamic resource allocation and load balancing

### Configuration & Control

```yaml
# Agent system configuration in config/agent_config.yaml
agents:
  orchestrator:
    enabled: true
    max_concurrent_workflows: 3
  
  web_discovery:
    enabled: true
    adaptive_query_generation: true
    authority_filtering: true
  
  llm_orchestration:
    enabled: true
    adaptive_resource_allocation: true
    performance_optimization: true
  
  intelligence_enhancement:
    enabled: true
    adaptive_attribute_processing: true
    dependency_aware_processing: true
  
  evidence_validation:
    enabled: true
    cross_source_validation: true
    conflict_resolution: true
  
  quality_assurance:
    enabled: true
    continuous_monitoring: true
    adaptive_interventions: true
```

### Testing the Agent System

```bash
# Test the complete agentic workflow
python test_agents.py

# Test individual agent capabilities
python -m agents.test_web_discovery
python -m agents.test_llm_orchestration
```

## 🎯 Core Architecture

### Enhanced Intelligence Pipeline

#### 1. Web Discovery (35-45s)
- **Smart Content Discovery**: Searches 10+ travel websites per destination
- **Authority-Based Filtering**: Prioritizes high-authority travel sources
- **Content Extraction**: Clean text extraction using Jina Reader API
- **Fallback Systems**: Built-in scrapers when APIs unavailable

#### 2. Focused Prompt Processing (0.01-0.03s)
**4-Phase Decomposition** prevents LLM truncation:
- **Phase 1 - Theme Discovery**: 5 parallel prompts for comprehensive coverage
- **Phase 2 - Theme Analysis**: Sequential analysis for depth
- **Phase 3 - Content Enhancement**: Parallel enhancement for quality
- **Phase 4 - Quality Assessment**: Sequential validation and scoring

#### 3. Enhanced Intelligence Processing (5-20s)
**18 Validation Attributes** per theme:

**Core Intelligence (14 attributes):**
- `nano_themes` - Micro-level theme breakdown
- `price_insights` - Comprehensive pricing analysis
- `seasonality` - Peak/shoulder/off-season recommendations
- `traveler_types` - Solo/couple/family/group suitability
- `accessibility` - Physical/dietary/budget accessibility
- `authenticity_analysis` - Local vs. tourist experience rating
- `hidden_gem_score` - Off-the-beaten-path potential
- `depth_analysis` - Experience depth and complexity
- `cultural_sensitivity` - Cultural considerations and etiquette
- `experience_intensity` - Physical and emotional intensity
- `time_commitment` - Duration recommendations
- `local_transportation` - Getting around information
- `accommodation_types` - Lodging recommendations
- `booking_considerations` - Advance planning requirements

**Content Intelligence (4 specialized attributes):**
- `iconic_landmarks` - Specific landmarks with compelling descriptions and unique characteristics
- `practical_travel_intelligence` - Actual costs, timing data, booking specifics, and money-saving tips
- `neighborhood_insights` - Area names, personalities, specialties, and accommodation recommendations
- `content_discovery_intelligence` - Source validation, marketing phrases, and authority metadata

#### 4. Evidence Validation & Dashboard Generation
- **Comprehensive Evidence Collection**: Validates all attributes with web evidence
- **Authority Scoring**: Sources ranked by domain authority and relevance
- **Interactive Dashboard**: Professional HTML with expandable content sections
- **Development Staging**: Automatic staging for immediate viewing

## 📊 Dashboard Features

### Professional Theme Cards
- **Clean Design**: Expedia-inspired styling with brand colors
- **Expandable Sections**: Click to reveal detailed content intelligence
- **Quality Indicators**: Visual status indicators for theme completeness
- **Responsive Layout**: Professional grid system for optimal viewing

### Content Intelligence Display
- **🏛️ Iconic Landmarks**: Specific locations with unique characteristics
- **💡 Practical Intelligence**: Real costs, booking timing, and money-saving tips
- **🏘️ Neighborhood Insights**: Area personalities and accommodation recommendations
- **🔍 Source Validation**: Travel authority scoring and content credibility

### Intelligence Insights
- **💎 Hidden Gems Detection**: Identifies off-the-beaten-path experiences
- **🏆 Authenticity Scoring**: Measures local vs. tourist-oriented experiences  
- **📈 Quality Metrics**: Comprehensive quality assessment with confidence scoring
- **🎨 Composition Analysis**: Theme distribution and diversity analysis

## 🔧 Configuration

### Core Settings (`config/config.yaml`)
```yaml
# Server configuration
server:
  default_port: 8000
  host: "localhost"
  auto_port_detection: true
  max_port_attempts: 10
  open_browser_by_default: true

# LLM settings
llm_settings:
  provider: "gemini"  # or "openai"
  gemini_model_name: "gemini-2.0-flash"
  openai_model_name: "gpt-4o-mini"

# Destinations to process
destinations:
  - "Paris, France"
  - "Tokyo, Japan"
  - "New York, USA"

# Agentic workflow settings
agentic_workflow:
  enabled: true
  orchestration_mode: "intelligent"  # or "sequential"
  parallel_processing: true
  max_concurrent_destinations: 2

# Quality settings
data_quality_heuristics:
  enabled: true
  rich_data_confidence: 0.75
  medium_data_confidence: 0.55
  poor_data_confidence: 0.35
```

### Agent-Specific Configuration (`config/agent_config.yaml`)
```yaml
# Complete agent system configuration
agents:
  orchestrator:
    enabled: true
    max_concurrent_workflows: 3
    workflow_timeout: 300  # 5 minutes
    enable_performance_monitoring: true
  
  web_discovery:
    enabled: true
    adaptive_query_generation: true
    authority_filtering: true
    max_sources_per_destination: 15
    content_quality_threshold: 0.6
  
  llm_orchestration:
    enabled: true
    adaptive_resource_allocation: true
    performance_optimization: true
    enable_intelligent_batching: true
    max_concurrent_requests: 8
  
  intelligence_enhancement:
    enabled: true
    adaptive_attribute_processing: true
    dependency_aware_processing: true
    quality_driven_optimization: true
  
  evidence_validation:
    enabled: true
    cross_source_validation: true
    conflict_resolution: true
    evidence_sufficiency_threshold: 0.7
  
  quality_assurance:
    enabled: true
    continuous_monitoring: true
    adaptive_interventions: true
    quality_threshold: 0.8
```

## 📈 Results & Output

### Dashboard Access
After processing, access results at:
- **Main Dashboard**: `http://localhost:8000/index.html`
- **Individual Destinations**: `http://localhost:8000/paris__france.html`
- **Development Staging**: Automatically staged in `dev_staging/dashboard/`

### File Structure
```
outputs/session_YYYYMMDD_HHMMSS/
├── dashboard/
│   ├── index.html              # Main dashboard
│   ├── paris__france.html      # Individual destination pages
│   └── ...
├── json/
│   ├── paris__france_enhanced.json    # Enhanced theme data
│   ├── paris__france_evidence.json    # Evidence data
│   └── ...
└── session_summary.json       # Processing summary

dev_staging/
├── dashboard/                  # Latest session staged for development
└── json/                      # Latest JSON data
```

## 🚀 Advanced Usage

### Agentic Workflow Integration

The application now supports **two processing modes**:

#### Traditional Mode (Backward Compatible)
```bash
# Use existing functionality with enhanced performance
python main.py
```

#### Agentic Workflow Mode
```bash
# Enable multi-agent orchestration in config/config.yaml
agentic_workflow:
  enabled: true
  orchestration_mode: "intelligent"

# Run with agent orchestration
python main.py --use-agents

# Test agent system specifically
python test_agents.py
```

### Separated Architecture
**Processing**: `main.py` handles data processing and staging
**Server**: `start_server.py` provides standalone web server

Benefits:
- Independent processing and serving
- Multiple processing sessions with persistent server
- Better development workflow control
- Agent-based parallel processing for improved performance

### Command Line Options

#### Data Processing (`main.py`)
```bash
# Process default destinations from config
python main.py

# Process specific destinations
python main.py --destinations "Bali, Indonesia" "Santorini, Greece"

# Process without browser instructions
python main.py --no-browser
```

#### Standalone Server (`start_server.py`)
```bash
# Start server for latest processed data
python start_server.py

# Custom port
python start_server.py --port 8080

# No browser opening
python start_server.py --no-browser

# List available sessions
python start_server.py --list-sessions

# Serve specific session
python start_server.py --session session_20250617_231222
```

### Utility Scripts

#### Cleanup for Fresh Runs
```bash
# Clean all caches, outputs, and staging for fresh processing
python cleanup_for_fresh_run.py
```

#### Dashboard Opener
```bash
# Quick dashboard access utility
python open_dashboard.py
```

## 📊 Performance Metrics

### Processing Times
- **Small destinations**: ~40-50 seconds
- **Major cities**: ~60-70 seconds  
- **Multiple destinations**: ~20-25s per destination (parallel)

### Quality Distribution
- **Excellent**: 0.8+ (comprehensive themes with strong evidence)
- **Good**: 0.6-0.8 (solid themes with moderate evidence)
- **Acceptable**: 0.4-0.6 (basic themes, limited evidence)

### Resource Usage
- **Memory**: 200-500MB depending on complexity
- **Storage**: 1-5MB per destination
- **Cache Hit Rate**: 100% for repeated processing

## 🛠️ Troubleshooting

### Common Issues

**"No evidence validation data"**
- ✅ **Fixed**: Now shows "Enhanced theme analysis complete" 
- Content intelligence attributes properly integrated

**Port Conflicts**
- ✅ **Fixed**: Automatic port detection and conflict resolution
- Clear messaging about active ports and URLs

**Content Intelligence Missing**
- Ensure LLM API keys are properly configured
- Check logs for content intelligence processing status

## 🎨 Customization

### Adding Destinations
Edit `config/config.yaml`:
```yaml
destinations:
  - "Your Custom Destination"
  - "Another Location"
```

### Adjusting Quality Thresholds
```yaml
data_quality_heuristics:
  rich_data_confidence: 0.75    # Strict filtering
  poor_data_confidence: 0.35    # Lenient filtering
```

### Styling Customization
Theme cards use Expedia brand colors and professional styling defined in the enhanced viewer generator. Modify `src/enhanced_viewer_generator.py` for custom styling.

## 🏗️ Project Structure

```
SmartDestinationThemes/
├── src/                        # Core application code
│   ├── core/                   # Core processing modules
│   ├── utils/                  # Utility functions
│   ├── enhanced_data_processor.py
│   ├── enhanced_viewer_generator.py
│   ├── content_intelligence_processor.py
│   └── schemas.py
├── tools/                      # External tool integrations
├── config/                     # Configuration files
├── main.py                     # Main processing script
├── start_server.py            # Standalone server
├── cleanup_for_fresh_run.py   # Cleanup utility
├── open_dashboard.py          # Dashboard opener
└── requirements.txt           # Dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Built for intelligent travel content strategy and destination analysis*
