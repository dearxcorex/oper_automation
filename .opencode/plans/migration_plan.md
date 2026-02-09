# Migration Plan: Playwright → SeleniumBase for Cloudflare Bypass

## Executive Summary

Migrate from Playwright to SeleniumBase with UC Mode to bypass Cloudflare detection and human verification. The refactoring will:
- Replace Playwright with SeleniumBase (UC Mode)
- Remove LLM integration (Claude/OpenAI)
- Implement automatic CAPTCHA solving
- Keep spectrum analysis module unchanged
- Simplify code by using SeleniumBase's built-in methods

---

## Current Architecture

### Existing Files
1. **analyze_spectrum.py** - Spectrum image analysis (KEEP UNCHANGED)
2. **browser_use_automation.py** - browser-use AI library (DEPRECATED)
3. **llm_browser_automation.py** - Playwright + LLM integration (TO BE REPLACED)

### Current Dependencies
```
playwright==1.55.0
playwright-stealth==2.0.0
anthropic>=0.68.0  # Claude API
openai>=1.0.0      # GPT API
easyocr==1.7.2      # Image analysis (KEEP)
opencv-python==4.10.0.84
rich==13.9.4
python-dotenv==1.0.1
```

---

## Target Architecture

### New File Structure
```
inspection_fm/
├── analyze_spectrum.py              # KEEP UNCHANGED
├── seleniumbase_automation.py     # NEW - Main automation
├── requirements.txt                # UPDATED
├── .env                          # KEEP (add SeleniumBase options)
├── AGENTS.md                     # UPDATED
└── picture/                      # KEEP
```

### New Dependencies
```
seleniumbase                      # Core framework
easyocr==1.7.2                  # KEEP (spectrum analysis)
opencv-python==4.10.0.84          # KEEP
numpy                             # KEEP
torch                             # KEEP (for EasyOCR)
pillow                            # KEEP
rich==13.9.4                      # KEEP
python-dotenv==1.0.1               # KEEP
```

### Removed Dependencies
```
playwright==1.55.0               # REMOVE
playwright-stealth==2.0.0         # REMOVE
anthropic>=0.68.0                # REMOVE
openai>=1.0.0                    # REMOVE
```

---

## Migration Steps

### Phase 1: Setup & Dependencies (Estimated: 15 min)

**Tasks:**
1. Update `requirements.txt`
2. Uninstall Playwright dependencies
3. Install SeleniumBase
4. Remove Playwright browser installation

**Commands:**
```bash
# Uninstall Playwright
pip uninstall playwright playwright-stealth anthropic openai -y

# Install SeleniumBase
uv pip install seleniumbase

# Verify installation
seleniumbase --help
```

**Files to Modify:**
- `requirements.txt` - Replace Playwright with SeleniumBase

---

### Phase 2: Create New Automation Script (Estimated: 2-3 hours)

**Create:** `seleniumbase_automation.py`

**Core Components:**

#### 1. Class Structure
```python
from seleniumbase import SB
from dotenv import load_dotenv
from rich.console import Console
from analyze_spectrum import AnalyzeSpectrum

class NBTCSeleniumBaseAgent:
    """SeleniumBase UC Mode automation for NBTC FM inspection"""
```

#### 2. Initialization
```python
def __init__(self):
    self.console = Console()
    self.username = os.getenv("NBTC_USERNAME")
    self.password = os.getenv("NBTC_PASSWORD")
    self.login_url = os.getenv("NBTC_LOGIN_URL")
    self.analyzer = AnalyzeSpectrum()
    self.sb = None  # Will be initialized with UC Mode
```

#### 3. SeleniumBase UC Mode Setup
```python
def initialize_browser(self):
    """Initialize SeleniumBase with UC Mode for Cloudflare bypass"""
    self.sb = SB(
        uc=True,           # Undetected-Chromedriver Mode
        test=True,         # Enable test features
        incognito=True,     # Use incognito for better stealth
        locale="th",       # Thai locale
        headless=False     # Show browser (UC Mode detectable in headless)
    )
    self.log("✅ SeleniumBase UC Mode initialized", "green")
    return True
```

#### 4. Cloudflare Auto-Handling
```python
def handle_cloudflare(self):
    """Automatically handle Cloudflare challenges"""
    try:
        # Check for Cloudflare elements
        if self.sb.is_element_visible("div.cf-browser-verification"):
            self.log("🛡️ Cloudflare detected, solving...", "yellow")
            self.sb.uc_gui_click_captcha()  # Auto-solve CAPTCHA
            self.sb.sleep(3)
            self.log("✅ Cloudflare bypassed", "green")
        return True
    except Exception as e:
        self.log(f"⚠️ Cloudflare handling: {e}", "yellow")
        return True  # Continue anyway
```

#### 5. Login Flow (No LLM)
```python
def login(self):
    """Login to NBTC using SeleniumBase methods"""
    try:
        self.log("🔐 Logging in...", "cyan")

        # Navigate to login
        self.sb.uc_open_with_reconnect(self.login_url, reconnect_time=3)
        self.sb.sleep(2)

        # Handle Cloudflare
        self.handle_cloudflare()

        # Fill login form (using SeleniumBase built-in methods)
        self.sb.type("#UserName", self.username)
        self.sb.type("#Password", self.password)
        self.sb.click("#bLogin")  # Login button

        # Wait for success
        self.sb.sleep(3)
        self.sb.wait_for_element('a.nbtcros-sectionpage--item', timeout=15)

        self.log("✅ Login successful", "green")
        return True
    except Exception as e:
        self.log(f"❌ Login failed: {e}", "red")
        return False
```

#### 6. Navigation (Direct Selectors)
```python
def navigate_to_fm_standards(self):
    """Navigate to FM standards page"""
    try:
        self.log("🧭 Navigating to FM standards...", "cyan")

        # Click FM operations section
        self.sb.wait_for_clickable('a.nbtcros-sectionpage--item[onclick*="Oper"]')
        self.sb.click('a.nbtcros-sectionpage--item[onclick*="Oper"]')
        self.sb.sleep(2)

        # Click frequency inspection (Thai text)
        self.sb.click('a:contains("งานตรวจสอบคลื่นความถี่")')
        self.sb.sleep(2)

        # Click standards submenu
        self.sb.click('a:contains("4.การตรวจสอบมาตรฐานการแพร่")')
        self.sb.sleep(2)

        self.log("✅ Navigation complete", "green")
        return True
    except Exception as e:
        self.log(f"❌ Navigation failed: {e}", "red")
        return False
```

#### 7. Add FM Station
```python
def add_fm_station(self, fm_number):
    """Add FM station to system"""
    try:
        self.log(f"📻 Adding FM station: {fm_number}", "cyan")

        # Click inspection link
        self.sb.click('a:contains("การตรวจสอบมาตรฐานการแพร่")')
        self.sb.sleep(2)

        # Click plus button
        self.sb.click(".iso-icon--plus")
        self.sb.sleep(2)

        # Click primary add button
        self.sb.click('button:contains("เพิ่ม")')
        self.sb.sleep(3)

        # Handle iframe
        iframe = self.sb.switch_to_frame("iframe")  # Or use selector
        if iframe:
            self.sb.select_option("#StnTypeID", index=8)  # FM station
            self.sb.type("#SiteCode", fm_number)
            self.sb.select_option("#SrcData", index=1)  # Source data
            self.sb.click(".iso-icon--search")  # Search button
            self.sb.sleep(3)
            self.sb.click('a:contains("1")')  # First result
            self.log(f"✅ FM station {fm_number} selected", "green")
            return True

        return False
    except Exception as e:
        self.log(f"❌ Add station failed: {e}", "red")
        return False
```

#### 8. Fill Form Details
```python
def fill_station_details(self, pictures_folder):
    """Fill station details form"""
    try:
        self.log("📋 Filling station details...", "cyan")

        # Analyze pictures for date
        picture_files = list(Path(pictures_folder).glob("*.[jJ][pP][gG]"))
        pattern_type, date_text = self.analyzer.analyze_spectrum(str(picture_files[0]))

        # Convert to Buddhist calendar
        day, month, year = date_text[0].split("/")
        buddhist_year = int(year) + 543
        formatted_date = f"{day.zfill(2)}{month.zfill(2)}2{buddhist_year}"

        # Expand all panels
        for panel_id in [1, 2, 3, 4]:
            self.sb.click(f'button[onclick="togglePanel({panel_id})"]')

        # Fill station details
        self.sb.select_option('select[name="AntennaPlacement"]', index=1)
        self.sb.select_option('select[name="AntennaFound"]', index=1)
        self.sb.type("#FreqMhz", self.sb.get_attribute("#FreqMhz", "value"))  # Copy
        self.sb.select_option('select[name="AntennaType"]', index=1)
        self.sb.select_option('select[name="CableType"]', index=5)
        self.sb.type("#Power", "500")
        self.sb.type("#Gain", "6")
        self.sb.type("#Height", "60")

        # Add frequency patterns (3 times)
        for i in range(3):
            self.sb.click('button[onclick="editFqItem(0)"]')
            self.sb.select_option('#FreqPatternType', index=i)
            self.sb.select_option('#FreqResult', index=1)
            self.sb.click('button:contains("บันทึก")')

        # Add pictures
        for idx, pic_file in enumerate(picture_files):
            self.sb.click('button[onclick="editItem(0)"]')
            self.sb.select_option('#PictureType', index=idx)
            self.sb.choose_file('#PictureUpload', str(pic_file))
            self.sb.type("#PictureRemark", self.analyzer.get_remark_text(pattern_type))
            self.sb.click('button:contains("บันทึก")')

        # Fill inspection opinion
        self.sb.select_option('#Opinion', index=1)
        self.sb.type("#Remark", "ปฏิบัติตามหลักเกณฑ์")

        # Add equipment
        self.sb.click('button[onclick="editItemEqu(0)"]')
        self.sb.select_option('#EquipmentType', index=10)
        self.sb.select_option('#Equipment', index=3)
        self.sb.click('button:contains("บันทึก")')

        # Set dates
        self.sb.type("#DtTest", formatted_date)
        self.sb.type("#DtTest2", formatted_date)
        self.sb.click('.calendar-day.active')

        # Set inspectors
        self.sb.select_option('#ChkAuthID_1', index=6)
        self.sb.select_option('#ChkAuthID_2', index=16)
        self.sb.select_option('#ChkAuthID_3', index=11)
        self.sb.select_option('#ApvNaID', index=1)

        # Save form
        self.sb.click("#bSave")
        self.sb.wait_for_element_visible('button:contains("ตกลง")', timeout=5)
        self.sb.click('button:contains("ตกลง")')

        self.log("✅ Details filled successfully", "green")
        return True
    except Exception as e:
        self.log(f"❌ Fill details failed: {e}", "red")
        return False
```

#### 9. Main Workflow
```python
def run_automation(self, fm_folder):
    """Run complete automation workflow"""
    try:
        fm_number = Path(fm_folder).name

        self.console.print("🤖 SELENIUMBASE UC MODE AUTOMATION", style="bold green")
        self.console.print(f"📁 Processing: {fm_number}", style="green")
        self.console.print("🛡️ Cloudflare bypass enabled", style="green")
        self.console.print("🤖 Auto CAPTCHA solving", style="green")

        with self.sb:
            # Initialize and login
            if not self.login():
                return False

            # Navigate
            if not self.navigate_to_fm_standards():
                return False

            # Add station
            if not self.add_fm_station(fm_number):
                return False

            # Fill details
            if not self.fill_station_details(fm_folder):
                return False

        self.console.print("✅ AUTOMATION SUCCESS!", style="bold green")
        return True

    except Exception as e:
        self.log(f"❌ Automation failed: {e}", "red")
        return False
```

---

### Phase 3: Update Configuration (Estimated: 10 min)

**Update:** `.env`

```bash
# NBTC Credentials (existing)
NBTC_USERNAME=your_username
NBTC_PASSWORD=your_password
NBTC_LOGIN_URL=https://your-login-url.com

# SeleniumBase Options (new)
SELENIUMBASE_UC_MODE=True
SELENIUMBASE_LOCALE=th
SELENIUMBASE_HEADLESS=False
```

**Update:** `.gitignore`

```bash
# Add SeleniumBase logs
latest_logs/
archived_logs/
dashboard.html
```

---

### Phase 4: Update Documentation (Estimated: 30 min)

**Update:** `AGENTS.md`

**Key Sections:**
1. Replace Playwright commands with SeleniumBase
2. Update setup instructions
3. Remove LLM integration guidelines
4. Add UC Mode configuration options
5. Add Cloudflare handling patterns
6. Update code style examples

**Key Changes:**
```markdown
### Running the Application
```bash
# Main SeleniumBase automation
python seleniumbase_automation.py

# Test spectrum analysis only
python analyze_spectrum.py

# Quick test SeleniumBase is ready
python -c "from seleniumbase import SB; sb = SB(uc=True); print('SB ready')"
```

### Installation
```bash
uv pip install seleniumbase
# (No browser installation needed - auto-downloads)
```

### Cloudflare Handling
- Use `uc_gui_click_captcha()` for automatic solving
- Use `uc_open_with_reconnect(url, reconnect_time)` for stealth navigation
- Enable `uc=True` and `incognito=True` for better bypass
```

---

### Phase 5: Testing (Estimated: 1-2 hours)

**Test Plan:**

1. **Unit Tests**
   - Test spectrum analysis (unchanged)
   - Test SeleniumBase initialization
   - Test Cloudflare detection

2. **Integration Tests**
   - Test login flow
   - Test navigation
   - Test form filling

3. **End-to-End Tests**
   - Complete automation with test FM folder
   - Verify Cloudflare bypass
   - Verify form submission

**Testing Commands:**
```bash
# Test SeleniumBase setup
python -c "from seleniumbase import SB; sb = SB(uc=True); sb.open('https://google.com'); print('OK')"

# Test automation with demo
python seleniumbase_automation.py --demo

# Test with headful mode (debugging)
python seleniumbase_automation.py --headful

# Test with specific FM folder
python seleniumbase_automation.py picture/FM103.5
```

**Success Criteria:**
- ✅ Cloudflare bypass works automatically
- ✅ Login succeeds without manual intervention
- ✅ Navigation completes to FM standards
- ✅ Form fills and submits correctly
- ✅ No CAPTCHA errors in logs

---

### Phase 6: Cleanup (Estimated: 15 min)

**Tasks:**
1. Remove old files:
   - `browser_use_automation.py`
   - `llm_browser_automation.py`
   - `LLM_AUTOMATION_README.md`

2. Remove old dependencies:
   - Playwright browser binaries
   - Node modules (if any)

3. Clean git history:
   ```bash
   git rm browser_use_automation.py
   git rm llm_browser_automation.py
   git commit -m "Remove Playwright-based automation"
   ```

---

## Key Benefits

### Before (Playwright + LLM)
- ❌ Complex CSS selectors
- ❌ Fails on Cloudflare
- ❌ Requires LLM API costs (~$0.01-0.05/run)
- ❌ Manual CAPTCHA intervention
- ❌ 700+ lines of code

### After (SeleniumBase UC Mode)
- ✅ Simple, direct selectors
- ✅ Automatic Cloudflare bypass
- ✅ No LLM costs
- ✅ Auto CAPTCHA solving
- ✅ ~400 lines of code
- ✅ Better reliability
- ✅ Faster execution

---

## Risk Assessment

### Low Risk
- Removing LLM simplifies code
- SeleniumBase is mature and stable
- UC Mode proven for Cloudflare bypass

### Medium Risk
- Need to verify all selectors work without LLM
- Cloudflare may update detection (ongoing)

### Mitigation
- Thorough testing before production
- Keep Playwright code as fallback for 1-2 weeks
- Monitor Cloudflare bypass effectiveness

---

## Timeline Summary

| Phase | Duration | Priority |
|-------|----------|----------|
| Phase 1: Setup | 15 min | High |
| Phase 2: Create Script | 2-3 hrs | High |
| Phase 3: Config | 10 min | Medium |
| Phase 4: Docs | 30 min | Medium |
| Phase 5: Testing | 1-2 hrs | High |
| Phase 6: Cleanup | 15 min | Low |
| **Total** | **4-6 hrs** | - |

---

## Next Steps

1. **Review this plan** - Confirm approach matches requirements
2. **Backup current code** - Save working Playwright version
3. **Begin Phase 1** - Update dependencies
4. **Create new automation script** - Follow Phase 2 detailed specs
5. **Test thoroughly** - Don't skip Phase 5
6. **Deploy** - Only after successful testing

---

## Questions Before Implementation

1. Should we keep the old Playwright scripts as reference?
2. Do you have a test NBTC account for development?
3. Are there any special form fields not covered in the plan?
4. Should we add retry logic for network failures?
5. Any specific Cloudflare challenges you've seen before?

---

*Ready to begin implementation upon approval.*
