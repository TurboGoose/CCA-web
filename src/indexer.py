import os

from whoosh.fields import *
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser


class IndexManager:
    def __init__(self, indices_dir):
        self.indices_dir = indices_dir
        if not os.path.exists(indices_dir):
            os.mkdir(indices_dir)

    def index(self, index_name, dataset):
        index_dir = os.path.join(self.indices_dir, index_name)
        if not os.path.exists(index_dir):
            os.mkdir(index_dir)

        schema = Schema(id=NUMERIC(stored=True, unique=True, bits=64), text=TEXT)
        index = create_in(index_dir, schema)
        writer = index.writer()

        for i, row in dataset.iterrows():
            writer.add_document(id=i, text=row["text"])

        writer.commit()

    def search(self, index_name, query):
        index_dir = os.path.join(self.indices_dir, index_name)
        if not os.path.exists(index_dir):
            raise FileNotFoundError(f"Index directory '{index_dir}' does not exist")
        index = open_dir(index_dir)

        matched_docs = []
        with index.searcher() as searcher:
            query = QueryParser("text", index.schema).parse(query)
            results = searcher.search(query)
            for res in results:
                matched_docs.append(res["id"])

        return matched_docs


if __name__ == '__main__':
    from csv_reader import CsvReader
    data = CsvReader("../datasets/test.csv").read_data()

    indexer = IndexManager("../indices")
    # indexer.index("test", data)

    query = "Hello there"
    results = indexer.search("test", query)

    for id in results:
        print(f"{id}: {data.loc[id].text}")