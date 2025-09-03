import pandas as pd
import streamlit as st
import sqlite3
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from constantes import FASE_PROCESSO
from pagina_pesquisa import salvar_extrato_planilha

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

def processos_por_fase():
    conectar_banco_de_dados()
    st.subheader("Processos por Fase")

    # Selectbox para selecionar a fase
    fase_selecionada = st.selectbox(
        "Selecione a fase do processo:",
        options=FASE_PROCESSO
    )

    # Verificar se uma fase foi selecionada (ignorar opção vazia)
    if fase_selecionada:  # Só prossegue se uma fase for selecionada (não vazia)
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
    else:
        st.warning("Selecione uma fase para visualizar os processos.")

    st.markdown(
                    f"<p style='color: #FFFFFF; background-color: #1f77b4; padding: 1px; border-radius: 1px;'>",
                    unsafe_allow_html=True
                )

def grafico_processos_por_fase():
    conn = conectar_banco_de_dados()
    cursor = conn.cursor()

    cursor.execute("SELECT Fase_Processo, COUNT(*) as Total FROM processos WHERE Fase_Processo != 'Inicial' GROUP BY Fase_Processo")
    registros = cursor.fetchall()

    if registros:
        # Extrair os dados das fases e suas contagens
        fases = [registro[0] for registro in registros]
        contagens = [registro[1] for registro in registros]
        data = pd.DataFrame({'Fase': fases, 'Contagem': contagens})

        col1, col2 = st.columns(2)

        with col2:
            st.write(" ")
        with col1:
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.barplot(x=contagens, y=fases, data=data, palette="Set1")

            # Configurações do gráfico
            ax.set_title('Processos por Fase', fontsize=16)
            sns.despine(right=True, top=True, bottom=True, left=True)
            plt.tick_params(bottom=False, labelbottom=False)

            # Adicionar rótulos (quantidades) ao lado de cada barra
            for i, contagens in enumerate(contagens):
                ax.text(contagens + 0.1, i, str(contagens), ha='left', va='center', weight='bold', fontsize='10')

            plt.tight_layout()
            st.pyplot(fig)
    else:
        st.warning('Não há registros para exibir.', title='Erro')
    
    st.markdown(
                    f"<p style='color: #FFFFFF; background-color: #1f77b4; padding: 1px; border-radius: 1px;'>",
                    unsafe_allow_html=True
                )

def processos_por_municipio():
    st.write("### Processos por Município")
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
        
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(data, height=660)
            st.write("Comunidades quilombolas que demandam regularização estão presentes em 79 dos 217 municípios do Maranhão.")
        with col2:
            data = data.sort_values(by='Número de Processos', ascending=False)
            fig, ax = plt.subplots(figsize=(6, 10))
            num_cores = len(municipios) 
            palette = sns.color_palette("viridis", num_cores)
            sns.barplot(x='Número de Processos', y='Municípios', data=data, palette=palette)

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
    
    # Fechar a conexão com o banco de dados
    cursor.close()
    conn.close()

def data_abertura():
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

        col1, col2 = st.columns(2)
        with col1:
            # Plot do gráfico de linhas
            fig, ax = plt.subplots(figsize=(8, 6))
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
        with col2:
            st.write("")

def plotar_mapa_interativo():
    if st.button("Plotar Mapa"):
        st.write("### Geolocalização das Comunidades Quilombolas")
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
                    zoom=6,
                    hover_name='Comunidade',
                    hover_data='Num_Familias',
                    height=700,
                )

                fig.update_layout(mapbox_style="streets")
                fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                )

                with st.spinner("Gerando o mapa..."):
                    st.plotly_chart(fig)

            else:
                st.warning('Não há registros válidos para exibir.', icon="⚠️")
        else:
            st.warning('Não há registros para exibir.', icon="⚠️")

    st.markdown(
                    f"<p style='color: #FFFFFF; background-color: #1f77b4; padding: 1px; border-radius: 1px;'>",
                    unsafe_allow_html=True
                )
    


# Função de conexão
def conectar_banco_de_dados():
    return sqlite3.connect("sisreq.db")

# Função adaptada para Streamlit
def exibir_status_pnra():
    conn = conectar_banco_de_dados()
    cursor = conn.cursor()

    # Consulta ao banco
    cursor.execute("""
        SELECT PNRA, COUNT(*) AS Tipo_PNRA 
        FROM processos 
        WHERE PNRA IN ('ANDAMENTO', 'CONCLUIDO') 
        GROUP BY PNRA
    """)
    resultados = cursor.fetchall()
    conn.close()

    if resultados:
        # Separar os resultados
        pnra_status = [r[0] for r in resultados]
        tipo_pnra = [r[1] for r in resultados]

        # Criar DataFrame
        data = pd.DataFrame({'Status PNRA': pnra_status, 'Quantidade': tipo_pnra})

        # Exibir tabela
        st.subheader("📊 Status do PNRA em Regularização Quilombola")
        st.dataframe(data, use_container_width=True)

        # Criar gráfico de barras com Matplotlib
        fig, ax = plt.subplots(figsize=(5, 2))
        ax.barh(pnra_status, tipo_pnra, color="steelblue")
        
        # Configurações do gráfico
        #ax.set_xlabel("Quantidade")
        #ax.set_ylabel("Status PNRA")
        ax.set_title("Status do PNRA em Regularização Quilombola")
        ax.set_xlabel('')
        ax.set_ylabel('')
        sns.set_style("white")
        sns.despine(right=True, top=True, bottom=False, left=False)
        plt.xticks(rotation=45)  # Rotacionar os rótulos do eixo x para melhor legibilidade


        # Adicionar rótulos
        for i, quantidade in enumerate(tipo_pnra):
            ax.text(quantidade + 0.1, i, str(quantidade), va='center', weight='bold')

        # Mostrar gráfico no Streamlit
        st.pyplot(fig)

    else:
        st.warning("⚠️ Não há registros para exibir no banco de dados.")


def criar_dataframe(cursor, registros):
    """Cria DataFrame a partir de registros do banco sem quebrar mesmo que o schema mude"""
    try:
        colnames = [desc[0] for desc in cursor.description]  # tenta pegar nomes reais
        if len(colnames) == len(registros[0]):  # confere se bate o número de colunas
            return pd.DataFrame(registros, columns=colnames)
        else:
            # nomes inconsistentes, gera genéricos
            return pd.DataFrame(registros, columns=[f"col_{i}" for i in range(len(registros[0]))])
    except Exception:
        # fallback: nomes genéricos
        return pd.DataFrame(registros, columns=[f"col_{i}" for i in range(len(registros[0]))])


# Conexão com banco
def conectar_banco_de_dados():
    return sqlite3.connect("sisreq.db")

def territorios_identificados():
    conn = conectar_banco_de_dados()
    cursor = conn.cursor()

    query_base = """
        SELECT * FROM processos WHERE 
        Relatorio_Antropologico LIKE '%Execução_Direta%' OR 
        Relatorio_Antropologico LIKE '%Contrato%' OR 
        Relatorio_Antropologico LIKE '%Doação%' OR 
        Relatorio_Antropologico LIKE '%Acordo_Coop_Técnica%' OR 
        Relatorio_Antropologico LIKE '%Termo_Execução_Descentralizada%'
    """
    cursor.execute(query_base)
    registros = cursor.fetchall()

    # usa função robusta
    df = criar_dataframe(cursor, registros)

    cursor.execute(f"SELECT COUNT(*) FROM ({query_base})")
    total = cursor.fetchone()[0]
    conn.close()

    st.subheader("📑 Territórios Identificados")

    if not df.empty:
        if 'ID' in df.columns:
            df = df.drop(columns=['ID'])
            df.index = df.index + 1
        filtro = st.text_input("🔍 Filtrar por Fase do Processo:")

        if filtro and "Fase_Processo" in df.columns:
            df_filtrado = df[df["Fase_Processo"].str.contains(filtro, case=False, na=False)]
        else:
            df_filtrado = df

        st.dataframe(df_filtrado, use_container_width=True)
        if st.button("Área Total Identificada"):
            exibir_area_total_em_territorios_identificados()
        st.info(f"✅ Total de Processos: {total} registros encontrados com Território Identificado")

    else:
        st.warning("⚠️ Não há registros de Territórios Identificados.")
    
    st.markdown(
                    f"<p style='color: #FFFFFF; background-color: #1f77b4; padding: 1px; border-radius: 1px;'>",
                    unsafe_allow_html=True
                )
        

def exibir_area_total_em_territorios_identificados():
    conn = conectar_banco_de_dados()
    cursor = conn.cursor()

    query = """
        SELECT SUM(Area_ha) 
        FROM processos 
        WHERE Relatorio_Antropologico LIKE '%Execução_Direta%' 
        OR Relatorio_Antropologico LIKE '%Contrato%' 
        OR Relatorio_Antropologico LIKE '%Doação%' 
        OR Relatorio_Antropologico LIKE '%Acordo_Coop_Técnica%' 
        OR Relatorio_Antropologico LIKE '%Termo_Execução_Descentralizada%'
    """
    cursor.execute(query)
    totalArea = cursor.fetchone()[0]
    conn.close()

    if totalArea is not None:
        total_area_formatado = f"{totalArea:,.2f}".replace(",", ".")  # Formato decimal brasileiro
        st.success(f"🌍 Área Total: **{total_area_formatado} hectares** em Territórios Identificados.")
    else:
        st.warning("⚠️ Não há registros de área para exibir.")

def exibir_total_de_familias_em_territorios_identificados():
    conn = conectar_banco_de_dados()
    cursor = conn.cursor()

    query = """
        SELECT SUM(Num_familias) 
        FROM processos 
        WHERE Relatorio_Antropologico LIKE '%Execução_Direta%' 
        OR Relatorio_Antropologico LIKE '%Contrato%' 
        OR Relatorio_Antropologico LIKE '%Doação%' 
        OR Relatorio_Antropologico LIKE '%Acordo_Coop_Técnica%' 
        OR Relatorio_Antropologico LIKE '%Termo_Execução_Descentralizada%'
    """
    cursor.execute(query)
    total_familias = cursor.fetchone()[0]
    conn.close()

    if total_familias is not None:
        total_familias_formatado = f"{int(total_familias):,}".replace(",", ".")  # formato brasileiro
        st.success(f"👨‍👩‍👧 Total de Famílias: **{total_familias_formatado}** em Territórios Identificados.")
    else:
        st.warning("⚠️ Não há registros de famílias para exibir.")



# Função: Territórios Não Identificados
def territorios_nao_identificados():
    conn = conectar_banco_de_dados()
    cursor = conn.cursor()

    query = "SELECT * FROM processos WHERE Relatorio_Antropologico LIKE '%Sem_Relatório%'"
    cursor.execute(query)
    registros = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM processos WHERE Relatorio_Antropologico LIKE '%Sem_Relatório%'")
    total = cursor.fetchone()[0]
    conn.close()

    st.subheader("📑 Territórios Não Identificados")

    if registros:
        colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(registros, columns=colnames)

        # Filtro por Ano de Abertura (coluna 2) ou ACP (coluna 23 no seu código)
        filtro = st.text_input("🔍 Filtrar por Ano de Abertura do Processo ou ACP:")

        if filtro:
            df_filtrado = df[
                df["Data_Abertura"].str.contains(filtro, case=False, na=False) |
                df["Acao_Civil_Publica"].str.contains(filtro, case=False, na=False)
            ]
        else:
            df_filtrado = df

        st.dataframe(df_filtrado, use_container_width=True)
        st.info(f"✅ Total de Processos: {total} Território(s) Não Identificado(s)")

        if st.button("📄 Extrato"):
            salvar_extrato_planilha(df_filtrado)

    else:
        st.warning("⚠️ Não há registros de Territórios Não Identificados.")


def exibir_processos_com_acao_civil():
    conn = conectar_banco_de_dados()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Acao_Civil_Publica, COUNT(*) AS Tipo_AcaoCivilPublica 
        FROM processos 
        WHERE Acao_Civil_Publica != 'Sem ACP' 
        GROUP BY Acao_Civil_Publica
    """)
    resultados = cursor.fetchall()
    conn.close()

    st.subheader("⚖️ Ação Civil Pública em Regularização Quilombola")


    if resultados:
        acaocivil = []
        tipo_decisao = []

        for resultado in resultados:
            acaocivil.append(resultado[0])
            tipo_decisao.append(resultado[1])

        # Criar DataFrame
        data = pd.DataFrame({
            'ACP': acaocivil,
            'Quantidade': tipo_decisao
        })

        # Plot do gráfico
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(x="Quantidade", y="ACP", data=data, palette="Set1", ax=ax)

        # Configurações do gráfico
        ax.set_title('Ação Civil Pública em Regularização Quilombola')
        ax.set_xlabel('')
        ax.set_ylabel('')
        sns.set_style("white")
        sns.despine(right=True, top=True, bottom=False, left=False)

        # Adicionar rótulos (quantidades) ao lado de cada barra
        for i, quantidade in enumerate(data["Quantidade"]):
            ax.text(quantidade + 0.1, i, str(quantidade), 
                    ha='left', va='center', weight='bold')

        plt.tight_layout()

        # Exibir no Streamlit
        st.pyplot(fig)
        st.dataframe(data, use_container_width=True)

    else:
        st.warning("⚠️ Não há registros de Ação Civil Pública para exibir.")

def exibir_status_pnra():
    conn = conectar_banco_de_dados()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT PNRA, COUNT(*) AS Tipo_PNRA 
        FROM processos 
        WHERE PNRA IN ('ANDAMENTO', 'CONCLUIDO', 'NAO-INICIADO') 
        GROUP BY PNRA
    """)
    resultados = cursor.fetchall()

    if resultados:
        pnra_status = []
        tipo_pnra = []

        for resultado in resultados:
            pnra_status.append(resultado[0])
            tipo_pnra.append(resultado[1])

        # Criar DataFrame
        data = pd.DataFrame({
            'Status PNRA': pnra_status,
            'Quantidade': tipo_pnra
        })

        # Criar gráfico com Plotly
        fig = px.bar(
            data,
            x="Quantidade",
            y="Status PNRA",
            orientation="h",  # barras horizontais
            text="Quantidade",
            color="Status PNRA",
            color_discrete_sequence=px.colors.qualitative.Set1
        )

        # Ajustes visuais
        fig.update_layout(
            title="Status do PNRA em Regularização Quilombola",
            xaxis_title="Quantidade",
            yaxis_title="",
            plot_bgcolor="black",
            showlegend=False
        )

        fig.update_traces(
            textposition="outside",
        )

        # Exibir no Streamlit
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Não há registros para exibir.")

import streamlit as st
import pandas as pd

def rtids_publicados():
    conn = conectar_banco_de_dados()
    cursor = conn.cursor()
    
    # Contagem total de RTID publicados
    cursor.execute("SELECT COUNT(*) as Total FROM processos WHERE Edital_DOU IS NOT NULL AND Edital_DOU != ''")
    totalRtidPublicado = cursor.fetchone()[0]

    # Busca todos os registros com Edital_DOU
    cursor.execute("SELECT * FROM processos WHERE Edital_DOU IS NOT NULL AND Edital_DOU != ''")
    registros = cursor.fetchall()

    if registros:
        # Obter nomes das colunas
        colunas = [desc[0] for desc in cursor.description]

        # Criar DataFrame
        df = pd.DataFrame(registros, columns=colunas)

        # Campo de filtro
        filtro = st.text_input("🔎 Filtrar por Ano de Publicação (coluna Edital_DOU):")

        # Aplicar filtro
        if filtro:
            df_filtrado = df[df["Edital_DOU"].astype(str).str.contains(filtro, case=False, na=False)]
        else:
            df_filtrado = df

        # Exibir tabela no Streamlit
        st.dataframe(df_filtrado, use_container_width=True)

        # Exibir total
        st.metric(label="📊 Total de RTID´s Publicados", value=totalRtidPublicado)

        # Botões de ações
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Extrato"):
                salvar_extrato_planilha(df_filtrado.to_records(index=False))
                st.success("✅ Extrato exportado com sucesso!")

        with col2:
            if st.button("👨‍👩‍👧 Número de Famílias"):
                exibir_total_de_familias_em_rtids_publicados()

        with col3:
            if st.button("🌍 Área Identificada"):
                exibir_area_total_em_rtids_publicados()

    else:
        st.warning("⚠️ Não há registros para exibir.")
