import os
from tempfile import TemporaryDirectory
from threading import Thread

from flask import Flask, request, redirect, url_for, send_file, render_template
from pandas import DataFrame
from werkzeug.security import safe_join
from werkzeug.utils import secure_filename

import db
from consts import DATASET_FOLDER, INDEX_FOLDER
from datasets import *
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

    dataset_path = compose_dataset_path(dataset_name)
    if not os.path.exists(dataset_path):
        # flash
        return redirect('/')

    query = request.args.get('query')
    data = handle_search(dataset_path, query) if query else read_csv_dataset(dataset_path)

    current_dataset = dataset_name
    other_datasets = get_dataset_list(current_dataset=current_dataset)

    labels = db.get_labels_for_dataset(dataset_name)

    return render_template('viewer.html', data=data, query=query, labels=labels,
                           current_dataset=current_dataset, other_datasets=other_datasets)


@app.post('/label')
def add_new_label():
    dataset_name = request.form.get('dataset')
    if not dataset_name:
        # flash
        return redirect(url_for('show_data'))
    new_label = request.form.get('label')
    if new_label not in db.get_labels_for_dataset(dataset_name):
        db.save_label_for_dataset(new_label, dataset_name)
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
        db.save_dataset(dataset_name)
        transform_and_write_csv_dataset(dataset_path)
        Thread(target=indexer.create_index, args=(dataset_path,)).start()
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


@app.get('/download')
def download_dataset():
    file_format = request.args.get("format", default="csv")
    dataset_name = request.args.get("dataset")
    dataset_path = compose_dataset_path(dataset_name)

    if file_format == "csv":
        file_to_send = "../" + dataset_path
        return send_file(file_to_send, as_attachment=True)

    elif file_format == "json":
        temp_dataset_name = extract_filename(dataset_name) + ".json"
        with TemporaryDirectory() as tempdir:
            data = read_csv_dataset(dataset_path)
            data.to_json(os.path.join(tempdir, temp_dataset_name), orient="records")
            file_to_send = safe_join(tempdir, temp_dataset_name)
            return send_file(file_to_send, as_attachment=True)


@app.post("/dataset/delete")
def delete_dataset():
    dataset_name = request.form.get('dataset')
    dataset_path = compose_dataset_path(dataset_name)
    db.delete_dataset(dataset_name)
    delete_csv_dataset(dataset_path)
    indexer.delete_index(dataset_path)
    return redirect(url_for('show_data', dataset=None))


def extract_filename(dataset_name: str) -> str:
    return dataset_name[:dataset_name.rfind(".")]


def set_label_for_dataset_rows(dataset: DataFrame, ids: list[int], label: str) -> None:
    dataset.loc[ids, "label"] = label


def compose_dataset_path(dataset_name):
    return safe_join(DATASET_FOLDER, dataset_name)


def handle_search(dataset_path, query):
    return search(dataset_path, query)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


def get_dataset_list(current_dataset=None):
    all_datasets = db.get_datasets()
    if current_dataset is not None and current_dataset in all_datasets:
        all_datasets.remove(current_dataset)
    return all_datasets


if __name__ == '__main__':
    app.run(debug=True, port=8080)
