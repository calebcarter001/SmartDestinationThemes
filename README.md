# 🌍 SmartDestinationThemes

An intelligent destination analysis system that discovers and analyzes travel themes using focused prompt processing and web discovery.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone and setup
git clone <repository>
cd SmartDestinationThemes
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Your Setup
```bash
# Copy and edit configuration
cp config/config.yaml.example config/config.yaml
# Edit config/config.yaml with your destinations and settings
```

### 3. Add Your Destinations
Edit `config/config.yaml` and add your destinations:
```yaml
destinations:
  - "Paris, France"
  - "Tokyo, Japan"
  - "New York, USA"
```

### 4. Run Processing
```bash
# Full pipeline with web discovery
python main.py

# Or specify destinations directly
python main.py --destinations "Tokyo, Japan" "Paris, France"

# Start development server for existing results
python main.py --mode server
```

## 🎯 Processing Modes

### Full Pipeline Mode (Default)
- **Web Discovery**: Searches for destination content using configurable APIs
- **Focused Prompt Processing**: Uses 4-phase decomposed prompts to avoid LLM truncation
- **Enhanced Intelligence**: Adds depth analysis, authenticity scoring, and evidence validation
- **Dashboard Generation**: Creates interactive HTML dashboard

### Server Mode
- **Development Server**: Serves existing results via HTTP
- **Auto Port Detection**: Finds available ports automatically
- **Browser Integration**: Opens dashboard automatically

## 🔧 Configuration

### Core Settings (`config/config.yaml`)

```yaml
# Server configuration
server:
  default_port: 8000
  host: "localhost"
  auto_port_detection: true
  max_port_attempts: 10

# Destinations to process
destinations:
  - "Your destination here"

# Web discovery settings
processing_settings:
  web_discovery:
    max_sources_per_destination: 10
    timeout_seconds: 30
    enable_content_validation: true
    custom_queries:
      - "{destination} hidden gems local secrets"
      - "{destination} authentic experiences off beaten path"

  # Demographic mapping
  demographic_mapping:
    family: ["families with children", "multi-generational groups"]
    solo: ["solo travelers"]
    couple: ["couples"]
    group: ["friend groups"]
    business: ["business travelers"]
```

### API Keys (Optional)
Set environment variables for enhanced web discovery:
```bash
export BRAVE_SEARCH_API_KEY="your_brave_api_key"
export JINA_API_KEY="your_jina_api_key"
export GEMINI_API_KEY="your_gemini_key"
export OPENAI_API_KEY="your_openai_key"
```

## 📊 Results & Dashboard

After processing, access your results:
- **Dashboard**: `http://localhost:8000`
- **Individual Results**: `http://localhost:8000/paris__france.html`

### Dashboard Features
- **Theme Overview**: Visual theme distribution across categories
- **Confidence Scoring**: Quality metrics for each theme
- **Evidence Validation**: Supporting evidence for theme claims
- **Traveler Insights**: Recommendations by traveler type
- **Seasonal Analysis**: Best times to visit for each theme

## 🏗️ Architecture

### Focused Prompt Processing
Solves LLM truncation issues through 4-phase decomposition:

1. **Theme Discovery** (5 parallel prompts, ~500 tokens each)
   - Cultural themes
   - Culinary experiences  
   - Adventure activities
   - Entertainment options
   - Luxury experiences

2. **Theme Analysis** (4 sequential prompts, ~400-800 tokens each)
   - Seasonality analysis
   - Traveler type matching
   - Pricing insights
   - Confidence scoring

3. **Content Enhancement** (3 parallel prompts, ~600-800 tokens each)
   - Sub-theme development
   - Rationale refinement
   - Unique selling points

4. **Quality Assessment** (3 sequential prompts, ~400-600 tokens each)
   - Authenticity validation
   - Theme overlap detection
   - Overall quality scoring

### Benefits
- **No Truncation**: Individual prompts stay under token limits
- **Parallel Processing**: Multiple prompts run simultaneously
- **Better Quality**: Focused prompts produce more specific results
- **Scalable**: Easy to add new categories or analysis phases

## 🔍 Web Discovery

### Automatic Content Discovery
- **Search Integration**: Uses Brave Search API when available
- **Content Extraction**: Jina Reader API for clean content extraction
- **Fallback Sources**: Common travel websites when APIs unavailable
- **Content Validation**: Quality filtering and spam detection

### Configurable Search Queries
Customize search patterns in `config.yaml`:
```yaml
custom_queries:
  - "{destination} hidden gems local secrets"
  - "{destination} seasonal events festivals"
  - "{destination} authentic local experiences"
```

## 🎨 Customization

### Theme Categories
Add custom categories in your configuration:
```yaml
seed_themes:
  - culture
  - food
  - adventure
  - your_custom_theme
```

### Experience Levels
Configure experience level detection:
```yaml
experience_level_keywords:
  advanced: ["extreme", "expert", "challenging"]
  intermediate: ["moderate", "some experience"]
  beginner: ["easy", "introductory", "basic"]
```

### Accessibility Mapping
Customize accessibility level detection:
```yaml
accessibility_keywords:
  high_physical_demands: ["extreme", "strenuous", "demanding"]
  requires_mobility: ["hiking", "climbing", "walking"]
  accessible: ["wheelchair", "easy access", "level ground"]
```

## 🚀 Advanced Usage

### Custom Processing
```bash
# Process specific destinations with custom port
python main.py --destinations "Bali, Indonesia" --port 8080

# Run server without opening browser
python main.py --mode server --no-browser

# Use standalone server script
python start_server.py --port 8080 --no-browser
```

### Development Server
```bash
# Start dedicated server
python start_server.py

# With custom configuration
python start_server.py --config custom_config.yaml --port 9000
```

## 📈 Performance

### Typical Processing Times
- **Small destinations**: ~30-40 seconds
- **Major cities**: ~40-60 seconds
- **Multiple destinations**: Parallel processing where possible

### Resource Usage
- **Memory**: ~200-500MB depending on destination size
- **Storage**: ~1-5MB per destination for results
- **Network**: Depends on web discovery API usage

## 🛠️ Troubleshooting

### Common Issues

**Port Already in Use**
- System automatically finds alternative ports
- Use `--port` to specify different port

**No API Keys**
- System works without API keys using fallback sources
- Add API keys for enhanced web discovery

**Empty Results**
- Check destination spelling in config.yaml
- Verify internet connection for web discovery
- Review logs for specific error messages

**Dashboard Not Loading**
- Run `python main.py` first to generate data
- Check that `dev_staging/dashboard` directory exists
- Verify server is running on correct port

## 📝 Sample Output

Generated themes include rich metadata:

```json
{
  "theme": "Culinary Heritage",
  "category": "food",
  "confidence": 0.87,
  "sub_themes": ["Traditional Markets", "Local Specialties"],
  "traveler_types": ["family", "couple", "solo"],
  "seasonality": {
    "peak": ["March", "April", "October"],
    "avoid": ["August"]
  },
  "price_point": "mid",
  "authenticity_level": "authentic_local"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 