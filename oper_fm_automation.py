import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import Select

from pathlib import Path
from analyze_spectrum import AnalyzeSpectrum


from dotenv import load_dotenv
import os 

load_dotenv()
class NBTC_Automation:
    def __init__(self):
        self.username = os.getenv("NBTC_USERNAME")
        self.password = os.getenv("NBTC_PASSWORD")
        self.driver = self.initialize_driver()
        self.login_url = os.getenv("NBTC_LOGIN_URL")
        self.analyzer = AnalyzeSpectrum()


    def initialize_driver(self):
        options = Options()
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        #size window
        # options.add_argument('--window-size=1270,1390')
        # options.add_argument('--window-position=0,0')

        options.add_argument('--start-maximized')
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def login(self):
        self.driver.get(self.login_url)
        username_input = self.driver.find_element(By.ID, "UserName")
        username_input.send_keys(self.username)
        password_input = self.driver.find_element(By.ID, "Password")
        password_input.send_keys(self.password)
        login_button = self.driver.find_element(By.ID, "bLogin")
        login_button.click()

    def navigate_to_fm_page(self):
        try:
            click_fm_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.nbtcros-sectionpage--item[onclick*='Oper']"))
            )
            click_fm_button.click()

            time.sleep(2)

            menu_item = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'งานตรวจสอบคลื่นความถี่')]"))
            )
            menu_item.click()
            time.sleep(2)

           
            submenu_item = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '4.การตรวจสอบมาตรฐานการแพร่')]"))
            )
            submenu_item.click()

            time.sleep(2)

        
  
            
        except TimeoutException:

            print("TimeoutException: Failed to navigate to FM page")
        except Exception as e:
            print(f"An error occurred: {e}")



    def input_fm(self,number_fm):
       try:

            submenu_item = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "การตรวจสอบมาตรฐานการแพร่"))
            )
            submenu_item.click()

            time.sleep(2)

            submenu_item = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".iso-icon--plus"))
            )
            submenu_item.click()

            time.sleep(2)

            search_buttton = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.x-add"))
            )
            search_buttton.click()

            time.sleep(2)


            modal = WebDriverWait(self.driver,10).until(
                EC.presence_of_element_located((By.CLASS_NAME,"modal-content"))
            )
            iframe = modal.find_elements(By.TAG_NAME, "iframe")

            if len(iframe) > 0:
                # print(f"found {len(iframe)} iframe in modal")
                self.driver.switch_to.frame(iframe[0])

                input_station_type = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID,"StnTypeID"))
                )
                station_type = Select(input_station_type)
                station_type.select_by_index(8)
                time.sleep(2)
                input_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID,"SiteCode"))
                )
                input_field.send_keys(number_fm)

                #select source 
                source = Select(self.driver.find_element(By.ID, "SrcData"))
                source.select_by_index(1)

                search_fm_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "iso-icon--search"))
                )
                search_fm_button.click()

                time.sleep(2)

                list_list = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[text()='1']"))
                )


                time.sleep(2)
                row = list_list.find_element(By.XPATH, "./ancestor::tr")
                station_name = row.find_element(By.XPATH, "./td[5]").text
                frequency = row.find_element(By.XPATH, "./td[6]").text
                address = row.find_element(By.XPATH,'./td[7]').text
                source = row.find_element(By.XPATH,'./td[8]').text


                print(f"\nStation Name:)") 
                print(f"ชื่อสถานี: {station_name}")
                print(f"ความถี่: {frequency}")
                print(f"แหล่งข้อมูล: {address}")
                print(f"แหล่งข้อมูล: {source}")


                list_list.click()

            else:
                print("No iframe found!") 
                

       except Exception as e:
           print(f"An error occurred: {e}")


    # รายละเอียดสถานี 
    def input_detail_fm(self,path_picture):
        try:
            self.driver.switch_to.default_content()
            time.sleep(2)

            # List of panel IDs to toggle
            try:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.TAG_NAME, "iframe"))
                    )
                    self.driver.switch_to.default_content()
                    time.sleep(1)
                except Exception as e:
                    print(f"Error toggle panel: {panel_id} : {e}")
                    
                panel_ids = ['1', '2', '3', '4']
                for panel_id in panel_ids:
                    try:
                        # Wait for any overlays or modals to disappear
                        time.sleep(1)
                        self.driver.switch_to.default_content()
                        
                        # Wait for panel to be both present and clickable
                        toggle_button = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, f"p[href='#collapse_panel_{panel_id}']"))
                        )
                        
                        # Scroll into view with offset to avoid header overlap
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                            toggle_button
                        )
                        time.sleep(1)
                        
                        # Try JavaScript click if regular click fails
                        try:
                            toggle_button.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", toggle_button)
                        
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"Error toggling panel {panel_id}: {str(e)}")
                        # Try alternative clicking method
                        try:
                            element = self.driver.find_element(By.CSS_SELECTOR, f"p[href='#collapse_panel_{panel_id}']")
                            self.driver.execute_script("arguments[0].click();", element)
                        except:
                            print(f"Failed alternative click for panel {panel_id}")
                        continue
            except Exception as e:
                print(f"Error toggle panel: {e}")

            #scroll to รายละเอียดสถานี
            panel_heading = WebDriverWait(self.driver,10).until(
                EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'รายละเอียดสถานี')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", panel_heading)
            time.sleep(0.5)

            # input รายละเอียดสถานี
           
            place_antenna = Select(self.driver.find_element(By.ID, "DetAnt"))
            place_antenna.select_by_index(1)

            antenna_found = Select(self.driver.find_element(By.ID, "DetAerial"))
            antenna_found.select_by_index(1)

            
            time.sleep(2)
            frequency_span = self.driver.find_element(By.ID,"FreqMhz")
            frequency_value = frequency_span.text.strip()
            frequency = self.driver.find_element(By.ID, "DetFrq")
            frequency.send_keys(frequency_value)

            #check dropdown type antenna
            dropdown_type_antenna = Select(self.driver.find_element(By.ID, "AntID"))

            if dropdown_type_antenna.first_selected_option.text == "กรุณาเลือก":
                #test 
                dropdown_type_antenna.select_by_index(1)
            #check dropdown cable type
            cable_type = Select(self.driver.find_element(By.ID, "CableID"))
            cable_type.select_by_index(5)

            #power
            power = self.driver.find_element(By.ID, "DetPow")
            power_value = power.get_attribute("value")
            
            if not power_value:
                power.clear()
                power.send_keys("500")

           #Gain 
            gain = self.driver.find_element(By.ID, "DetDBI")
            gain_value = gain.get_attribute("value")
            if not gain_value:
                gain.clear()
                gain.send_keys("6")

            #height
            height = self.driver.find_element(By.ID, "DetAntHeight")
            height_value = height.get_attribute("value")
            if not height_value:
                height.clear()
                height.send_keys("60")

            # add buttom 
            scroll_to_add_button =  self.driver.find_element(By.CSS_SELECTOR, "p[href='#collapse_panel_3']") 
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", scroll_to_add_button)
            time.sleep(0.5)

            #add detail for pattern frequency
            for click_result in range(1,4):
                self.driver.switch_to.default_content()
                add_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick='editFqItem(0)']"))
                )
                time.sleep(0.5)
                add_button.click()

                #switch to iframe 
                modal_body = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "modal-content"))
                )
                iframe = modal_body.find_elements(By.TAG_NAME, "iframe")
                if len(iframe) > 0:
                    # print(f"found {len(iframe)} iframe in modal")
                    self.driver.switch_to.frame(iframe[0])

                    #select source 
                    dropdown_patten = self.driver.find_element(By.ID, "DiffPara")
                    time.sleep(1)
                    source_dropdown_patten = Select(dropdown_patten)
                    source_dropdown_patten.select_by_index(click_result)
                    time.sleep(1)
    
                    
                
                    result_dropdown_patten = Select(self.driver.find_element(By.ID, "DiffRes"))
                    result_dropdown_patten.select_by_index(1)
                    time.sleep(1)

                    #save
                    save_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary i.iso-icon--save")
                    save_button.click()

                    time.sleep(1)
                    self.driver.switch_to.default_content()






            #add picture
            scroll_to_add_pictures =  self.driver.find_element(By.CSS_SELECTOR, "p[href='#collapse_panel_4']") 
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", scroll_to_add_pictures)
            time.sleep(0.5)
            # Sort files by extension priority
            picture_files = []
            # First add all .jpg files
            picture_files.extend(sorted(Path(path_picture).glob("*.[jJ][pP][gG]")))
            picture_files.extend(sorted(Path(path_picture).glob("*.[jJ][pP][eE][gG]")))
            # Then add all .png files
            picture_files.extend(sorted(Path(path_picture).glob("*.[pP][nN][gG]")))

            if not picture_files:
                print("No picture files found")
                return

            # Get first date text
            pattern_type, date_text = self.analyzer.analyze_spectrum(str(picture_files[0]))
            print(f"Initial pattern: {pattern_type}")
            print(f"Initial date: {date_text}")

            # Check if date_text is empty or contains empty string
            if not date_text or not date_text[0]:
                print("No date found in first image, searching other images...")
                # Try to find date in other images
                for picture_file in picture_files[1:]:
                    pattern_type, date_text = self.analyzer.analyze_spectrum(str(picture_file))
                    if date_text and date_text[0]:
                        print(f"Found date in {picture_file.name}: {date_text[0]}")
                        break
                else:  # No date found in any image
                    print("No date found in any image!")
                    return

            print(f"Using date: {date_text[0]}")

            for picture_file in picture_files:

                try:
                    pattern_type ,_ = self.analyzer.analyze_spectrum(picture_file)
                    
                    analtze_spectrum_pictures = self.analyzer.get_remark_text(pattern_type)
                    print(f"remark: {analtze_spectrum_pictures}")

                
                    add_picture = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick='editItem(0)']"))
                    )
                    add_picture.click()
                    #switch to iframe
                    time.sleep(1)
                    modal_body = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "modal-content"))
                    )
                    iframe = modal_body.find_elements(By.TAG_NAME, "iframe")
                    if len(iframe) > 0:
                        # print(f"found {len(iframe)} iframe in modal")
                        self.driver.switch_to.frame(iframe[0])

                        #Select dropdown
                        time.sleep(1)
                        find_dropdown_picture = self.driver.find_element(By.ID, "PicTypeID")
                        drop_down_picture = Select(find_dropdown_picture)
                        if analtze_spectrum_pictures == "รูปภาพจากการตรวจสอบคลื่นความถี่":
                            drop_down_picture.select_by_index(6)
                        else:
                            drop_down_picture.select_by_index(2) 

                    

                        #upload picture 
                        time.sleep(1)
                        upload_picture = self.driver.find_element(By.ID, "File1")
                        upload_picture.send_keys(str(picture_file.absolute()))

                        #remark 
                        time.sleep(1)
                        remark = self.driver.find_element(By.ID, "Remark")
                        remark.send_keys(analtze_spectrum_pictures)

                        #save
                        time.sleep(1)
                        save_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary i.iso-icon--save")
                        save_button.click()



                        time.sleep(1)
                        self.driver.switch_to.default_content()
            
                except Exception as e:
                    print(f"Error add picture: {e}")
            print(f"pattern_type_in_input_detail_fm: {pattern_type}")
            print(f"date_text_in_input_detail_fm: {date_text}")

            # opinion inspection
            time.sleep(1)
            find_dropdown_opinion = self.driver.find_element(By.ID, "OpinionDet")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", find_dropdown_opinion)
            drop_down_opinion = Select(find_dropdown_opinion)
            drop_down_opinion.select_by_index(1)
            time.sleep(0.5)

            type_opinion = self.driver.find_element(By.ID, "Remark")
            type_opinion.send_keys("ปฏิบัติตามหลักเกณฑ์")


            #click add equipment
            time.sleep(1)
            add_equipment = self.driver.find_element(By.CSS_SELECTOR, "button[onclick='editItemEqu(0)']")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", add_equipment)
            add_equipment.click()

            #switch to iframe
            time.sleep(1)
            modal_body = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "modal-content"))
            )
            iframe = modal_body.find_elements(By.TAG_NAME, "iframe")
            if len(iframe) > 0:
                # print(f"found {len(iframe)} iframe in modal")
                self.driver.switch_to.frame(iframe[0])

                #select source 
                dropdown_equipment = self.driver.find_element(By.ID, "EquTypeID")
                time.sleep(1)
                source_dropdown_equipment = Select(dropdown_equipment)
                source_dropdown_equipment.select_by_index(10)
                time.sleep(1)


                #select equipment
                time.sleep(1)
                equipment = self.driver.find_element(By.ID, "EquID")
                source_dropdown_equipment_type = Select(equipment)
                source_dropdown_equipment_type.select_by_index(3)
                time.sleep(1)


                #save
                time.sleep(1)
                save_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary i.iso-icon--save")
                save_button.click()


                time.sleep(1)
                self.driver.switch_to.default_content()

           #Scroll to bottom
        

            #input date
            
        
            date_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "DtTest"))
            )
            print(f"found date input")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", date_input)
            time.sleep(1)
            data_input_2 = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "DtTest2"))
            )
            # date_text_test = ["21/01/25"]
            day,month,year = date_text[0].split("/")
            buddhist_year = int(year) + 543
            time.sleep(1)
            date_input.clear()
            time.sleep(1)
            formatted_date = f"{day.zfill(2)}{month.zfill(2)}2{buddhist_year}"
            date_input.send_keys(formatted_date)

            active_date = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "td.active.day"))
            )
            active_date.click()
            print(f"found active date")
            #input date 2
            time.sleep(1)
            data_input_2.clear()
            data_input_2.send_keys(formatted_date)

            active_date = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "td.active.day"))
            )
            active_date.click()


            #select inspector
            time.sleep(1)
            inspector_leader = self.driver.find_element(By.ID, "ChkAuthID_1")
            source_dropdown_inspector_leader = Select(inspector_leader)
            source_dropdown_inspector_leader.select_by_index(6)
            time.sleep(1)

            #select inspector
            time.sleep(1)
            inspector_crew_1 = self.driver.find_element(By.ID, "ChkAuthID_2")
            source_dropdown_inspector_crew_1 = Select(inspector_crew_1)
            source_dropdown_inspector_crew_1.select_by_index(16)
            time.sleep(1)

            #select inspector
            time.sleep(1)
            inspector_crew_2 = self.driver.find_element(By.ID, "ChkAuthID_3")
            source_dropdown_inspector_crew_2 = Select(inspector_crew_2)
            source_dropdown_inspector_crew_2.select_by_index(11)
            time.sleep(1)

            #select inspector 
            # time.sleep(1)
            # inspector_crew_3 = self.driver.find_element(By.ID, "ChkAuthID_4")
            # source_dropdown_inspector_crew_3 = Select(inspector_crew_3)
            # source_dropdown_inspector_crew_3.select_by_index(12)
            # time.sleep(1)

            #boss 
            time.sleep(1)
            boss = self.driver.find_element(By.ID, "ApvNaID")
          
            source_dropdown_boss = Select(boss)
            source_dropdown_boss.select_by_index(1)
            time.sleep(1)

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            #click save
            #scroll to save button
            try:

                save_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "bSave"))
                )
               
                save_button.click()
                time.sleep(2)
                modal_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.btn-primary.swal2-styled"))
                )
                modal_button.click()

                time.sleep(5)

                
            except Exception as e:
                print(f"Error save: {e}")


        except Exception as e:
                    print(f"Error input detail: {e}") 
            


   


