import pandas as pd
import streamlit as st
import sqlite3
import io
from constantes import MUNICIPIOS

def filtrar_por_municipio():
    st.subheader("Pesquisar por Município")

    # Selecionar o município
    municipio = st.selectbox("Selecione o município:", 

    options=MUNICIPIOS)

    # Verificar se o município foi selecionado
    if municipio:
        # Conexão com o banco de dados
        conn = sqlite3.connect('sisreq.db')
        cursor = conn.cursor()

        # Consulta ao banco para filtrar os registros do município
        query = "SELECT * FROM processos WHERE Municipio = ?"
        cursor.execute(query, (municipio,))
        registros = cursor.fetchall()

        # Verificar se há registros para o município selecionado
        if registros:
            # Converter os registros em um DataFrame
            colunas = [desc[0] for desc in cursor.description]
            
            df = pd.DataFrame(registros, columns=colunas)
            df.index = df.index + 1

            st.dataframe(df)

            # Exibir a contagem de registros
            st.write(f"Total de processos para {municipio}: {len(df)}")

            # Botão para salvar e baixar o extrato em uma planilha
            if st.button("Salvar e Baixar Extrato em Planilha"):
                salvar_extrato_planilha(df, municipio)
        else:
            st.warning(f"Não foram encontrados registros para o município: {municipio}.")
        
        # Fechar a conexão com o banco de dados
        conn.close()
    else:
        st.info("Selecione um município para iniciar a busca.")

# Função para salvar o extrato em uma planilha
def salvar_extrato_planilha(df, municipio):
    

    # Criar um arquivo Excel em memória
    arquivo_virtual = io.BytesIO()

    # Salvar o DataFrame no arquivo Excel
    df.to_excel(arquivo_virtual, index=False, engine='openpyxl')
    arquivo_virtual.seek(0)  # Garantir que o ponteiro do arquivo esteja no início

    # Nome do arquivo baseado no município
    arquivo_nome = f"extrato_{municipio.replace(' ', '_')}.xlsx"

    # Fornecer botão para baixar a planilha
    st.download_button(
        label=f"Baixar Planilha para {municipio}",
        data=arquivo_virtual,
        file_name=arquivo_nome,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.success(f"Extrato para {municipio} salvo e pronto para download!")
