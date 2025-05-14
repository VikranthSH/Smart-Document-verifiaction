from flask import Flask, render_template, request, redirect, url_for
import os
import re
from werkzeug.utils import secure_filename
from aadhaar_extractor import AadhaarExtractor
from marksheet_extractor import MarksheetExtractor
from compare import compare_data
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
app.secret_key = 'your-secret-key-here'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Validate form data
        user_data = {
            'Name': request.form['name'].strip(),
            'DOB': request.form['dob'].strip(),
            'Aadhar': request.form['aadhar'].strip(),
            'Mobile': request.form['mobile'].strip()
        }

        # Validate date format
        try:
            datetime.strptime(user_data['DOB'], '%d-%m-%Y')
        except ValueError:
            return render_template('error.html', message="Invalid date format. Use DD-MM-YYYY")
# ...existing code...        # Validate Aadhaar number
        if not re.match(r'^\d{4}\s?\d{4}\s?\d{4}$', user_data['Aadhar']):
            return render_template('error.html', message="Invalid Aadhaar number format")

        # Validate mobile number - accept both with and without country code
        if not re.match(r'^(0|91)?[6789]\d{9}$', user_data['Mobile']):
            return render_template('error.html', message="Invalid mobile number")

        # Process file uploads
        if 'aadhar_img' not in request.files or 'marks_img' not in request.files:
            return render_template('error.html', message="Missing file uploads")

        aadhar_img = request.files['aadhar_img']
        marks_img = request.files['marks_img']

        if not (aadhar_img and allowed_file(aadhar_img.filename) and 
                marks_img and allowed_file(marks_img.filename)):
            return render_template('error.html', message="Invalid file type")

        # Save files
        aadhar_filename = secure_filename(f"aadhar_{datetime.now().strftime('%Y%m%d%H%M%S')}_{aadhar_img.filename}")
        marks_filename = secure_filename(f"marks_{datetime.now().strftime('%Y%m%d%H%M%S')}_{marks_img.filename}")
        
        aadhar_path = os.path.join(app.config['UPLOAD_FOLDER'], aadhar_filename)
        marks_path = os.path.join(app.config['UPLOAD_FOLDER'], marks_filename)
        
        aadhar_img.save(aadhar_path)
        marks_img.save(marks_path)

        # Extract data
        aadhar_extractor = AadhaarExtractor()
        marksheet_extractor = MarksheetExtractor()
        
        extracted_aadhar = aadhar_extractor.extract(aadhar_path)
        extracted_marks = marksheet_extractor.extract(marks_path)

        # Compare data
        aadhar_comparison = compare_data(user_data, extracted_aadhar)
        marks_comparison = compare_data(user_data, extracted_marks)

        return render_template('result.html',
                            user_data=user_data,
                            aadhar_info=extracted_aadhar,
                            marks_info=extracted_marks,
                            aadhar_result=aadhar_comparison,
                            marks_result=marks_comparison)

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return render_template('error.html', message="An error occurred during processing")

if __name__ == '__main__':
    app.run(debug=True)