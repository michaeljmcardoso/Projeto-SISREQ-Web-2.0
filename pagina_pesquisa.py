import sqlite3
import pandas as pd
import io
import streamlit as st
from constantes import MUNICIPIOS

#def filtrar_por_comunidade():

def criar_submenu():
    submenu = st.radio("",
           options=["Escolha uma Opção de Pesquisa:" ,"Município", "Comunidade", "Nº do Processo"])
    #Lógica do submenu
    if submenu == "Município":
        filtrar_por_municipio()
    elif submenu == "Comunidade":
        ()
    elif submenu == "Nº do Processo":
        ()

def filtrar_por_municipio():
    
    st.markdown('<h4 style="color: "#1f77b4";">Pesquisar por Município</h4>', unsafe_allow_html=True)
    #st.subheader("Pesquisar por Município")

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
    
def criar_menu():
    submenu = st.sidebar.selectbox("Escolha uma opção de pesquisa",
        options=["" ,"Pesquisar Por Município", "Pesquisar Por Comunidade"])
    # Lógica do submenu
    if submenu == "Pesquisar Por Município":
        filtrar_por_municipio()
    elif submenu == "Pesquisar Por Comunidade":
        ()

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

def faseInicial():
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect('sisreq.db')
        cursor = conn.cursor()

        # Consultar a contagem e os registros
        cursor.execute("SELECT COUNT(*) as Total FROM processos WHERE Fase_Processo LIKE '%Inicial%'")
        total_fase_inicial = cursor.fetchone()[0]

        cursor.execute("SELECT * FROM processos WHERE Fase_Processo LIKE '%Inicial%'")
        registros = cursor.fetchall()

        if registros:
            # Criar DataFrame com os registros
            colunas = [desc[0] for desc in cursor.description]  # Nome das colunas
            df = pd.DataFrame(registros, columns=colunas)
            df.index = df.index + 1  # Ajustar o índice para começar em 1

            # Exibir o DataFrame no Streamlit
            st.dataframe(df)

            # Exibir a contagem de registros
            st.write(f"Total de processos para fase inicial: {total_fase_inicial}")

            # Botão para salvar e baixar o extrato
            if st.button("Salvar e Baixar Extrato em Planilha"):
                salvar_extrato_planilha(df, "Fase_Inicial")
        else:
            st.warning("Não há registros para exibir.")
    except Exception as e:
        st.error(f"Erro ao processar os dados: {e}")
    finally:
        # Garantir o fechamento da conexão
        conn.close()

# Função para salvar o extrato em uma planilha
def salvar_extrato_planilha(df, fase):
    # Criar um arquivo Excel em memória
    arquivo_virtual = io.BytesIO()

    # Salvar o DataFrame no arquivo Excel
    df.to_excel(arquivo_virtual, index=False, engine='openpyxl')
    arquivo_virtual.seek(0)  # Garantir que o ponteiro do arquivo esteja no início

    # Nome do arquivo baseado na fase
    arquivo_nome = f"extrato_{fase}.xlsx"

    # Fornecer botão para baixar a planilha
    st.download_button(
        label=f"Baixar Planilha para {fase}",
        data=arquivo_virtual,
        file_name=arquivo_nome,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.success(f"Extrato para {fase} salvo e pronto para download!")
