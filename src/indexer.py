import os

from whoosh.fields import *
from whoosh.index import create_in

from csv_reader import read_csv_dataset


class IndexManager:
    def __init__(self, indices_dir):
        self.indices_dir = indices_dir
        if not os.path.exists(indices_dir):
            os.mkdir(indices_dir)

    def index(self, dataset_path):
        index_name = os.path.basename(dataset_path)
        index_dir = os.path.join(self.indices_dir, index_name)
        if not os.path.exists(index_dir):
            os.mkdir(index_dir)

        schema = Schema(id=NUMERIC(stored=True, unique=True, bits=64, sortable=True), text=TEXT)
        index = create_in(index_dir, schema)
        writer = index.writer()

        dataset = read_csv_dataset(dataset_path)
        for i, row in dataset.iterrows():
            writer.add_document(id=i, text=row["text"])

        writer.commit()

    # index deletion
    # index update