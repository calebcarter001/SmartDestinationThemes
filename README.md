# SmartDestinationThemes 🌍

**An AI-powered destination theme analysis system that generates comprehensive travel affinities using advanced LLM models, web augmentation, and quality assurance workflows.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Overview

SmartDestinationThemes analyzes travel destinations and generates detailed theme affinities using:

- **🤖 Multi-LLM Processing**: OpenAI GPT-4 and Google Gemini models
- **🔍 Web Augmentation**: Real-time web search and content validation  
- **📊 Quality Assessment**: Multi-dimensional quality scoring system
- **👥 Human Review Workflow**: Intelligent QA routing and reviewer management
- **🛡️ Priority Data Extraction**: Safety, visa, and health information
- **📈 Real-time Monitoring**: System health tracking and alerting
- **🌐 Modern Dashboard**: Interactive HTML visualization with modular architecture

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Dashboard](#-dashboard)
- [API Reference](#-api-reference)
- [Production Deployment](#-production-deployment)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🎯 Core Capabilities
- **Intelligent Theme Generation**: AI-powered analysis of destination characteristics
- **Multi-Model Consensus**: Combines insights from multiple LLM providers
- **Evidence-Based Validation**: Web search integration for factual verification
- **Seasonal Analysis**: Peak/avoid periods for optimal travel planning
- **Traveler Segmentation**: Personalized recommendations by traveler type
- **Price Point Analysis**: Budget, mid-range, and luxury categorization

### 🏭 Production Features
- **Quality Scoring**: 5-dimensional quality assessment system
- **Human Review Workflow**: Intelligent routing based on quality thresholds
- **Priority Data Extraction**: Automated safety and regulatory information
- **System Monitoring**: Real-time health tracking and alerting
- **Knowledge Graph Integration**: RDF/SPARQL-based data storage
- **Caching System**: Multi-layered caching for performance optimization

### 📊 Visualization & Reporting
- **Modular Dashboard**: Separate pages for each destination
- **Interactive Analytics**: Quality distribution and performance charts
- **Mobile-Responsive Design**: Optimized for all devices
- **Export Capabilities**: JSON, HTML, and future PDF support
- **Shareable URLs**: Individual destination pages for easy sharing

## 🏗️ Architecture

The system follows a 4-stage pipeline:

1. **LLM Baseline Generation**: Multi-model theme generation
2. **Web Augmentation**: Search-based validation and enhancement
3. **Quality Assessment**: Multi-dimensional scoring and validation
4. **Dashboard Generation**: Interactive visualization and reporting

### 🔧 System Components

1. **LLM Factory** (`src/core/llm_factory.py`)
   - Multi-provider LLM integration (OpenAI, Gemini)
   - Model selection and fallback handling
   - Structured output generation

2. **Web Discovery** (`src/core/web_discovery_logic.py`)
   - Brave Search API integration
   - Content extraction and analysis
   - Authority-based source ranking

3. **Quality Assessment** (`src/scorer.py`)
   - Multi-dimensional quality scoring
   - Evidence-based validation
   - Actionable improvement recommendations

4. **QA Workflow** (`src/qa_flow.py`)
   - Intelligent review routing
   - Multi-reviewer support
   - Feedback collection and analysis

5. **Priority Extraction** (`tools/priority_data_extraction_tool.py`)
   - Safety concern identification
   - Visa requirement extraction
   - Health advisory processing

6. **Monitoring System** (`src/monitoring.py`)
   - Real-time performance tracking
   - System health assessment
   - Configurable alerting

7. **Dashboard Generation** (`src/html_viewer_generator.py`)
   - Interactive HTML visualization
   - Modular architecture

## 🛠️ Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Git

### Quick Setup
```bash
# Clone repository
git clone https://github.com/calebcarter001/SmartDestinationThemes.git
cd SmartDestinationThemes

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file:
```env
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here

# Model Configuration
OPENAI_MODEL_NAME=gpt-4o-mini
GEMINI_MODEL_NAME=gemini-2.0-flash
```

## 🚀 Quick Start

### Basic Usage
```bash
# Run the complete system
python main.py

# Open the generated dashboard
python open_dashboard.py
```

### Custom Destinations
Edit destinations in `main.py`:
```python
destinations_to_process = [
    "Tokyo, Japan",
    "Paris, France", 
    "Barcelona, Spain"
]
```

## 🌐 Dashboard

### Modular Architecture
The dashboard uses a modular structure:

```
dashboard/
├── index.html                    # Main overview page
├── las_vegas_nevada.html        # Individual destination pages
├── new_york_new_york.html       # Individual destination pages
└── [destination].html           # Auto-generated pages
```

### Features
- **Overview Page**: Summary of all destinations with key metrics
- **Individual Pages**: Detailed analysis for each destination  
- **Quality Visualization**: Interactive charts and scoring
- **Mobile Responsive**: Optimized for all devices
- **Shareable URLs**: Easy sharing of specific destinations

### Opening Dashboard
```bash
python open_dashboard.py
```

## 📊 Generated Output

The system produces:

1. **JSON Data**: `destination_affinities_production.json`
2. **Processing Summary**: `processing_summary.json` 
3. **Interactive Dashboard**: `dashboard/` directory
4. **System Logs**: `logs/` directory

### Sample Theme Output
```json
{
  "theme": "Thrill seeking",
  "category": "adventure", 
  "confidence": 0.95,
  "sub_themes": ["High roller", "Off-roading", "Extreme sports"],
  "seasonality": {
    "peak": ["March", "April", "October", "November"],
    "avoid": ["July", "August"]
  },
  "traveler_types": ["solo", "couple", "group"],
  "price_point": "mid",
  "validation": "Evidence found in web content"
}
```

## ⚙️ Configuration

### Quality Thresholds
Configure in `config/config.yaml`:
```yaml
quality_assessment:
  excellent_threshold: 0.85
  good_threshold: 0.75
  acceptable_threshold: 0.65
```

### Caching Settings
```yaml
caching:
  search_results_ttl: 604800  # 7 days
  content_cache_ttl: 2592000  # 30 days
  affinities_cache_ttl: 86400 # 1 day
```

## 🔧 Development

### Code Style
```bash
# Format code
black src/ tools/ tests/

# Lint code  
flake8 src/ tools/ tests/

# Type checking
mypy src/ tools/
```

### Testing
```bash
# Run tests
pytest

# With coverage
pytest --cov=src --cov-report=html
```

## 🏭 Production Deployment

### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Environment Variables
```bash
export OPENAI_API_KEY="your_key"
export GEMINI_API_KEY="your_key" 
export BRAVE_SEARCH_API_KEY="your_key"
export LOG_LEVEL="INFO"
```

## 📚 API Reference

### Core Classes

#### `AffinityPipeline`
```python
async def process_destination(destination: str) -> Dict[str, Any]
```

#### `AffinityQualityScorer`
```python
def score_affinities(affinities: Dict, destination: str) -> Dict[str, Any]
```

#### `QualityAssuranceFlow`
```python
def submit_for_review(affinities: Dict, quality_score: float, destination: str) -> Dict[str, Any]
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔮 Roadmap

### Short Term
- [ ] Real-time dashboard updates
- [ ] PDF export functionality
- [ ] Advanced filtering and search
- [ ] Multi-language support

### Long Term  
- [ ] Machine learning recommendations
- [ ] Mobile application
- [ ] Predictive analytics
- [ ] AR/VR integration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/calebcarter001/SmartDestinationThemes/issues)
- **Documentation**: Check the `DASHBOARD_README.md` for detailed dashboard info
- **Wiki**: [GitHub Wiki](https://github.com/calebcarter001/SmartDestinationThemes/wiki)

---

**Made with ❤️ by the SmartDestinationThemes Team**

*Transforming travel planning through intelligent destination analysis* 