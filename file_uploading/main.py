import os
import shutil
import numpy as np
import tensorflow as tf
from flask import Flask, request, render_template, url_for, session, jsonify , redirect, url_for
from pdf2image import convert_from_path

from functools import partial
import ocr.ocr_id as ocr_id
import ocr.ocr_passport as ocr_passport
import ocr.ocr_dl as ocr_dl
import ocr.ocr_hr1 as ocr_hr1
import ocr.ocr_hr2 as ocr_hr2
import ocr.ocr_cm as ocr_cm


app = Flask(__name__)

# Configurations
BASE_UPLOAD_FOLDER = '..\\file_uploading\\upload'
UPLOAD_FOLDER = os.path.join(BASE_UPLOAD_FOLDER, 'static', 'temp')
ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png', 'pdf'}
MAX_FILE_SIZE = 2 * 1024  *1024  # 2MB 1024
MODEL_PATH = '..\\file_uploading\\model\\model_up'
OCR_MODULES = {'id': ocr_id,'passport': ocr_passport,'dl': ocr_dl,'hr1': ocr_hr1,'hr2': ocr_hr2,'cm': ocr_cm}
DIRECTORY_PATH = "..\\file_uploading\\upload\\static\\temp"


POPPLER_PATH = 'C:\\Users\\cdgs\\OneDrive\\Desktop\\poppler-23.07.0\\Library\\bin'

#secret key
app.secret_key = 'some_random_string_here'


model = tf.keras.models.load_model(MODEL_PATH)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path, desired_height=224, desired_width=224):
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(desired_height, desired_width))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    return img_array

def extract_category(predictions):
    categories = ['commercial_registration','driver_license', 'house_register', 'national_id_card', 'passport']
    
    # Extract the index of the maximum prediction and its value
    predicted_idx = np.argmax(predictions[0])
    confidence = predictions[0][predicted_idx]
    print(confidence)
    
    return categories[predicted_idx], confidence

@app.route('/')
def main():
    return render_template("index.html")


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        files = request.files.getlist('file[]')

        file_names = []
        file_categories = []

        category_map = {
            "national_id_card": "National ID Card",
            "passport": "Passport",
            "house_register": "House Register",
            "driver_license": "Driver License",
            "commercial_registration": "Commercial Registration"
        }

        if not files:
            return render_template("error.html", error="No file selected")

        file_names = []       # List to store names of all uploaded files
        file_categories = []  # List to store categories of all uploaded files

        for i, f in enumerate(files):
            if f.filename == '':
                continue
        
            if not allowed_file(f.filename):
                return render_template("error.html", error="Invalid file type. Allowed types: jpeg, jpg, png, pdf")

            if len(f.read()) > MAX_FILE_SIZE:
                return render_template("error.html", error="File is too large. Max allowed size is 2MB")
            f.seek(0)  # Reset the file pointer after reading

            original_name, ext = os.path.splitext(f.filename)

            if ext.lower() == ".pdf":
                f.save(os.path.join(UPLOAD_FOLDER, f.filename))
                images = convert_from_path(os.path.join(UPLOAD_FOLDER, f.filename), poppler_path=POPPLER_PATH)
                file_path = os.path.join(UPLOAD_FOLDER, original_name + ".jpg")
                images[0].save(file_path, 'JPEG')
                os.remove(os.path.join(UPLOAD_FOLDER, f.filename))  # remove the original PDF
                filename = original_name + ".jpg"
            else:
                file_path = os.path.join(UPLOAD_FOLDER, f.filename)
                if os.path.exists(file_path):
                    counter = 1
                    while os.path.exists(os.path.join(UPLOAD_FOLDER, f"{original_name}({counter}){ext}")):
                        counter += 1
                    f.filename = f"{original_name}({counter}){ext}"
                    file_path = os.path.join(UPLOAD_FOLDER, f.filename)
                f.save(file_path)
                filename = f.filename

            confidence_threshold = 0.85

            # Predict the category of the uploaded file
            image = preprocess_image(file_path)
            predictions = model.predict(image)
            predicted_category, confidence = extract_category(predictions)

            # Get the expected category from the frontend (HTML)
            expected_category = request.form.getlist('file_category[]')[i] 

            if confidence < confidence_threshold:
                error_msg = f"The uploaded file for {category_map[expected_category]} seems to be a random document. Please check and upload again."
                return render_template("error.html", error=error_msg)

            if predicted_category != expected_category:
                error_msg = f"The uploaded file for {category_map[expected_category]} seems to be of type {predicted_category}. Please check and upload again."
                return render_template("error.html", error=error_msg)
            
            img_url = url_for('static', filename=f'temp\\{filename}')

            if predicted_category in category_map.keys():
                dest_folder = os.path.join(BASE_UPLOAD_FOLDER, 'static', predicted_category)
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                dest_path = os.path.join(dest_folder, filename)
                shutil.move(file_path, dest_path)
                
                img_url = url_for('static', filename=f'{predicted_category}/{filename}')
                # img_url = BASE_UPLOAD_FOLDER + img_url
                # img_url = img_url.replace('\\', '/')

            # Store the filename and predicted category in their respective lists
            file_names.append(filename)
            file_categories.append(predicted_category)

        file_data = list(zip(file_names, file_categories))


        # Send the lists to the template
        return render_template("Acknowledgement.html", names=file_names, categories=file_categories, img_path=img_url)

    return render_template("error.html", error="Invalid request method")

@app.route('/list-uploads')
def list_uploads():
    base_dir = os.path.join(BASE_UPLOAD_FOLDER, 'static')
    
    # List all directories in the base_dir
    directories = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    all_files = {}
    
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        
        # Here we sort the files by their modification time in descending order
        sorted_files = sorted(os.listdir(dir_path), key=lambda x: os.path.getmtime(os.path.join(dir_path, x)), reverse=False)
        all_files[directory] = sorted_files
    
    return render_template('list_uploads.html', files_dict=all_files)



#run_ocr
def generic_run_ocr(key, module):
    try:
        ocr_data = module.process_directory_images(module.IMG_DIR)
        session[f'ocr_{key}_data'] = ocr_data or {}
        return jsonify(success=True)
    except Exception as e:
        print(f"Error during OCR {key} processing: {e}")
        return jsonify(success=False, error=str(e))

def generic_display_ocr_results(key, module):
    ocr_data = session.get(f'ocr_{key}_data', {})
    return render_template(f'ocr_{key}_results.html', **ocr_data)

for key, module in OCR_MODULES.items():
    run_view_func = partial(generic_run_ocr, key, module)
    display_view_func = partial(generic_display_ocr_results, key, module)
    
    # Set custom endpoint names
    run_endpoint = f"run_ocr_{key}"
    display_endpoint = f"display_ocr_{key}_results"

    app.add_url_rule(f'/run_ocr_{key}', view_func=run_view_func, methods=['POST'], endpoint=run_endpoint)
    app.add_url_rule(f'/display_ocr_{key}_results', view_func=display_view_func, endpoint=display_endpoint)


# Common functions  ###################################################################################################
def get_image_from_directory(directory_path):
    files = os.listdir(directory_path)
    
    if files:
        img_name = files[0]
        full_path = os.path.join(directory_path, img_name)
        return img_name, full_path
    else:
        print("No file found in the directory")
        return None, None
def delete_image_from_directory(full_path, img_name):
    if full_path:
        try:
            os.remove(full_path)
            print(f"Deleted image {img_name} from the directory.")
        except Exception as e:
            print(f"Error deleting image: {e}")
def extract_data_from_request(fields):
    return {key: request.form.get(key) for key in fields}
############################################################################################################


# Saving result to database

@app.route('/save_edits', methods=['POST'])
def save_edits():
    print("Inside save_edits route")
    fields = ['id_id', 'id_name', 'id_thai_name', 'id_birth_date', 'id_address', 'id_date_of_issue', 'id_date_expire']
    data = extract_data_from_request(fields)
    
    img_name, full_path = get_image_from_directory(DIRECTORY_PATH)

    ocr_id.insert_data_to_db(img_name, data)
    print('Finished editing and saved to database.')

    delete_image_from_directory(full_path, img_name)

    return render_template("index.html")

@app.route('/save_passport_edits', methods=['POST'])
def save_passport_edits():
    print("Inside save_passport_edits route")
    fields = ['pp_type', 'pp_country_code', 'pp_passport_num', 'pp_surname', 'pp_name', 'pp_thai_name', 'pp_nationality', 'pp_birth_date', 'pp_id_num', 'pp_sex', 'pp_place_of_birth', 'pp_height', 'pp_date_of_issue','pp_date_expire']
    data = extract_data_from_request(fields)
    
    img_name, full_path = get_image_from_directory(DIRECTORY_PATH)

    ocr_passport.insert_data_to_db(img_name, data)
    print('Finished editing and saved to database.')

    delete_image_from_directory(full_path, img_name)

    return render_template("index.html")

@app.route('/save_dl_edits', methods=['POST'])
def save_dl_edits():
    print("Inside save_dl_edits route")
    fields = ['dl_no', 'dl_name', 'dl_thai_name', 'dl_birth_date', 'dl_id_num', 'dl_date_of_issue', 'dl_date_expire', 'dl_province']
    data = extract_data_from_request(fields)
    
    img_name, full_path = get_image_from_directory(DIRECTORY_PATH)

    ocr_dl.insert_data_to_db(img_name, data)
    print('Finished editing and saved to database.')

    delete_image_from_directory(full_path, img_name)

    return render_template("index.html")

@app.route('/save_hr1_edits', methods=['POST'])
def save_hr1_edits():
    print("Inside save_hr1_edits route")
    fields = ['hr1_home_id', 'hr1_registration_office', 'hr1_address', 'hr1_village_name', 'hr1_house_name', 'hr1_house_type', 'hr1_house_characteristics', 'hr1_house_registration_date']
    data = extract_data_from_request(fields)
    
    img_name, full_path = get_image_from_directory(DIRECTORY_PATH)

    ocr_hr1.insert_data_to_db(img_name, data)
    print('Finished editing and saved to database.')

    delete_image_from_directory(full_path, img_name)

    return render_template("index.html")

@app.route('/save_hr2_edits', methods=['POST'])
def save_hr2_edits():
    print("Inside save_hr2_edits route")
    fields = [' hr2_vol_num','hr2_order_num','hr2_house_id','hr2_name', 'hr2_nationality', 'hr2_gender', 'hr2_person_id', 'hr2_status', 'hr2_birth_date', 'hr2_mother_name', 'hr2_mother_id', 'hr2_mother_nationality', 'hr2_father_name', 'hr2_father_id', 'hr2_father_nationality', 'hr2_origin', 'hr2_destination']
    data = extract_data_from_request(fields)
    
    img_name, full_path = get_image_from_directory(DIRECTORY_PATH)

    ocr_hr2.insert_data_to_db(img_name, data)
    print('Finished editing and saved to database.')

    delete_image_from_directory(full_path, img_name)

    return render_template("index.html")

@app.route('/save_cm_edits', methods=['POST'])
def save_cm_edits():
    print("Inside save_cm_edits route")
    fields = ['cm_registration_id','cm_company_name','cm_location','cm_date']
    data = extract_data_from_request(fields)
    
    img_name, full_path = get_image_from_directory(DIRECTORY_PATH)

    ocr_cm.insert_data_to_db(img_name, data)
    print('Finished editing and saved to database.')

    delete_image_from_directory(full_path, img_name)

    return render_template("index.html")



if __name__ == '__main__':
    app.run(debug=True)
