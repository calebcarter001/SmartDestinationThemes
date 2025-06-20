# 🌍 Smart Destination Themes & Nuances

**AI-Powered Multi-Agent Travel Intelligence System**

A sophisticated multi-agent system that discovers, analyzes, and curates comprehensive travel insights for destinations worldwide. Features **dual-mode processing** for both destination themes and nuanced expectations, powered by advanced LLM orchestration and intelligent web discovery.

## ✨ **Latest Features**

### 🎯 **Destination Nuance Generation** *(NEW)*
- **3-Tier Nuance System**: Destination experiences, hotel expectations, vacation rental features
- **Multi-LLM Generation**: Supports OpenAI GPT-4, Gemini 2.0 Flash, and Anthropic Claude
- **Comprehensive Evidence Collection**: 90+ evidence pieces per destination with real web validation
- **Search Validation**: Real-time web search validation for every generated nuance
- **Quality Scoring**: 0.8+ quality scores with confidence metrics and authority validation

### 🔄 **Selective Processing Modes** *(NEW)*
- **Theme-Only Processing**: Generate comprehensive destination themes without nuances
- **Nuance-Only Processing**: Focus solely on nuance generation while preserving existing themes
- **Full Processing**: Complete theme + nuance generation in one pass
- **Surgical Debugging**: Selective cleanup and regeneration for targeted troubleshooting

### 🤖 **Enhanced Multi-Agent System**
- **7-Agent Orchestration**: Web Discovery, LLM Orchestration, Intelligence Enhancement, Evidence Validation, Destination Nuance, Seasonal Images, Quality Assurance
- **Intelligent Fallback**: Graceful degradation and error recovery across all agents
- **Parallel Processing**: Concurrent agent execution for maximum efficiency
- **Advanced Evidence Pipeline**: Dual-stream evidence collection with deduplication and quality scoring

### 🎨 **AI-Powered Seasonal Image Generation**
- **DALL-E 3 Integration**: Professional travel photography for all 4 seasons per destination
- **Seasonal Visual Themes**: Spring blooms, summer festivals, autumn colors, winter atmospheres
- **Automatic Collages**: Beautiful 2x2 seasonal grids combining seasonal images
- **Smart Caching**: Detects existing images to avoid unnecessary regeneration

## 🚀 **Quick Start**

### 1. **Environment Setup**
```bash
# Clone and setup
git clone https://github.com/calebcarter001/SmartDestinationThemes.git
cd SmartDestinationThemes
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. **API Configuration**
Create a `.env` file in the project root:
```bash
# LLM APIs (at least one required)
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Web Discovery APIs (optional, fallbacks available)
BRAVE_SEARCH_API_KEY=your_brave_search_api_key
JINA_API_KEY=your_jina_api_key
```

### 3. **Processing Modes**

#### **Full Processing** (Themes + Nuances)
```bash
python main.py
```

#### **Theme-Only Processing**
```bash
# Edit config/config.yaml:
processing_mode:
  enable_theme_processing: true
  enable_nuance_processing: false
  enable_seasonal_images: true

python main.py
```

#### **Nuance-Only Processing**
```bash
# Edit config/config.yaml:
processing_mode:
  enable_theme_processing: false
  enable_nuance_processing: true
  enable_seasonal_images: false

python main.py
```

### 4. **Dashboard Access**
```bash
# Start the dashboard server
python start_server.py

# Access at: http://localhost:8000
```

## 🛠️ **Utility Scripts**

### **Selective Cleanup**
```bash
# Clean everything for fresh run
python cleanup_for_fresh_run.py

# Preserve themes, clean only nuances
python cleanup_for_fresh_run.py --preserve-themes
```

### **Server Management**
```bash
# Start server with auto-detection
python start_server.py

# Check dashboard status
python open_dashboard.py

# Generate standalone seasonal images
python generate_seasonal_images.py --destination "Tokyo, Japan"
```

## 🎯 **Nuance Generation System**

### **3-Tier Nuance Architecture**
The system generates nuanced insights across three critical travel categories:

#### 🏖️ **Destination Nuances**
- **Cultural Experiences**: Local traditions, festivals, authentic interactions
- **Hidden Gems**: Off-the-beaten-path discoveries and local secrets
- **Activity Specifics**: Unique activities and experiences specific to the destination
- **Seasonal Variations**: Best times to visit and seasonal considerations

#### 🏨 **Hotel Expectations**
- **Amenity Preferences**: Technology, comfort, and service expectations
- **Cultural Accommodations**: Traditional vs. modern accommodation styles
- **Location Priorities**: Proximity to attractions, transportation, nightlife
- **Service Standards**: Multilingual staff, concierge services, local expertise

#### 🏡 **Vacation Rental Expectations**
- **Authentic Living**: Traditional architecture and local neighborhood integration
- **Practical Amenities**: Kitchen facilities, local market access, transportation
- **Cultural Immersion**: Traditional design elements and local living experiences
- **Convenience Factors**: Proximity to attractions, local services, and public transport

### **Multi-LLM Integration**
- **OpenAI GPT-4**: Advanced reasoning and creative nuance generation
- **Gemini 2.0 Flash**: High-speed processing with quality insights
- **Anthropic Claude**: Ethical AI with cultural sensitivity focus
- **Intelligent Load Balancing**: Optimized model selection for each nuance type

## 🌍 **Supported Destinations**

The system is pre-configured with **25 premier travel destinations**:

### 🏛️ **Historic & Cultural**
- **Tokyo, Japan** - Modern metropolis meets ancient tradition
- **Paris, France** - City of light and romance
- **Rome, Italy** - Eternal city with millennia of history
- **Santorini, Greece** - Stunning sunsets and volcanic beauty
- **Kyoto, Japan** - Traditional temples and cultural heritage

### 🏞️ **Natural Wonders**
- **Reykjavik, Iceland** - Northern Lights and volcanic landscapes
- **Banff, Canada** - Rocky Mountain wilderness and pristine lakes
- **Lofoten Islands, Norway** - Dramatic peaks and Arctic beauty
- **Cape Town, South Africa** - Table Mountain and wine country
- **Queenstown, New Zealand** - Adventure capital with stunning landscapes

### 🏖️ **Tropical Paradises**
- **Maldives** - Overwater bungalows and coral reefs
- **Bora Bora, French Polynesia** - Lagoon paradise and luxury resorts
- **Tulum, Mexico** - Mayan ruins and Caribbean beaches
- **Ubud, Bali** - Rice terraces and spiritual retreats
- **Goa, India** - Portuguese heritage and beach culture

### 🏔️ **Adventure Destinations**
- **Whistler, Canada** - World-class skiing and mountain biking
- **Zermatt, Switzerland** - Matterhorn views and alpine excellence
- **Machu Picchu, Peru** - Lost city of the Incas
- **Serengeti, Tanzania** - The Great Migration and wildlife
- **Siem Reap, Cambodia** - Gateway to Angkor Wat temples

### 🏙️ **Urban Experiences**
- **New York City, USA** - The city that never sleeps
- **Edinburgh, Scotland** - Historic charm and festival culture
- **Lisbon, Portugal** - Colorful neighborhoods and coastal beauty
- **Marrakech, Morocco** - Imperial city and desert gateway
- **Amalfi Coast, Italy** - Dramatic coastline and charming villages

## 📈 **System Performance**

### **Processing Metrics**
- **Theme Generation**: ~30-45 seconds per destination
- **Nuance Generation**: ~15-20 seconds per destination  
- **Evidence Collection**: 90+ pieces per destination
- **Quality Scores**: 0.8+ average across all categories
- **Success Rate**: 100% with intelligent fallback systems

### **Agent Performance**
- **Web Discovery**: ~11.6 seconds, 9 sources average
- **LLM Orchestration**: ~0.01 seconds (cached), 23 themes average
- **Intelligence Enhancement**: 18 attributes, dependency-aware processing
- **Evidence Validation**: ~0.11 seconds, 38 evidence pieces average
- **Destination Nuance**: ~16 seconds, 32 nuances with full validation
- **Seasonal Images**: ~55-60 seconds (4 images + collage)

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

🌍 **Discover the world's destinations with AI-powered intelligence and nuanced insights.**
