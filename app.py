from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
import shutil
import datetime
import webbrowser
from werkzeug.utils import secure_filename
from docx import Document

app = Flask(__name__)
app.secret_key = 'your_secret_key'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SECTIONS = ['Employee', 'Material', 'Store']
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_files(section):
    section_path = os.path.join(DATA_DIR, section)
    files = []
    if os.path.exists(section_path):
        for filename in os.listdir(section_path):
            filepath = os.path.join(section_path, filename)
            if os.path.isfile(filepath):
                modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                files.append({'name': filename, 'mtime': modified_time})
    return files

@app.route('/')
def index():
    section = request.args.get('section', 'Employee')
    query = request.args.get('query', '').lower()
    files = get_files(section)
    if query:
        files = [f for f in files if query in f['name'].lower()]
    return render_template('index.html', sections=SECTIONS, section=section, files=files, query=query)

@app.route('/upload', methods=['POST'])
def upload_file():
    section = request.form.get('section')
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.referrer)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.referrer)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(DATA_DIR, section, filename)
        file.save(save_path)
        flash('File uploaded successfully!')
    return redirect(url_for('index', section=section))

@app.route('/delete/<section>/<filename>', methods=['POST'])
def delete_file(section, filename):
    file_path = os.path.join(DATA_DIR, section, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File deleted successfully!')
    return redirect(url_for('index', section=section))

@app.route('/view/<section>/<filename>')
def view_file(section, filename):
    file_path = os.path.join(DATA_DIR, section, filename)
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'pdf' or ext in ['png', 'jpg', 'jpeg']:
        return send_from_directory(os.path.join(DATA_DIR, section), filename)
    elif ext == 'txt':
        with open(file_path, 'r') as f:
            content = f.read()
        return render_template('preview.html', content=content, filename=filename, section=section)
    elif ext == 'docx':
        doc = Document(file_path)
        content = '\n'.join([para.text for para in doc.paragraphs])
        return render_template('preview.html', content=content, filename=filename, section=section)
    else:
        flash('File type not viewable')
        return redirect(url_for('index', section=section))

@app.route('/edit/<section>/<filename>', methods=['GET', 'POST'])
def edit_file(section, filename):
    file_path = os.path.join(DATA_DIR, section, filename)
    ext = filename.rsplit('.', 1)[1].lower()
    if request.method == 'POST':
        content = request.form['content']
        if ext == 'txt':
            with open(file_path, 'w') as f:
                f.write(content)
        elif ext == 'docx':
            doc = Document()
            for line in content.split('\n'):
                doc.add_paragraph(line)
            doc.save(file_path)
        flash('File updated successfully!')
        return redirect(url_for('index', section=section))
    else:
        if ext == 'txt':
            with open(file_path, 'r') as f:
                content = f.read()
        elif ext == 'docx':
            doc = Document(file_path)
            content = '\n'.join([para.text for para in doc.paragraphs])
        else:
            flash('File type not editable')
            return redirect(url_for('index', section=section))
        return render_template('edit.html', content=content, filename=filename, section=section)

if __name__ == '__main__':
    port = 5000
    webbrowser.open(f'http://127.0.0.1:{port}')
    app.run(debug=False, port=port)
