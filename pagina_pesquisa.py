import sqlite3
import pandas as pd
import io
import streamlit as st
from constantes import MUNICIPIOS
from obter_todos_registros import obter_todos_os_registros

def criar_submenu():
    submenu = st.radio("",
           options=["Escolha uma Opção de Pesquisa:" ,"Município", "Comunidade", "Nº do Processo", "Quilombos em Assentamentos"])
    #Lógica do submenu
    if submenu == "Município":
        filtrar_por_municipio()
    elif submenu == "Comunidade":
        filtrar_por_comunidade()
    elif submenu == "Nº do Processo":
        filtrar_por_numero_processo()
    elif submenu == "Quilombos em Assentamentos":
        quilombos_em_assentamentos()

def filtrar_por_comunidade():
    df = obter_todos_os_registros()
    if not df.empty:
        if 'ID' in df.columns:
            df = df.drop(columns=['ID'])
            df.index = df.index + 1
    
    # Criar identificadores únicos de comunidade e município
    df['Comunidade_Municipio'] = df['Comunidade'] + " - " + df['Municipio']
    comunidades_disponiveis = df['Comunidade_Municipio'].unique().tolist()
    
    # Adicionar opção vazia no início da lista
    opcoes = [""] + comunidades_disponiveis

    # Caixa de seleção para escolha da comunidade
    #st.markdown('<h4 style="color: #1f77b4;">Pesquisar por Comunidade</h4>', unsafe_allow_html=True)
    st.subheader("Pesquisar por Comunidade")
    comunidade_selecionada = st.selectbox(
        'Selecione a comunidade:', 
        options=opcoes,
        index=0,  # Seleciona a primeira opção (vazia)
        help="Selecione uma comunidade ou município para iniciar a busca"
    )
    
    # Mensagem informativa quando nenhuma comunidade está selecionada
    if not comunidade_selecionada:
        st.info('🔍 Selecione uma comunidade para iniciar a busca')
        return  # Sai da função sem processar mais nada

    # Validar a seleção da comunidade
    if comunidade_selecionada:
        comunidade, municipio = comunidade_selecionada.split(" - ")
        registros_filtrados = df[(df['Comunidade'] == comunidade) & (df['Municipio'] == municipio)]

        if not registros_filtrados.empty:
            for index, registro in registros_filtrados.iterrows():
                st.markdown(
                    f"<p style='color: #FFFFFF; background-color: #1f77b4; padding: 1px; border-radius: 1px;'>",
                    unsafe_allow_html=True
                )

                # Divisão em colunas para exibição de dados
                col1, col2, col3, col4 = st.columns(4)

                # Coluna 1
                with col1:
                    st.markdown(f"<p><strong>Número do Processo:</strong> {registro[0]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Data de Abertura:</strong> {registro[1]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Comunidade:</strong> {registro[2]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Município:</strong> {registro[3]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Número de Famílias:</strong> {registro[5]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Área Identificada (ha):</strong> {registro[4]}</p>", unsafe_allow_html=True)

                # Coluna 2
                with col2:
                    st.markdown(f"<p><strong>Fase do Processo:</strong> {registro[6]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Etapa RTID:</strong> {registro[7]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Relatório Antropológico:</strong> {registro[15]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Certidão FCP:</strong> {registro[18]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Data de Certificação:</strong> {registro[19]}</p>", unsafe_allow_html=True)

                # Coluna 3
                with col3:
                    st.markdown(f"<p><strong>Área Titulada (ha):</strong> {registro[12]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Título:</strong> {registro['Titulo']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>PNRA:</strong> {registro['PNRA']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Latitude:</strong> {registro['Latitude']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Longitude:</strong> {registro['Longitude']}</p>", unsafe_allow_html=True)

                # Coluna 4
                with col4:
                    st.markdown(f"<p><strong>Edital DOU:</strong> {registro['Edital_DOU']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Edital DOE:</strong> {registro['Edital_DOE']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Portaria DOU:</strong> {registro['Portaria_DOU']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Decreto DOU:</strong> {registro['Decreto_DOU']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Sobreposição Territorial:</strong> {registro['Sobreposicao']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Detalhes de Sobreposição:</strong> {registro['Analise_de_Sobreposicao']}</p>", unsafe_allow_html=True)
           
            # informações adicionais
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"<p><strong>Ação Civil Pública:</strong> {registro['Acao_Civil_Publica']}</p>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<p><strong>Data da Sentença:</strong> {registro['Data_Decisao']}</p>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<p><strong>Teor/Prazo da Sentença:</strong> {registro[24]}</p>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"<p><strong>Outras Informações:</strong> {registro['Outras_Informacoes']}</p>", unsafe_allow_html=True)
                
        else:
            st.warning("Comunidade não encontrada. Por favor, verifique o nome informado.")

def filtrar_por_municipio():
    
    #st.markdown('<h4 style="color: #1f77b4;">Pesquisar por Município</h4>', unsafe_allow_html=True)
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


def filtrar_por_numero_processo():
    df = obter_todos_os_registros()
    if not df.empty:
        if 'ID' in df.columns:
            df = df.drop(columns=['ID'])
            df.index = df.index + 1
    
    # Obter lista de números de processo disponíveis
    numeros_processo_disponiveis = df['Numero'].unique().tolist()
    
    # Adicionar opção vazia no início da lista
    opcoes = [""] + numeros_processo_disponiveis

    # Caixa de seleção para escolha do número do processo
    st.subheader('Pesquisar por Número do Processo')
    #st.markdown('<h4 style="color: #1f77b4;">Pesquisar por Número do Processo</h4>', unsafe_allow_html=True)
    numero_processo_selecionado = st.selectbox(
        'Selecione o número do processo:', 
        options=opcoes,
        index=0,  # Seleciona a primeira opção (vazia)
        help="Selecione um número de processo para iniciar a busca"
    )
    
    # Mensagem informativa quando nenhum processo está selecionado
    if not numero_processo_selecionado:
        st.info('🔍 Selecione um número de processo para iniciar a busca')
        return  # Sai da função sem processar mais nada

    # Validar a seleção do processo
    if numero_processo_selecionado:
        registros_filtrados = df[df['Numero'] == numero_processo_selecionado]

        if not registros_filtrados.empty:
            for index, registro in registros_filtrados.iterrows():
                st.markdown(
                    f"<div style='color: #FFFFFF; background-color: #1f77b4; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>"
                    f"<strong>Processo: {numero_processo_selecionado}</strong>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                # Divisão em colunas para exibição de dados
                col1, col2, col3, col4 = st.columns(4)

                # Coluna 1
                with col1:
                    st.markdown(f"<p><strong>Número do Processo:</strong> {registro[0]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Data de Abertura:</strong> {registro[1]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Comunidade:</strong> {registro[2]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Município:</strong> {registro[3]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Número de Famílias:</strong> {registro[5]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Área Identificada (ha):</strong> {registro[4]}</p>", unsafe_allow_html=True)

                # Coluna 2
                with col2:
                    st.markdown(f"<p><strong>Fase do Processo:</strong> {registro[6]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Etapa RTID:</strong> {registro[7]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Relatório Antropológico:</strong> {registro[15]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Certidão FCP:</strong> {registro[18]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Data de Certificação:</strong> {registro[19]}</p>", unsafe_allow_html=True)

                # Coluna 3
                with col3:
                    st.markdown(f"<p><strong>Área Titulada (ha):</strong> {registro[12]}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Título:</strong> {registro['Titulo']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>PNRA:</strong> {registro['PNRA']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Latitude:</strong> {registro['Latitude']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Longitude:</strong> {registro['Longitude']}</p>", unsafe_allow_html=True)

                # Coluna 4
                with col4:
                    st.markdown(f"<p><strong>Edital DOU:</strong> {registro['Edital_DOU']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Edital DOE:</strong> {registro['Edital_DOE']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Portaria DOU:</strong> {registro['Portaria_DOU']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Decreto DOU:</strong> {registro['Decreto_DOU']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Sobreposição Territorial:</strong> {registro['Sobreposicao']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Detalhes de Sobreposição:</strong> {registro['Analise_de_Sobreposicao']}</p>", unsafe_allow_html=True)
      
           
                     
        else:
            st.warning("Número do processo não encontrado. Por favor, verifique o número informado.")

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
    st.subheader('Quilombos em Assentamentos')
    # st.markdown('<h4 style="color: #1f77b4;">Quilombos em Assentamentos</h4>', unsafe_allow_html=True)
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