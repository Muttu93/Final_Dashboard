from flask import Flask, render_template, request, redirect, send_from_directory, url_for
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from docx import Document

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATA_FOLDER = 'data'
SECTIONS = ['Material', 'Store', 'Employee']

def get_files(section, search_query=None):
    folder = os.path.join(DATA_FOLDER, section)
    files = []
    if not os.path.exists(folder):
        os.makedirs(folder)
    for filename in os.listdir(folder):
        if search_query and search_query.lower() not in filename.lower():
            continue
        path = os.path.join(folder, filename)
        upload_time = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
        files.append({'name': filename, 'path': f'{section}/{filename}', 'upload_time': upload_time})
    return files

@app.route('/', methods=['GET'])
def index():
    section = request.args.get('section', SECTIONS[0])
    search_query = request.args.get('search', '').strip()
    files = get_files(section, search_query)
    return render_template('index.html', sections=SECTIONS, selected_section=section, files=files, search_query=search_query)

@app.route('/upload', methods=['POST'])
def upload_file():
    section = request.form.get('section')
    if 'file' not in request.files or not section:
        return redirect(url_for('index'))
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        folder = os.path.join(DATA_FOLDER, section)
        os.makedirs(folder, exist_ok=True)
        file.save(os.path.join(folder, filename))
    return redirect(url_for('index', section=section))

@app.route('/delete', methods=['POST'])
def delete_files():
    section = request.form.get('section')
    files_to_delete = request.form.getlist('files')
    folder = os.path.join(DATA_FOLDER, section)
    for filename in files_to_delete:
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    return redirect(url_for('index', section=section))

@app.route('/view/<path:filename>')
def view_file(filename):
    section = filename.split('/')[0]
    file_path = filename[len(section)+1:]
    return send_from_directory(os.path.join(DATA_FOLDER, section), file_path)

@app.route('/edit/<path:filename>', methods=['GET', 'POST'])
def edit_file(filename):
    section = filename.split('/')[0]
    file_path = filename[len(section)+1:]
    full_path = os.path.join(DATA_FOLDER, section, file_path)

    if request.method == 'POST':
        content = request.form.get('content')
        if filename.endswith('.txt') or filename.endswith('.md'):
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        elif filename.endswith('.docx'):
            doc = Document()
            doc.add_paragraph(content)
            doc.save(full_path)
        return redirect(url_for('index', section=section))

    file_content = ''
    if filename.endswith('.txt') or filename.endswith('.md'):
        with open(full_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
    elif filename.endswith('.docx'):
        doc = Document(full_path)
        file_content = '\n'.join([para.text for para in doc.paragraphs])

    return render_template('edit.html', filename=filename, content=file_content)

if __name__ == '__main__':
    import webbrowser
    from threading import Timer

    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000/')

    Timer(1, open_browser).start()
    app.run(debug=True)
