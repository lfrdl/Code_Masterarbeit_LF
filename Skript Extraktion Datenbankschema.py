import pyodbc
import json
from datetime import date

def default_converter(o):
    if isinstance(o, date):
        return o.isoformat()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

# Verbindungsdetails zur Datenbank
server = 'DESKTOP-2HRUGBA\\SQLEXPRESS'
database = 'Data_Marts'
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

try:
    # Verbindung zur Datenbank herstellen
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

    # Abfrage zur Extraktion des Schemas
    schema_query = """
    SELECT 
        TABLE_SCHEMA, 
        TABLE_NAME, 
        COLUMN_NAME, 
        DATA_TYPE,
        CHARACTER_MAXIMUM_LENGTH,
        IS_NULLABLE
    FROM 
        INFORMATION_SCHEMA.COLUMNS
    """

    cursor.execute(schema_query)
    schema_info = cursor.fetchall()

    # Schema in einem lesbaren Format speichern
    schema3 = {}
    for row in schema_info:
        table_schema, table_name, column_name, data_type, char_max_len, is_nullable = row
        if table_name not in schema3:
            schema3[table_name] = {
                'columns': [],
                'distinct_values': {}
            }
        schema3[table_name]['columns'].append({
            'column_name': column_name, 
            'data_type': data_type,
            'char_max_len': char_max_len,
            'is_nullable': is_nullable
        })

    # DISTINCT-Werte für jede Spalte außer 'Personalnummer' und 'Rentenaustritt_berechnet'
    for table_name in schema3.keys():
        for column in schema3[table_name]['columns']:
            column_name = column['column_name']
            if column_name.lower() not in ['personalnummer', 'Mitarbeitergruppe_Schlüssel', 'Mitarbeiterkreis_Schlüssel', 'Dienstart_Schlüssel', 'Unterdienstart_Schlüssel', 'Organisationseinheit_ID', 'Vertragsart_Schlüssel_letzte']:  # Ausschließen
                cursor.execute(f"SELECT DISTINCT {column_name} FROM {table_name}") 
                distinct_values = [row[0] for row in cursor.fetchall()]
                schema3[table_name]['distinct_values'][column_name] = distinct_values

    # Verbindung schließen
    cursor.close()
    connection.close()

    # Pfad zur schema3.json Datei
    schema3_path = 'C:\\Users\\leonf\\Desktop\\ChatGPT Projekt\\Programme\\RAG\\schema3.json'

    # Schema als JSON-Datei speichern
    with open(schema3_path, 'w') as f:
        json.dump(schema3, f, indent=4, default=default_converter)

    print(f"Schema3 erfolgreich extrahiert und gespeichert in {schema3_path}")

except pyodbc.Error as e:
    print("Fehler beim Verbinden mit der Datenbank:", e)
