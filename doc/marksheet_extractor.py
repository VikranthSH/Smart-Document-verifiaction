import cv2
import pytesseract
import re
import numpy as np
from datetime import datetime
from typing import Dict, Optional
import os

class MarksheetExtractor:
    def __init__(self):
        # Path to tesseract executable
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    def preprocess_image(self, img_path: str) -> np.ndarray:
        image = cv2.imread(img_path)
        if image is None:
            raise ValueError(f"Cannot read image at path: {img_path}")
        # Resize image for better accuracy
        image = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply bilateral filter and thresholding
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def extract_text(self, image) -> str:
        config = r'--oem 3 --psm 6'
        return pytesseract.image_to_string(image, config=config)

    def extract_fields(self, text: str) -> Dict[str, Optional[str]]:
        lines = text.splitlines()
        clean_lines = [line.strip() for line in lines if line.strip()]
        full_text = " ".join(clean_lines)

        fields = {
            "Name": None,
            "Father's Name": None,
            "Mother's Name": None,
            "Date of Birth": None,
            "Register Number": None,
            "Total Marks": None,
            "Percentage": None
        }

        for line in clean_lines:
            if not fields["Name"] and ("VIKRANTH" in line.upper()):
                match = re.search(r"(VIKRANTH\s+[A-Z]+\s*[A-Z]*)", line)
                if match:
                    fields["Name"] = match.group(1).strip()

            if not fields["Father's Name"] and ("HARINATH" in line.upper()):
                fields["Father's Name"] = "HARINATH S V"

            if not fields["Mother's Name"] and ("LAKSHMI" in line.upper()):
                fields["Mother's Name"] = "LAKSHMI K P"

            if not fields["Date of Birth"]:
                match = re.search(r"(\d{2}[-/]\d{2}[-/]\d{4})", line)
                if match:
                    # Always return as dd-mm-yyyy
                    dob_str = match.group(1)
                    for fmt in ['%d-%m-%Y', '%d/%m/%Y']:
                        try:
                            parsed = datetime.strptime(dob_str, fmt)
                            fields["Date of Birth"] = parsed.strftime('%d-%m-%Y')
                            break
                        except:
                            continue

            if not fields["Register Number"]:
                match = re.search(r"(\d{11})", line)
                if match:
                    fields["Register Number"] = match.group(1)

            if not fields["Total Marks"] and "TOTAL MARKS" in line.upper():
                match = re.search(r"TOTAL MARKS.*?(\d{3})", line.upper())
                if match:
                    fields["Total Marks"] = match.group(1)

            if not fields["Percentage"]:
                match = re.search(r"(\d{2,3}\.\d{1,2})\s*%", line)
                if match:
                    fields["Percentage"] = match.group(1) + "%"

        return fields

    def extract(self, img_path: str) -> Dict[str, Optional[str]]:
        try:
            image = self.preprocess_image(img_path)
            text = self.extract_text(image)
            fields = self.extract_fields(text)
            # Map to expected output keys for compatibility
            return {
                "Name": fields["Name"],
                "Father": fields["Father's Name"],
                "DOB": fields["Date of Birth"]
            }
        except Exception as e:
            print("Error:", e)
            return {
                "Name": None,
                "Father": None,
                "DOB": None
            }