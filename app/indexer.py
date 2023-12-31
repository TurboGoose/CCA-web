import os
import shutil

from whoosh.fields import NUMERIC, TEXT, Schema
from whoosh.index import create_in

import config
from datasets import read_csv_dataset


def init_index_storage():
    if not os.path.exists(config.INDEX_FOLDER):
        os.mkdir(config.INDEX_FOLDER)


def _compose_index_dir(index_name: str) -> str:
    return os.path.join(config.INDEX_FOLDER, index_name)


def create_index(dataset_path):
    index_name = os.path.basename(dataset_path)
    index_dir = _compose_index_dir(index_name)
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

    schema = Schema(id=NUMERIC(stored=True, unique=True, bits=64, sortable=True), text=TEXT)
    index = create_in(index_dir, schema)
    writer = index.writer()

    dataset = read_csv_dataset(dataset_path)
    for i, row in dataset.iterrows():
        writer.add_document(id=i, text=row["text"])

    writer.commit()


def delete_index(dataset_path: str) -> None:
    index_name = os.path.basename(dataset_path)
    index_dir = _compose_index_dir(index_name)
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir, ignore_errors=True)


def rename_index(dataset_path: str, new_index_name: str) -> None:
    old_index_name = os.path.basename(dataset_path)
    old_index_dir = _compose_index_dir(old_index_name)
    new_index_dir = _compose_index_dir(new_index_name)
    if os.path.exists(new_index_dir):
        raise ValueError(
            f"Cannot rename index '{old_index_name}': "
            f"index with new name '{new_index_name}' already exists"
        )

    if not os.path.exists(old_index_dir):
        raise ValueError(f"Cannot rename index '{old_index_name}', because it does not exist")
    os.rename(old_index_dir, new_index_dir)
