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

def exibir_grafico_fases_processo():
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