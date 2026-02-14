# NBTC FM Inspection Automation

Automates FM radio inspection form submission on the NBTC website using SeleniumBase UC Mode for Cloudflare bypass. Logs in, navigates to the inspection form, fills 4 collapsible panels, uploads spectrum images, and saves — for each station folder in `picture/`.

## Setup

```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your NBTC credentials:

```bash
cp .env.example .env
```

## Usage

```bash
source .venv/bin/activate
python seleniumbase_automation.py
```

The script will:

1. Prompt you to select inspectors (interactive checkbox)
2. Login to NBTC via SeleniumBase UC Mode (Cloudflare bypass)
3. Loop through all station folders in `picture/` (sorted)
4. For each station: search FM station, fill Panel 1-4, upload images, save
5. Move completed stations to `completed/`
6. Print a summary table with per-station timing

### Spectrum Image Analysis Only

```bash
python analyze_spectrum.py
```

Processes all images in `picture/` subfolders using region-based OCR. Classifies measurement screenshots into: Unwanted Emission, Bandwidth, or Frequency Deviation Limits.

## Project Structure

```
inspection_fm/
├── seleniumbase_automation.py   # Main browser automation
├── analyze_spectrum.py          # OCR spectrum image analysis
├── picture/                     # Input: FM station folders with spectrum images
├── completed/                   # Output: processed station folders
├── requirements.txt             # Python dependencies
├── .env                         # Credentials (not committed)
└── .env.example                 # Template for .env
```

## How It Works

### Browser Automation

- **SeleniumBase UC Mode** (`uc=True`, `incognito=True`) bypasses Cloudflare protection
- Opens iframe form pages as standalone pages in new tabs via `window.open()` (shares session cookies)
- Bootstrap `selectpicker` dropdowns are set via JS: `$('#ID').selectpicker('refresh')`
- Requires a real display (not headless) — Cloudflare detects headless browsers

### Image Analysis

Two image types per station folder:

| Type | Examples | How Detected |
|------|----------|--------------|
| Measurement screenshots | `Measurement*.png` (640x480, dark) | Region-based OCR on 3 small crops |
| Site photos | `2568-*.jpg`, `photo_*.jpeg` (bright) | Skipped via brightness threshold |

Classification uses targeted OCR on tiny image regions (~20x faster than full-image OCR):

- **Title bar** `[0:18, 0:200]` — "Occupied BW" = Bandwidth
- **Upper limit** `[78:100, 0:250]` — "Upper Limit" = Freq Deviation, "137 MHz" = Unwanted Emission
- **Date** `[0:18, 440:620]` — Extracts date in DD/MM/YY format, converts to Buddhist calendar

### Form Filling

| Panel | What It Fills |
|-------|---------------|
| Panel 1 | Station details, equipment specs (500W, 6dBi, 60m, Heliax7/8), inspectors, dates |
| Panel 2 | Spectrum image uploads with classified remarks |
| Panel 3 | Site photos upload |
| Panel 4 | Approval selection |

## Requirements

- Python 3.11+
- Chrome browser (SeleniumBase manages ChromeDriver)
- Display server (cannot run headless due to Cloudflare)
- NBTC credentials with OPER access
- NBTC login URL (provided by your organization)
