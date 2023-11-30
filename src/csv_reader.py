import os
from html import escape

import pandas as pd

from utils import parse_iso_datetime, format_datetime


def _transform_data(df):
    _format_time(df)
    _escape_html(df)


def _format_time(df):
    df["sent"] = df["sent"].apply(lambda dt: format_datetime(parse_iso_datetime(dt)))


def _escape_html(df):
    df["text"] = df["text"].apply(lambda t: escape(t))


def read_csv_dataset(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not exists")
    df = pd.read_csv(file_path)
    _transform_data(df)
    return df
