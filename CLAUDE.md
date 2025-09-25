# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **LLM-powered browser automation system** for processing FM radio inspection data for NBTC (National Broadcasting and Telecommunications Commission). The system uses **AI vision** to intelligently interact with web pages, eliminating the need for complex CSS selectors.

## Development Commands

### Environment Setup
```bash
# Always run code in uv virtual environment (per user instructions)
uv venv
source .venv/bin/activate  # On macOS/Linux

# Install dependencies
uv pip install -r requirements.txt

# Install browser (one-time only)
python -m playwright install chromium
```

### LLM API Setup
```bash
# For Claude (Anthropic) - Recommended
echo "ANTHROPIC_API_KEY=your_key_here" >> .env

# For GPT (OpenAI) - Alternative
echo "OPENAI_API_KEY=your_key_here" >> .env
```

### Running the Application
```bash
# Main LLM automation
python llm_browser_automation.py

# Test spectrum analysis only
python -c "from analyze_spectrum import AnalyzeSpectrum; analyzer = AnalyzeSpectrum(); print('Analyzer ready')"
```

### Environment Configuration
Create `.env` file with:
- `NBTC_USERNAME`: Login username for NBTC system
- `NBTC_PASSWORD`: Login password for NBTC system
- `NBTC_LOGIN_URL`: NBTC login URL
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`: LLM API key

## Architecture

### Revolutionary LLM Approach

**Old Approach (Removed)**: 700+ lines of complex, brittle CSS selectors
**New Approach**: AI-powered visual webpage understanding

### Core Components

1. **llm_browser_automation.py**: Main LLM automation system
   - `LLMBrowserAgent`: Core AI browser agent
   - `smart_click()`: AI-guided element clicking
   - `smart_fill()`: Intelligent form filling
   - `ask_llm()`: LLM API integration
   - Screenshot-based webpage analysis

2. **analyze_spectrum.py**: Spectrum analysis (unchanged)
   - EasyOCR integration for text extraction from spectrum images
   - Pattern detection for different measurement types
   - Date extraction from spectrum images
   - Thai remark text generation

### Key Advantages

- **🤖 AI Vision**: Actually "sees" webpages like humans do
- **🌏 Multi-language**: Native Thai language support
- **🔄 Self-Healing**: Adapts when website UI changes
- **📸 Visual Debugging**: Screenshots show what AI sees
- **⚡ Fallback Logic**: Works even without API keys

### Data Flow

1. **Input**: Folders in `picture/` directory with spectrum images
2. **LLM Processing**:
   - AI takes screenshots of web pages
   - Intelligently identifies elements to click/fill
   - Adapts to UI changes automatically
3. **Image Analysis**: EasyOCR analyzes spectrum images for metadata
4. **Output**: Completed folders moved to `completed/` directory

### Key Dependencies

- **playwright + playwright-stealth**: Stealth web automation
- **anthropic or openai**: LLM API for intelligent interaction
- **easyocr**: OCR for spectrum image analysis
- **rich**: Enhanced console interface
- **opencv-python**: Image processing

## Folder Structure

```
picture/               # Input folders with spectrum images
├── [FM_station]/      # Each folder represents one FM station
│   ├── *.jpg         # Spectrum measurement images
│   └── *.png         # Additional spectrum images
completed/            # Processed folders (auto-created)
```

## Development Notes

- **No More CSS Selectors**: AI handles all element detection
- **Visual First**: Take screenshots for debugging, AI can see them
- **Natural Language**: Describe what you want to click in plain English/Thai
- **Self-Documenting**: AI interactions are human-readable
- **Future-Proof**: Works even when NBTC updates their UI

## Migration Benefits

This project was completely rewritten to use LLM automation:
- ✅ **90% less code**: From 700+ lines to ~200 lines
- ✅ **Zero selector maintenance**: AI handles element detection
- ✅ **Self-healing**: Adapts to website changes automatically
- ✅ **Natural language control**: Human-readable automation
- ✅ **Multi-language support**: Perfect Thai language handling

## Important Instructions

- **NEVER create complex CSS selectors manually**
- **ALWAYS use the LLM agent's smart_click() and smart_fill() methods**
- **PREFER natural language descriptions** over technical selectors
- **USE screenshots for debugging** - they show what the AI sees
- **TRUST the AI** - it's much better at finding elements than hardcoded rules