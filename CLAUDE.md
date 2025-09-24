# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python automation system for processing FM radio inspection data for NBTC (National Broadcasting and Telecommunications Commission). The system uses Selenium WebDriver to automate web form submissions and EasyOCR to analyze spectrum images.

## Development Commands

### Environment Setup
```bash
# Always run code in uv virtual environment (per user instructions)
uv venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Install dependencies (including undetected-chromedriver for Cloudflare bypass)
uv pip install -r requirements.txt

# Alternative installation if uv doesn't work:
pip install undetected-chromedriver
```

### Cloudflare Bypass
This project now uses `undetected-chromedriver` to automatically bypass Cloudflare challenges. The system will:
- Automatically detect and handle "Verify you are human" challenges
- Use stealth browsing techniques to avoid detection
- Provide clear status messages during bypass attempts

### Running the Application
```bash
# Main automation script
python main.py

# Test spectrum analysis only
python analyze_spectrum.py
```

### Environment Configuration
- Copy `.env.example` to `.env` (if exists) or create `.env` with:
  - `NBTC_USERNAME`: Login username for NBTC system
  - `NBTC_PASSWORD`: Login password for NBTC system
  - `NBTC_LOGIN_URL`: NBTC login URL

## Architecture

### Core Components

1. **main.py**: Entry point that orchestrates the entire automation workflow
   - Handles progress tracking with Rich console interface
   - Manages folder processing loop
   - Coordinates between automation and analysis modules

2. **oper_fm_automation.py**: Main automation class (`NBTC_Automation`)
   - Selenium WebDriver setup and browser management
   - NBTC website login and navigation
   - Form filling for FM inspection data (`input_fm`, `input_detail_fm`)
   - Image upload and categorization

3. **analyze_spectrum.py**: Spectrum analysis class (`AnalyzeSpectrum`)
   - EasyOCR integration for text extraction from spectrum images
   - Pattern detection for different measurement types:
     - Unwanted Emission (Center/Start/Stop frequency analysis)
     - Bandwidth (OBW detection)
     - Frequency Deviation Limits
   - Date extraction from spectrum images
   - Thai remark text generation based on pattern type

4. **utils.py**: Helper utilities
   - Directory scanning for folders to process
   - Progress summary reporting
   - Completed folder management

### Data Flow

1. **Input**: Folders in `picture/` directory, each containing spectrum images
2. **Processing**:
   - Browser automation logs into NBTC system
   - For each folder: extracts FM station info, analyzes images, fills forms
   - Images analyzed for measurement type and date information
3. **Output**: Completed folders moved to `completed/` directory

### Key Dependencies

- **selenium + webdriver-manager**: Web automation
- **easyocr**: OCR for spectrum image analysis
- **rich**: Enhanced console interface with progress bars
- **opencv-python**: Image processing
- **python-dotenv**: Environment variable management

## Folder Structure

```
picture/               # Input folders with spectrum images
├── [folder_name]/     # Each folder represents one FM station
│   ├── *.jpg         # Spectrum measurement images
│   ├── *.png         # Additional spectrum images
│   └── *.jpeg        # More image formats
completed/            # Processed folders (auto-created)
```

## Development Notes

- The system expects specific Thai text patterns in the NBTC web interface
- Spectrum images must contain readable frequency and measurement data
- Chrome WebDriver is automatically managed via webdriver-manager
- Date format expected: DD/MM/YY in spectrum images
- The system handles iframe navigation for modal dialogs in the web interface
- Error handling includes retry logic for web element interactions