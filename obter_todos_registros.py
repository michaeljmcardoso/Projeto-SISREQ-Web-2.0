import pandas as pd
import sqlite3

def obter_todos_os_registros():
    conn = sqlite3.connect('sisreq.db')
    df = pd.read_sql_query('SELECT * FROM processos', conn)
    conn.close()
    return df

def obter_registro_por_id(item_id):
    conn = sqlite3.connect('sisreq.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM processos WHERE id = ?", (item_id,))
    registro = cursor.fetchone()
    conn.close()
    return registro