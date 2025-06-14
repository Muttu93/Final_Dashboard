from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
from datetime import datetime
import webbrowser
from werkzeug.utils import secure_filename
from docx import Document

app = Flask(__name__)
app.secret_key = 'your_secret_key'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

SECTIONS = ['Store', 'Material', 'Employee']

def get_file_dates(section):
    section_path = os.path.join(DATA_DIR, section)
    files = os.listdir(section_path)
    file_dates = {}
    for file in files:
        path = os.path.join(section_path, file)
        mod_time = os.path.getmtime(path)
        file_dates[file] = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
    return file_dates

@app.route('/')
def index():
    return render_template('index.html', sections=SECTIONS, current_section=None)

@app.route('/dashboard/<section>')
def dashboard(section):
    if section not in SECTIONS:
        flash('Invalid section!', 'error')
        return redirect(url_for('index'))
    
    query = request.args.get('query', '').lower()
    section_path = os.path.join(DATA_DIR, section)
    os.makedirs(section_path, exist_ok=True)
    files = os.listdir(section_path)

    if query:
        files = [f for f in files if query in f.lower()]
    
    file_dates = get_file_dates(section)
    return render_template('index.html', sections=SECTIONS, current_section=section, files=files, file_dates=file_dates, query=query)

@app.route('/upload/<section>', methods=['POST'])
def upload_file(section):
    if section not in SECTIONS:
        flash('Invalid section!', 'error')
        return redirect(url_for('index'))
    
    file = request.files.get('file')
    if file:
        filename = secure_filename(file.filename)
        section_path = os.path.join(DATA_DIR, section)
        os.makedirs(section_path, exist_ok=True)
        file.save(os.path.join(section_path, filename))
        flash('File uploaded successfully!', 'success')
    else:
        flash('No file selected.', 'error')
    
    return redirect(url_for('dashboard', section=section))

@app.route('/view/<section>/<filename>')
def view_file(section, filename):
    file_path = os.path.join(DATA_DIR, section, filename)
    ext = filename.rsplit('.', 1)[-1].lower()

    if ext == 'txt':
        with open(file_path, 'r') as f:
            content = f.read()
        return render_template('preview.html', filename=filename, content=content, section=section)
    
    elif ext == 'docx':
        doc = Document(file_path)
        content = "\n".join([para.text for para in doc.paragraphs])
        return render_template('preview.html', filename=filename, content=content, section=section)
    
    else:
        return send_from_directory(os.path.join(DATA_DIR, section), filename)

@app.route('/edit/<section>/<filename>', methods=['POST'])
def edit_file(section, filename):
    content = request.form.get('content')
    file_path = os.path.join(DATA_DIR, section, filename)
    ext = filename.rsplit('.', 1)[-1].lower()

    if ext == 'txt':
        with open(file_path, 'w') as f:
            f.write(content)
    elif ext == 'docx':
        doc = Document()
        for line in content.split('\n'):
            doc.add_paragraph(line)
        doc.save(file_path)

    flash('File saved successfully!', 'success')
    return redirect(url_for('dashboard', section=section))

@app.route('/delete/<section>/<filename>')
def delete_file(section, filename):
    try:
        os.remove(os.path.join(DATA_DIR, section, filename))
        flash('File deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting file.', 'error')
    return redirect(url_for('dashboard', section=section))

if __name__ == '__main__':
    port = 5000
    webbrowser.open(f'http://127.0.0.1:{port}/')
    app.run(debug=True, port=port)
