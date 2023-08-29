from flask import Flask, render_template, request, send_from_directory
import pandas as pd
from xml.etree import ElementTree as ET
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def flatten_xml(element, parent_key='', sep='_'):
    items_list = []

    def process_element(ele, parent_key=''):
        items = {}
        for child in ele:
            new_key = parent_key + sep + child.tag if parent_key else child.tag
            value = child.text.strip() if child.text else ""

            if child.attrib:
                attributes_data = {new_key + sep + k: v for k, v in child.attrib.items()}
                items.update(attributes_data)

            if child:
                child_items = process_element(child, new_key)
                items.update(child_items)
            else:
                items[new_key] = value
        return items

    if element:
        for child in element:
            items_list.append(process_element(child))
    return items_list


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            file_extension = file.filename.split(".")[-1]
            if file_extension in ["xml", "json"]:
                file_name = str(uuid.uuid4()) + '.' + file_extension
                file_path = os.path.join(UPLOAD_FOLDER, file_name)

                # Gravando o arquivo no disco
                file.save(file_path)

                if file_extension == "xml":
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    columns = list(flatten_xml(root)[0].keys())
                    return render_template("select_columns.html", columns=columns, file_name=file_name.split('.')[0])
                else:
                    # Similar logic for JSON if needed
                    pass
    return render_template("index.html")


@app.route("/convert/<filename>", methods=["POST"])
def convert(filename):
    selected_columns = request.form.getlist('columns')
    file_path = os.path.join(UPLOAD_FOLDER, filename + ".xml")

    tree = ET.parse(file_path)
    root = tree.getroot()
    data_list = flatten_xml(root)

    df = pd.DataFrame(data_list)

    valid_columns = [col for col in selected_columns if col in df.columns]
    df = df[valid_columns]

    excel_path = file_path.replace('.xml', '.xlsx')
    df.to_excel(excel_path, index=False)

    return render_template("download.html", file_name=filename + ".xlsx")


@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
