# Smart Document Verification (DOC)

A Flask-based web application for automated extraction and verification of user details from Aadhaar and 10th marks card images using OCR.

---

## Features

- Upload Aadhaar and 10th marks card images for verification.
- Extracts Name, Date of Birth, Aadhaar Number, and Mobile Number from Aadhaar card.
- Extracts Name, Father's Name, and Date of Birth from marks card.
- Compares extracted data with user input and highlights matches, mismatches, and missing fields.
- User-friendly web interface with clear result tables.

---

## Technologies Used

- **Python**: Core programming language.
- **Flask**: Web framework for backend and routing.
- **OpenCV**: Image preprocessing for better OCR.
- **pytesseract (Tesseract OCR)**: Text extraction from images.
- **Regular Expressions (re)**: Pattern matching for data extraction.
- **Werkzeug**: Secure file upload handling.
- **HTML/CSS/Jinja2**: User interface and result display.
- **NumPy**: Image array manipulation.

---

## Project Structure

```
├── app.py
├── aadhaar_extractor.py
├── marksheet_extractor.py
├── compare.py
├── uploads/                # Uploaded images are stored here
├── templates/
│   ├── index.html
│   ├── result.html
│   └── error.html
├── static/
│   └── style.css
└── README.md
```

---

## Setup Instructions

1. **Clone the repository**
    ```sh
    git clone https://github.com/yourusername/your-repo-name.git
    cd your-repo-name
    ```

2. **Install dependencies**
    ```sh
    pip install flask opencv-python pytesseract numpy
    ```

3. **Install Tesseract OCR**
    - Download and install from: [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)
    - Make sure the path in `aadhaar_extractor.py` and `marksheet_extractor.py` matches your installation:
      ```
      pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
      ```

4. **Run the application**
    ```sh
    python app.py
    ```
    - Open your browser and go to `http://127.0.0.1:5000/`

---

## Usage

1. Fill in your Name, Date of Birth (DD-MM-YYYY), Aadhaar Number, and Mobile Number.
2. Upload clear images of your Aadhaar card and 10th marks card.
3. Click **Compare**.
4. View the comparison results, with matches, mismatches, and missing fields highlighted.

---

## Screenshots

> _Add screenshots of your form and result pages here for better clarity._

---

## Notes

- For best results, upload clear, uncropped images of your documents.
- Date of Birth must be in **DD-MM-YYYY** format.
- Aadhaar number must be 12 digits (with or without spaces).
- Mobile number must be a valid Indian number.

---

## Troubleshooting

- **TesseractNotFoundError**: Ensure Tesseract is installed and the path is correct in your code.
- **OCR Errors**: Try to upload higher quality images or adjust preprocessing in the extractor files.
- **File Upload Issues**: Only `.png`, `.jpg`, `.jpeg`, and `.pdf` files are allowed.

---

## License

This project is for educational purposes.

---

## Credits

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [OpenCV](https://opencv.org/)
- [Flask](https://flask.palletsprojects.com/)
