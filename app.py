from flask import Flask, request, render_template
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/13-12-2023'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

file_metadata = []

def normalize_description(description):
    return description.lower().strip() if description else ''

def normalize_tags(tags):
    return [tag.strip().lower() for tag in tags.split(',')] if tags else ''

def save_file_metadata_auto(filename, date_time):
    metadata = {
        'filename': filename,
        'date_time': date_time,
        'automatic_index': True
    }
    file_metadata.append(metadata)

def save_file_metadata_manual(filename, description, tags):
    normalized_description = normalize_description(description)
    normalized_tags = normalize_tags(tags)
    
    metadata = {
        'filename': filename,
        'description': normalized_description,
        'tags': normalized_tags,
        'automatic_index': False
    }
    file_metadata.append(metadata)

def move_file_to_category(file_path, folder_name):
    new_folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
    
    new_path = os.path.join(new_folder_path, os.path.basename(file_path))
    os.replace(file_path, new_path)

def evaluate_classification():
    uploads_path = app.config['UPLOAD_FOLDER']
    extensions_folders = {'CSV': 'Csv Files', 'TXT': 'Txt_Files', 'PDF': 'Pdf Files'}

    correct_classification = {ext: 0 for ext in extensions_folders.values()}

    for root, _, files in os.walk(uploads_path):
        for file in files:
            _, ext = os.path.splitext(file)
            ext = ext[1:].upper()

            if ext in extensions_folders:
                expected_folder = extensions_folders[ext]
                file_path = os.path.join(root, file)
                if expected_folder in file_path:
                    correct_classification[expected_folder] += 1

    return correct_classification

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/success')
def upload_success():
    return render_template('upload_success.html')

@app.route('/uploader', methods=['POST'])
def uploader():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file:
            file_extension = os.path.splitext(uploaded_file.filename)[1]
            if file_extension in {'.csv', '.txt', '.pdf'}:
                description = request.form.get('description')
                tags = request.form.get('tags')
                automatic_index = 'automatic_index' in request.form

                now = datetime.now()
                date_time = now.strftime("%Y-%m-%d %H:%M:%S")

                file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
                uploaded_file.save(file_path)

                if automatic_index:
                    save_file_metadata_auto(uploaded_file.filename, date_time)
                else:
                    save_file_metadata_manual(uploaded_file.filename, description, tags)

                move_file_to_category(file_path, file_extension[1:].upper() + '_Files')

                return render_template('upload_success.html')
            else:
                return 'Extension de fichier non autorisée !'

@app.route('/evaluation')
def evaluation():
    evaluation_results = evaluate_classification()
    return render_template('evaluation.html', results=evaluation_results)

if __name__ == '__main__':
    app.run(debug=True)
