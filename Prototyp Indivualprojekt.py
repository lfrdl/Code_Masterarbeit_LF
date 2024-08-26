import os



os.environ['OPENAI_API_KEY'] = "sk-proj-xiavkVu3xjrFo9ZMCMyFT3BlbkFJyD8E3xe15DOkABNNvAEk"
import pyodbc
import tkinter as tk
import tkinter.ttk as ttk
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_openai import OpenAI
from langchain.agents import create_sql_agent, AgentExecutor

server = 'DESKTOP-2HRUGBA\\SQLEXPRESS'
database = 'Data_Marts'


uri = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

db = SQLDatabase.from_uri(uri)

llm = OpenAI(temperature=0)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True
)

root = tk.Tk()
root.title("Chatte mit der Datenbank")


entry = ttk.Entry(root, font=("Arial", 14))
entry.pack(padx=20, pady=20, fill=tk.X)

def on_enter(event=None):
    on_click()

entry.bind('<Return>', on_enter)

def on_click():
    
    query = entry.get()
   
    result = agent_executor.run(query)
    
    text.delete("1.0", tk.END)
    text.insert(tk.END, result)

button = ttk.Button(root, text="Chat", command=on_click)
button.pack(padx=20, pady=20)

text = tk.Text(root, height=10, width=60, font=("Arial", 14))
text.pack(padx=20, pady=20)

root.mainloop()