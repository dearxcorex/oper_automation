# AGENTS.md - Development Guidelines for NBTC FM Inspection Automation

## Environment & Build Commands

### Setup
```bash
# Always use uv virtual environment
uv venv
source .venv/bin/activate  # macOS/Linux

# Install dependencies
uv pip install -r requirements.txt
```

### Running the Application
```bash
# Main SeleniumBase UC Mode automation
python seleniumbase_automation.py

# Test spectrum analysis only
python analyze_spectrum.py

# Quick test SeleniumBase is ready
python -c "from seleniumbase import SB; sb = SB(uc=True); print('SB ready')"
```

### Running Tests
This project does not use pytest. Tests are run by directly executing the main scripts:
- Run `python analyze_spectrum.py` for spectrum analysis testing
- Run `python seleniumbase_automation.py` for full automation testing

### No Linting/Type Checking
This project has no configured linting or type checking tools.

## Code Style Guidelines

### Imports
- Standard library imports first (os, time, base64, pathlib)
- Third-party imports second (playwright, anthropic, openai, easyocr, cv2)
- Use `try/except ImportError` for optional dependencies
- Import `load_dotenv()` and call it immediately after imports

```python
# Standard library
import os
import time
import base64
from pathlib import Path

# Third-party
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Optional imports
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

load_dotenv()
```

### Classes
- Use PascalCase for class names
- Use descriptive names that reflect functionality
- Include docstring under class definition

```python
class AnalyzeSpectrum:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        self.current_date = None
```

### Functions & Methods
- Use snake_case for function/method names
- Methods that perform actions should be verbs (e.g., `smart_click`, `analyze_spectrum`)
- Methods that return booleans often start with `is_` or `has_`
- Use descriptive names that indicate what the function does

```python
def smart_click(self, description):
    def analyze_spectrum(self, image_path):
    def setup_llm(self):
```

### Constants
- Use UPPERCASE with underscores for module-level constants
- Use descriptive names that indicate boolean flags or configuration values

```python
HAS_ANTHROPIC = True
HAS_OPENAI = False
```

### Variables
- Use snake_case for all variables
- Use descriptive names that indicate purpose
- Prefer `self.attribute_name` over abbreviations

```python
self.username = os.getenv("NBTC_USERNAME")
screenshot_path = f"{name}.png"
fm_number = Path(fm_folder).name
```

### Type Hints
- Not used in this codebase
- Do not add type hints unless explicitly requested

### Docstrings
- Include docstrings for classes and complex methods
- Keep them brief and descriptive
- Triple-quoted strings with consistent indentation

```python
class NBTCBrowserUseAgent:
    """LLM-powered browser agent for NBTC automation"""

    def smart_click(self, description):
        """Use LLM to find and click elements intelligently"""
```

### Error Handling
- Use `try/except` blocks for operations that may fail
- Log/print errors with context
- Return `False` or `None` on failure when appropriate
- Use specific exception types when possible

```python
try:
    self.playwright = sync_playwright().start()
    # ... operations ...
except Exception as e:
    self.log(f"❌ Browser setup failed: {e}", "red")
    return False
```

### Logging & Output
- Use `rich.Console` for colored, formatted console output
- Create a `log()` method that adds timestamps
- Use emoji indicators for different log levels:
  - 🚀 Starting/Initializing
  - ✅ Success
  - ⚠️ Warning/Fallback
  - ❌ Error
  - 🛡️ Cloudflare/CAPTCHA handling
- Include timestamps in logs: `[HH:MM:SS]`

```python
from rich.console import Console

def log(self, message, style="white"):
    timestamp = time.strftime("%H:%M:%S")
    self.console.print(f"[{timestamp}] {message}", style=style)

# Usage
self.log("🚀 Starting SeleniumBase automation...", "cyan")
self.log("✅ Login successful", "green")
self.log("🛡️ Cloudflare bypassed", "yellow")
```

### String Formatting
- Use f-strings for all string interpolation
- Do not use `.format()` or `%` formatting
- Keep f-string expressions simple

```python
fm_number = Path(fm_folder).name
self.log(f"📻 Processing FM station: {fm_number}", "cyan")
```

### File Paths
- Use `pathlib.Path` for all path operations
- Convert paths to strings when needed with `str(path)`
- Use Path methods like `.exists()`, `.name`, `.glob()`

```python
from pathlib import Path

picture_dir = Path("picture")
fm_number = Path(fm_folder).name
screenshot_path = Path("current_page.png")
```

### Environment Variables
- Use `python-dotenv` for loading `.env` files
- Call `load_dotenv()` immediately after imports
- Use `os.getenv()` to retrieve values
- Provide default values where appropriate

```python
from dotenv import load_dotenv

load_dotenv()

self.username = os.getenv("NBTC_USERNAME")
self.password = os.getenv("NBTC_PASSWORD")
```

### Comments
- **DO NOT add any comments** unless explicitly requested
- Use descriptive variable and function names instead
- Docstrings are acceptable for classes and complex methods

### Shebang
- Include shebang at the top of main executable scripts
- Use `#!/usr/bin/env python3` for maximum portability

```python
#!/usr/bin/env python3
```

### Special Patterns

#### SeleniumBase UC Mode
- Always use `SB(uc=True)` for Cloudflare bypass
- Use `uc_open_with_reconnect()` for stealth navigation
- Use `uc_gui_click_captcha()` for automatic CAPTCHA solving
- Enable `incognito=True` for better anti-detection
- Never use `headless=True` with UC Mode (detectable)

#### Browser Automation
- Use SeleniumBase methods for all browser interactions
- Work in iframes with `.switch_to_frame()` and `.switch_to_default_content()`
- Use `:contains()` pseudo-selector for text matching
- Wait for elements with `wait_for_element()` and `wait_for_clickable()`
- Handle Cloudflare automatically with `uc_gui_click_captcha()`

#### Image Analysis
- Use EasyOCR for text extraction from images
- Use OpenCV (cv2) for image processing
- Use regex for pattern matching in extracted text
- Support Thai language in OCR when needed

#### Class Initialization
- Initialize `Console()` and other resources in `__init__`
- Use lazy initialization for expensive operations
- Store optional dependencies with flags (e.g., `HAS_ANTHROPIC`)

## Project-Specific Notes

### Selectors
- Use direct CSS selectors with SeleniumBase methods
- Use `:contains()` pseudo-selector for text matching (supports Thai)
- SeleniumBase automatically detects between CSS and XPath
- Keep selectors simple and direct
- Example: `self.sb.click('button:contains("Login")')`

### Multi-language Support
- Natural language strings in both English and Thai
- Thai text in user-facing messages and web page descriptions
- OCR supports English primarily

### Debugging
- Use screenshots extensively - they show what AI sees
- Keep browser open temporarily for inspection after operations
- Log all operations with timestamps and status indicators

### File Structure
- Input folders in `picture/` directory
- Completed folders moved to `completed/` directory
- Each folder represents one FM station with spectrum images
