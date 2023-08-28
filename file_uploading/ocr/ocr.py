import pytesseract
from pytesseract import Output
import cv2
from pdf2image import convert_from_path
import matplotlib.pyplot as plt
import re


plt.rcParams["figure.figsize"] = (20,30)

POPPLER_PATH = 'C:\\Users\\cdgs\\OneDrive\\Desktop\\poppler-23.07.0\\Library\\bin'

# Setting the tesseract command path
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\tesseract.exe'


def process_image(img_path):
    img = cv2.imread(img_path)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    ocr_result = pytesseract.image_to_string(img, lang='tha+eng')
    
    # Remove non-Thai and non-English letters and numbers
    cleaned_text = re.sub(r'[^\w\s\u0E00-\u0E7F]', '', ocr_result)
    # Replace multiple spaces with a single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()  # The strip() function is added to remove trailing and leading spaces
    print(cleaned_text)
    with open('ocr_result.txt', 'a', encoding='utf-8') as file:
        file.write(cleaned_text)
    
    d = pytesseract.image_to_data(img, lang='tha+eng', output_type=Output.DICT)
    
    print(f"Processed {img_path} with {len(d['text'])} words detected.")

    

def process_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    for i, image in enumerate(images):
        print(f"Processing page {i+1} of PDF...")
        img_path = f"temp_page_{i+1}.png"
        image.save(img_path, 'PNG')
        process_image(img_path)

# Process a single image
process_image("C:\\Users\\cdgs\\OneDrive\\Desktop\\document\\house_register\\1.jpg")


# If you want to process a PDF, uncomment the below line and provide your PDF path
# process_pdf("C:\\Users\\cdgs\\OneDrive\\Desktop\\file2.pdf")