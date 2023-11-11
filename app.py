from flask import Flask
from flask import render_template
from csv_reader import Csv_Reader

app = Flask(__name__)
reader = Csv_Reader("datasets/test.csv")
reader.read_data()
data = reader.data
header = reader.header


@app.route('/')
def show_data():
    return render_template("table.html", header=header, data=data)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
