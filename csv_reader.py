import csv

class Csv_Reader:
    def __init__(self, filename):
        self.filename = filename
        self.data = []
        self.header = None

    def read_data(self, has_header=True):
        with open(self.filename) as csvfile:
            reader = csv.reader(csvfile)
            header_read = False
            for row in reader:
                if has_header and not header_read:
                    self.header = row
                    header_read = True
                    continue
                self.data.append(row)