#!/usr/bin/env python3
import easyocr
import cv2
import re
import numpy as np
import os


class AnalyzeSpectrum:
    STANDARD_WIDTH = 640
    STANDARD_HEIGHT = 480
    BRIGHTNESS_THRESHOLD = 60

    REGION_TITLE = (0, 18, 0, 200)
    REGION_DATE = (0, 18, 440, 620)
    REGION_UPPER = (78, 100, 0, 250)

    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        self.current_date = None

    def _is_standard_screenshot(self, image):
        h, w = image.shape[:2]
        return h == self.STANDARD_HEIGHT and w == self.STANDARD_WIDTH

    def _is_dark_image(self, image):
        return image.mean() < self.BRIGHTNESS_THRESHOLD

    def _ocr_region(self, image, region):
        y1, y2, x1, x2 = region
        crop = image[y1:y2, x1:x2]
        results = self.reader.readtext(crop)
        return " ".join(text.strip() for _, text, _ in results)

    def _extract_date_from_region(self, image):
        text = self._ocr_region(image, self.REGION_DATE)
        date_match = re.search(r'\d{2}/\d{2}/\d{2}', text)
        if date_match:
            self.current_date = date_match.group()
            return True
        return False

    def _detect_pattern_from_regions(self, image):
        title_text = self._ocr_region(image, self.REGION_TITLE)

        if "Occupied" in title_text or "BW" in title_text:
            return "Bandwidth"

        if "Spectrum" in title_text or "pectrum" in title_text:
            upper_text = self._ocr_region(image, self.REGION_UPPER)

            if "Upper" in upper_text or "Limit" in upper_text:
                return "Frequency Deviation Limits"

            if "137" in upper_text or "M3" in upper_text:
                return "Unwanted Emission"

            return "Unwanted Emission"

        return None

    def _analyze_full_image(self, image):
        results = self.reader.readtext(image)
        if not results:
            return "Not pattern detected"

        for _, text, _ in results:
            text = text.strip()
            date_match = re.search(r'\d{2}/\d{2}/\d{2}', text)
            if date_match:
                self.current_date = date_match.group()
                break

        for _, text, _ in results:
            text = text.strip()

            if "Center:" in text:
                center_match = re.search(r'Center:?\s*(\d+\.?\d*)\s*MHz', text)
                if center_match and float(center_match.group(1)) == 112:
                    return "Unwanted Emission"

            if "Stop:" in text:
                stop_match = re.search(r'Stop:?\s*(\d+\.?\d*)\s*MHz', text)
                if stop_match and float(stop_match.group(1)) == 137:
                    return "Unwanted Emission"

            if "Start:" in text:
                start_match = re.search(r'Start:?\s*(\d+\.?\d*)\s*MHz', text)
                if start_match and float(start_match.group(1)) == 87:
                    return "Unwanted Emission"

            if any(pattern in text for pattern in ["Occupied BW", "N dB:", "OBW:"]):
                return "Bandwidth"

            if "Upper Limit:" in text:
                return "Frequency Deviation Limits"

        return "Not pattern detected"

    def analyze_spectrum(self, image_path):
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                return "Not pattern detected", [self.current_date] if self.current_date else []

            if not self._is_dark_image(image):
                return "Not pattern detected", [self.current_date] if self.current_date else []

            if self._is_standard_screenshot(image):
                self._extract_date_from_region(image)
                pattern = self._detect_pattern_from_regions(image)
                if pattern:
                    return pattern, [self.current_date] if self.current_date else []

            pattern = self._analyze_full_image(image)
            return pattern, [self.current_date] if self.current_date else []

        except Exception as e:
            return "Not pattern detected", [self.current_date] if self.current_date else []

    def get_remark_text(self, pattern_type):
        remarks = {
            "Unwanted Emission": "รูปภาพการตรวจสอบการแพร่แปลกปลอม",
            "Bandwidth": "รูปภาพการตรวจสอบแบนด์วิดท์",
            "Frequency Deviation Limits": "รูปภาพการตรวจสอบค่าเบี่ยงเบนความถี่",
            "Not pattern detected": "รูปภาพจากการตรวจสอบคลื่นความถี่"
        }
        return remarks.get(pattern_type)


if __name__ == "__main__":
    from pathlib import Path

    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        picture_dir = os.path.join(current_dir, "picture")

        analyzer = AnalyzeSpectrum()
        total_images = 0
        processed_images = 0

        for root, dirs, files in os.walk(picture_dir):
            for folder in sorted(dirs):
                folder_path = os.path.join(root, folder)
                print(f"\nProcessing folder: {folder}")
                print("=" * 50)

                image_files = []
                for ext in ['*.png', '*.jpg', '*.jpeg']:
                    image_files.extend(Path(folder_path).glob(ext))

                if not image_files:
                    print(f"No images found in {folder}")
                    continue

                for image_path in sorted(image_files, key=lambda p: p.name):
                    total_images += 1
                    try:
                        pattern_type, date_text = analyzer.analyze_spectrum(str(image_path))
                        remark = analyzer.get_remark_text(pattern_type)
                        print(f"  {image_path.name}: {pattern_type} | {date_text}")
                        processed_images += 1
                    except Exception as e:
                        print(f"  {image_path.name}: ERROR - {e}")

        print(f"\nSummary: {processed_images}/{total_images} processed")

    except Exception as e:
        print(f"Error: {e}")
