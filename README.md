# 🌍 SmartDestinationThemes

An intelligent destination analysis system that discovers, analyzes, and validates travel themes using advanced prompt processing, web discovery, and evidence-based validation. Built as an internal tool for content strategists and product managers, featuring an interactive dashboard with comprehensive theme analysis and professional Expedia-inspired design.

## ✨ Key Features

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

# Quality settings
data_quality_heuristics:
  enabled: true
  rich_data_confidence: 0.75
  medium_data_confidence: 0.55
  poor_data_confidence: 0.35
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

### Separated Architecture
**Processing**: `main.py` handles data processing and staging
**Server**: `start_server.py` provides standalone web server

Benefits:
- Independent processing and serving
- Multiple processing sessions with persistent server
- Better development workflow control

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
