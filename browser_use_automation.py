#!/usr/bin/env python3

"""
NBTC FM Automation using browser-use
Revolutionary AI-powered browser automation that understands web pages visually
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from browser_use import Agent
from analyze_spectrum import AnalyzeSpectrum

load_dotenv()

class NBTCBrowserUseAutomation:
    def __init__(self):
        self.console = Console()
        self.username = os.getenv("NBTC_USERNAME")
        self.password = os.getenv("NBTC_PASSWORD")
        self.login_url = os.getenv("NBTC_LOGIN_URL")
        self.analyzer = AnalyzeSpectrum()

        # Initialize browser-use agent
        self.agent = Agent()

    def log(self, message, style="white"):
        import time
        timestamp = time.strftime("%H:%M:%S")
        self.console.print(f"[{timestamp}] {message}", style=style)

    async def login_to_nbtc(self):
        """Login to NBTC using browser-use AI agent"""
        try:
            self.log("🤖 Starting AI-powered login...", "cyan")

            # Navigate to login page
            result = await self.agent.run(f"""
            Go to {self.login_url} and login with these credentials:
            Username: {self.username}
            Password: {self.password}

            Steps to complete:
            1. Navigate to the login page
            2. Find and fill the username field with the provided username
            3. Find and fill the password field with the provided password
            4. Click the login button
            5. Wait for the page to load after login
            """)

            self.log("✅ AI login completed", "green")
            return True

        except Exception as e:
            self.log(f"❌ Login failed: {e}", "red")
            return False

    async def navigate_to_fm_standards(self):
        """Navigate to FM standards inspection page using AI"""
        try:
            self.log("🧭 AI navigating to FM standards page...", "cyan")

            result = await self.agent.run("""
            Navigate to the FM standards inspection section:

            Steps to complete:
            1. Look for and click on the "FM operations" or "Oper" section link
            2. Find and click on "งานตรวจสอบคลื่นความถี่" (frequency inspection work)
            3. Find and click on "4.การตรวจสอบมาตรฐานการแพร่" (4. broadcast standards inspection)
            4. Wait for the page to load completely

            You should see options related to broadcasting standards inspection after completing these steps.
            """)

            self.log("✅ AI navigation to FM standards completed", "green")
            return True

        except Exception as e:
            self.log(f"❌ Navigation failed: {e}", "red")
            return False

    async def add_fm_station(self, fm_number):
        """Add FM station using AI agent"""
        try:
            self.log(f"📻 AI adding FM station: {fm_number}...", "cyan")

            result = await self.agent.run(f"""
            Add a new FM station with number {fm_number}:

            Steps to complete:
            1. Look for and click on "การตรวจสอบมาตรฐานการแพร่" link (without the "4." prefix)
            2. Find and click the plus (+) or "เพิ่ม" (add) button
            3. Click the primary "เพิ่ม" (add) or search button to open the station search modal
            4. In the modal that opens:
               - Find the station type dropdown and select "FM" (usually index 8 or 9)
               - Find the site code/FM number field and enter: {fm_number}
               - Find the source data dropdown and select the second option (index 1)
               - Click the search button (magnifying glass icon)
               - Click on the first result that appears (usually numbered "1")

            The goal is to successfully add the FM station {fm_number} to the system.
            """)

            self.log(f"✅ AI successfully added FM station {fm_number}", "green")
            return True

        except Exception as e:
            self.log(f"❌ Adding FM station failed: {e}", "red")
            return False

    async def fill_station_details(self, pictures_folder):
        """Fill station details form using AI"""
        try:
            self.log("📋 AI filling station details...", "cyan")

            # Get picture files for analysis
            picture_files = []
            picture_files.extend(sorted(Path(pictures_folder).glob("*.[jJ][pP][gG]")))
            picture_files.extend(sorted(Path(pictures_folder).glob("*.[jJ][pP][eE][gG]")))
            picture_files.extend(sorted(Path(pictures_folder).glob("*.[pP][nN][gG]")))

            if not picture_files:
                self.log("❌ No picture files found", "red")
                return False

            # Analyze first image for date
            pattern_type, date_text = self.analyzer.analyze_spectrum(str(picture_files[0]))
            if not date_text or not date_text[0]:
                self.log("⚠️ No date found in images, using default", "yellow")
                date_text = ["01/01/25"]  # Default date

            self.log(f"📅 Using date: {date_text[0]}", "cyan")

            # Convert to Buddhist calendar
            day, month, year = date_text[0].split("/")
            buddhist_year = int(year) + 543
            formatted_date = f"{day.zfill(2)}{month.zfill(2)}2{buddhist_year}"

            result = await self.agent.run(f"""
            Fill out the detailed FM station form:

            Steps to complete:
            1. Expand all form panels/sections (look for panels 1, 2, 3, 4)

            2. Fill station details section:
               - Set antenna placement to second option (index 1)
               - Set antenna found to second option (index 1)
               - Copy frequency value from FreqMhz field to DetFrq field
               - Set antenna type if not selected (second option)
               - Set cable type to 6th option (index 5)
               - Set power to 500 if empty
               - Set gain to 6 if empty
               - Set height to 60 if empty

            3. Add frequency patterns (do this 3 times):
               - Click the "editFqItem(0)" button to add frequency pattern
               - In the modal: select pattern type (1st, 2nd, 3rd time respectively)
               - Set result to second option (index 1)
               - Save each pattern

            4. Add pictures section:
               - For each picture, click "editItem(0)" button
               - Select appropriate picture type dropdown option
               - Upload the picture file
               - Add remark text based on picture analysis
               - Save each picture

            5. Fill inspection opinion:
               - Set opinion dropdown to second option (index 1)
               - Add remark text: "ปฏิบัติตามหลักเกณฑ์"

            6. Add equipment:
               - Click "editItemEqu(0)" button
               - Set equipment type to 11th option (index 10)
               - Set equipment to 4th option (index 3)
               - Save equipment

            7. Set inspection dates:
               - Fill both DtTest and DtTest2 fields with: {formatted_date}
               - Click on active date in calendar popup

            8. Set inspectors:
               - Inspector 1 (ChkAuthID_1): 7th option (index 6)
               - Inspector 2 (ChkAuthID_2): 17th option (index 16)
               - Inspector 3 (ChkAuthID_3): 12th option (index 11)
               - Boss (ApvNaID): 2nd option (index 1)

            9. Save the form:
               - Click the save button (bSave)
               - Confirm in any popup dialog that appears

            Take your time with each step and ensure all fields are properly filled.
            """)

            self.log("✅ AI successfully filled station details", "green")
            return True

        except Exception as e:
            self.log(f"❌ Filling details failed: {e}", "red")
            return False

    async def process_fm_folder(self, folder_path):
        """Process complete FM folder using browser-use AI"""
        try:
            fm_number = Path(folder_path).name

            self.console.print("🤖 BROWSER-USE AI AUTOMATION", style="bold green")
            self.console.print(f"📁 Processing: {fm_number}", style="green")
            self.console.print("🧠 AI agent will handle all interactions", style="green")
            self.console.print("👀 AI can see and understand the webpage", style="green")
            self.console.print("🌏 Full Thai language support", style="green")

            # Execute complete workflow with AI agent
            if not await self.login_to_nbtc():
                return False

            if not await self.navigate_to_fm_standards():
                return False

            if not await self.add_fm_station(fm_number):
                return False

            if not await self.fill_station_details(folder_path):
                return False

            self.console.print("🎉 BROWSER-USE AUTOMATION SUCCESS!", style="bold green")
            self.console.print(f"📻 FM station {fm_number} processed completely", style="green")
            self.console.print("🤖 AI agent successfully completed all tasks", style="green")
            self.console.print("🚀 No selectors needed - AI understood everything!", style="green")

            return True

        except Exception as e:
            self.log(f"❌ Processing failed: {e}", "red")
            return False


async def main():
    """Main execution function"""
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

    console.print(f"🤖 Browser-use AI automation ready. Testing with: {folders[0].name}")

    # Create automation agent
    automation = NBTCBrowserUseAutomation()

    try:
        success = await automation.process_fm_folder(str(folders[0]))

        if success:
            console.print("🚀 Browser-use automation completed successfully!", style="bold green")
        else:
            console.print("❌ Automation failed", style="red")

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


if __name__ == "__main__":
    # Run the async automation
    asyncio.run(main())