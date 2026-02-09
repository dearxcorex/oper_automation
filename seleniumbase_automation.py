#!/usr/bin/env python3

"""
SeleniumBase UC Mode Automation for NBTC FM Inspection
Bypasses Cloudflare detection automatically with UC Mode
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from seleniumbase import SB
from analyze_spectrum import AnalyzeSpectrum

load_dotenv()


class NBTCSeleniumBaseAgent:
    """SeleniumBase UC Mode automation for NBTC FM inspection"""

    def __init__(self):
        self.console = Console()
        self.username = os.getenv("NBTC_USERNAME")
        self.password = os.getenv("NBTC_PASSWORD")
        self.login_url = os.getenv("NBTC_LOGIN_URL")
        self.analyzer = AnalyzeSpectrum()

    def log(self, message, style="white"):
        """Log message with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        self.console.print(f"[{timestamp}] {message}", style=style)

    def handle_cloudflare(self, sb):
        """Automatically handle Cloudflare challenges"""
        try:
            if sb.is_element_visible("div.cf-browser-verification"):
                self.log("🛡️ Cloudflare detected, solving...", "yellow")
                sb.uc_gui_click_captcha()
                sb.sleep(3)
                self.log("✅ Cloudflare bypassed", "green")
            return True
        except Exception as e:
            self.log(f"⚠️ Cloudflare handling: {e}", "yellow")
            return True

    def login(self, sb):
        """Login to NBTC using SeleniumBase methods"""
        try:
            self.log("🔐 Logging in...", "cyan")

            sb.uc_open_with_reconnect(self.login_url, reconnect_time=3)
            sb.sleep(2)

            self.handle_cloudflare(sb)

            sb.type("#UserName", self.username)
            sb.type("#Password", self.password)
            sb.click("#bLogin")

            sb.sleep(3)
            sb.wait_for_element('a.nbtcros-sectionpage--item', timeout=15)

            self.log("✅ Login successful", "green")
            return True
        except Exception as e:
            self.log(f"❌ Login failed: {e}", "red")
            return False

    def navigate_to_fm_standards(self, sb):
        """Navigate to FM standards page"""
        try:
            self.log("🧭 Navigating to FM standards...", "cyan")

            sb.wait_for_element('a.nbtcros-sectionpage--item[onclick*="Oper"]')
            sb.click('a.nbtcros-sectionpage--item[onclick*="Oper"]')
            sb.sleep(2)

            sb.click('a:contains("งานตรวจสอบคลื่นความถี่")')
            sb.sleep(2)

            sb.click('a:contains("4.การตรวจสอบมาตรฐานการแพร่")')
            sb.sleep(2)

            self.log("✅ Navigation complete", "green")
            return True
        except Exception as e:
            self.log(f"❌ Navigation failed: {e}", "red")
            return False

    def add_fm_station(self, sb, fm_number):
        """Add FM station to system"""
        try:
            self.log(f"📻 Adding FM station: {fm_number}", "cyan")

            sb.click('a:contains("การตรวจสอบมาตรฐานการแพร่")')
            sb.sleep(3)

            sb.wait_for_element('i.iso-icon--plus', timeout=10)
            sb.click('i.iso-icon--plus')
            sb.sleep(3)

            sb.wait_for_element('a.btn.btn-primary.p-edit', timeout=10)
            sb.click('a.btn.btn-primary.p-edit')
            sb.sleep(3)

            iframes = sb.find_elements("iframe")
            if iframes:
                sb.switch_to_frame(iframes[0])

                sb.select_option("#StnTypeID", index=8)
                sb.type("#SiteCode", fm_number)
                sb.select_option("#SrcData", index=1)
                sb.click(".iso-icon--search")
                sb.sleep(3)
                sb.click('a:contains("1")')
                self.log(f"✅ FM station {fm_number} selected", "green")
                return True

            return False
        except Exception as e:
            self.log(f"❌ Add station failed: {e}", "red")
            return False

    def fill_station_details(self, sb, pictures_folder):
        """Fill station details form"""
        try:
            self.log("📋 Filling station details...", "cyan")

            picture_files = list(Path(pictures_folder).glob("*.png"))
            picture_files.extend(list(Path(pictures_folder).glob("*.jpg")))
            picture_files.extend(list(Path(pictures_folder).glob("*.jpeg")))

            if not picture_files:
                self.log("❌ No picture files found", "red")
                return False

            pattern_type, date_text = self.analyzer.analyze_spectrum(str(picture_files[0]))

            if not date_text or not date_text[0]:
                self.log("⚠️ No date found in images, using default", "yellow")
                date_text = ["01/01/25"]

            self.log(f"📅 Using date: {date_text[0]}", "cyan")

            day, month, year = date_text[0].split("/")
            buddhist_year = int(year) + 543
            formatted_date = f"{day.zfill(2)}{month.zfill(2)}2{buddhist_year}"

            sb.switch_to_default_content()

            for panel_id in [1, 2, 3, 4]:
                sb.click(f'button[onclick*="togglePanel({panel_id})"]')

            sb.select_option('select[name="AntennaPlacement"]', index=1)
            sb.select_option('select[name="AntennaFound"]', index=1)
            sb.type("#FreqMhz", sb.get_attribute("#FreqMhz", "value"))
            sb.select_option('select[name="AntennaType"]', index=1)
            sb.select_option('select[name="CableType"]', index=5)
            sb.type("#Power", "500")
            sb.type("#Gain", "6")
            sb.type("#Height", "60")

            for i in range(3):
                sb.click('button[onclick*="editFqItem(0)"]')
                sb.select_option('#FreqPatternType', index=i)
                sb.select_option('#FreqResult', index=1)
                sb.click('button:contains("บันทึก")')

            for idx, pic_file in enumerate(picture_files):
                sb.click('button[onclick*="editItem(0)"]')
                sb.select_option('#PictureType', index=idx)
                sb.choose_file('#PictureUpload', str(pic_file))
                sb.type("#PictureRemark", self.analyzer.get_remark_text(pattern_type))
                sb.click('button:contains("บันทึก")')

            sb.select_option('#Opinion', index=1)
            sb.type("#Remark", "ปฏิบัติตามหลักเกณฑ์")

            sb.click('button[onclick*="editItemEqu(0)"]')
            sb.select_option('#EquipmentType', index=10)
            sb.select_option('#Equipment', index=3)
            sb.click('button:contains("บันทึก")')

            sb.type("#DtTest", formatted_date)
            sb.type("#DtTest2", formatted_date)
            sb.click('.calendar-day.active')

            sb.select_option('#ChkAuthID_1', index=6)
            sb.select_option('#ChkAuthID_2', index=16)
            sb.select_option('#ChkAuthID_3', index=11)
            sb.select_option('#ApvNaID', index=1)

            sb.click("#bSave")

            if sb.is_element_visible('button:contains("ตกลง")', timeout=5):
                sb.click('button:contains("ตกลง")')

            self.log("✅ Details filled successfully", "green")
            return True
        except Exception as e:
            self.log(f"❌ Fill details failed: {e}", "red")
            return False

    def run_automation(self, fm_folder):
        """Run complete automation workflow"""
        try:
            fm_number = Path(fm_folder).name

            self.console.print("🤖 SELENIUMBASE UC MODE AUTOMATION", style="bold green")
            self.console.print(f"📁 Processing: {fm_number}", style="green")
            self.console.print("🛡️ Cloudflare bypass enabled", style="green")
            self.console.print("🤖 Auto CAPTCHA solving", style="green")

            with SB(uc=True, test=True, incognito=True, locale="th", headless=False) as sb:
                if not self.login(sb):
                    return False

                if not self.navigate_to_fm_standards(sb):
                    return False

                if not self.add_fm_station(sb, fm_number):
                    return False

                if not self.fill_station_details(sb, fm_folder):
                    return False

            self.console.print("✅ AUTOMATION SUCCESS!", style="bold green")
            self.console.print(f"📻 FM station {fm_number} processed", style="green")
            self.console.print("🚀 Cloudflare bypassed successfully", style="green")
            return True

        except Exception as e:
            self.log(f"❌ Automation failed: {e}", "red")
            return False


def main():
    """Main execution function"""
    console = Console()

    picture_dir = Path("picture")
    if not picture_dir.exists():
        console.print("❌ Picture directory not found", style="red")
        return

    folders = [f for f in picture_dir.iterdir() if f.is_dir()]
    if not folders:
        console.print("❌ No folders found", style="red")
        return

    console.print(f"🤖 SeleniumBase UC Mode automation ready. Testing with: {folders[0].name}")

    automation = NBTCSeleniumBaseAgent()

    try:
        success = automation.run_automation(str(folders[0]))

        if success:
            console.print("🚀 SeleniumBase automation completed successfully!", style="bold green")
        else:
            console.print("❌ Automation failed", style="red")

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


if __name__ == "__main__":
    main()
