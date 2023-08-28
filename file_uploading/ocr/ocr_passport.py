# Essential Imports
import cv2
import pytesseract
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from datetime import date
import os
import shutil

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\tesseract.exe'


#My custom class for declare region of interest.
class ImageConstantROI():
    class CCCD(object):
        ROIS = {
            "pp_type": [(759, 214, 80, 73)],
            "pp_country_code": [(1061, 218, 166, 67)],
            "pp_passport_num": [(1676, 208, 336, 80)],
            "pp_surname": [ (766, 330, 525, 64)],
            "pp_name": [(759, 442, 532, 76)],
            "pp_thai_name": [(759, 567, 596, 86)],
            "pp_nationality":[(763, 702, 169, 73)],
            "pp_birth_date": [(1163, 702, 400, 70)],
            "pp_id_num": [(1683, 714, 416, 64)],
            "pp_sex":[(753, 814, 112, 76)],
            "pp_place_of_birth":[(1160, 817, 294, 70)],
            "pp_height": [(753, 942, 173, 73)],
            "pp_date_of_issue": [(753, 1058, 343, 76)],
            "pp_date_expire": [(763, 1189, 336, 67)],
        }

#Custom function to show open cv image on notebook.
def display_img(cvImg):
    cvImg = cv2.cvtColor(cvImg, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(10,8))
    plt.imshow(cvImg)
    plt.axis('off')
    plt.show()

#Loading image using cv2
baseImg = cv2.imread('..\\file_uploading\\base_img\\passport_base_img.jpg')
#Declare image size, width height and chanel
baseH, baseW, baseC = baseImg.shape


#Create a custom function to cropped image base on religion of interest
def cropImageRoi(image, roi):
    roi_cropped = image[
        int(roi[1]) : int(roi[1] + roi[3]), int(roi[0]) : int(roi[0] + roi[2])
    ]
    return roi_cropped


def preprocessing_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.multiply(gray, 1)
    return gray

MODEL_CONFIG = '-l tha+eng --oem 1 --psm 6'

NO_PREPROCESSING_CATEGORIES = {}
def extractDataFromIdCard(img):
    extracted_data_dict = {}

    for key, roi in ImageConstantROI.CCCD.ROIS.items():
        data_strings = []

        for r in roi:
            crop_img = cropImageRoi(img, r)

            # Apply preprocessing if the key is not in the set of no preprocessing categories
            if key not in NO_PREPROCESSING_CATEGORIES:
                crop_img = preprocessing_image(crop_img)

            #display_img(crop_img)

            # Extract data from image using pytesseract
            extracted_text = pytesseract.image_to_string(crop_img, config=MODEL_CONFIG)
            data_strings.append(extracted_text.strip())

        extracted_data = ' '.join(data_strings)
        extracted_data_dict[key] = extracted_data
        #print(f"{key} : {extracted_data}")

    return extracted_data_dict

# Define constants
DB_FILE = 'result_pp.db'
TABLE_NAME = 'passport_data'

def initialize_database():
    """
    Initializes (or connects to) an SQLite database.
    Creates a table if it does not exist.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create a table to store extracted ID data
    c.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    file_name TEXT PRIMARY KEY,
                    pp_type TEXT,
                    pp_country_code TEXT,
                    pp_passport_num TEXT,
                    pp_surname TEXT,
                    pp_name TEXT,
                    pp_thai_name TEXT,
                    pp_nationality TEXT,
                    pp_birth_date TEXT,
                    pp_id_num TEXT,
                    pp_sex TEXT,
                    pp_place_of_birth TEXT,
                    pp_height TEXT,
                    pp_date_of_issue TEXT,
                    pp_date_expire TEXT,
                    pp_extraction_date DATE)''')
    conn.commit()
    conn.close()

def insert_data_to_db(file_name, data):
    """
    Inserts extracted data into the database.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Insert or replace data based on file name as the primary key
    c.execute(f"INSERT OR REPLACE INTO {TABLE_NAME} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (file_name,
               data.get("pp_type", ""),
               data.get("pp_country_code", ""),
               data.get("pp_passport_num", ""),
               data.get("pp_surname", ""),
               data.get("pp_name", ""),
               data.get("pp_thai_name", ""),
               data.get("pp_nationality", ""),
               data.get("pp_birth_date", ""),
               data.get("pp_id_num", ""),
               data.get("pp_sex", ""),
               data.get("pp_place_of_birth", ""),
               data.get("pp_height", ""),
               data.get("pp_date_of_issue", ""),
               data.get("pp_date_expire", ""),
               date.today()))
    conn.commit()
    conn.close()


path = '..\\file_uploading\\upload\\static\\'
IMG_DIR = path + 'passport'


def process_directory_images(directory_path):
    print('process_directory image is running')
    
    # # If the database file exists, delete it
    # if os.path.exists(DB_FILE):
    #     os.remove(DB_FILE)
        
    # Initialize the database (creates table if it doesn't exist)
    initialize_database()
    
    sift = cv2.SIFT_create()

    for img_file in os.listdir(IMG_DIR):
        img_path = os.path.join(IMG_DIR, img_file)
        if not os.path.isfile(img_path):
            continue
        
        # Load the image
        img2 = cv2.imread(img_path)
        
        # Detect keypoints and descriptors on base Image and img2
        kp, des = sift.detectAndCompute(baseImg, None)
        kp1, des1 = sift.detectAndCompute(img2, None)
        
        # Init BF Matcher with cross checking and find the matches points of two images
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des, k=2)
        
        # Lowe's ratio test
        good_matches = [m for m, n in matches if m.distance < 0.70 * n.distance]
        
        # Extracting location of good matched keypoints
        srcPoints = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dstPoints = np.float32([kp[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        # Find homography matrix
        matrix_relationship, _ = cv2.findHomography(srcPoints, dstPoints, cv2.RANSAC, 5.0)
        
        # Warp the image
        img_final = cv2.warpPerspective(img2, matrix_relationship, (baseW, baseH))
        
        # Extract data from the ID card
        extracted_data = extractDataFromIdCard(img_final)
        
        # Insert the extracted data into the database
        insert_data_to_db(img_file, extracted_data)

        # Move the processed file to the specified temp directory
        temp_dir = '..\\file_uploading\\upload\\static\\temp'
        shutil.move(img_path, os.path.join(temp_dir, img_file))

        if extracted_data is None:
            extracted_data = {}
        return extracted_data
        



# You can now query the database and retrieve the data into a pandas DataFrame if needed
# process_directory_images(IMG_DIR)

