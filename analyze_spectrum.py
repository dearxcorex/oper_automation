import easyocr
import cv2
import re
import numpy as np
import os 


class AnalyzeSpectrum:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        self.current_date = None  # Single date storage

    def analyze_spectrum(self, image_path):
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                print(f"Failed to read image: {image_path}")
                return "Not pattern detected", [self.current_date] if self.current_date else []

            results = self.reader.readtext(image)
            if not results:
                print("No text detected in image")
                return "Not pattern detected", [self.current_date] if self.current_date else []

            pattern_type = "Not pattern detected"
            found_date = False

            # First look for date in current image
            for _, text, _ in results:
                text = text.strip()
                date_match = re.search(r'\d{2}/\d{2}/\d{2}', text)
                if date_match:
                    self.current_date = date_match.group()
                    found_date = True
                    print(f"Found date in current image: {self.current_date}")
                    break

            # If no date found in current image, keep using previous date
            if not found_date and self.current_date:
                print(f"Using previous date: {self.current_date}")

            date_text = [self.current_date] if self.current_date else []

            # Pattern detection with early returns
            for _, text, _ in results:
                text = text.strip()
                
                # Check for Center frequency
                if "Center:" in text:
                    center_match = re.search(r'Center:?\s*(\d+\.?\d*)\s*MHz', text)
                    if center_match and float(center_match.group(1)) == 112:
                        return "Unwanted Emission", date_text
                
                # Check for Stop frequency
                if "Stop:" in text:
                    stop_match = re.search(r'Stop:?\s*(\d+\.?\d*)\s*MHz', text)
                    if stop_match and float(stop_match.group(1)) == 137:
                        return "Unwanted Emission", date_text
                
                # Check for Start frequency
                if "Start:" in text:
                    start_match = re.search(r'Start:?\s*(\d+\.?\d*)\s*MHz', text)
                    if start_match and float(start_match.group(1)) == 87:
                        return "Unwanted Emission", date_text
                
                # Check for Bandwidth
                if any(pattern in text for pattern in ["Occupied BW", "N dB:", "OBW:"]):
                    return "Bandwidth", date_text
                
                # Check for Frequency Deviation
                if "Upper Limit:" in text:
                    return "Frequency Deviation Limits", date_text

            return "Not pattern detected", date_text

        except Exception as e:
            print(f"Error in analyze_spectrum: {e}")
            return "Not pattern detected", [self.current_date] if self.current_date else []

    def get_remark_text(self, pattern_type):
        remarks = {
            "Unwanted Emission": "รูปภาพการตรวจสอบการแพร่แปลกปลอม",
            "Bandwidth": "รูปภาพการตรวจสอบแบนด์วิดท์",
            "Frequency Deviation Limits": "รูปภาพการตรวจสอบค่าเบี่ยงเบนความถี่",
            "Not pattern detected": "รูปภาพจากการตรวจสอบคลื่นความถี่"
        }
        remark = remarks.get(pattern_type)
        print(f"Pattern type: {pattern_type} -> Remark: {remark}")
        return remark

if __name__ == "__main__":
    from pathlib import Path
    try:
    
        # Get the base picture directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        picture_dir = os.path.join(current_dir, "picture")
        
  
            
        analyzer = AnalyzeSpectrum()
        total_images = 0
        processed_images = 0
        
        # Walk through all subfolders
        for root, dirs, files in os.walk(picture_dir):
            # Process each subfolder
            for folder in dirs:
                folder_path = os.path.join(root, folder)
                print(f"\nProcessing folder: {folder}")
                print("=" * 50)
                
                # Get all images in this folder
                image_files = []
                for ext in ['*.png', '*.jpg', '*.jpeg']:
                    image_files.extend(Path(folder_path).glob(ext))
                
                if not image_files:
                    print(f"No images found in {folder}")
                    continue
                    
                # Process each image in the folder
                for image_path in image_files:
                    total_images += 1
                    print(f"\nAnalyzing image: {image_path.name}")
                    try:
                        pattern_type, date_text = analyzer.analyze_spectrum(str(image_path))
                        remark = analyzer.get_remark_text(pattern_type)
                        
                        print(f"✓ Pattern type: {pattern_type}")
                        print(f"✓ Date: {date_text}")
                        print(f"✓ Remark: {remark}")
                        
                        processed_images += 1
                        
                    except Exception as e:
                        print(f"❌ Error processing {image_path.name}: {str(e)}")
        
        # Print summary
        print("\nProcessing Summary")
        print("=" * 50)
        print(f"Total folders processed: {len(list(Path(picture_dir).glob('*/')))}")
        print(f"Total images found: {total_images}")
        print(f"Successfully processed: {processed_images}")
        print(f"Failed: {total_images - processed_images}")
        
    except Exception as e:
        print(f"Error during processing: {str(e)}") 