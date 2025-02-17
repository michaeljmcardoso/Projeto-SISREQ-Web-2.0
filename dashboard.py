import pandas as pd
import streamlit as st
import sqlite3
from constantes import FASE_PROCESSO
import matplotlib.pyplot as plt
import seaborn as sns

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
def processos_por_fase():
    conectar_banco_de_dados()
    st.subheader("Visualização de Processos por Fase")

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

def grafico_processos_por_fase():
    st.subheader("Gráfico de Processos por Fase")
    conn = conectar_banco_de_dados()
    cursor = conn.cursor()

    cursor.execute("SELECT Fase_Processo, COUNT(*) as Total FROM processos WHERE Fase_Processo != 'Inicial' GROUP BY Fase_Processo")
    registros = cursor.fetchall()

    if registros:
        # Extrair os dados das fases e suas contagens
        fases = [registro[0] for registro in registros]
        contagens = [registro[1] for registro in registros]

        # criar um DataFrame
        data = pd.DataFrame({'Fase': fases, 'Contagem': contagens})

        # Criar o gráfico de barras
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=contagens, y=fases, data=data, palette="Set1")

        # Configurações do gráfico
        ax.set(title='Processos por Fase')
        sns.despine(right=True, top=True, bottom=True, left=True)
        plt.tick_params(bottom=False, labelbottom=False)

        # Adicionar rótulos (quantidades) ao lado de cada barra
        for i, contagens in enumerate(contagens):
            ax.text(contagens + 0.1, i, str(contagens), ha='left', va='center', weight='bold', fontsize='10')

        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning('Não há registros para exibir.', title='Erro')

def processos_por_municipio():
    # Conectar ao banco de dados
    conn = conectar_banco_de_dados()
    cursor = conn.cursor()

    # Consulta para obter o número de processos por município
    cursor.execute("SELECT Municipio, COUNT(*) AS Num_Processos FROM processos GROUP BY Municipio")
    resultados = cursor.fetchall()

    if resultados:
        # Preparar os dados
        municipios = []
        num_processos = []
        for resultado in resultados:
            municipios.append(resultado[0])
            num_processos.append(resultado[1])

       # Criar DataFrame
        data = pd.DataFrame({
            'Municípios': municipios,
            'Número de Processos': num_processos
        })
       
        # Ajustar o índice para começar em 1
        data.index = data.index + 1  

        # Exibir o DataFrame no Streamlit
        st.write("### Número de Processos por Município")
        st.dataframe(data)
        
        # Ordenar os dados por número de processos (decrescente)
        data = data.sort_values(by='Número de Processos', ascending=False)

        # Plot do gráfico
        st.write("### Gráfico de Processos por Município")
        fig, ax = plt.subplots(figsize=(10, 18))
        num_cores = len(municipios)
        palette = sns.color_palette("viridis", num_cores)
        sns.barplot(x='Número de Processos', y='Municípios', data=data, palette='viridis')

        # Configurações do gráfico
        sns.set_style("white")
        ax.set_xlabel('')
        ax.set_ylabel('')
        sns.despine(right=True, top=True, bottom=True, left=True)
        plt.tick_params(bottom=False, labelbottom=False)

        # Adicionar rótulos (quantidades) ao lado de cada barra
        for i, num_processos in enumerate(data['Número de Processos']):
            ax.text(num_processos + 0.5, i, f"{num_processos}", ha='left', va='center', weight='bold', fontsize='10')

        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("Não há registros para exibir.")