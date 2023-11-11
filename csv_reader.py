import csv
from models import Message
from utils import parse_iso_datetime


class CsvReader:
    def __init__(self, filename):
        self.filename = filename
        self.data = []

    def read_data(self):
        with open(self.filename) as csv_file:
            dr = csv.DictReader(csv_file)
            for row in dr:
                self.data.append(Message(
                    row["username"],
                    parse_iso_datetime(row["sent"]),
                    row["text"]
                ))
        return self.data