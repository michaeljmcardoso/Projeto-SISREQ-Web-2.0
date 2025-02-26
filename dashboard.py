import pandas as pd
import streamlit as st
import sqlite3
import webbrowser
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from constantes import FASE_PROCESSO

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

        # Botão para salvar e baixar extrato
        if st.button("Salvar e Baixar Extrato"):
            # Salvar o DataFrame em um arquivo Excel
            file_name = f"Extrato_fase_{fase_selecionada}.xlsx"
            df.to_excel(file_name, index=False)
            st.success(f"Extrato salvo como '{file_name}'")

            # Oferecer o arquivo para download
            with open(file_name, "rb") as file:
                st.download_button(
                    label="Baixar Excel",
                    data=file,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
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

def exibir_processos_por_data_abertura():
    st.write("### Ano de Abertura dos Processos")
    conn = conectar_banco_de_dados()
    cursor = conn.cursor()

    cursor.execute("SELECT Data_Abertura, COUNT(*) AS Num_Processos FROM processos GROUP BY Data_Abertura")
    resultados = cursor.fetchall()

    if resultados:
        datas_abertura = []
        num_processos = []

        for resultado in resultados:
            datas_abertura.append(resultado[0])
            num_processos.append(resultado[1])

        # Criar DataFrame
        data = pd.DataFrame({'Data de Abertura': datas_abertura, 'Número de Processos': num_processos})

        # Converter a coluna de datas para o formato apropriado (opcional)
        data['Data de Abertura'] = pd.to_datetime(data['Data de Abertura'], format="%d-%m-%Y")

        # Ordenar o DataFrame por data de abertura
        data = data.sort_values(by='Data de Abertura')

        # Calcular o acumulado de processos por ano
        data['Ano'] = data['Data de Abertura'].dt.year
        acumulado_por_ano = data.groupby('Ano')['Número de Processos'].cumsum()

        # Adicionar a coluna de acumulado de processos ao DataFrame
        data['Acumulado'] = acumulado_por_ano

        # Plot do gráfico de linhas
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(x='Data de Abertura', y='Acumulado', data=data, palette="Set1")

        # Configurações do gráfico
        ax.set(title='Acumulado de Processos por Ano')
        ax.set_xlabel('')
        ax.set_ylabel('')
        sns.set_style("white")
        sns.despine(right=True, top=True, bottom=False, left=False)
        plt.xticks(rotation=45)  # Rotacionar os rótulos do eixo x para melhor legibilidade

        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning('Não há registros para exibir.', title='Erro')

def plotar_mapa_interativo():
    st.write("### Geolocalização das Comunidades Quilombolas")
    if st.button("Plotar Mapa"):
        conn = conectar_banco_de_dados()
        cursor = conn.cursor()

        cursor.execute("SELECT Municipio, Comunidade, Latitude, Longitude, Num_Familias FROM processos")
        resultados = cursor.fetchall()

        if resultados:
            municipios = []
            comunidades = []
            latitudes = []
            longitudes = []
            numero_de_familias = []

            for resultado in resultados:
                municipios.append(resultado[0])
                comunidades.append(resultado[1])

                # Verificar se os valores de latitude e longitude são numéricos antes de adicioná-los
                if isinstance(resultado[2], (float, int)) and isinstance(resultado[3], (float, int)):
                    latitudes.append(resultado[2])
                    longitudes.append(resultado[3])
                else:
                    latitudes.append(None)  # Se não for numérico, adicione None
                    longitudes.append(None)

                numero_de_familias.append(resultado[4])

            df = pd.DataFrame({
                'Municipio': municipios, 
                'Comunidade': comunidades, 
                'Latitude': latitudes, 
                'Longitude': longitudes, 
                'Num_Familias': numero_de_familias
            })

            # Filtrar linhas com valores não nulos nas colunas de latitude e longitude
            df = df.dropna(subset=['Latitude', 'Longitude'])

            if not df.empty:
                px.set_mapbox_access_token('pk.eyJ1IjoibWpkYXRhc2NpZW5jZSIsImEiOiJjbGFlY3hwbGcwbWlxM3Nxa2NuOWh4cmNzIn0.2ye_ghCe_WAgIpqueUqedA')

                fig = px.scatter_mapbox(
                    df, 
                    lat='Latitude', 
                    lon='Longitude',
                    color=df['Municipio'],
                    color_discrete_sequence=["fuchsia"],
                    size_max=15,
                    zoom=10,
                    hover_name='Comunidade',
                    hover_data='Num_Familias',
                    height=700,
                )

                fig.update_layout(mapbox_style="streets")
                fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
                fig.write_html('mapa_interativo.html')

                webbrowser.open('mapa_interativo.html')

            else:
                st.warning('Não há registros válidos para exibir.', title='Erro')
        else:
            st.warning('Não há registros para exibir.', title='Erro')