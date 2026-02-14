#!/usr/bin/env python3

"""
SeleniumBase UC Mode Automation for NBTC FM Inspection
Uses WebDriver window.open() for new tabs (shares session cookies).
Fills iframe forms in separate tabs to avoid Cloudflare iframe blocking.
"""

import datetime
import os
import random
import shutil
import time
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from seleniumbase import SB

from analyze_spectrum import AnalyzeSpectrum

load_dotenv()

FORM_BASE_URL = "https://fmr.nbtc.go.th/Oper/ISO/11"


def rid():
    return "".join([str(random.randint(0, 9)) for _ in range(8)])


class NBTCSeleniumBaseAgent:

    def __init__(self):
        self.console = Console()
        self.username = os.getenv("NBTC_USERNAME")
        self.password = os.getenv("NBTC_PASSWORD")
        self.login_url = os.getenv("NBTC_LOGIN_URL")
        self.analyzer = AnalyzeSpectrum()

    def log(self, message, style="white"):
        timestamp = time.strftime("%H:%M:%S")
        self.console.print(f"[{timestamp}] {message}", style=style)

    def handle_cloudflare(self, sb):
        try:
            if sb.is_element_visible("div.cf-browser-verification"):
                self.log("Cloudflare detected, solving...", "yellow")
                sb.uc_gui_click_captcha()
                sb.sleep(3)
            return True
        except Exception:
            return True

    def login(self, sb):
        try:
            self.log("Logging in...", "cyan")
            sb.uc_open_with_reconnect(self.login_url, reconnect_time=3)
            sb.sleep(2)
            self.handle_cloudflare(sb)
            sb.type("#UserName", self.username)
            sb.type("#Password", self.password)
            sb.click("#bLogin")
            sb.sleep(3)
            sb.wait_for_element('a.nbtcros-sectionpage--item', timeout=15)
            self.log("Login successful", "green")
            return True
        except Exception as e:
            self.log(f"Login failed: {e}", "red")
            return False

    def navigate_to_fm_standards(self, sb):
        try:
            self.log("Navigating to FM standards...", "cyan")
            sb.wait_for_element('a.nbtcros-sectionpage--item[onclick*="Oper"]')
            sb.click('a.nbtcros-sectionpage--item[onclick*="Oper"]')
            sb.sleep(3)
            sb.wait_for_element('a:contains("งานตรวจสอบคลื่นความถี่")', timeout=15)
            sb.click('a:contains("งานตรวจสอบคลื่นความถี่")')
            sb.sleep(2)
            sb.wait_for_element('a:contains("4.การตรวจสอบมาตรฐานการแพร่")', timeout=10)
            sb.click('a:contains("4.การตรวจสอบมาตรฐานการแพร่")')
            sb.sleep(2)
            sb.wait_for_element('a[href*="FF11ChkSch"]', timeout=10)
            sb.click('a[href*="FF11ChkSch"]')
            sb.sleep(3)
            self.log("Navigation complete", "green")
            return True
        except Exception as e:
            self.log(f"Navigation failed: {e}", "red")
            return False

    def add_fm_station(self, sb, fm_number):
        try:
            self.log(f"Adding FM station: {fm_number}", "cyan")
            sb.wait_for_element('a[href*="fno=add"]', timeout=10)
            sb.click('a[href*="fno=add"]')
            sb.sleep(3)
            sb.wait_for_element('button:contains("ค้นหา")', timeout=10)
            sb.click('button:contains("ค้นหา")')
            sb.sleep(3)
            sb.wait_for_element('iframe[src*="mStnSch"]', timeout=10)
            sb.uc_switch_to_frame('iframe[src*="mStnSch"]')
            sb.select_option_by_text("#StnTypeID", "สถานีวิทยุกระจายเสียง")
            sb.type("#SiteCode", fm_number)
            sb.click('button:contains("ค้นหา")')
            sb.sleep(3)
            sb.click('a:contains("1")')
            sb.switch_to_default_content()
            self.log(f"FM station {fm_number} selected", "green")
            return True
        except Exception as e:
            self.log(f"Add station failed: {e}", "red")
            return False

    def fill_panel1(self, sb):
        try:
            sb.click('p[href="#collapse_panel_1"]')
            sb.sleep(1)
            if sb.is_element_present('#DetAnt'):
                sb.select_option_by_text('#DetAnt', "พบ")
            if sb.is_element_present('#DetAerial'):
                sb.select_option_by_text('#DetAerial', "พบ")
            if sb.is_element_present('#DetFrq'):
                freq_value = sb.execute_script(
                    'return document.querySelector(".FreqMhz")'
                    ' ? document.querySelector(".FreqMhz").textContent.replace(/[^0-9.]/g, "") : ""'
                )
                if freq_value:
                    sb.type("#DetFrq", freq_value)
            if sb.is_element_present('#CableID'):
                sb.select_option_by_text('#CableID', "Heliax7/8")
            if sb.is_element_present('#DetPow'):
                if not sb.execute_script('return document.getElementById("DetPow").value'):
                    sb.type("#DetPow", "500")
            if sb.is_element_present('#DetDBI'):
                if not sb.execute_script('return document.getElementById("DetDBI").value'):
                    sb.type("#DetDBI", "6")
            if sb.is_element_present('#DetAntHeight'):
                if not sb.execute_script('return document.getElementById("DetAntHeight").value'):
                    sb.type("#DetAntHeight", "60")
            self.log("Panel 1: Station details filled", "green")
            return True
        except Exception as e:
            self.log(f"Panel 1 error: {e}", "yellow")
            return True

    def open_new_tab_js(self, sb, url):
        main_handle = sb.driver.current_window_handle
        sb.execute_script(f'window.open("{url}", "_blank")')
        sb.sleep(3)
        handles = sb.driver.window_handles
        for h in handles:
            if h != main_handle:
                sb.driver.switch_to.window(h)
                break
        sb.sleep(2)
        return main_handle

    def close_tab_and_return(self, sb, main_handle):
        sb.driver.close()
        sb.sleep(1)
        sb.driver.switch_to.window(main_handle)
        sb.sleep(1)

    def wait_for_element_js(self, sb, element_id, timeout=20):
        for _ in range(timeout):
            found = sb.execute_script(
                f'return document.getElementById("{element_id}") !== null'
            )
            if found:
                return True
            sb.sleep(1)
        return False

    def fill_fq_item(self, sb, tmp_key, pattern):
        fq_url = f"{FORM_BASE_URL}/mFF11FqDoc.aspx?ChkID=&TmpKey={tmp_key}&ChkFqID=0&r={rid()}"
        main_handle = self.open_new_tab_js(sb, fq_url)
        try:
            if not self.wait_for_element_js(sb, "DiffPara", timeout=15):
                page_url = sb.execute_script('return window.location.href')
                self.log(f"FQ tab failed to load. URL: {page_url}", "red")
                self.close_tab_and_return(sb, main_handle)
                return False

            sb.execute_script(f'''
                document.getElementById("DiffPara").value = "{pattern}";
                if (typeof $ !== "undefined") $("#DiffPara").selectpicker("refresh");
                document.getElementById("DiffRes").value = "ผ่าน";
                if (typeof $ !== "undefined") $("#DiffRes").selectpicker("refresh");
            ''')
            sb.sleep(1)
            sb.execute_script(
                "if (typeof(Page_ClientValidate) == 'function') Page_ClientValidate('');"
                " __doPostBack('ctl15','')"
            )
            sb.sleep(5)
            try:
                if sb.is_element_visible("button.confirm"):
                    sb.click("button.confirm")
                    sb.sleep(1)
            except Exception:
                pass
            self.close_tab_and_return(sb, main_handle)
            return True
        except Exception as e:
            self.log(f"FQ item error: {e}", "red")
            try:
                self.close_tab_and_return(sb, main_handle)
            except Exception:
                pass
            return False

    def fill_pic_item(self, sb, tmp_key, pic_file, pattern):
        doc_url = f"{FORM_BASE_URL}/mFF11Doc.aspx?ChkID=&TmpKey={tmp_key}&ChkPicID=0&r={rid()}"
        main_handle = self.open_new_tab_js(sb, doc_url)
        try:
            if not self.wait_for_element_js(sb, "PicTypeID", timeout=15):
                page_url = sb.execute_script('return window.location.href')
                self.log(f"Pic tab failed to load. URL: {page_url}", "red")
                self.close_tab_and_return(sb, main_handle)
                return False

            sb.execute_script('''
                document.getElementById("PicTypeID").value = "1";
                if (typeof $ !== "undefined") $("#PicTypeID").selectpicker("refresh");
            ''')
            sb.sleep(1)

            file_input = sb.driver.find_element("css selector", "#File1")
            file_input.send_keys(str(pic_file.resolve()))
            sb.sleep(2)

            remark_text = self.analyzer.get_remark_text(pattern) or ""
            remark_text = remark_text.replace("\\", "\\\\").replace("'", "\\'").replace('\n', '\\n')
            sb.execute_script(f"document.getElementById('Remark').value = '{remark_text}'")
            sb.sleep(1)

            sb.execute_script(
                "if (typeof(Page_ClientValidate) == 'function') Page_ClientValidate('');"
                " __doPostBack('ctl15','')"
            )
            sb.sleep(5)
            try:
                if sb.is_element_visible("button.confirm"):
                    sb.click("button.confirm")
                    sb.sleep(1)
            except Exception:
                pass
            self.close_tab_and_return(sb, main_handle)
            return True
        except Exception as e:
            self.log(f"Pic item error: {e}", "red")
            try:
                self.close_tab_and_return(sb, main_handle)
            except Exception:
                pass
            return False

    def fill_equipment(self, sb, tmp_key, area_id, equ_type_id, equ_name_search):
        equ_url = (
            f"https://fmr.nbtc.go.th/Oper/ISO/Equ/mChkEqu.aspx"
            f"?ff=F11&ChkID=&AreaID={area_id}&TmpKey={tmp_key}&ChkEquID=0&r={rid()}"
        )
        main_handle = self.open_new_tab_js(sb, equ_url)
        try:
            if not self.wait_for_element_js(sb, "EquTypeID", timeout=15):
                page_url = sb.execute_script('return window.location.href')
                self.log(f"Equ tab failed to load. URL: {page_url}", "red")
                self.close_tab_and_return(sb, main_handle)
                return False

            sb.execute_script(f'''
                document.getElementById("EquTypeID").value = "{equ_type_id}";
                if (typeof $ !== "undefined") {{
                    $("#EquTypeID").selectpicker("refresh");
                    $("#EquTypeID").trigger("change");
                }}
            ''')
            sb.sleep(3)

            self.wait_for_element_js(sb, "EquID", timeout=10)
            sb.execute_script(f'''
                var el = document.getElementById("EquID");
                if (el) {{
                    for (var i = 0; i < el.options.length; i++) {{
                        if (el.options[i].text.indexOf("{equ_name_search}") >= 0) {{
                            el.value = el.options[i].value;
                            break;
                        }}
                    }}
                    if (typeof $ !== "undefined") $("#EquID").selectpicker("refresh");
                }}
            ''')
            sb.sleep(1)

            sb.execute_script(
                "if (typeof(Page_ClientValidate) == 'function') Page_ClientValidate('');"
                " __doPostBack('ctl15','')"
            )
            sb.sleep(5)
            try:
                if sb.is_element_visible("button.confirm"):
                    sb.click("button.confirm")
                    sb.sleep(1)
            except Exception:
                pass
            self.close_tab_and_return(sb, main_handle)
            return True
        except Exception as e:
            self.log(f"Equ item error: {e}", "red")
            try:
                self.close_tab_and_return(sb, main_handle)
            except Exception:
                pass
            return False

    def fill_station_details(self, sb, pictures_folder):
        try:
            self.log("Filling station details...", "cyan")

            picture_files = sorted(
                list(Path(pictures_folder).glob("*.png"))
                + list(Path(pictures_folder).glob("*.jpg"))
                + list(Path(pictures_folder).glob("*.jpeg"))
            )

            if not picture_files:
                self.log("No picture files found", "red")
                return False

            image_analysis = []
            for pic_file in picture_files:
                pattern_type, date_text = self.analyzer.analyze_spectrum(str(pic_file))
                image_analysis.append({"file": pic_file, "pattern": pattern_type, "date": date_text})

            first_date = None
            for item in image_analysis:
                if item["date"] and item["date"][0]:
                    first_date = item["date"][0]
                    break

            if not first_date:
                self.log("No date found in images, using default", "yellow")
                first_date = "01/01/25"

            self.log(f"Using date: {first_date}", "cyan")

            day, month, year = first_date.split("/")
            buddhist_year = 2000 + int(year) + 543
            formatted_date = f"{day.zfill(2)}/{month.zfill(2)}/{buddhist_year}"

            today = datetime.date.today()
            today_thai = f"{today.day:02d}/{today.month:02d}/{today.year + 543}"

            sb.switch_to_default_content()
            sb.sleep(2)
            sb.execute_script('window.scrollTo(0, 0)')
            sb.sleep(1)

            # --- Panel 1 (WebDriver mode) ---
            self.fill_panel1(sb)

            # --- Get TmpKey and AreaID ---
            tmp_key = sb.execute_script('return document.getElementById("TmpKey").value')
            area_id = sb.execute_script('return document.getElementById("AreaID").value')
            self.log(f"TmpKey: {tmp_key}, AreaID: {area_id}", "cyan")

            # --- Panel 2: Frequency details (new tabs via window.open) ---
            try:
                unique_patterns = []
                seen = set()
                for item in image_analysis:
                    if item["pattern"] != "Not pattern detected" and item["pattern"] not in seen:
                        unique_patterns.append(item["pattern"])
                        seen.add(item["pattern"])

                for pattern in unique_patterns:
                    success = self.fill_fq_item(sb, tmp_key, pattern)
                    if success:
                        self.log(f"Added frequency detail: {pattern}", "cyan")
                    else:
                        self.log(f"Failed frequency detail: {pattern}", "red")

                sb.execute_script('loadFqItem()')
                sb.sleep(3)
                self.log("Panel 2: Frequency details done", "green")
            except Exception as e:
                self.log(f"Panel 2 error: {e}", "yellow")

            # --- Panel 3: Pictures (new tabs via window.open) ---
            try:
                for item in image_analysis:
                    pic_file = item["file"]
                    pattern = item["pattern"]
                    success = self.fill_pic_item(sb, tmp_key, pic_file, pattern)
                    if success:
                        self.log(f"Uploaded: {pic_file.name} ({pattern})", "cyan")
                    else:
                        self.log(f"Failed upload: {pic_file.name}", "red")

                sb.execute_script('loadItem()')
                sb.sleep(3)
                self.log("Panel 3: Pictures done", "green")
            except Exception as e:
                self.log(f"Panel 3 error: {e}", "yellow")

            # --- Equipment table (need >= 2 rows for validation) ---
            try:
                equipment_list = [
                    ("10", "H-R&S-FSH8"),
                    ("12", "ชุดเครื่องมือวัดแพร่แปลกปลอม"),
                ]
                for equ_type_id, equ_name_search in equipment_list:
                    success = self.fill_equipment(sb, tmp_key, area_id, equ_type_id, equ_name_search)
                    if success:
                        sb.execute_script('loadItemEqu()')
                        sb.sleep(3)
                self.log("Equipment table done", "green")
            except Exception as e:
                self.log(f"Equipment error: {e}", "yellow")

            # --- Panel 4: Inspector opinion ---
            try:
                sb.execute_script('''
                    var p = document.querySelector('p[href="#collapse_panel_4"]');
                    if (p) p.click();
                ''')
                sb.sleep(1)
                sb.execute_script('''
                    var el = document.getElementById("OpinionDet");
                    if (el) {
                        el.value = "ตรงตามมาตรฐาน";
                        if (typeof $ !== "undefined") $("#OpinionDet").selectpicker("refresh");
                    }
                    var remark = document.getElementById("Remark");
                    if (remark) remark.value = "ตรงตามมาตรฐาน";
                ''')
                sb.sleep(1)
                self.log("Panel 4: Opinion filled", "green")
            except Exception as e:
                self.log(f"Panel 4 error: {e}", "yellow")

            # --- Test equipment dropdowns ---
            try:
                sb.execute_script('''
                    var el = document.getElementById("TestEq");
                    if (el) {
                        for (var i = 0; i < el.options.length; i++) {
                            if (el.options[i].text.indexOf("H-FSH8") >= 0) {
                                el.selectedIndex = i; break;
                            }
                        }
                        if (typeof $ !== "undefined") $("#TestEq").selectpicker("refresh");
                    }
                ''')
                sb.sleep(1)
                self.log("Test equipment dropdown filled", "green")
            except Exception as e:
                self.log(f"Test equipment error: {e}", "yellow")

            # --- Approvers ---
            try:
                sb.execute_script('''
                    var fields = [
                        {id: "ChkAuthID_1", idx: 10},
                        {id: "ChkAuthID_2", idx: 11},
                        {id: "ChkAuthID_3", idx: 8},
                        {id: "ApvNaID", idx: 1}
                    ];
                    fields.forEach(function(f) {
                        var el = document.getElementById(f.id);
                        if (el && el.options.length > f.idx) {
                            el.selectedIndex = f.idx;
                            if (typeof $ !== "undefined") $("#" + f.id).selectpicker("refresh");
                        }
                    });
                ''')
                sb.sleep(1)
                self.log("Approvers filled", "green")
            except Exception as e:
                self.log(f"Approvers error: {e}", "yellow")

            # --- Dates ---
            try:
                sb.execute_script(f'''
                    document.getElementById("DtTest").value = "{formatted_date}";
                    document.getElementById("DtTest2").value = "{formatted_date}";
                    document.getElementById("DtTestRep").value = "{formatted_date}";
                    document.getElementById("DtApv").value = "{today_thai}";
                ''')
                sb.sleep(1)
                self.log(f"Dates filled: {formatted_date}", "green")
            except Exception as e:
                self.log(f"Dates error: {e}", "yellow")

            # --- Save ---
            try:
                self.log("Saving form...", "cyan")
                sb.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                sb.sleep(2)

                save_result = sb.execute_script('''
                    if (typeof Page_ClientValidate === 'function') {
                        var isValid = Page_ClientValidate('');
                        if (!isValid) {
                            var errors = [];
                            for (var i = 0; i < Page_Validators.length; i++) {
                                if (!Page_Validators[i].isvalid) {
                                    errors.push(Page_Validators[i].id);
                                }
                            }
                            return "VALIDATION_FAILED:" + errors.join(",");
                        }
                    }
                    __doPostBack('bSave','');
                    return "SAVE_TRIGGERED";
                ''')
                self.log(f"Save result: {save_result}", "cyan")

                if str(save_result).startswith("VALIDATION_FAILED"):
                    failed_validators = str(save_result).split(":")[1]
                    self.log(f"Validation failed: {failed_validators}", "red")
                    return False

                sb.sleep(8)

                try:
                    if sb.is_element_visible("button.confirm"):
                        sb.click("button.confirm")
                        sb.sleep(2)
                except Exception:
                    pass

                self.log("Form saved successfully", "green")
            except Exception as e:
                self.log(f"Save failed: {e}", "red")
                return False

            self.log("Station processing complete", "green")
            return True
        except Exception as e:
            self.log(f"Fill details failed: {e}", "red")
            return False

    def run_automation(self, fm_folder):
        try:
            fm_number = Path(fm_folder).name
            self.console.print(f"\nProcessing: {fm_number}", style="bold green")

            with SB(uc=True, test=True, incognito=True, locale="th", headless=False) as sb:
                if not self.login(sb):
                    return False
                if not self.navigate_to_fm_standards(sb):
                    return False
                if not self.add_fm_station(sb, fm_number):
                    return False
                if not self.fill_station_details(sb, fm_folder):
                    return False

            self.console.print(f"FM station {fm_number} processed successfully", style="bold green")
            return True
        except Exception as e:
            self.log(f"Automation failed: {e}", "red")
            return False


def main():
    console = Console()

    picture_dir = Path("picture")
    completed_dir = Path("completed")
    completed_dir.mkdir(exist_ok=True)

    if not picture_dir.exists():
        console.print("Picture directory not found", style="red")
        return

    folders = sorted([f for f in picture_dir.iterdir() if f.is_dir()])
    if not folders:
        console.print("No folders found", style="red")
        return

    console.print(
        f"SeleniumBase UC Mode ready. {len(folders)} station(s) to process.",
        style="bold cyan",
    )
    for f in folders:
        console.print(f"   {f.name}", style="cyan")

    automation = NBTCSeleniumBaseAgent()
    succeeded = []
    failed = []

    for folder in folders:
        console.print(f"\n{'='*50}", style="bold white")
        console.print(
            f"Processing: {folder.name} ({folders.index(folder)+1}/{len(folders)})",
            style="bold cyan",
        )
        console.print(f"{'='*50}", style="bold white")

        try:
            success = automation.run_automation(str(folder))
            if success:
                dest = completed_dir / folder.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.move(str(folder), str(dest))
                console.print(f"Moved {folder.name} -> completed/", style="green")
                succeeded.append(folder.name)
            else:
                console.print(f"Station {folder.name} failed, skipping", style="red")
                failed.append(folder.name)
        except Exception as e:
            console.print(f"Error processing {folder.name}: {e}", style="red")
            failed.append(folder.name)

    console.print(f"\n{'='*50}", style="bold white")
    console.print(f"SUMMARY: {len(succeeded)} succeeded, {len(failed)} failed", style="bold cyan")
    if succeeded:
        console.print(f"   OK: {', '.join(succeeded)}", style="green")
    if failed:
        console.print(f"   FAIL: {', '.join(failed)}", style="red")


if __name__ == "__main__":
    main()
