import os

from flask import Flask, request, redirect, url_for
from flask import render_template
from werkzeug.utils import secure_filename
from threading import Thread
from db import *

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
        return render_template('viewer.html', data=None, other_datasets=get_dataset_list())

    dataset_path = os.path.join(DATASET_FOLDER, dataset_name)
    if not os.path.exists(dataset_path):
        # flash
        return redirect('/')

    query = request.args.get('query')
    data = handle_search(dataset_path, query) if query else retrieve_data(dataset_path)

    current_dataset = dataset_name
    other_datasets = get_dataset_list(current_dataset=current_dataset)

    current_label = get_labels_for_dataset(dataset_name)[0]  # TODO: replace to actual chosen label
    other_labels = get_label_list_for_dataset(current_dataset, current_label=current_label)

    return render_template('viewer.html', data=data, query=query,
                           current_label=current_label, other_labels=other_labels,
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
        save_dataset(dataset_name)
        dataset_path = os.path.join(DATASET_FOLDER, dataset_name)
        file.save(dataset_path)
        Thread(target=indexer.index, args=(dataset_path, )).start()
        return redirect(url_for('show_data', dataset=dataset_name))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


def get_label_list_for_dataset(dataset, current_label=None):
    all_labels = get_labels_for_dataset(dataset)
    if current_label is not None and current_label in all_labels:
        all_labels.remove(current_label)
    return all_labels


def get_dataset_list(current_dataset=None):
    all_datasets = get_datasets()
    if current_dataset is not None and current_dataset in all_datasets:
        all_datasets.remove(current_dataset)
    return all_datasets


if __name__ == '__main__':
    app.run(debug=True, port=8080)
