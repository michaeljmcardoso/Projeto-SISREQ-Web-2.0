import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

# Função para conectar ao banco de dados
def conectar_banco_de_dados():
    conn = sqlite3.connect('sisreq.db')
    return conn

def exibir_processos_por_municipio():
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

        # Calcular o total de processos
        total_processos = sum(num_processos)

        # Calcular a porcentagem de processos para cada município
        porcentagens = [(num / total_processos) * 100 for num in num_processos]

        # Criar DataFrame
        data = pd.DataFrame({
            'Municípios': municipios,
            'Número de Processos': num_processos,
            'Porcentagem (%)': porcentagens
        })

        # Arredondar a coluna 'Porcentagem (%)' para uma casa decimal
        data['Porcentagem (%)'] = data['Porcentagem (%)'].round(1)
        # Ajustar o índice para começar em 1
        data.index = data.index + 1     

        # Exibir o DataFrame no Streamlit
        st.write("### Número de Processos por Município")
        st.dataframe(data)  # Exibe a tabela de dados

        # Plot do gráfico
        st.write("### Gráfico de Processos por Município")
        fig, ax = plt.subplots(figsize=(10, 6))
        num_cores = len(municipios)
        palette = sns.color_palette("viridis", num_cores)
        sns.barplot(x=num_processos, y=municipios, data=data, palette=palette)

        # Configurações do gráfico
        ax.set(title='Número de Processos por Município')  # Título
        sns.set_style("white")
        sns.despine(right=True, top=True, bottom=True, left=True)
        plt.tick_params(bottom=False, labelbottom=False)
        

        # Adicionar rótulos (quantidades) ao lado de cada barra
        for i, num in enumerate(num_processos):
            ax.text(num + 0.1, i, str(num), ha='left', va='center', weight='bold', fontsize='8')

        plt.tight_layout()

        # Exibir o gráfico no Streamlit
        st.pyplot(fig)

    else:
        st.warning("Não há registros para exibir.")