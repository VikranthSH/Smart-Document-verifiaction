import cv2
import numpy as np
import pytesseract
import re
from datetime import datetime
from typing import Dict, Optional

class AadhaarExtractor:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def preprocess_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Unable to read image: {image_path}")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        preprocessed_images = []
        # 1. Standard Thresholding
        thresh_binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        preprocessed_images.append(thresh_binary)
        # 2. Adaptive Thresholding
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        preprocessed_images.append(adaptive_thresh)
        # 3. Noise Reduction
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        thresh_denoised = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        preprocessed_images.append(thresh_denoised)
        # 4. Contrast Enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast_enhanced = clahe.apply(gray)
        thresh_contrast = cv2.threshold(contrast_enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        preprocessed_images.append(thresh_contrast)
        return preprocessed_images

    def _clean_text(self, text):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\x20-\x7E\n]', '', text)
        cleaned_lines = []
        for line in text.split('\n'):
            stripped_line = line.strip()
            if len(stripped_line.split()) > 1 or len(stripped_line) > 5:
                cleaned_lines.append(stripped_line)
        return '\n'.join(cleaned_lines).strip()

    def extract_text_from_image(self, img):
        extraction_configs = [
            r'--oem 3 --psm 6',
            r'--oem 3 --psm 11',
            r'--oem 3 --psm 4',
            r'--oem 3 --psm 3'
        ]
        extracted_texts = []
        for config in extraction_configs:
            try:
                text_eng = pytesseract.image_to_string(img, config=config, lang='eng+hin')
                if text_eng.strip():
                    extracted_texts.append(text_eng)
            except Exception as e:
                continue
        return ' '.join(extracted_texts) if extracted_texts else ''

    def parse_aadhaar_data(self, text):
        text = self._clean_text(text)
        data = {
            'Name': None,
            'DOB': None,
            'Aadhar': None,
            'Mobile': None
        }
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        full_text = ' '.join(lines)

        # Aadhaar Number Extraction
        aadhaar_patterns = [
            r'\b\d{4}\s?\d{4}\s?\d{4}\b',  # Spaced format
            r'\b\d{12}\b',  # Continuous 12 digits
        ]
        for pattern in aadhaar_patterns:
            match = re.search(pattern, full_text)
            if match:
                digits = re.sub(r'\D', '', match.group(0))
                if len(digits) == 12:
                    data['Aadhar'] = f"{digits[:4]} {digits[4:8]} {digits[8:]}"
                    break

        # Date of Birth Extraction
        dob_patterns = [
            r'\b(\d{2}/\d{2}/\d{4})\b',  # DD/MM/YYYY
            r'\b(\d{2}-\d{2}-\d{4})\b',  # DD-MM-YYYY
            r'\b(\d{4}-\d{2}-\d{2})\b',  # YYYY-MM-DD
            r'\b(\d{4}/\d{2}/\d{2})\b',  # YYYY/MM/DD
        ]
        for pattern in dob_patterns:
            match = re.search(pattern, full_text)
            if match:
                dob_str = match.group(1)
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d']:
                    try:
                        dob = datetime.strptime(dob_str, fmt)
                        data['DOB'] = dob.strftime('%d-%m-%Y')
                        break
                    except ValueError:
                        continue
                if data['DOB']:
                    break

        # Mobile Number Extraction (HARDCODED as requested)
        data['Mobile'] = "9448648170"

        # Name Extraction (first non-keyword line, fallback)
        keywords = ['dob', 'birth', 'year', 'govt', 'male', 'female', 'aadhar', 'uidai', 'government', 'address']
        for line in lines[:10]:
            if not any(k in line.lower() for k in keywords) and not any(char.isdigit() for char in line):
                if len(line.split()) >= 2 and re.match(r'^[A-Za-z\s\.-]+$', line):
                    data['Name'] = line.title()
                    break

        return data

    def extract(self, img_path: str) -> Dict[str, Optional[str]]:
        try:
            preprocessed_images = self.preprocess_image(img_path)
            for img in preprocessed_images:
                text = self.extract_text_from_image(img)
                aadhaar_data = self.parse_aadhaar_data(text)
                # If at least Aadhaar or Name or DOB is found, return
                if any([aadhaar_data['Aadhar'], aadhaar_data['Name'], aadhaar_data['DOB']]):
                    return aadhaar_data
            # If nothing found, return empty
            return {
                "Name": None,
                "DOB": None,
                "Aadhar": None,
                "Mobile": None
            }
        except Exception as e:
            print(f"Extraction error: {e}")
            return {
                "Name": None,
                "DOB": None,
                "Aadhar": None,
                "Mobile": None
            }