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
    ('ฉบับที่: ', r'ฉบับที่(.*?)no', 1),
    ('วันอนุญาต: ', r'วัน.*?\b\s(.*?)วันสิ้น', 1),
    ('วันสิ้นอายุ: ', r'วันสิ้นอายุ(.*?)issue', 1),
    ('ชื่อ: ', r'ชื่อ(.*?)name', 1),
    ('name: ', r'name(.*?)เ', 1),
    ('เกิด: ', r'เกิดวันที่(.*?)birth', 1),
    ('birth date: ', r'birth date(.*?)เ', 1),
    ('ID: ', r'd no\.\s*((?:\S+\s*){0,4}\S+)', 1)
]

# Dictionary to map prefix to the database column
prefix_to_column = {
    'ฉบับที่: ': 'dl_no',
    'วันอนุญาต: ': 'dl_date_of_issue',
    'วันสิ้นอายุ: ': 'dl_date_expire',
    'ชื่อ: ': 'dl_thai_name',
    'name: ': 'dl_name',
    'เกิด: ': 'dl_house_type',
    'birth date: ': 'dl_birth_date',
    'ID: ': 'dl_id_num'
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
DB_FILE = 'result_dl.db'
TABLE_NAME = 'dl_data'

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create a table to store extracted ID data
    c.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    file_name TEXT PRIMARY KEY,
                    dl_no TEXT,
                    dl_name TEXT,
                    dl_thai_name TEXT,
                    dl_birth_date TEXT,
                    dl_id_num TEXT,
                    dl_date_of_issue TEXT,
                    dl_date_expire TEXT,
                    dl_province TEXT,
                    extraction_date DATE)''')
    conn.commit()
    conn.close()

def insert_data_to_db(file_name, data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Insert or replace data based on file name as the primary key
    c.execute(f"INSERT OR REPLACE INTO {TABLE_NAME} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (file_name,
               data.get("dl_no", ""),
               data.get("dl_name", ""),
               data.get("dl_thai_name", ""),
               data.get("dl_birth_date", ""),
               data.get("dl_id_num", ""),
               data.get("dl_date_of_issue", ""),
               data.get("dl_date_expire", ""),
               data.get("dl_province", ""),
               date.today()))
    conn.commit()
    conn.close()

path = '..\\file_uploading\\upload\\static\\'
IMG_DIR = path + 'driver_license'

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


