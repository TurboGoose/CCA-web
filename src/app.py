import os

from flask import Flask, request, redirect, url_for
from flask import render_template
from werkzeug.utils import secure_filename
from threading import Thread

from consts import DATASET_FOLDER, INDEX_FOLDER
from csv_reader import read_csv_dataset
from indexer import IndexManager

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = DATASET_FOLDER

indexer = IndexManager(INDEX_FOLDER)

@app.get('/')
def show_data():
    filename = request.args.get('filename')

    if not filename:
        # flash
        return render_template('viewer.html', data=None)

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        # flash
        return redirect('/')

    query = request.args.get('query')
    data = handle_search(file_path, query) if query else retrieve_data(file_path)

    return render_template('viewer.html', data=data)


def retrieve_data(file_path):
    return read_csv_dataset(file_path)


def handle_search(file_path, query):
    # searcher = Searcher(dataset_name)
    # data = searcher.search(query)
    return retrieve_data(file_path)[:5]


@app.post('/upload')
def upload_file():
    if 'file' not in request.files:
        # flash('No file part')
        return redirect('/')

    file = request.files['file']
    if file.filename == '':
        # flash('No selected file')
        return redirect('/')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        Thread(target=indexer.index, args=(filename, read_csv_dataset(file_path))).start()
        return redirect(url_for('show_data', filename=filename))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


if __name__ == '__main__':
    app.run(debug=True, port=8080)
