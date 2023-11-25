import pandas as pd

from utils import parse_iso_datetime, format_datetime


class CsvReader:
    def __init__(self, filename):
        self.filename = filename
        self.data = None

    def read_data(self):
        df = pd.read_csv(self.filename)
        self._transform_data(df)
        return df

    def _transform_data(self, df):
        df["sent"] = df["sent"].apply(lambda dt: format_datetime(parse_iso_datetime(dt)))
