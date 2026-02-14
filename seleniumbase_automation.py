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

import questionary
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from seleniumbase import SB

from analyze_spectrum import AnalyzeSpectrum

load_dotenv()

FORM_BASE_URL = "https://fmr.nbtc.go.th/Oper/ISO/11"

INSPECTOR_OPTIONS = [
    {"value": "491", "name": "นางสาว ปิยาพัชร เกิดไพบูลย์ (เจ้าหน้าที่ตรวจสอบและปฏิบัติการ)"},
    {"value": "529", "name": "นาย ธีราทร ภิรมย์ไกรภักดิ์ (ลูกจ้างประจำ)"},
    {"value": "637", "name": "พรคุณพระ กิตติวราพล (นตป. ก2)"},
]


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
        icons = {"cyan": ">>", "green": "OK", "yellow": "!!", "red": "XX"}
        icon = icons.get(style, "  ")
        self.console.print(f"  [bold]{icon}[/bold] {timestamp}  {message}", style=style)

    def prompt_inspectors(self):
        self.console.print()
        choices = [
            questionary.Choice(title=opt["name"], value=opt["value"], checked=True)
            for opt in INSPECTOR_OPTIONS
        ]

        selected_values = questionary.checkbox(
            "Select inspectors (Space=toggle, Enter=confirm, min 1)",
            choices=choices,
            validate=lambda result: len(result) >= 1 or "Pick at least 1 inspector",
        ).ask()

        selected = []
        lines = []
        for val in selected_values:
            name = next(opt["name"] for opt in INSPECTOR_OPTIONS if opt["value"] == val)
            selected.append(val)
            lines.append(f"  [green]ChkAuthID_{len(selected)}[/green]: {name}")
        while len(selected) < 4:
            selected.append(None)

        lines.append(f"\n  [dim]Defaults: 500W / 6dBi / 60m / Heliax7/8[/dim]")
        self.console.print(Panel("\n".join(lines), title="Configuration", border_style="cyan"))
        self.selected_inspectors = selected

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
                    'return document.getElementById("FreqMhz")'
                    ' ? document.getElementById("FreqMhz").textContent.replace(/[^0-9.]/g, "").trim() : ""'
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
            # --- [1/7] Analyze images ---
            self.log("[1/7] Analyzing images...", "cyan")

            picture_files = sorted(
                list(Path(pictures_folder).glob("*.png"))
                + list(Path(pictures_folder).glob("*.jpg"))
                + list(Path(pictures_folder).glob("*.jpeg"))
            )

            if not picture_files:
                self.log("[1/7] No picture files found", "red")
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
                self.log("[1/7] No date found in images, using default", "yellow")
                first_date = "01/01/25"

            day, month, year = first_date.split("/")
            buddhist_year = 2000 + int(year) + 543
            formatted_date = f"{day.zfill(2)}/{month.zfill(2)}/{buddhist_year}"

            today = datetime.date.today()
            today_thai = f"{today.day:02d}/{today.month:02d}/{today.year + 543}"

            unique_patterns = []
            seen = set()
            for item in image_analysis:
                if item["pattern"] != "Not pattern detected" and item["pattern"] not in seen:
                    unique_patterns.append(item["pattern"])
                    seen.add(item["pattern"])

            self.log(f"[1/7] {len(picture_files)} images, {len(unique_patterns)} patterns, date: {first_date} -> {formatted_date}", "green")

            sb.switch_to_default_content()
            sb.sleep(2)
            sb.execute_script('window.scrollTo(0, 0)')
            sb.sleep(1)

            # --- [2/7] Panel 1: Station details ---
            self.log("[2/7] Panel 1: Station details...", "cyan")
            self.fill_panel1(sb)

            tmp_key = sb.execute_script('return document.getElementById("TmpKey").value')
            area_id = sb.execute_script('return document.getElementById("AreaID").value')
            self.log("[2/7] Panel 1 done", "green")

            # --- [3/7] Panel 2: Frequency details ---
            self.log(f"[3/7] Panel 2: Frequency details ({len(unique_patterns)} patterns)...", "cyan")
            try:
                for pattern in unique_patterns:
                    success = self.fill_fq_item(sb, tmp_key, pattern)
                    if success:
                        self.log(f"       + {pattern}", "green")
                    else:
                        self.log(f"       x {pattern}", "red")

                sb.execute_script('loadFqItem()')
                sb.sleep(3)
                self.log("[3/7] Panel 2 done", "green")
            except Exception as e:
                self.log(f"[3/7] Panel 2 error: {e}", "yellow")

            # --- [4/7] Panel 3: Pictures ---
            self.log(f"[4/7] Panel 3: Uploading {len(image_analysis)} pictures...", "cyan")
            try:
                for item in image_analysis:
                    pic_file = item["file"]
                    pattern = item["pattern"]
                    success = self.fill_pic_item(sb, tmp_key, pic_file, pattern)
                    if success:
                        self.log(f"       + {pic_file.name}", "green")
                    else:
                        self.log(f"       x {pic_file.name}", "red")

                sb.execute_script('loadItem()')
                sb.sleep(3)
                self.log("[4/7] Panel 3 done", "green")
            except Exception as e:
                self.log(f"[4/7] Panel 3 error: {e}", "yellow")

            # --- [5/7] Equipment table ---
            self.log("[5/7] Equipment table...", "cyan")
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
                self.log(f"[5/7] Equipment done ({len(equipment_list)} items)", "green")
            except Exception as e:
                self.log(f"[5/7] Equipment error: {e}", "yellow")

            # --- [6/7] Panel 4: Opinion + Approvers + Dates ---
            self.log("[6/7] Panel 4: Opinion, approvers, dates...", "cyan")
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
            except Exception as e:
                self.log(f"[6/7] Opinion error: {e}", "yellow")

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
            except Exception as e:
                self.log(f"[6/7] Test equipment error: {e}", "yellow")

            try:
                inspector_js_parts = []
                for i, val in enumerate(self.selected_inspectors):
                    if val:
                        field_id = f"ChkAuthID_{i+1}"
                        inspector_js_parts.append(
                            f'var el{i} = document.getElementById("{field_id}");'
                            f' if (el{i}) {{ el{i}.value = "{val}";'
                            f' if (typeof $ !== "undefined") $("#{field_id}").selectpicker("refresh"); }}'
                        )
                inspector_js_parts.append(
                    'var apv = document.getElementById("ApvNaID");'
                    ' if (apv && apv.options.length > 1) { apv.selectedIndex = 1;'
                    ' if (typeof $ !== "undefined") $("#ApvNaID").selectpicker("refresh"); }'
                )
                sb.execute_script("\n".join(inspector_js_parts))
                sb.sleep(1)
            except Exception as e:
                self.log(f"[6/7] Approvers error: {e}", "yellow")

            try:
                sb.execute_script(f'''
                    document.getElementById("DtTest").value = "{formatted_date}";
                    document.getElementById("DtTest2").value = "{formatted_date}";
                    document.getElementById("DtTestRep").value = "{today_thai}";
                    document.getElementById("DtApv").value = "{today_thai}";
                ''')
                sb.sleep(1)
                self.log(f"[6/7] Done (test: {formatted_date}, report: {today_thai})", "green")
            except Exception as e:
                self.log(f"[6/7] Dates error: {e}", "yellow")

            # --- [7/7] Save ---
            self.log("[7/7] Saving form...", "cyan")
            try:
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

                if str(save_result).startswith("VALIDATION_FAILED"):
                    failed_validators = str(save_result).split(":")[1]
                    self.log(f"[7/7] Validation failed: {failed_validators}", "red")
                    return False

                sb.sleep(8)

                try:
                    if sb.is_element_visible("button.confirm"):
                        sb.click("button.confirm")
                        sb.sleep(2)
                except Exception:
                    pass

                self.log("[7/7] Form saved", "green")
            except Exception as e:
                self.log(f"[7/7] Save failed: {e}", "red")
                return False

            return True
        except Exception as e:
            self.log(f"Fill details failed: {e}", "red")
            return False

    def run_automation(self, fm_folder):
        start_time = time.time()
        try:
            fm_number = Path(fm_folder).name

            with SB(uc=True, test=True, incognito=True, locale="th", headless=False) as sb:
                if not self.login(sb):
                    return False, 0
                if not self.navigate_to_fm_standards(sb):
                    return False, 0
                if not self.add_fm_station(sb, fm_number):
                    return False, 0
                if not self.fill_station_details(sb, fm_folder):
                    return False, 0

            elapsed = time.time() - start_time
            return True, elapsed
        except Exception as e:
            self.log(f"Automation failed: {e}", "red")
            elapsed = time.time() - start_time
            return False, elapsed


def format_elapsed(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s:02d}s" if m else f"{s}s"


def main():
    console = Console()

    picture_dir = Path("picture")
    completed_dir = Path("completed")
    completed_dir.mkdir(exist_ok=True)

    if not picture_dir.exists():
        console.print(Panel("[red]Picture directory not found[/red]", title="Error", border_style="red"))
        return

    folders = sorted([f for f in picture_dir.iterdir() if f.is_dir()])
    if not folders:
        console.print(Panel("[red]No station folders found in picture/[/red]", title="Error", border_style="red"))
        return

    station_list = "\n".join(f"  [cyan]{i+1}.[/cyan] {f.name}" for i, f in enumerate(folders))
    console.print(Panel(
        f"  Stations to process: [bold]{len(folders)}[/bold]\n\n{station_list}",
        title="NBTC FM Inspection Automation",
        border_style="cyan",
    ))

    automation = NBTCSeleniumBaseAgent()
    automation.prompt_inspectors()

    if not questionary.confirm("Start processing?", default=True).ask():
        console.print("[yellow]Cancelled.[/yellow]")
        return

    console.print()
    results = []

    for idx, folder in enumerate(folders):
        console.print(Panel(
            f"  [bold]{folder.name}[/bold]  ({idx+1}/{len(folders)})\n"
            f"  Login -> Navigate -> Select -> Fill -> Save",
            title=f"Station {idx+1}/{len(folders)}",
            border_style="blue",
        ))

        try:
            success, elapsed = automation.run_automation(str(folder))
            if success:
                dest = completed_dir / folder.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.move(str(folder), str(dest))
                console.print(f"  [green]OK[/green] {folder.name} -> completed/ ({format_elapsed(elapsed)})\n")
                results.append({"station": folder.name, "status": "OK", "time": format_elapsed(elapsed)})
            else:
                console.print(f"  [red]FAILED[/red] {folder.name} ({format_elapsed(elapsed)})\n")
                results.append({"station": folder.name, "status": "FAILED", "time": format_elapsed(elapsed)})
        except Exception as e:
            console.print(f"  [red]ERROR[/red] {folder.name}: {e}\n")
            results.append({"station": folder.name, "status": "ERROR", "time": "--"})

    table = Table(title="Summary", border_style="cyan", show_lines=True)
    table.add_column("Station", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Time", justify="right")

    ok_count = 0
    for r in results:
        status_style = "green" if r["status"] == "OK" else "red"
        table.add_row(r["station"], f"[{status_style}]{r['status']}[/{status_style}]", r["time"])
        if r["status"] == "OK":
            ok_count += 1

    console.print()
    console.print(table)
    fail_count = len(results) - ok_count
    console.print(f"\n  [bold]{ok_count}[/bold] succeeded, [bold]{fail_count}[/bold] failed\n")


if __name__ == "__main__":
    main()
