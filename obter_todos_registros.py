import pandas as pd
import sqlite3

def obter_ordem_colunas_processo(df):
    colunas = list(df.columns)
    if 'Acao_Civil_Publica' in colunas and 'Numero_Processo_Judicial' in colunas:
        colunas.remove('Numero_Processo_Judicial')
        indice_acao_civil = colunas.index('Acao_Civil_Publica')
        colunas.insert(indice_acao_civil + 1, 'Numero_Processo_Judicial')
    return colunas

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