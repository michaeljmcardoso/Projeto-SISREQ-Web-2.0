import sqlite3
import pandas as pd
import io
import streamlit as st
from constantes import MUNICIPIOS, TIPO_SOBREPOSICAO

#def filtrar_por_comunidade():

def criar_submenu():
    submenu = st.radio("",
           options=["Escolha uma Opção de Pesquisa:" ,"Município", "Comunidade", "Nº do Processo", "Quilombos em Assentamentos"])
    #Lógica do submenu
    if submenu == "Município":
        filtrar_por_municipio()
    elif submenu == "Comunidade":
        ()
    elif submenu == "Nº do Processo":
        ()
    elif submenu == "Quilombos em Assentamentos":
        quilombos_em_assentamentos()

def filtrar_por_municipio():
    
    st.markdown('<h4 style="color: #1f77b4;">Pesquisar por Município</h4>', unsafe_allow_html=True)
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


def conectar_banco_de_dados():
    return sqlite3.connect('sisreq.db')

def quilombos_em_assentamentos():
    st.markdown('<h4 style="color: #1f77b4;">Quilombos em Assentamentos</h4>', unsafe_allow_html=True)
    try:
        # Conectar ao banco de dados
        conn = conectar_banco_de_dados()
        cursor = conn.cursor()

        # Definir colunas específicas a serem consultadas
        colunas_desejadas = [
            "Numero", "Comunidade", "Sobreposicao", "Analise_de_Sobreposicao",
            "Municipio", "Etapa_RTID", "Area_ha", "Num_familias"
        ]
        colunas_str = ", ".join(colunas_desejadas)

        # Buscar registros filtrando apenas as colunas necessárias
        query = f"SELECT {colunas_str} FROM processos WHERE Sobreposicao LIKE '%PA_INCRA%' OR Sobreposicao LIKE '%PA_ITERMA%'"
        cursor.execute(query)
        registros = cursor.fetchall()

        if registros:
            # Criar DataFrame apenas com as colunas selecionadas
            df = pd.DataFrame(registros, columns=colunas_desejadas)
            df.index = df.index + 1  # Ajustar o índice para começar em 1

            # Obter lista única de tipos de sobreposição disponíveis
            tipos_sobreposicao = sorted(df["Sobreposicao"].dropna().unique())

            # Criar uma lista suspensa para o usuário selecionar os tipos
            selecao = st.multiselect("Selecione o Tipo de Sobreposição:", tipos_sobreposicao)

            # Filtrar o DataFrame com base na seleção do usuário
            if selecao:
                df_filtrado = df[df["Sobreposicao"].isin(selecao)]
            else:
                df_filtrado = df  # Se nada for selecionado, mostra tudo

            # Exibir o total de registros e o DataFrame filtrado
            st.write(f"Total: {len(df_filtrado)}")
            st.dataframe(df_filtrado)

            # Botão para salvar e baixar o extrato
            if not df_filtrado.empty and st.button("Salvar e Baixar Extrato em Planilha"):
                salvar_extrato_planilha(df_filtrado, "Territorios_Quilombolas_em_Assentamentos")
        else:
            st.warning("Não há registros para exibir.")
    except Exception as e:
        st.error(f"Erro ao processar os dados: {e}")
    finally:
        # Garantir o fechamento da conexão
        conn.close()

# Função para salvar o extrato em uma planilha
def salvar_extrato_planilha(df, nome_arquivo):
    # Criar um arquivo Excel em memória
    arquivo_virtual = io.BytesIO()

    # Salvar o DataFrame no arquivo Excel
    df.to_excel(arquivo_virtual, index=False, engine='openpyxl')
    arquivo_virtual.seek(0)  # Garantir que o ponteiro do arquivo esteja no início

    # Nome do arquivo baseado na fase
    arquivo_nome = f"extrato_{nome_arquivo}.xlsx"

    # Fornecer botão para baixar a planilha
    st.download_button(
        label=f"Baixar Planilha para {nome_arquivo}",
        data=arquivo_virtual,
        file_name=arquivo_nome,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.success(f"Extrato para {nome_arquivo} salvo e pronto para download!")


