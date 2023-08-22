# Intern_project

# README for OCR-based Document Classification and Data Extraction
## Description
This project provides a web-based platform where users can upload various types of documents like ID cards, passports, driver's licenses, and others. The application classifies the uploaded document type and then uses Optical Character Recognition (OCR) to extract relevant data from the document.
## Features
Upload multiple file formats: jpeg, jpg, png, pdf.
Automatic document type classification with a trained TensorFlow model.
OCR extraction for different document types.
Option to review and edit the extracted data before saving.
View the list of uploaded documents.
Move processed files to their respective categories.
## Dependencies
Flask
TensorFlow
numpy
pdf2image
poppler-utils (for pdf2image)
## Setup
Ensure you have all the required dependencies installed.
Clone the repository.
Navigate to the project's root directory.
## Configuration
Set the BASE_UPLOAD_FOLDER to your preferred directory for storing uploaded documents.
Ensure the POPPLER_PATH points to the directory containing the poppler binary. This is required for the pdf2image library to convert PDFs into images.
Ensure the MODEL_PATH points to the trained TensorFlow model directory.
Update the ALLOWED_EXTENSIONS and MAX_FILE_SIZE if needed.
Certainly! Here's an additional section you can add to the README to inform users about the required configuration for the pytesseract library:
## Configuring pytesseract
If you're using the pytesseract library to handle OCR, you'll need to ensure that Tesseract-OCR is correctly installed on your system and properly configured within your Python environment. check ocr_ID and Passport

