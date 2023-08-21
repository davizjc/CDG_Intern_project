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
    ('เล่มที่: ', r'เล่มที่(.*?)รายการบุคคลในบ้านของเลขรหัสประจำบ้าน', 1),
    ('รายการบุคคลในบ้านของเลขรหัสประจำบ้าน: ', r'รายการบุคคลในบ้านของเลขรหัสประจำบ้าน(.*?)ลำดับที่', 1),
    ('ลำดับที่: ', r'ลำดับที่\s*(\d+)', 1),
    ('ชื่อ: ', r'ชื่อ(.*?)สัญชาติ', 1),
    ('สัญชาติ: ', r'สัญชาติ(.*?)เพศ ', 1),
    ('เพศ : ', r'เพศ((?:\S+\s*){0,1}\S+)', 1),
    ('เลขประจำตัวประชาชน: ', r'เลขประจำตัวประชาชน(.*?) สถานภาพ', 1),
    ('สถานภาพ: ', r'สถานภาพ(.*?)เกิด ', 1),
    ('เกิดเมื่อ: ', r'เกิดเมื่อ(.*?)มารดา', 1),
    # ('มารดา: ', r'มารดา.*?\bอ(.*?)สัญชาติ', 1),
    ('มารดา: ', r'มารดา(.*?)สัญชาติ', 1),
    ('สัญชาติแม่: ', r'สัญชาติ (.*?)\s', 2),
    # ('บิดา: ', r'บิดา.*?\bอ(.*?)สัญชาติ', 1),
    ('บิดา: ', r'บิดา(.*?)สัญชาติ', 1),
    ('สัญชาติพ่อ: ', r'สัญชาติ (.*?)\s', 3),
    ('มาจาก: ', r'มาจาก(.*?) \(', 1),
    ('ไปที่: ', r'ไปที่(.*?)นายทะเบียน', 1)
]

# Dictionary to map prefix to the database column
prefix_to_column = {
    'เล่มที่: ': 'hr2_vol_num',
    'รายการบุคคลในบ้านของเลขรหัสประจำบ้าน: ': 'hr2_house_id',
    'ลำดับที่: ': 'hr2_order_num',
    'ชื่อ: ': 'hr2_name',
    'สัญชาติ: ': 'hr2_nationality',
    'เพศ : ': 'hr2_gender',
    'เลขประจำตัวประชาชน: ': 'hr2_person_id',
    'สถานภาพ: ': 'hr2_status',
    'เกิดเมือ: ': 'hr2_birth_date',
    'มารดา: ': 'hr2_mother_name',
    'สัญชาติแม่่: ': 'hr2_mother_nationality',  # The second occurrence of 'สัญชาติ'
    'บิดา: ': 'hr2_father_name',
    'สัญชาติพ่อ: ': 'hr2_father_nationality',  # The third occurrence of 'สัญชาติ'
    'มาจาก: ': 'hr2_origin',
    'ไปที่: ': 'hr2_destination',
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
DB_FILE = 'result_hr2.db'
TABLE_NAME = 'hr2_data'

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create a table to store extracted person_id data
    c.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    file_name TEXT PRIMARY KEY,
                    hr2_vol_num TEXT,
                    hr2_house_id TEXT,
                    hr2_order_num TEXT,
                    hr2_name TEXT,
                    hr2_nationality TEXT,
                    hr2_gender TEXT,
                    hr2_person_id TEXT,
                    hr2_status TEXT,
                    hr2_birth_date TEXT,
                    hr2_mother_name TEXT,
                    hr2_mother_nationality TEXT,
                    hr2_father_name TEXT,
                    hr2_father_nationality TEXT,
                    hr2_origin TEXT,
                    hr2_destination TEXT,
                    extraction_date DATE)''')
    conn.commit()
    conn.close()

def insert_data_to_db(file_name, data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Insert or replace data based on file name as the primary key
    c.execute(f"INSERT OR REPLACE INTO {TABLE_NAME} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?)",
        (file_name,
        data.get("hr2_vol_num", ""),
        data.get("hr2_house_id", ""),
        data.get("hr2_order_num", ""),
        data.get("hr2_name", ""),
        data.get("hr2_nationality", ""),
        data.get("hr2_gender", ""),
        data.get("hr2_person_id", ""),
        data.get("hr2_status", ""),
        data.get("hr2_birth_date", ""),
        data.get("hr2_mother_name", ""),
        data.get("hr2_mother_nationality", ""),
        data.get("hr2_father_name", ""),
        data.get("hr2_father_nationality", ""),
        data.get("hr2_origin", ""),
        data.get("hr2_destination", ""),
        date.today()))
    conn.commit()
    conn.close()


path = '..\\file_uploading\\upload\\static\\'
IMG_DIR = path + 'house_register'

def process_directory_images(directory_path):
    print('process_directory image is running')
    extracted_data = {}  # Initialize the dictionary at the beginning

    # If the database file exists, delete it

    # if os.path.exists(DB_FILE):
    #     os.remove(DB_FILE)

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


