import os

import pandas as pd
from whoosh import highlight
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

from consts import INDEX_FOLDER
from datasets import read_csv_dataset


def search(dataset_path, query):
    dataset_name = os.path.basename(dataset_path)
    index_dir = os.path.join(INDEX_FOLDER, dataset_name)
    if not os.path.exists(index_dir):
        raise FileNotFoundError(f"Index directory '{index_dir}' does not exist")

    dataset = read_csv_dataset(dataset_path)
    index = open_dir(index_dir)
    hit_messages = []
    with index.searcher() as searcher:
        query = QueryParser("text", index.schema).parse(query)
        results = searcher.search(query, limit=None, sortedby="id")
        results.formatter = MarkFormatter()
        for hit in results:
            message = dataset.loc[hit["id"]].copy()
            message["text"] = hit.highlights("text", text=message["text"])
            hit_messages.append(message)

    sorted_dataset = pd.DataFrame(hit_messages, columns=dataset.columns)
    return sorted_dataset


class MarkFormatter(highlight.Formatter):
    def format_token(self, text, token, replace=False):
        token_text = highlight.get_text(text, token, replace)
        return f'<mark class="bg-warning">{token_text}</mark>'
