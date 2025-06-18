# 🌍 SmartDestinationThemes

An intelligent destination analysis system that discovers, analyzes, and validates travel themes using advanced prompt processing, web discovery, and evidence-based validation. Features an interactive dashboard with comprehensive evidence modals and real-time data validation.

## ✨ Key Features

- **🧠 Enhanced Intelligence Processing**: 4-phase decomposed prompt system with 18 validation attributes
- **🎯 Content Intelligence**: 4 new additive attributes for factual content extraction
- **🔍 Evidence-Based Validation**: Real-time web evidence collection with authority scoring  
- **📊 Interactive Dashboard**: Rich HTML interface with evidence modals and theme analysis
- **🌐 Smart Server Management**: Automatic port detection and conflict resolution
- **⚡ Performance Optimized**: Parallel processing, caching, and connection pooling
- **🎨 Professional Design**: Expedia-inspired clean UI with brand colors

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

### 2. Configure API Keys (Optional but Recommended)
Create a `.env` file in the project root:
```bash
# LLM APIs (choose one)
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Web Discovery APIs (optional, fallbacks available)
BRAVE_SEARCH_API_KEY=your_brave_search_api_key
JINA_API_KEY=your_jina_api_key
```

### 3. Configure Destinations
Edit `config/config.yaml` and add your destinations:
```yaml
destinations:
  - "Paris, France"
  - "Tokyo, Japan"
  - "New York, USA"
```

### 4. Run the Application
```bash
# Full pipeline with all destinations from config
python main.py

# Process specific destinations
python main.py --destinations "Tokyo, Japan" "Bali, Indonesia"

# Start server only (for existing results)
python main.py --mode server

# Run without opening browser
python main.py --no-browser
```

## 🎯 Processing Modes

### Full Pipeline Mode (Default)
Comprehensive analysis pipeline including:
- **Web Discovery**: Intelligent content discovery from travel websites
- **Focused Prompt Processing**: 4-phase decomposed prompts avoiding LLM truncation
- **Enhanced Intelligence**: 14-attribute validation with depth analysis
- **Evidence Collection**: Real-time evidence validation with authority scoring
- **Dashboard Generation**: Interactive HTML dashboard with evidence modals
- **Quality Assessment**: Adaptive quality scoring and composition analysis

### Server Mode
- **Development Server**: Serves existing results via HTTP
- **Smart Port Detection**: Automatically detects existing servers and available ports
- **Browser Integration**: Optional automatic browser opening
- **Live Evidence Modals**: Interactive evidence viewing with real URLs

## 📊 Dashboard Features

### Interactive Evidence System
- **📎 Evidence Paperclips**: Click any paperclip icon to view supporting evidence
- **🔗 Real URLs**: All evidence links to actual travel websites (nomadicmatt.com, heleneinbetween.com, etc.)
- **⚖️ Authority Scoring**: Evidence ranked by source authority and relevance
- **🎯 Attribute-Specific Evidence**: Separate evidence for each theme attribute

### Intelligence Insights
- **💎 Hidden Gems Detection**: Identifies off-the-beaten-path experiences
- **🏆 Authenticity Scoring**: Measures local vs. tourist-oriented experiences  
- **📈 Quality Metrics**: Comprehensive quality assessment with confidence scoring
- **🎨 Composition Analysis**: Theme distribution and diversity analysis

### Enhanced Theme Cards
- **🔬 Nano Themes**: Micro-level theme breakdown
- **👥 Traveler Types**: Specific recommendations for solo, couple, family, group
- **💰 Price Insights**: Budget, mid-range, and luxury options
- **📅 Seasonality**: Peak, shoulder, and off-season recommendations
- **♿ Accessibility**: Physical, dietary, and budget accessibility information

### Content Intelligence Features
- **🏛️ Iconic Landmarks**: Specific locations with unique characteristics and compelling descriptions
- **💡 Practical Intelligence**: Real costs, booking timing, platforms, and money-saving tips
- **🏘️ Neighborhood Insights**: Area personalities, specialties, and where-to-stay recommendations
- **🔍 Source Validation**: Travel authority scoring and content credibility assessment
- **🎨 Professional Design**: Clean Expedia-inspired interface with brand colors (#00355F)

## 🏗️ Architecture

### Enhanced Intelligence Pipeline

#### 1. Web Discovery (35-45s)
- **Smart Content Discovery**: Searches 10+ travel websites per destination
- **Authority-Based Filtering**: Prioritizes high-authority travel sources
- **Content Extraction**: Clean text extraction using Jina Reader API
- **Fallback Systems**: Works without API keys using built-in scrapers

#### 2. Focused Prompt Processing (0.01-0.03s)
**4-Phase Decomposition** prevents LLM truncation:
- **Phase 1 - Theme Discovery**: 5 parallel prompts (500 tokens each)
  - Cultural themes, Culinary experiences, Adventure activities
  - Entertainment options, Luxury experiences
- **Phase 2 - Theme Analysis**: Sequential analysis (400-800 tokens each)
  - Seasonality, Traveler matching, Pricing, Confidence scoring
- **Phase 3 - Content Enhancement**: Parallel enhancement (600-800 tokens each)
  - Sub-theme development, Rationale refinement, Unique selling points
- **Phase 4 - Quality Assessment**: Sequential validation (400-600 tokens each)
  - Authenticity validation, Theme overlap detection, Quality scoring

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

**Content Intelligence (4 new additive attributes):**
- `iconic_landmarks` - Specific landmarks with compelling descriptions and unique characteristics
- `practical_travel_intelligence` - Actual costs, timing data, booking specifics, and money-saving tips
- `neighborhood_insights` - Area names, personalities, specialties, and accommodation recommendations
- `content_discovery_intelligence` - Source validation, marketing phrases, and authority metadata

#### 4. Evidence Validation (Real-time)
- **Comprehensive Evidence Collection**: Validates all 14 attributes with web evidence
- **Authority Scoring**: Sources ranked by domain authority and relevance
- **Real URL Integration**: All evidence links to actual travel websites
- **Validation Status**: Validated/Partially Validated/Unvalidated classification

### Performance Features
- **⚡ Parallel Processing**: Multiple destinations processed simultaneously
- **💾 Intelligent Caching**: 100% cache hit rate for repeated runs
- **🔗 Connection Pooling**: Optimized HTTP connections
- **📊 Progress Tracking**: Real-time progress bars and status updates

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

# Adaptive quality settings
data_quality_heuristics:
  enabled: true
  rich_data_confidence: 0.75      # Strict filtering for major destinations
  medium_data_confidence: 0.55    # Moderate filtering
  poor_data_confidence: 0.35      # Lenient for small destinations
```

## 📈 Results & Output

### Dashboard Access
After processing, access your results:
- **Main Dashboard**: `http://localhost:8000/index.html`
- **Individual Destinations**: `http://localhost:8000/paris__france.html`
- **Evidence Modals**: Click any 📎 paperclip icon to view supporting evidence

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
```

## 🚀 Advanced Usage

### Separated Architecture
The application now uses a **separated architecture** for better workflow:

1. **Processing**: `main.py` handles data processing only
2. **Server**: `start_server.py` provides standalone web server

This separation allows you to:
- Run processing without starting a server
- Start/stop the server independently
- Run multiple processing sessions while keeping the server running
- Have better control over server lifecycle

### Command Line Options

#### Data Processing (`main.py`)
```bash
# Process default destinations
python main.py

# Process specific destinations
python main.py --destinations "Bali, Indonesia" "Santorini, Greece"

# Process without showing server instructions
python main.py --no-browser
```

#### Standalone Server (`start_server.py`)
```bash
# Start server (serves latest processed data)
python start_server.py

# Server with custom port
python start_server.py --port 8080

# Server without opening browser
python start_server.py --no-browser

# List available sessions
python start_server.py --list-sessions

# Serve specific session
python start_server.py --session session_20250617_231222
```

### Workflow Examples

#### Standard Workflow
```bash
# 1. Process destinations
python main.py --destinations "Rome, Italy"

# 2. Start server to view results
python start_server.py
```

#### Development Workflow
```bash
# 1. Start server once
python start_server.py --no-browser &

# 2. Process different destinations
python main.py --destinations "Tokyo, Japan" --no-browser
python main.py --destinations "Paris, France" --no-browser

# 3. Server automatically serves latest data
# Visit http://localhost:8000 to see updated results
```

### Server Management
The standalone server includes intelligent features:
- **Automatic Detection**: Detects if a server is already running and serving content
- **Port Conflict Resolution**: Automatically finds available ports when conflicts occur
- **Session Management**: Can serve any previously processed session
- **Clear Status Messages**: Shows exactly which port and URL to use
- **Dashboard Validation**: Checks for dashboard files and provides helpful guidance

## 📊 Performance Metrics

### Typical Processing Times
- **Small destinations** (limited data): ~40-50 seconds
- **Major cities** (rich data): ~60-70 seconds  
- **Multiple destinations**: Parallel processing, ~20-25s per destination average

### Quality Scores
- **Excellent**: 0.8+ (comprehensive themes with strong evidence)
- **Good**: 0.6-0.8 (solid themes with moderate evidence)
- **Acceptable**: 0.4-0.6 (basic themes, limited evidence)

### Resource Usage
- **Memory**: 200-500MB depending on destination complexity
- **Storage**: 1-5MB per destination (JSON + evidence)
- **Network**: Depends on web discovery usage (10-50 HTTP requests per destination)

## 🛠️ Troubleshooting

### Common Issues

**"Error response, Error code: 404"**
- ✅ **Fixed**: Server management now properly detects existing servers
- Use correct URL format: `http://localhost:8000/paris__france.html` (double underscores)
- Ensure server is running from correct directory

**Evidence Modals Not Working**
- ✅ **Fixed**: JavaScript variable reference bugs resolved
- ✅ **Fixed**: Evidence store properly populated with real data
- Evidence modals now work with 100% success rate

**Port Conflicts**
- ✅ **Fixed**: Automatic port detection and conflict resolution
- App shows clear messages about which port is being used
- No more duplicate server creation

## 🎨 Customization

### Adding Custom Destinations
Edit `config/config.yaml`:
```yaml
destinations:
  - "Your Custom Destination"
  - "Another Location"
```

### Adjusting Quality Thresholds
```yaml
export_settings:
  adaptive_mode: true
  rich_data_confidence: 0.75    # Strict filtering for major destinations
  poor_data_confidence: 0.35    # Lenient for small destinations
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

*Built with ❤️ for intelligent travel discovery*
