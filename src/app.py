import os

from flask import Flask, request, redirect, url_for
from flask import render_template
from werkzeug.utils import secure_filename
from threading import Thread

from consts import DATASET_FOLDER, INDEX_FOLDER
from csv_reader import read_csv_dataset
from indexer import IndexManager
from searcher import search

app = Flask(__name__)

indexer = IndexManager(INDEX_FOLDER)


@app.get('/')
def show_data():
    dataset_name = request.args.get('dataset')

    if not dataset_name:
        # flash
        return render_template('viewer.html', data=None, other_datasets=list_files())

    dataset_path = os.path.join(DATASET_FOLDER, dataset_name)
    if not os.path.exists(dataset_path):
        # flash
        return redirect('/')

    query = request.args.get('query')
    data = handle_search(dataset_path, query) if query else retrieve_data(dataset_path)

    current_dataset = dataset_name
    other_datasets = list_files(exclude=current_dataset)
    return render_template('viewer.html', data=data, query=query,
                           current_dataset=current_dataset, other_datasets=other_datasets)


def retrieve_data(dataset_path):
    return read_csv_dataset(dataset_path)


def handle_search(dataset_path, query):
    return search(dataset_path, query)


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
        dataset_name = secure_filename(file.filename)
        dataset_path = os.path.join(DATASET_FOLDER, dataset_name)
        file.save(dataset_path)
        Thread(target=indexer.index, args=(dataset_path, )).start()
        return redirect(url_for('show_data', dataset=dataset_name))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


def list_files(exclude=None):
    files = []
    with os.scandir(DATASET_FOLDER) as it:
        for entry in it:
            if entry.name.endswith(".csv") and entry.is_file() and entry.name != exclude:
                files.append(entry.name)
    return files


if __name__ == '__main__':
    app.run(debug=True, port=8080)
