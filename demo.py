from flask import Flask, render_template, request, send_file
import re
import os
from io import BytesIO
from werkzeug.utils import secure_filename
from docx import Document
import PyPDF2
import csv
import json



app = Flask(__name__)

def replace_words_in_text(text, replacements):
    """
    Replace words in the text based on the replacements dictionary.

    :param text: str, the text content
    :param replacements: dict, a dictionary with words as keys and their replacements as values
    :return: str, the modified text
    """
    # Create a regular expression from the dictionary keys
    regex = re.compile(r'\b(%s)\b' % "|".join(map(re.escape, replacements.keys())))
    return regex.sub(lambda match: replacements[match.group(0)], text)

def read_file_content(file):
    """
    Read the content of the uploaded file.

    :param file: FileStorage, the uploaded file
    :return: str, the content of the file
    """
    filename = file.filename
    file_stream = BytesIO(file.read())
    content = ""
    if filename.endswith('.docx'):
        doc = Document(file_stream)
        content = "\n".join([paragraph.text for paragraph in doc.paragraphs])

    elif filename.endswith('.pdf'):
        raw_text = ""
        reader = PyPDF2.PdfReader(file_stream)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            raw_text += page.extract_text()
        lines = raw_text.split()
        formatted_text = " ".join(lines)
        content = formatted_text.strip()

    elif filename.endswith('.csv'):
        file_stream.seek(0)
        reader = csv.reader(file_stream.read().decode('utf-8').splitlines())
        for row in reader:
            content += ",".join(row) + "\n"

    elif filename.endswith('.txt'):
        file_stream.seek(0)
        content = file_stream.read().decode('utf-8')

    return content

# Define the words to be replaced and their replacements
# replacements = {
#     "video message": "Julian",
#     "prospects": "potential clients",
#     "paying customers": "paying clients",
#     "machines": "devices",
#     "computers": "computing systems"
# }
replacements = {}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/words', methods=['POST', 'DELETE', 'PUT'])
def words():
    key = request.form.get('key')
    value = request.form.get('value')
    multiple = request.form.get('multiple')
    if multiple:
        # Convert the string to a Python dictionary
        dict_string = multiple.replace("'", '"')
        python_dict = json.loads(dict_string)
        replacements.update(python_dict)

    replacements.update({key: value})
    print(replacements)
    return render_template('index.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        content = read_file_content(file)
        modified_content = replace_words_in_text(content, replacements)
        return render_template("index.html", text=modified_content)

@app.route('/dummy', methods=['GET', 'POST', "DELETE"])
def dummy():
    auth = request.headers

    if auth['key'] != "Julian":
        return "Error not authorized!"
    else:
        if request.method == "GET":
            return "Dummy"

        if request.method == 'POST':
            data = request.get_json()
            return f'Data recieved: {data}'

        if request.method == "DELETE":
            return "Data successfully deleted!"

if __name__ == "__main__":
    app.run(debug=True)
