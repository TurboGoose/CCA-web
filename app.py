from flask import Flask
from flask import render_template
from csv_reader import CsvReader

app = Flask(__name__)

reader = CsvReader("datasets/test.csv")
reader.read_data()


@app.route('/')
def show_data():
    return render_template("viewer.html", data=reader.data)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
