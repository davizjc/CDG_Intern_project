# Intern_project

# README for OCR-based Document Classification and Data Extraction
## Description
This project provides a web-based platform where users can upload various types of documents like ID cards, passports, driver's licenses, and others. The application classifies the uploaded document type and then uses Optical Character Recognition (OCR) to extract relevant data from the document.
## Features
1. Upload multiple file formats: jpeg, jpg, png, pdf.
1. Automatic document type classification with a trained TensorFlow model.
1. OCR extraction for different document types.
1.  Option to review and edit the extracted data before saving.
1. View the list of uploaded documents.
1. Move processed files to their respective categories.
## Dependencies
1. Flask
1. TensorFlow
1. numpy
1. pdf2image
1. poppler-utils (for pdf2image)
## Setup
1. Ensure you have all the required dependencies installed.
2. donwload and set up sql broweser from ,  https://sqlitebrowser.org/
1. Clone the repository.
1. Navigate to the project's root directory.
   
## Configuration
Set the BASE_UPLOAD_FOLDER to your preferred directory for storing uploaded documents.
Ensure the POPPLER_PATH points to the directory containing the poppler binary. This is required for the pdf2image library to convert PDFs into images.
Ensure the MODEL_PATH points to the trained TensorFlow model directory.
Update the ALLOWED_EXTENSIONS and MAX_FILE_SIZE if needed.
Certainly! Here's an additional section you can add to the README to inform users about the required configuration for the pytesseract library:

## Configuring pytesseract
If you're using the pytesseract library to handle OCR, you'll need to ensure that Tesseract-OCR is correctly installed on your system and properly configured within your Python environment. check ocr_ID and Passport
## configuring POPPLER_PATH
Make sure poppler is downloaded and install in the path 
1. poppler-23.07.0\\Library\\bin'

## Usage
1. Start a browser and navigate to http://127.0.0.1:5000/.
1. Follow the instructions on the website to upload your documents.
1. Once uploaded, the system will automatically classify the document type and start the OCR extraction.
1. Review and edit the extracted data if necessary.
1. Save the extracted and edited data to the database.
