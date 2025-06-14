from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
from werkzeug.utils import secure_filename
import webbrowser
import threading
from datetime import datetime
from docx import Document

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change for production use
DATA_DIR = 'data'  # All files stored under this folder

# Allowed extensions for upload
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'csv', 'pptx', 'mp4', 'mp3', 'zip'}

SECTIONS = ['Store', 'Material', 'Employee']  # Your 3 sections

# Create section folders if they don't exist
for section in SECTIONS:
    path = os.path.join(DATA_DIR, section)
    os.makedirs(path, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    section = request.args.get('section', SECTIONS[0])
    section_path = os.path.join(DATA_DIR, section)
    files = []
    for filename in os.listdir(section_path):
        filepath = os.path.join(section_path, filename)
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            files.append({
                'name': filename,
                'size': round(stat.st_size / 1024, 2),
                'mtime': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    return render_template('index.html', sections=SECTIONS, current_section=section, files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    section = request.form['section']
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index', section=section))
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index', section=section))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(DATA_DIR, section, filename))
        flash('File uploaded successfully!')
    else:
        flash('File type not allowed.')
    return redirect(url_for('index', section=section))

@app.route('/delete/<section>/<filename>')
def delete_file(section, filename):
    file_path = os.path.join(DATA_DIR, section, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File deleted successfully!')
    else:
        flash('File not found!')
    return redirect(url_for('index', section=section))

@app.route('/view/<section>/<filename>')
def view_file(section, filename):
    file_path = os.path.join(DATA_DIR, section, filename)
    ext = filename.rsplit('.', 1)[1].lower()

    try:
        if ext in ['pdf', 'png', 'jpg', 'jpeg']:
            return send_from_directory(os.path.join(DATA_DIR, section), filename)
        elif ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return render_template('preview.html', content=content, filename=filename, section=section)
        elif ext == 'docx':
            doc = Document(file_path)
            content = '\n'.join([para.text for para in doc.paragraphs if para.text.strip() != ''])
            return render_template('preview.html', content=content, filename=filename, section=section)
        else:
            flash('Preview not supported for this file type.')
            return redirect(url_for('index', section=section))
    except Exception as e:
        flash(f"Error while previewing file: {str(e)}")
        return redirect(url_for('index', section=section))

@app.route('/save/<section>/<filename>', methods=['POST'])
def save_file(section, filename):
    content = request.form['content']
    file_path = os.path.join(DATA_DIR, section, filename)
    ext = filename.rsplit('.', 1)[1].lower()

    try:
        if ext == 'txt':
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            flash('Text file saved successfully!')
        elif ext == 'docx':
            doc = Document()
            for line in content.split('\n'):
                doc.add_paragraph(line)
            doc.save(file_path)
            flash('Word document saved successfully!')
        else:
            flash('Editing not supported for this file type.')
    except Exception as e:
        flash(f"Error saving file: {str(e)}")
    return redirect(url_for('index', section=section))

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    threading.Timer(1.5, open_browser).start()
    app.run(debug=False)
