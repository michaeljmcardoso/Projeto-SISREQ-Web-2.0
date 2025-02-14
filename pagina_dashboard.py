import pandas as pd
import streamlit as st
import sqlite3
from constantes import FASE_PROCESSO

"""Funções para a filtrar por fase do processo"""

# Função para conectar ao banco de dados
def conectar_banco_de_dados():
    conn = sqlite3.connect('sisreq.db')
    return conn

# Função para buscar registros por fase
def buscar_registros_por_fase(fase):
    conn = conectar_banco_de_dados()
    cursor = conn.cursor()
    
    # Busca o total de registros
    cursor.execute(f"SELECT COUNT(*) as Total FROM processos WHERE Fase_Processo LIKE '%{fase}%'")
    total = cursor.fetchone()[0]

    # Busca os registros
    cursor.execute(f"SELECT * FROM processos WHERE Fase_Processo LIKE '%{fase}%'")
    registros = cursor.fetchall()

    # Obtém os nomes das colunas
    if cursor.description:
        colunas = [desc[0] for desc in cursor.description]
    else:
        colunas = []  # Caso não haja resultados

    conn.close()
    return total, registros, colunas

# Função principal
def main():
    st.subheader("Visualização de Processos por Fase")

    # Lista de fases disponíveis
    #fases = ["Inicial", "Estudo de Identificação"]

    # Selectbox para selecionar a fase
    fase_selecionada = st.selectbox(
        "Selecione a fase do processo:",
        options=FASE_PROCESSO
    )

    # Buscar registros com base na fase selecionada
    total, registros, colunas = buscar_registros_por_fase(fase_selecionada)

    if registros:
        st.write(f"Total de processos na fase '{fase_selecionada}': {total}")

        # Exibir os registros em uma tabela
        df = pd.DataFrame(registros, columns=colunas)
        if 'ID' in df.columns:
            df = df.drop(columns=['ID'])
            df.index = df.index + 1
            st.dataframe(df)
        

        # Botão para salvar extrato
        if st.button('Salvar Extrato'):
            df.to_excel(f"extrato_{fase_selecionada}.xlsx", index=False)
            st.success(f"Extrato salvo como 'extrato_{fase_selecionada}.xlsx'")
    else:
        st.warning(f"Não há registros para a fase '{fase_selecionada}'.")

if __name__ == "__main__":
    main()