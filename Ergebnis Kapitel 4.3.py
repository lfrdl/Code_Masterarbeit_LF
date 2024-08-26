import json
from flask import Flask, request, jsonify
from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={'api_key': 'sk-fZ...'})

vn.connect_to_mssql(odbc_conn_str='DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-2HRUGBA\\SQLEXPRESS;DATABASE=Data_Marts;Trusted_Connection=yes')

df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
plan = vn.get_training_plan_generic(df_information_schema)

vn.train(ddl="""
    CREATE TABLE IF NOT EXISTS my-table (
        id INT PRIMARY KEY,
        name VARCHAR(100),
        age INT
    )
""")
vn.train(documentation="Given is an employee table of a university (THM). Departments and organizational unit are in the column 'Organsiationseinheit_Bezeichnung'.")
vn.train(sql="SELECT Count(*) FROM Mitarbeiter WHERE Organisationseinheit_Bezeichnung = 'MNI'")

def add_training_data_from_json(vn_instance, json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for entry in data:
            if 'ddl' in entry:
                vn_instance.train(ddl=entry['ddl'])
            if 'documentation' in entry:
                vn_instance.train(documentation=entry['documentation'])
            if 'sql' in entry:
                vn_instance.train(sql=entry['sql'])

json_file_path = 'path_to_your_json_file.json'
add_training_data_from_json(vn, json_file_path)

training_data = vn.get_training_data()

app = Flask(__name__)

@app.route('/')
def home():
    return "VannaDB Flask app is running."

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    answer = vn.ask(question=question)
    return jsonify({"status": "success", "answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)