from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
import shutil
import webbrowser
from werkzeug.utils import secure_filename
from docx import Document
import pandas as pd

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # safe for local
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'data')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SECTIONS = ['Store', 'Material', 'Employee']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    section = request.args.get('section', 'Store')
    search_query = request.args.get('search', '').lower()

    files = []
    section_path = os.path.join(UPLOAD_FOLDER, section)
    if os.path.exists(section_path):
        for file in os.listdir(section_path):
            if search_query in file.lower():
                files.append(file)
    return render_template('index.html', files=files, sections=SECTIONS, current_section=section)

@app.route('/upload', methods=['POST'])
def upload_file():
    section = request.form['section']
    if 'file' not in request.files:
        flash('No file part.', 'error')
        return redirect(url_for('index', section=section))
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, section, filename)
        file.save(save_path)
        flash('File uploaded successfully.', 'success')
    else:
        flash('Invalid file type.', 'error')
    return redirect(url_for('index', section=section))

@app.route('/delete/<section>/<filename>')
def delete_file(section, filename):
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, section, filename))
        flash('File deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'error')
    return redirect(url_for('index', section=section))

@app.route('/view/<section>/<filename>')
def view_file(section, filename):
    filepath = os.path.join(UPLOAD_FOLDER, section, filename)
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ['txt', 'docx']:
        return redirect(url_for('edit_file', section=section, filename=filename))
    elif ext == 'xlsx':
        df = pd.read_excel(filepath)
        return render_template('excel_preview.html', data=df.to_html(), filename=filename, section=section)
    else:
        return send_from_directory(os.path.join(UPLOAD_FOLDER, section), filename)

@app.route('/edit/<section>/<filename>', methods=['GET', 'POST'])
def edit_file(section, filename):
    filepath = os.path.join(UPLOAD_FOLDER, section, filename)
    ext = filename.rsplit('.', 1)[1].lower()

    if request.method == 'POST':
        content = request.form['content']
        if ext == 'txt':
            with open(filepath, 'w') as f:
                f.write(content)
        elif ext == 'docx':
            doc = Document()
            doc.add_paragraph(content)
            doc.save(filepath)
        flash('File edited successfully.', 'success')
        return redirect(url_for('index', section=section))

    if ext == 'txt':
        with open(filepath, 'r') as f:
            content = f.read()
    elif ext == 'docx':
        doc = Document(filepath)
        content = '\n'.join([p.text for p in doc.paragraphs])
    else:
        flash('Unsupported file for editing.', 'error')
        return redirect(url_for('index', section=section))

    return render_template('edit.html', filename=filename, section=section, content=content)

if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)
