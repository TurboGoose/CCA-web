import os
from threading import Thread
from pandas import DataFrame

from flask import Flask, request, redirect, url_for
from flask import render_template
from werkzeug.utils import secure_filename

from consts import DATASET_FOLDER, INDEX_FOLDER
from db import *
from indexer import IndexManager
from searcher import search
from csv_util import write_csv_dataset, read_csv_dataset, transform_and_write_csv_dataset

app = Flask(__name__)

indexer = IndexManager(INDEX_FOLDER)


@app.get('/')
def show_data():
    dataset_name = request.args.get('dataset')

    if not dataset_name:
        # flash
        return render_template('viewer.html', data=None, other_datasets=get_dataset_list())

    dataset_path = compose_dataset_path(dataset_name)
    if not os.path.exists(dataset_path):
        # flash
        return redirect('/')

    query = request.args.get('query')
    data = handle_search(dataset_path, query) if query else read_csv_dataset(dataset_path)

    current_dataset = dataset_name
    other_datasets = get_dataset_list(current_dataset=current_dataset)

    current_label = get_current_label(dataset_name)
    other_labels = get_label_list_for_dataset(current_dataset, current_label=current_label)

    return render_template('viewer.html', data=data, query=query,
                           current_label=current_label, other_labels=other_labels,
                           current_dataset=current_dataset, other_datasets=other_datasets)


@app.post('/label')
def add_new_label():
    dataset_name = request.form.get('dataset')
    if not dataset_name:
        # flash
        return redirect(url_for('show_data'))
    new_label = request.form.get('label')
    if new_label not in get_label_list_for_dataset(dataset_name):
        add_label_for_dataset(new_label, dataset_name)
    # else: flash
    return redirect(url_for('show_data', dataset=dataset_name))


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
        dataset_path = compose_dataset_path(dataset_name)

        file.save(dataset_path)
        add_dataset_to_db(dataset_name)
        transform_and_write_csv_dataset(dataset_path)
        Thread(target=indexer.index, args=(dataset_path,)).start()
        return redirect(url_for('show_data', dataset=dataset_name))


@app.post('/mark')
def mark_label():
    mark_data = request.json
    dataset_path = compose_dataset_path(mark_data["dataset"])
    dataset = read_csv_dataset(dataset_path)
    mark_data["dataset"] = dataset
    set_label_for_dataset_rows(**mark_data)
    write_csv_dataset(dataset, dataset_path)
    return "", 200


def set_label_for_dataset_rows(dataset: DataFrame, ids: list[int], label: str) -> None:
    dataset.loc[ids, "label"] = label


def compose_dataset_path(dataset_name):
    return os.path.join(DATASET_FOLDER, dataset_name)


def get_current_label(dataset_name):
    all_labels = get_labels_for_dataset(dataset_name)
    if not all_labels:
        return None
    return all_labels[0]  # TODO: replace to actual chosen label


def handle_search(dataset_path, query):
    return search(dataset_path, query)


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
