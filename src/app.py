import os
import sys
from tempfile import TemporaryDirectory
from threading import Thread

from flask import Flask, request, redirect, url_for, send_file, render_template
from pandas import DataFrame
from werkzeug.security import safe_join
from werkzeug.utils import secure_filename

import models
from config import DATASET_FOLDER, INDEX_FOLDER, DATA_FOLDER, DATABASE_FILE
from datasets import (
    init_dataset_storage,
    read_csv_dataset,
    transform_and_write_csv_dataset,
    write_csv_dataset,
    delete_csv_dataset,
    rename_csv_dataset,
)
from indexer import IndexManager
from searcher import search

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.abspath(DATABASE_FILE)
models.db.init_app(app)

if not os.path.exists(DATA_FOLDER):
    os.mkdir(DATA_FOLDER)

init_dataset_storage()
indexer = IndexManager(INDEX_FOLDER)


@app.get("/")
def show_data():
    dataset_name = request.args.get("dataset")

    if not dataset_name:
        # flash
        return render_template("viewer.html", data=None, other_datasets=get_dataset_list())

    dataset_path = compose_dataset_path(dataset_name)
    if not os.path.exists(dataset_path):
        return redirect("/")

    query = request.args.get("query")
    data = handle_search(dataset_path, query) if query else read_csv_dataset(dataset_path)

    current_dataset = dataset_name
    other_datasets = get_dataset_list(current_dataset=current_dataset)

    labels = models.get_labels_for_dataset(dataset_name)

    return render_template(
        "viewer.html",
        data=data,
        query=query,
        labels=labels,
        current_dataset=current_dataset,
        other_datasets=other_datasets,
    )


@app.post("/label")
def add_new_label():
    dataset_name = request.form.get("dataset")
    if not dataset_name:
        # flash
        return redirect(url_for("show_data"))
    new_label = request.form.get("label")
    if new_label not in models.get_labels_for_dataset(dataset_name):
        models.save_label_for_dataset(new_label, dataset_name)
    # else: flash
    return redirect(url_for("show_data", dataset=dataset_name))


@app.post("/upload")
def upload_file():
    if "file" not in request.files:
        # flash("No file part")
        return redirect("/")

    file = request.files["file"]
    if file.filename == "":
        # flash("No selected file")
        return redirect("/")
    if file and allowed_file(file.filename):
        dataset_name = secure_filename(file.filename)
        dataset_path = compose_dataset_path(dataset_name)

        file.save(dataset_path)
        models.save_dataset(dataset_name)
        transform_and_write_csv_dataset(dataset_path)
        Thread(target=indexer.create_index, args=(dataset_path,)).start()
        return redirect(url_for("show_data", dataset=dataset_name))


@app.post("/mark")
def mark_label():
    mark_data = request.json
    dataset_path = compose_dataset_path(mark_data["dataset"])
    dataset = read_csv_dataset(dataset_path)
    mark_data["dataset"] = dataset
    set_label_for_dataset_rows(**mark_data)
    write_csv_dataset(dataset, dataset_path)
    return "", 200


@app.get("/download")
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
    dataset_name = request.form.get("dataset")
    dataset_path = compose_dataset_path(dataset_name)
    models.delete_dataset(dataset_name)
    delete_csv_dataset(dataset_path)
    indexer.delete_index(dataset_path)
    return redirect(url_for("show_data", dataset=None))


@app.post("/dataset/rename")
def rename_dataset():
    dataset_name = request.form.get("dataset")
    dataset_path = compose_dataset_path(dataset_name)
    new_name = request.form.get("new_name")
    try:
        rename_csv_dataset(dataset_path, new_name)
        indexer.rename_index(dataset_path, new_name)
        models.rename_dataset(dataset_name, new_name)
    except ValueError:
        new_name = dataset_name
        # flash
    return redirect(url_for("show_data", dataset=new_name))


@app.post("/label/rename")
def rename_label():
    dataset = request.form.get("dataset")
    old_name = request.form.get("old_name")
    new_name = request.form.get("new_name")
    models.rename_label_for_dataset(dataset, old_name, new_name)
    return redirect(url_for("show_data", dataset=dataset))


@app.post("/label/delete")
def delete_label():
    dataset = request.form.get("dataset")
    label = request.form.get("label")
    models.delete_label_for_dataset(label, dataset)
    return redirect(url_for("show_data", dataset=dataset))


def extract_filename(dataset_name: str) -> str:
    return dataset_name[: dataset_name.rfind(".")]


def set_label_for_dataset_rows(dataset: DataFrame, ids: list[int], label: str) -> None:
    dataset.loc[ids, "label"] = label


def compose_dataset_path(dataset_name):
    return safe_join(DATASET_FOLDER, dataset_name)


def handle_search(dataset_path, query):
    return search(dataset_path, query)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "csv"


def get_dataset_list(current_dataset=None):
    all_datasets = models.get_datasets()
    if current_dataset is not None and current_dataset in all_datasets:
        all_datasets.remove(current_dataset)
    return all_datasets


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            with app.app_context():
                models.init_db()
    else:
        app.run(port=8080, debug=True)
