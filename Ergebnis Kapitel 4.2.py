import os
import json
import tkinter as tk
import tkinter.ttk as ttk
from langchain_openai import OpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.agents import create_sql_agent

os.environ['OPENAI_API_KEY'] = "sk-fZ..."

server = 'DESKTOP-2HRUGBA\\SQLEXPRESS'
database = 'Data_Marts'
uri = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

db = SQLDatabase.from_uri(uri)
llm = OpenAI(temperature=0)

schema2_path = 'C:\\Users\\leonf\\Desktop\\ChatGPT Projekt\\Programme\\RAG\\schema2.json'

try:
    with open(schema2_path, 'r') as f:
        schema2 = json.load(f)
except FileNotFoundError:
    print(f"Die Datei '{schema2_path}' wurde nicht gefunden. Stellen Sie sicher, dass die Datei existiert.")
    exit(1)

#Schema Tabelle
def get_table_schema(table_name):
    if table_name in schema2:
        table = schema2[table_name]
        schema_desc = f"Table: {table_name}\n"
        for column in table['columns']:
            schema_desc += f"  Column: {column['column_name']}, Type: {column['data_type']}, Max Length: {column.get('char_max_len', 'N/A')}, Nullable: {column['is_nullable']}"
            if 'instruction' in column:
                schema_desc += f", Instruction: {column['instruction']}"
            schema_desc += "\n"
        schema_desc += "Sample data:\n"
        for row in table.get('sample_data', []):
            schema_desc += "  " + str(row) + "\n"
        schema_desc += "Distinct values:\n"
        for column_name, distinct_values in table['distinct_values'].items():
            schema_desc += f"  {column_name}: {distinct_values}\n"
        return schema_desc
    return "Table schema not found."

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    handle_parsing_errors=True
)

# UI-Fenster
root = tk.Tk()
root.title("Chatte mit der Datenbank")

entry = ttk.Entry(root, font=("Arial", 14))
entry.pack(padx=20, pady=20, fill=tk.X)

def on_enter(event=None):
    on_click()

entry.bind('<Return>', on_enter)

def on_click():
    query = entry.get()
    try:
        
        table_name = "Mitarbeiter"  
        table_schema = get_table_schema(table_name)
        
        
        instruction = (f"Use only the provided relationship types and properties in the schema."
                        f"make sure that the values of the queries match the values of the schema 1:1. "
                       f"Do not use any other relationship types or properties that are not provided."
                       f"Ensure to interpret the columns correctly based on their types and instructions provided: {table_schema}. "
                      # f"Make sure to map the values to the correct columns and their cells provieded:  {table_schema}."
                       f"Do not generate any CREATE TABLE statements. "

                        f"Do not use any values or combinations of values that are not explicitly listed in the schema. "
                      
                      #  f"Make sure to map the values to the correct columns and their cells as provided: {table_schema}. " Wie viele mitarbeiter gibt es im Fachbereich ZDH?
                       f"Query: {query}")
        
       
        result = agent_executor.run(instruction)
        
        
    except Exception as e:
        result = f"Ein Fehler ist aufgetreten: {str(e)}"

    text.delete("1.0", tk.END)
    text.insert(tk.END, result)

button = ttk.Button(root, text="Chat", command=on_click)
button.pack(padx=20, pady=20)

text = tk.Text(root, height=10, width=60, font=("Arial", 14))
text.pack(padx=20, pady=20)

root.mainloop()
