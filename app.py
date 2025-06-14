from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
import os
from werkzeug.utils import secure_filename
from docx import Document
import webbrowser
import threading

app = Flask(__name__)
app.secret_key = 'supersecretkey'

BASE_DIR = 'data'
SECTIONS = ['Store', 'Material', 'Employee']

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_files(section):
    folder_path = os.path.join(BASE_DIR, section)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return os.listdir(folder_path)

@app.route('/')
def index():
    section = request.args.get('section', 'Store')
    files = get_files(section)
    return render_template('index.html', sections=SECTIONS, current_section=section, files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    section = request.form['section']
    if 'file' not in request.files:
        return jsonify({'status': 'fail', 'message': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'fail', 'message': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        folder_path = os.path.join(BASE_DIR, section)
        file.save(os.path.join(folder_path, filename))
        return jsonify({'status': 'success', 'message': 'File uploaded successfully'})
    return jsonify({'status': 'fail', 'message': 'Invalid file type'})

@app.route('/view/<section>/<filename>')
def view_file(section, filename):
    folder_path = os.path.join(BASE_DIR, section)
    return send_from_directory(folder_path, filename)

@app.route('/delete/<section>/<filename>', methods=['POST'])
def delete_file(section, filename):
    folder_path = os.path.join(BASE_DIR, section)
    file_path = os.path.join(folder_path, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'status': 'success', 'message': 'File deleted successfully'})
    return jsonify({'status': 'fail', 'message': 'File not found'})

@app.route('/edit/<section>/<filename>', methods=['GET', 'POST'])
def edit_file(section, filename):
    folder_path = os.path.join(BASE_DIR, section)
    file_path = os.path.join(folder_path, filename)

    if request.method == 'POST':
        new_content = request.form['content']
        if filename.endswith('.txt'):
            with open(file_path, 'w') as f:
                f.write(new_content)
        elif filename.endswith('.docx'):
            doc = Document()
            doc.add_paragraph(new_content)
            doc.save(file_path)
        return jsonify({'status': 'success', 'message': 'File saved successfully'})

    content = ""
    if filename.endswith('.txt'):
        with open(file_path, 'r') as f:
            content = f.read()
    elif filename.endswith('.docx'):
        doc = Document(file_path)
        content = "\n".join([para.text for para in doc.paragraphs])

    return jsonify({'content': content})

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    threading.Timer(1.25, open_browser).start()
    app.run(debug=False)
