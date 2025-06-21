# SmartDestinationThemes Processing Modes Guide

This guide documents all the available processing modes and configuration combinations for the SmartDestinationThemes system.

## 🎯 Processing Mode Matrix

| Mode | Themes | Nuances | Images | Session Type | Use Case |
|------|--------|---------|--------|--------------|----------|
| **Full Processing** | ✅ | ✅ | ✅ | `session_agent_*` | Complete destination intelligence |
| **Theme-Only** | ✅ | 🛡️ | ❌ | `session_theme_*` | Theme testing & refinement |
| **Nuance-Only** | 🛡️ | ✅ | ❌ | `session_nuance_*` | Nuance debugging & testing |
| **Themes + Images** | ✅ | 🛡️ | ✅ | `session_agent_*` | Visual content creation |
| **Nuances + Images** | 🛡️ | ✅ | ✅ | `session_agent_*` | Content + visuals without themes |

Legend: ✅ = Generate New | 🛡️ = Preserve Existing | ❌ = Disabled

## 📋 Quick Configuration Reference

### 🎯 Full Processing Mode (Themes + Nuances + Images)
**Best for: Complete destination intelligence processing**

```yaml
processing_mode:
  enable_theme_processing: true
  enable_nuance_processing: true  
  enable_seasonal_images: true
  theme_controls:
    theme_only_mode: false
  nuance_controls:
    nuance_only_mode: false

seasonal_imagery:
  enabled: true
```

**Command:**
```bash
python main.py --destinations "Paris, France"
```

**Expected Output:**
- ✅ 20-30 travel themes with evidence
- ✅ 30+ destination nuances (12 destination + 10 hotel + 10 vacation rental)  
- ✅ 5 seasonal images via DALL-E 3 (spring, summer, autumn, winter, collage)
- ✅ Quality scores: Themes (~0.95), Nuances (~0.80)
- ✅ Processing time: 2-4 minutes per destination

---

### 🎨 Theme-Only Mode
**Best for: Theme system testing, incremental theme updates**

```yaml
processing_mode:
  enable_theme_processing: true
  enable_nuance_processing: false
  enable_seasonal_images: false
  theme_controls:
    theme_only_mode: true
```

**Command:**
```bash
python main.py --destinations "Barcelona, Spain"
```

**Expected Output:**
- ✅ 20-30 fresh themes with full web discovery
- 🛡️ Existing nuances preserved and copied for dashboard
- ❌ No image generation
- ✅ Quality scores: Themes (~0.97)
- ✅ Processing time: 1-2 minutes per destination

---

### 🎯 Nuance-Only Mode  
**Best for: Nuance system debugging, accommodation insights**

```yaml
processing_mode:
  enable_theme_processing: false
  enable_nuance_processing: true
  enable_seasonal_images: false
  nuance_controls:
    nuance_only_mode: true
```

**Command:**
```bash
python main.py --destinations "Tokyo, Japan"
```

**Expected Output:**
- 🛡️ Existing themes preserved and copied for dashboard
- ✅ 30+ fresh nuances via multi-LLM generation (OpenAI + Gemini + Anthropic)
- ❌ No image generation
- ✅ Quality scores: Nuances (~0.80)
- ✅ Processing time: 15-30 seconds per destination

---

## 🛠️ Advanced Configuration Options

### 🔄 Incremental Processing Controls

```yaml
processing_mode:
  # Theme incremental processing
  theme_controls:
    force_theme_regeneration: false    # Use incremental updates
    preserve_theme_files: false       # Allow updates
    
  # Nuance incremental processing  
  nuance_controls:
    force_nuance_regeneration: false  # Use incremental updates
    preserve_nuance_files: false      # Allow updates
```

### 🎨 Seasonal Image Configuration

```yaml
seasonal_imagery:
  enabled: true
  model: "dall-e-3"
  image_size: "1024x1024"
  quality: "standard"                 # or "hd"
  parallel_generation: true
  create_collage: true
  
  season_prompts:
    spring: "soft cherry blossoms, pastel light, fresh blooms"
    summer: "vibrant colors, lively festivals, sunny skies"
    autumn: "golden leaves, warm evening glow, harvest colors"
    winter: "snow-covered streets, twinkling lights, cozy atmosphere"
```

### 🧹 Cleanup & Preservation Patterns

```yaml
processing_mode:
  cleanup_controls:
    patterns_to_preserve:
      - "*_enhanced.json"              # Preserve theme files
      - "*_nuances.json"               # Preserve nuance files
    patterns_to_clean:
      - "*_old_*.json"                 # Clean old backup files
```

## 📊 Processing Performance Matrix

| Mode | Processing Time | Memory Usage | API Calls | Quality Score |
|------|----------------|--------------|-----------|---------------|
| **Full Processing** | 2-4 min | High | ~50-100 | 0.85-0.95 |
| **Theme-Only** | 1-2 min | Medium | ~30-50 | 0.90-0.97 |
| **Nuance-Only** | 15-30 sec | Low | ~10-20 | 0.75-0.85 |
| **Images-Only** | 1-2 min | Medium | ~5-10 | N/A |

## 🎛️ Command Line Options

### Basic Usage
```bash
# Single destination - full processing
python main.py --destinations "Rome, Italy"

# Multiple destinations
python main.py --destinations "Paris, France" "Tokyo, Japan" "New York, USA"

# With explicit seasonal images
python main.py --destinations "Santorini, Greece" --seasonal-images

# Without opening browser
python main.py --destinations "London, UK" --no-browser
```

### Export Integration
```bash
# Process and export immediately
python main.py --destinations "Venice, Italy"
python export_data.py --destination "Venice, Italy" --format structured

# Bulk export after processing
python export_data.py --all --format json
```

## 📁 Session Directory Structure

### Full Processing Session (`session_agent_*`)
```
outputs/session_agent_20250620_121036/
├── dashboard/
│   ├── index.html                    # Multi-destination index
│   └── destination_name.html         # Individual destination page
├── json/
│   ├── destination_enhanced.json     # Theme data
│   ├── destination_evidence.json     # Theme evidence  
│   ├── destination_nuances.json      # Nuance data
│   └── destination_nuances_evidence.json # Nuance evidence
└── images/                          # (Created in orchestrator session)
    └── destination_name/
        ├── spring.jpg
        ├── summer.jpg
        ├── autumn.jpg
        ├── winter.jpg
        └── seasonal_collage.jpg
```

### Theme-Only Session (`session_theme_*`)
```
outputs/session_theme_20250620_115304/
├── dashboard/
│   └── destination_name.html
├── json/
│   ├── destination_enhanced.json     # NEW theme data
│   ├── destination_evidence.json     # NEW theme evidence
│   ├── destination_nuances.json      # COPIED from existing
│   └── destination_nuances_evidence.json # COPIED from existing
```

### Nuance-Only Session (`session_nuance_*`)  
```
outputs/session_nuance_20250620_103048/
├── dashboard/
│   └── destination_name.html
├── json/
│   ├── destination_enhanced.json     # COPIED from existing
│   ├── destination_evidence.json     # COPIED from existing
│   ├── destination_nuances.json      # NEW nuance data
│   └── destination_nuances_evidence.json # NEW nuance evidence
```

## 🎯 Use Case Scenarios

### 🚀 Production Deployment
**Goal:** Generate complete destination intelligence
```yaml
# Full processing with all components
enable_theme_processing: true
enable_nuance_processing: true  
enable_seasonal_images: true
```

### 🧪 Development & Testing
**Goal:** Test specific components in isolation
```yaml
# Theme development
enable_theme_processing: true
enable_nuance_processing: false
enable_seasonal_images: false
theme_only_mode: true
```

### 🔧 Debugging & Troubleshooting  
**Goal:** Isolate issues in specific subsystems
```yaml
# Nuance debugging
enable_theme_processing: false
enable_nuance_processing: true
enable_seasonal_images: false
nuance_only_mode: true
```

### 📊 Content Creation Pipeline
**Goal:** Generate visual content for existing data
```yaml
# Add images to existing themes/nuances
enable_theme_processing: false
enable_nuance_processing: false
enable_seasonal_images: true
```

### 🔄 Incremental Updates
**Goal:** Update specific data types without full regeneration
```yaml
# Incremental theme updates
enable_theme_processing: true
enable_nuance_processing: true
theme_controls:
  force_theme_regeneration: false
nuance_controls:
  force_nuance_regeneration: false
```

## 🎨 Multi-LLM Integration

The system supports multiple AI models for enhanced quality:

### Theme Generation
- **Primary:** Gemini 2.0 Flash (fast, high-quality)
- **Fallback:** OpenAI GPT-4o-mini
- **Enhancement:** Citation extraction & validation

### Nuance Generation  
- **Multi-LLM Consensus:** OpenAI GPT-4o-mini + Gemini 2.0 Flash + Anthropic Claude 3 Haiku
- **Validation:** Brave Search API with evidence collection
- **Quality Scoring:** Multi-factor scoring with source authority weighting

### Image Generation
- **DALL-E 3:** Professional travel photography prompts
- **Seasons:** Spring, Summer, Autumn, Winter + Collage
- **Quality:** 1024x1024 standard or HD quality

## 📈 Quality Metrics & Benchmarks

### Expected Quality Scores
- **Themes:** 0.90-0.97 (Excellent)
- **Nuances:** 0.75-0.85 (Good to Excellent) 
- **Evidence:** 70-120 pieces per destination
- **Images:** Professional quality DALL-E 3 output

### Performance Benchmarks
- **Web Discovery:** 6-8 high-authority sources per destination
- **LLM Processing:** 95%+ cache hit rate for repeated processing
- **Multi-LLM Consensus:** 85%+ agreement between models
- **Search Validation:** 90%+ evidence validation success

## 🔄 Session Consolidation & Export

The system includes advanced data management capabilities:

### Session Consolidation
- **Cross-session data merging** with quality-based selection
- **Versioned caching** with SHA256 integrity checking  
- **Incremental processing** with smart data preservation

### Export System
- **Structured exports** with separate theme/nuance/evidence files
- **JSON exports** with complete consolidated data
- **Schema validation** with JSON schemas included
- **Image manifests** with metadata and integrity checking

### Enhanced Caching
- **Redis-based persistent caching** with TTL management
- **Version tracking** with diff calculation
- **Export caching** for faster repeated exports

## 📚 Additional Resources

- **Main README:** [README.md](README.md) - System overview and setup
- **Export Guide:** [Export System Documentation](#export-system)
- **Agent Architecture:** [docs/architecture-overview.md](docs/architecture-overview.md)
- **Configuration Reference:** [config/config.yaml](config/config.yaml)

---

**💡 Pro Tip:** Start with theme-only or nuance-only modes for development, then switch to full processing for production deployments! 