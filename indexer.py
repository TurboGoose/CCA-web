import os
from whoosh.index import create_in, open_dir
from whoosh.fields import *

class DatasetIndexer:
    def __init__(self, indices_dir):
        self.indices_dir = indices_dir
        if not os.path.exists(indices_dir):
            os.mkdir(indices_dir)

    def index(self, index_name, dataset):
        index_dir = os.path.join(self.indices_dir, index_name);
        if not os.path.exists(index_dir):
            os.mkdir(index_dir)

        schema = Schema(username=TEXT, text=TEXT)
        index = create_in(index_dir, schema)
        writer = index.writer()

        for i, row in dataset.iterrows():
            writer.add_document(username=row["username"], text=row["text"])

        writer.commit()


if __name__ == '__main__':
    from csv_reader import CsvReader

    data = CsvReader("datasets/test.csv").read_data()
    DatasetIndexer("indices").index("test", data)