# Essential Imports
import easyocr
import cv2
from matplotlib import pyplot as plt
import numpy as np
import re
import sqlite3
from datetime import date
import os
import shutil


def display_img(cvImg):
    cvImg = cv2.cvtColor(cvImg, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(10,8))
    plt.imshow(cvImg)
    plt.axis('off')
    plt.show()


def preprocessing_image(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced_gray = cv2.multiply(gray, 1.5)
    display_img(enhanced_gray)
    return enhanced_gray

patterns = [
    ('ทะเบียนเลขที่: ', r'ที่\s*(\d+)\s', 1),
    ('บริษัท: ', r'แสดงว่า(.*?)ได้จดทะ', 1),
    ('ที่: ', r'พาณิชย์(.*?)เมื่อ', 1),
    ('เมื่อวันที่: ', r'เมื่อวันที่(.*?)ออก', 1),
]


# Dictionary to map prefix to the database column
prefix_to_column = {
    'ทะเบียนเลขที่: ': 'cm_registration_id',
    'บริษัท: ': 'cm_company_name',
    'ที่: ': 'cm_location',
    'เมื่อวันที่: ': 'cm_date'
}


def extractDataFromIdCard(img_path):
    img = cv2.imread(img_path)
    if img is None:
        print('Could not read image.')
        return

    reader = easyocr.Reader(['en', 'th'])
    result = reader.readtext(img)

    all_text = ' '.join([text for (bbox, text, prob) in result])
    print(all_text)

    extracted_data = {}
    for prefix, pattern, occurrence in patterns:
        match = find_occurrence(pattern, all_text, occurrence)

        if match:
            extracted_text = match.strip()
            print(prefix + extracted_text)
            db_column = prefix_to_column.get(prefix)
            if db_column:
                extracted_data[db_column] = extracted_text
        else:
            print(prefix)
            db_column = prefix_to_column.get(prefix)
            if db_column:
                extracted_data[db_column] = None

    return extracted_data

def find_occurrence(pattern, text, occurrence=1):
    matches = re.findall(pattern, text)
    if len(matches) >= occurrence:
        return matches[occurrence-1]
    return 



# Define constants
DB_FILE = 'result_cm.db'
TABLE_NAME = 'cm_data'

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create a table to store extracted ID data
    c.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    file_name TEXT PRIMARY KEY,
                    cm_registration_id TEXT,
                    cm_company_name TEXT,
                    cm_location TEXT,
                    cm_date TEXT,
                    extraction_date DATE)''')
    conn.commit()
    conn.close()

def insert_data_to_db(file_name, data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Insert or replace data based on file name as the primary key
    c.execute(f"INSERT OR REPLACE INTO {TABLE_NAME} VALUES (?, ?, ?, ?, ?, ?)",
              (file_name,
               data.get("cm_registration_id", ""),
               data.get("cm_company_name", ""),
               data.get("cm_location", ""),
               data.get("cm_date", ""),
               date.today()))
    conn.commit()
    conn.close()

path = '..\\file_uploading\\upload\\static\\'
IMG_DIR = path + 'commercial_registration'

def process_directory_images(directory_path):
    print('process_directory image is running')
    extracted_data = {}  # Initialize the dictionary at the beginning
    initialize_database()

    for img_file in os.listdir(directory_path):
        img_path = os.path.join(directory_path, img_file)
        if not os.path.isfile(img_path):
            continue

        # Extract data from the ID card
        extracted_data = extractDataFromIdCard(img_path)

        # Insert the extracted data into the database
        insert_data_to_db(img_file, extracted_data)

        # Move the processed file to the specified temp directory
        temp_dir = '..\\file_uploading\\upload\\static\\temp'
        shutil.move(img_path, os.path.join(temp_dir, img_file))

        if not extracted_data:
            extracted_data = {}

    return extracted_data
        
# process_directory_images(IMG_DIR)


