from pathlib import Path

from flask import Flask, request, flash, redirect, url_for
from flask import render_template
from csv_reader import CsvReader
from werkzeug.utils import secure_filename
from consts import UPLOAD_FOLDER


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.get('/')
def show_data():
    filename = request.args.get('filename')
    data = None
    if filename:
        file_path = Path(app.config['UPLOAD_FOLDER']) / filename
        file_path.resolve()
        data = CsvReader(file_path).read_data()
    return render_template('viewer.html', data=data)


@app.post('/upload')
def upload_file():
    if 'file' not in request.files:
        # flash('No file part')
        return redirect('/')

    file = request.files['file']
    if file.filename == '':
        # flash('No selected file')
        return redirect('/')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        file_path = Path(app.config['UPLOAD_FOLDER']) / filename
        file_path.resolve()
        file.save(file_path)
        return redirect(url_for('show_data', filename=filename))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


if __name__ == '__main__':
    app.run(debug=True, port=8080)
