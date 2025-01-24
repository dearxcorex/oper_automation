import easyocr
import cv2
import re
import numpy as np
import os 


class AnalyzeSpectrum:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])

    def analyze_spectrum(self, image_path):
   
        try:
            image = cv2.imread(image_path)
            results = self.reader.readtext(image)
            # print(results)
            stop_freq = None
            date_text = []
            for(bbox,text,prob) in results:
                text = text.strip()
                # print(text)
                # Check for date pattern
                date_pattern = r'\d{2}/\d{2}/\d{2}'
                date_match = re.search(date_pattern, text)
                if date_match :
                    date = date_match.group()

                    if date not in date_text:
                        date_text.append(date)
                        print(f"Found date: {date}")
                    
                center_match = re.search(r'Center:?\s*(\d+\.?\d*)\s*MHz', text)
                if center_match:
                    center_freq = int(center_match.group(1))
                    if center_freq == 112:
                        return "Unwanted Emission",date_text
                elif "Stop" in text:
                    matches = re.findall(r'Stop:?\s*(\d+\.?\d*)\s*MHz', text)
                    if matches:
                        stop_freq = float(matches[0])
                    if stop_freq == 137:
                        # print("Found unwanted emission pattern")
                        return "Unwanted Emission",date_text
                 
                elif "Occupied BW" in text or "N dB:" in text or "OBW:" in text:
                    return "Bandwidth",date_text

                elif "Upper Limit:" in text:
                    return "Frequency Deviation Limits",date_text
                
            return "Not pattern detected" , date_text
        except Exception as e:
            print(f"Error reading image: {e}")
            return None , []
    def get_remark_text(self,patten_type,date_text=None):
        remarks = {
            "Unwanted Emission": "รูปภาพการตรวจสอบการแพร่แปลกปลอม",
            "Bandwidth": "รูปภาพการตรวจสอบแบนด์วิดท์",
            "Frequency Deviation Limits": "รูปภาพการตรวจสอบค่าเบี่ยงเบนความถี่",
            "Not pattern detected": "รูปภาพจากการตรวจสอบคลื่นความถี่"
        }
        remark = remarks.get(patten_type, "รูปภาพจากการตรวจสอบคลื่นความถี่")
        return remark

         
        
    



if __name__ == "__main__":
    path = "picture/Measurement7100.png"
    analyzer = AnalyzeSpectrum()
    patten_type , date_text = analyzer.analyze_spectrum(path)
    print(date_text)
    remark = analyzer.get_remark_text(patten_type)
    print(remark)