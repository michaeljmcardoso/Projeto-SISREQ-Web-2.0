import sqlite3
import pandas as pd

# Carregar dados do banco
def converter_area_para_numeric():
    conn = sqlite3.connect('sisreq.db')
    df = pd.read_sql_query("SELECT * FROM processos", conn)

    # Garantir que todos os valores sejam strings antes de usar `.str.replace()`
    df['Area_ha_Titulada'] = df['Area_ha_Titulada'].astype(str).str.replace(',', '.', regex=False)

    # Converter para valores numéricos, substituindo valores inválidos por 0
    df['Area_ha_Titulada'] = pd.to_numeric(df['Area_ha_Titulada'], errors='coerce').fillna(0)

    # Atualizar os valores diretamente no banco
    for index, row in df.iterrows():
        conn.execute(
            "UPDATE processos SET Area_ha_Titulada = ? WHERE ID = ?",
            (row['Area_ha_Titulada'], row['ID'])
        )

    conn.commit()
    conn.close()

# Carregar dados do banco
def converter_familias_para_numeric():
    conn = sqlite3.connect('sisreq.db')
    df = pd.read_sql_query("SELECT * FROM processos", conn)

    # Garantir que todos os valores sejam strings antes de usar `.str.replace()`
    df['Num_familias'] = df['Num_familias'].astype(str).str.replace(',', '.', regex=False)

    # Converter para valores numéricos, substituindo valores inválidos por 0
    df['Num_familias'] = pd.to_numeric(df['Num_familias'], errors='coerce').fillna(0)

    # Atualizar os valores diretamente no banco
    for index, row in df.iterrows():
        conn.execute(
            "UPDATE processos SET Num_familias = ? WHERE ID = ?",
            (row['Num_familias'], row['ID'])
        )

    conn.commit()
    conn.close()

# Carregar dados do banco
def converter_latitude_para_numeric():
    conn = sqlite3.connect('sisreq.db')
    df = pd.read_sql_query("SELECT * FROM processos", conn)

    # Garantir que todos os valores sejam strings antes de usar `.str.replace()`
    df['Latitude'] = df['Latitude'].astype(str).str.replace(',', '.', regex=False)

    # Converter para valores numéricos, substituindo valores inválidos por 0
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')

    # Atualizar os valores diretamente no banco
    for index, row in df.iterrows():
        # Se a latitude for NaN, atualize com NULL no banco de dados
        latitude_value = row['Latitude'] if not pd.isna(row['Latitude']) else None
        conn.execute(
            "UPDATE processos SET Latitude = ? WHERE ID = ?",
            (latitude_value, row['ID'])
        )

    conn.commit()
    conn.close()

# Carregar dados do banco
def converter_longitude_para_numeric():
    conn = sqlite3.connect('sisreq.db')
    df = pd.read_sql_query("SELECT * FROM processos", conn)

    # Garantir que todos os valores sejam strings antes de usar `.str.replace()`
    df['Longitude'] = df['Longitude'].astype(str).str.replace(',', '.', regex=False)

    # Converter para valores numéricos, substituindo valores inválidos por 0
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

    # Atualizar os valores diretamente no banco
    for index, row in df.iterrows():
        # Se a lotude for NaN, atualize com NULL no banco de dados
        longitude_value = row['Longitude'] if not pd.isna(row['Longitude']) else None
        conn.execute(
            "UPDATE processos SET longitude = ? WHERE ID = ?",
            (longitude_value, row['ID'])
        )

    conn.commit()
    conn.close()