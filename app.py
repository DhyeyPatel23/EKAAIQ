from flask import Flask, request, render_template, flash
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return render_template('upload.html')
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return render_template('upload.html')
        if file and allowed_file(file.filename):
            try:
                df = pd.read_excel(file)
                # Process the DataFrame (df) as needed
                # ...existing code...
                flash('File successfully processed')
            except Exception as e:
                flash(f'There was an error processing the file: {e}')
            return render_template('upload.html')
    return render_template('upload.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xls', 'xlsx'}

if __name__ == '__main__':
    app.run(debug=True)
