import pandas as pd

from utils import parse_iso_datetime, format_datetime


def _transform_data(df):
    df["sent"] = df["sent"].apply(lambda dt: format_datetime(parse_iso_datetime(dt)))


class CsvReader:
    def __init__(self, filename):
        self.filename = filename
        self.data = None

    def read_data(self):
        df = pd.read_csv(self.filename)
        _transform_data(df)
        return df
