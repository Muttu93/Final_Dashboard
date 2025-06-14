# app.py
import os
import mimetypes
import shutil
import webbrowser
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify, render_template_string
from werkzeug.utils import secure_filename
from docx import Document
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SECTIONS = ['Store', 'Material', 'Employee']
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'xlsx', 'xls', 'png', 'jpg', 'jpeg'}

for section in SECTIONS:
    os.makedirs(os.path.join(DATA_DIR, section), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    section_files = {}
    for section in SECTIONS:
        section_path = os.path.join(DATA_DIR, section)
        files = os.listdir(section_path)
        section_files[section] = files
    return render_template('index.html', sections=SECTIONS, section_files=section_files)

@app.route('/upload', methods=['POST'])
def upload_file():
    section = request.form['section']
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(DATA_DIR, section, filename))
        flash('File uploaded successfully!')
    return redirect(url_for('index'))

@app.route('/view/<section>/<filename>')
def view_file(section, filename):
    file_path = os.path.join(DATA_DIR, section, filename)
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ['pdf', 'png', 'jpg', 'jpeg']:
        return send_from_directory(os.path.join(DATA_DIR, section), filename)
    elif ext == 'txt':
        with open(file_path, 'r') as f:
            content = f.read()
        return render_template_string("""<h3>{{filename}}</h3><pre>{{content}}</pre><a href='/'>Back</a>""", filename=filename, content=content)
    elif ext == 'docx':
        doc = Document(file_path)
        fullText = '\n'.join([para.text for para in doc.paragraphs])
        return render_template_string("""<h3>{{filename}}</h3><pre>{{content}}</pre><a href='/'>Back</a>""", filename=filename, content=fullText)
    elif ext in ['xlsx', 'xls']:
        df = pd.read_excel(file_path)
        return render_template_string("""<h3>{{filename}}</h3>{{ df.to_html() }}<br><a href='/'>Back</a>""", filename=filename, df=df)
    else:
        return send_from_directory(os.path.join(DATA_DIR, section), filename)

@app.route('/delete/<section>/<filename>', methods=['POST'])
def delete_file(section, filename):
    os.remove(os.path.join(DATA_DIR, section, filename))
    flash('File deleted successfully!')
    return redirect(url_for('index'))

@app.route('/edit/<section>/<filename>', methods=['GET', 'POST'])
def edit_file(section, filename):
    file_path = os.path.join(DATA_DIR, section, filename)
    ext = filename.rsplit('.', 1)[1].lower()
    if request.method == 'POST':
        new_content = request.form['content']
        if ext == 'txt':
            with open(file_path, 'w') as f:
                f.write(new_content)
        elif ext == 'docx':
            doc = Document()
            for line in new_content.split('\n'):
                doc.add_paragraph(line)
            doc.save(file_path)
        flash('File updated successfully!')
        return redirect(url_for('index'))
    else:
        content = ''
        if ext == 'txt':
            with open(file_path, 'r') as f:
                content = f.read()
        elif ext == 'docx':
            doc = Document(file_path)
            content = '\n'.join([para.text for para in doc.paragraphs])
        return render_template('edit.html', section=section, filename=filename, content=content)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query').lower()
    result_files = {}
    for section in SECTIONS:
        section_path = os.path.join(DATA_DIR, section)
        files = [f for f in os.listdir(section_path) if query in f.lower()]
        if files:
            result_files[section] = files
    return render_template('index.html', sections=SECTIONS, section_files=result_files)

if __name__ == '__main__':
    webbrowser.open_new('http://127.0.0.1:5000')
    app.run(debug=True)
