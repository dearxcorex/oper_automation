# AGENTS.md - NBTC FM Inspection Automation

Python automation that logs into the NBTC website, analyzes FM radio spectrum images via OCR, and fills inspection forms using SeleniumBase UC Mode for Cloudflare bypass.

## Project Structure

```
inspection_fm/
├── seleniumbase_automation.py   # Main browser automation (NBTCSeleniumBaseAgent)
├── analyze_spectrum.py          # OCR spectrum image analysis (AnalyzeSpectrum)
├── picture/                     # Input: FM station folders with spectrum images
├── completed/                   # Output: processed station folders
├── requirements.txt             # Python dependencies (uv)
├── .env                         # Credentials (NBTC_USERNAME, NBTC_PASSWORD, NBTC_LOGIN_URL)
└── .env.example                 # Template for .env
```

## Environment & Commands

### Setup
```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

### Running
```bash
python seleniumbase_automation.py          # Full automation
python analyze_spectrum.py                 # Spectrum analysis only
```

### Testing
No test framework (no pytest). Verify by running scripts directly:
- `python analyze_spectrum.py` -- processes all images in `picture/`, prints summary
- `python seleniumbase_automation.py` -- runs full end-to-end automation

### Linting / Type Checking
None configured. No linters, formatters, or type checkers.

## Code Style Guidelines

### Imports
Three groups separated by blank lines: (1) standard library, (2) third-party, (3) local.
Call `load_dotenv()` immediately after imports at module level.
Use `try/except ImportError` with boolean flags for optional dependencies.

```python
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from seleniumbase import SB

from analyze_spectrum import AnalyzeSpectrum

load_dotenv()
```

### Naming Conventions
| Element        | Convention   | Examples                                    |
|----------------|-------------|---------------------------------------------|
| Classes        | PascalCase  | `AnalyzeSpectrum`, `NBTCSeleniumBaseAgent`  |
| Functions      | snake_case  | `analyze_spectrum`, `handle_cloudflare`     |
| Variables      | snake_case  | `fm_number`, `picture_files`                |
| Constants      | UPPER_SNAKE | `HAS_ANTHROPIC = True`                      |
| Files          | snake_case  | `analyze_spectrum.py`                       |

### Type Hints
Not used. Do not add type hints unless explicitly requested.

### Strings
Use f-strings exclusively. No `.format()` or `%` formatting.

### File Paths
Use `pathlib.Path` for all path operations. Convert with `str(path)` when needed.

### Comments
**Do not add comments** unless explicitly requested. Use descriptive names instead.
Docstrings are acceptable for classes and complex methods.

### Shebang
Include `#!/usr/bin/env python3` at the top of executable scripts.

### Environment Variables
Load with `python-dotenv`. Access via `os.getenv("KEY")`.
Never commit `.env` -- use `.env.example` as the template.

### Error Handling
Wrap operations in `try/except Exception`. Return `False` on failure.
Chain calls with early-return-on-failure in orchestrator methods.

```python
try:
    # operation
    self.log("Success message", "green")
    return True
except Exception as e:
    self.log(f"Operation failed: {e}", "red")
    return False

# Orchestrator pattern
def run_automation(self, fm_folder):
    if not self.login(sb):
        return False
    if not self.navigate_to_fm_standards(sb):
        return False
```

### Logging
Use `rich.Console` with timestamped output. Color by severity.
`analyze_spectrum.py` uses plain `print()` instead.

```python
def log(self, message, style="white"):
    timestamp = time.strftime("%H:%M:%S")
    self.console.print(f"[{timestamp}] {message}", style=style)
```

| Style      | Use for                    |
|------------|----------------------------|
| `"cyan"`   | Info, starting operations  |
| `"green"`  | Success                    |
| `"yellow"` | Warnings, Cloudflare       |
| `"red"`    | Errors                     |

## SeleniumBase Patterns

### UC Mode Configuration
```python
with SB(uc=True, test=True, incognito=True, locale="th", headless=False) as sb:
```
- Always `uc=True` for Cloudflare bypass
- Always `incognito=True` for anti-detection
- Never `headless=True` (detectable by Cloudflare)

### Navigation & CAPTCHA
- `sb.uc_open_with_reconnect(url, reconnect_time)` for stealth navigation
- `sb.uc_gui_click_captcha()` for automatic CAPTCHA solving

### Iframe Handling
```python
sb.switch_to_frame("iframe#selector")
# ... interact with elements inside iframe ...
sb.switch_to_default_content()
```

### Selectors
- Use CSS selectors with SeleniumBase methods
- Use `:contains("text")` pseudo-selector for text matching (supports Thai)
- SeleniumBase auto-detects CSS vs XPath
- Example: `sb.click('a:contains("บันทึก")')`

### Waits
- `sb.wait_for_element("selector")` before interacting
- `sb.wait_for_element_clickable("selector")` before clicking
- `time.sleep()` for hard waits when needed (Cloudflare timing)

## Image Analysis Patterns

### OCR Pipeline
- EasyOCR with English reader: `easyocr.Reader(['en'])`
- OpenCV (`cv2`) for image loading
- Regex for pattern detection in OCR text

### Spectrum Pattern Types
| Pattern                     | Detection Keywords                          |
|-----------------------------|---------------------------------------------|
| Unwanted Emission           | `Center:`, `Stop:`, `Start:` with specific MHz |
| Bandwidth                   | `Occupied BW`, `N dB:`, `OBW:`             |
| Frequency Deviation Limits  | `Upper Limit:`                              |

### Date Handling
- Dates extracted from images in `DD/MM/YY` format via regex
- Converted to Buddhist calendar: `DDMM2{YY+543}` for form submission
- Persisted across images via `self.current_date` (images without dates inherit the last found date)

## Multi-language Notes
- Web UI interaction uses Thai text (navigation links, button labels, form fields)
- Log messages use English with emoji prefixes
- OCR runs in English mode only
