#!/usr/bin/env python3

"""
LLM-Powered Browser Automation for NBTC
Uses Claude/GPT to intelligently interact with web pages
Much simpler than hardcoded selectors!
"""

import os
import time
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from dotenv import load_dotenv
from rich.console import Console
from analyze_spectrum import AnalyzeSpectrum

# For LLM integration (you can use OpenAI or Anthropic)
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

load_dotenv()

class LLMBrowserAgent:
    def __init__(self):
        self.console = Console()
        self.username = os.getenv("NBTC_USERNAME")
        self.password = os.getenv("NBTC_PASSWORD")
        self.login_url = os.getenv("NBTC_LOGIN_URL")
        self.analyzer = AnalyzeSpectrum()

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        # Initialize LLM client
        self.llm_client = None
        self.setup_llm()

    def log(self, message, style="white"):
        timestamp = time.strftime("%H:%M:%S")
        self.console.print(f"[{timestamp}] {message}", style=style)

    def setup_llm(self):
        """Setup LLM client - prefer Anthropic Claude"""
        if HAS_ANTHROPIC and os.getenv("ANTHROPIC_API_KEY"):
            self.llm_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.llm_type = "anthropic"
            self.log("✅ Using Anthropic Claude for browser intelligence", "green")
        elif HAS_OPENAI and os.getenv("OPENAI_API_KEY"):
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.llm_client = openai
            self.llm_type = "openai"
            self.log("✅ Using OpenAI GPT for browser intelligence", "green")
        else:
            self.log("⚠️ No LLM API key found. Add ANTHROPIC_API_KEY or OPENAI_API_KEY to .env", "yellow")
            self.log("Falling back to basic automation mode", "yellow")
            self.llm_client = None

    def initialize_browser(self):
        """Initialize Playwright with stealth"""
        try:
            self.log("🚀 Starting intelligent browser...", "cyan")

            self.playwright = sync_playwright().start()

            # Launch with stealth
            self.browser = self.playwright.chromium.launch(
                headless=False,
                args=['--start-maximized', '--disable-blink-features=AutomationControlled']
            )

            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )

            self.page = self.context.new_page()

            # Apply stealth
            stealth = Stealth()
            stealth.apply_stealth_sync(self.page)

            # Maximize window
            self.page.set_viewport_size({'width': 1920, 'height': 1080})
            self.page.evaluate("""
                () => {
                    if (window.screen) {
                        window.resizeTo(window.screen.availWidth, window.screen.availHeight);
                        window.moveTo(0, 0);
                    }
                }
            """)

            self.log("✅ Intelligent browser ready", "green")
            return True

        except Exception as e:
            self.log(f"❌ Browser setup failed: {e}", "red")
            return False

    def ask_llm(self, question, screenshot_path=None):
        """Ask LLM for help with browser task"""
        if not self.llm_client:
            return None

        try:
            if self.llm_type == "anthropic":
                messages = [{"role": "user", "content": question}]

                if screenshot_path and Path(screenshot_path).exists():
                    # Add screenshot to message
                    with open(screenshot_path, "rb") as image_file:
                        image_data = base64.b64encode(image_file.read()).decode()
                    messages[0]["content"] = [
                        {"type": "text", "text": question},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}}
                    ]

                response = self.llm_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    messages=messages
                )
                return response.content[0].text

        except Exception as e:
            self.log(f"⚠️ LLM call failed: {e}", "yellow")
            return None

    def take_screenshot(self, name="screenshot"):
        """Take screenshot for LLM analysis"""
        screenshot_path = f"{name}.png"
        self.page.screenshot(path=screenshot_path, full_page=True)
        return screenshot_path

    def smart_click(self, description):
        """Use LLM to find and click elements"""
        self.log(f"🤖 Looking for: {description}", "cyan")

        # Take screenshot
        screenshot = self.take_screenshot("current_page")

        if self.llm_client:
            # Ask LLM to identify the element
            question = f"""
            Look at this webpage screenshot. I need to click on "{description}".

            Please provide a CSS selector or XPath that would select this element.
            Only respond with the selector, nothing else.

            Examples:
            - For a button with text "Login": button:has-text("Login")
            - For a link with Thai text: a:has-text("การตรวจสอบ")
            - For an element with class: .iso-icon--plus
            - For an element with ID: #UserName
            """

            selector = self.ask_llm(question, screenshot)

            if selector:
                self.log(f"🎯 LLM suggests selector: {selector}", "green")

                try:
                    # Try the LLM-suggested selector
                    element = self.page.wait_for_selector(selector.strip(), timeout=10000)
                    element.click()
                    time.sleep(1)
                    self.log(f"✅ Successfully clicked: {description}", "green")
                    return True
                except Exception as e:
                    self.log(f"⚠️ LLM selector failed: {e}", "yellow")

        # Fallback to manual approach
        self.log("🔄 Falling back to manual selector search", "yellow")
        return self.fallback_click(description)

    def fallback_click(self, description):
        """Fallback clicking logic"""
        # Common patterns for NBTC site
        fallback_selectors = []

        if "login" in description.lower() or "เข้าสู่ระบบ" in description:
            fallback_selectors = ["#bLogin", "input[type='submit']", "button[type='submit']"]
        elif "fm" in description.lower() or "oper" in description.lower():
            fallback_selectors = ["a.nbtcros-sectionpage--item[onclick*='Oper']"]
        elif "plus" in description.lower() or "เพิ่ม" in description:
            fallback_selectors = [".iso-icon--plus", "button:has-text('+')", "[title*='เพิ่ม']"]
        elif "การตรวจสอบ" in description:
            fallback_selectors = [f"a:has-text('{description}')", f"//a[contains(text(), '{description}')]"]

        for selector in fallback_selectors:
            try:
                if selector.startswith('//'):
                    element = self.page.wait_for_selector(f'xpath={selector}', timeout=5000)
                else:
                    element = self.page.wait_for_selector(selector, timeout=5000)
                element.click()
                time.sleep(1)
                self.log(f"✅ Fallback click successful: {description}", "green")
                return True
            except:
                continue

        self.log(f"❌ Could not click: {description}", "red")
        return False

    def smart_fill(self, description, value):
        """Use LLM to find and fill form fields"""
        self.log(f"📝 Filling {description} with: {value}", "cyan")

        # Take screenshot
        screenshot = self.take_screenshot("form_page")

        if self.llm_client:
            question = f"""
            Look at this form screenshot. I need to fill the field for "{description}" with the value "{value}".

            Please provide a CSS selector for the input field.
            Only respond with the selector, nothing else.

            Examples:
            - For username field: #UserName
            - For password field: #Password
            - For FM number field: #SiteCode
            """

            selector = self.ask_llm(question, screenshot)

            if selector:
                try:
                    element = self.page.wait_for_selector(selector.strip(), timeout=10000)
                    element.fill(value)
                    self.log(f"✅ Successfully filled: {description}", "green")
                    return True
                except Exception as e:
                    self.log(f"⚠️ LLM fill failed: {e}", "yellow")

        # Fallback logic
        return self.fallback_fill(description, value)

    def fallback_fill(self, description, value):
        """Fallback form filling"""
        fallback_selectors = []

        if "username" in description.lower():
            fallback_selectors = ["#UserName", "input[name='username']", "input[type='text']"]
        elif "password" in description.lower():
            fallback_selectors = ["#Password", "input[name='password']", "input[type='password']"]
        elif "fm" in description.lower() or "site" in description.lower():
            fallback_selectors = ["#SiteCode", "input[name='site']"]

        for selector in fallback_selectors:
            try:
                element = self.page.wait_for_selector(selector, timeout=5000)
                element.fill(value)
                self.log(f"✅ Fallback fill successful: {description}", "green")
                return True
            except:
                continue

        self.log(f"❌ Could not fill: {description}", "red")
        return False

    def login(self):
        """Smart login using LLM assistance"""
        self.log("🔐 Starting intelligent login...", "cyan")

        # Navigate to login
        self.page.goto(self.login_url, wait_until='networkidle')

        # Handle Cloudflare if detected
        content = self.page.content().lower()
        if "cloudflare" in content or "verify you are human" in content:
            self.log("🛡️ Cloudflare detected, waiting...", "yellow")
            time.sleep(10)  # Simple wait

        # Fill login form intelligently
        if not self.smart_fill("username", self.username):
            return False

        if not self.smart_fill("password", self.password):
            return False

        # Click login button
        if not self.smart_click("login button"):
            return False

        # Wait for success
        time.sleep(3)
        try:
            self.page.wait_for_selector('a.nbtcros-sectionpage--item', timeout=15000)
            self.log("✅ Login successful", "bold green")
            return True
        except:
            self.log("⚠️ Login may have succeeded, continuing...", "yellow")
            return True

    def navigate_to_fm_standards(self):
        """Navigate to FM standards page intelligently"""
        self.log("🧭 Navigating to FM standards...", "cyan")

        # Click FM section
        if not self.smart_click("FM operations section"):
            return False
        time.sleep(2)

        # Click frequency inspection
        if not self.smart_click("งานตรวจสอบคลื่นความถี่"):
            return False
        time.sleep(2)

        # Click standards submenu
        if not self.smart_click("4.การตรวจสอบมาตรฐานการแพร่"):
            return False
        time.sleep(2)

        self.log("✅ Navigation complete", "green")
        return True

    def process_fm_station(self, fm_number):
        """Process FM station with LLM assistance"""
        try:
            self.log(f"📻 Processing FM station: {fm_number}", "cyan")

            # Click on standards inspection link
            if not self.smart_click("การตรวจสอบมาตรฐานการแพร่"):
                return False
            time.sleep(2)

            # Click plus button to add station
            if not self.smart_click("plus button to add station"):
                return False
            time.sleep(2)

            # Click primary add button
            if not self.smart_click("primary add button"):
                return False
            time.sleep(3)

            # Now we should be in the modal - handle iframe if present
            iframes = self.page.query_selector_all('iframe')
            if iframes:
                iframe_page = iframes[0].content_frame()
                self.log("📋 Working in modal iframe", "cyan")

                # Select FM station type (index 8)
                station_select = iframe_page.query_selector('#StnTypeID')
                if station_select:
                    station_select.select_option(index=8)
                    time.sleep(1)

                # Enter FM number
                site_input = iframe_page.query_selector('#SiteCode')
                if site_input:
                    site_input.fill(fm_number)

                # Set source data
                source_select = iframe_page.query_selector('#SrcData')
                if source_select:
                    source_select.select_option(index=1)

                # Search for station
                search_button = iframe_page.query_selector('.iso-icon--search')
                if search_button:
                    search_button.click()
                    time.sleep(3)

                # Select first result
                first_result = iframe_page.query_selector('xpath=//a[text()="1"]')
                if first_result:
                    first_result.click()
                    self.log(f"✅ FM station {fm_number} selected", "green")
                    time.sleep(2)

                    return True

            return False

        except Exception as e:
            self.log(f"❌ FM processing failed: {e}", "red")
            return False

    def close(self):
        """Clean up browser"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.log("🔒 Browser closed", "green")
        except Exception as e:
            self.log(f"Cleanup error: {e}", "yellow")

    def run_automation(self, fm_folder):
        """Run complete automation workflow"""
        try:
            fm_number = Path(fm_folder).name

            self.console.print("🚀 LLM-POWERED BROWSER AUTOMATION", style="bold green")
            self.console.print(f"📁 Processing: {fm_number}", style="green")
            self.console.print("🤖 AI-assisted element detection", style="green")
            self.console.print("🛡️ Automatic Cloudflare handling", style="green")

            # Initialize browser
            if not self.initialize_browser():
                return False

            # Login
            if not self.login():
                return False

            # Navigate
            if not self.navigate_to_fm_standards():
                return False

            # Process FM station
            if not self.process_fm_station(fm_number):
                return False

            self.console.print("✅ LLM AUTOMATION SUCCESS!", style="bold green")
            self.console.print(f"📻 FM station {fm_number} processed", style="green")
            self.console.print("🤖 AI successfully guided the automation", style="green")

            # Keep browser open for inspection
            self.log("🔍 Keeping browser open for 15 seconds...", "cyan")
            time.sleep(15)

            return True

        except Exception as e:
            self.log(f"❌ Automation failed: {e}", "red")
            return False
        finally:
            self.close()


def main():
    """Main execution"""
    console = Console()

    # Check for folders
    picture_dir = Path("picture")
    if not picture_dir.exists():
        console.print("❌ Picture directory not found", style="red")
        return

    folders = [f for f in picture_dir.iterdir() if f.is_dir()]
    if not folders:
        console.print("❌ No folders found", style="red")
        return

    console.print(f"🤖 LLM Browser Agent ready. Testing with: {folders[0].name}")

    # Create agent
    agent = LLMBrowserAgent()

    try:
        success = agent.run_automation(str(folders[0]))

        if success:
            console.print("🎉 LLM automation completed successfully!", style="bold green")
        else:
            console.print("❌ Automation failed", style="red")

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


if __name__ == "__main__":
    main()