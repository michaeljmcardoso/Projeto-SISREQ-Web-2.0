import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import io
from datetime import datetime
from obter_todos_registros import obter_todos_os_registros
from pagina_cadastro import tela_de_cadastro
from pagina_editar import pagina_editar
from pagina_dashboard import dashboard
from pagina_pesquisa import criar_submenu
from pagina_chat import iniciar_chat

# Função para hash de senha 
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def iniciar_banco_de_dados():
    conn = sqlite3.connect('sisreq.db')
    cursor = conn.cursor()
    
    #Tabela para registros
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS processos (
            ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            Numero TEXT, 
            Data_Abertura DATE,
            Comunidade TEXT,
            Municipio TEXT,
            Area_ha NUMERIC,
            Num_familias NUMERIC,
            Fase_Processo TEXT,
            Etapa_RTID TEXT,
            Edital_DOU TEXT,
            Edital_DOE TEXT,
            Portaria_DOU DATE,
            Decreto_DOU DATE,
            Area_ha_Titulada NUMERIC,
            Titulo TEXT,
            PNRA TEXT,
            Relatorio_Antropologico TEXT,
            Latitude NUMERIC,
            Longitude NUMERIC,
            Certidao_FCP TEXT,
            Data_Certificacao DATE,
            Sobreposicao TEXT,
            Analise_de_Sobreposicao TEXT,
            Acao_Civil_Publica TEXT,
            Data_Decisao DATE,
            Teor_Decisao_Prazo_Sentenca TEXT,
            Outras_Informacoes TEXT
        )
        '''
    )

    # Tabela para usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            senha TEXT
        )
    ''')

    # # Tabela para contatos
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS contatos (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         comunidade TEXT,
    #         nome TEXT,
    #         contato NUMERIC UNIQUE
    #     )
    # ''')
    
    # Adicionar um usuário administrador (somente na primeira execução)
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO usuarios (usuario, senha) VALUES (?, ?)', 
                       ('admin', hash_senha('admin123')))
        st.info("Usuário administrador criado.")
    
    conn.commit()
    conn.close()

# Verificar credenciais
def verificar_credenciais(usuario, senha):
    conn = sqlite3.connect('sisreq.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE usuario = ? AND senha = ?', (usuario, hash_senha(senha)))
    dados = cursor.fetchone()
    conn.close()
    return dados is not None

# Inicializar banco de dados
iniciar_banco_de_dados()

# Carregar dados do banco
conn = sqlite3.connect('sisreq.db')
df = pd.read_sql_query("SELECT * FROM processos", conn)

# Garantir que todos os valores sejam strings antes de usar `.str.replace()`
df['Area_ha'] = df['Area_ha'].astype(str).str.replace(',', '.', regex=False)

# Converter para valores numéricos, substituindo valores inválidos por 0
df['Area_ha'] = pd.to_numeric(df['Area_ha'], errors='coerce').fillna(0)

# Atualizar os valores diretamente no banco
for index, row in df.iterrows():
    conn.execute(
        "UPDATE processos SET Area_ha = ? WHERE ID = ?",
        (row['Area_ha'], row['ID'])
    )

conn.commit()
conn.close()

# Carregar dados do banco
conn = sqlite3.connect('sisreq.db')
df = pd.read_sql_query("SELECT * FROM processos", conn)

# Garantir que todos os valores sejam strings antes de usar `.str.replace()`
df['Area_ha_Titulada'] = df['Area_ha_Titulada'].astype(str).str.replace(',', '.', regex=False)

# Converter para valores numéricos, substituindo valores inválidos por 0
df['Area_ha_Titulada'] = pd.to_numeric(df['Area_ha_Titulada'], errors='coerce').fillna(0)

# Atualizar os valores diretamente no banco
for index, row in df.iterrows():
    conn.execute(
        "UPDATE processos SET Area_ha_Titulada = ? WHERE ID = ?",
        (row['Area_ha_Titulada'], row['ID'])
    )

conn.commit()
conn.close()

# Carregar dados do banco
conn = sqlite3.connect('sisreq.db')
df = pd.read_sql_query("SELECT * FROM processos", conn)

# Garantir que todos os valores sejam strings antes de usar `.str.replace()`
df['Num_familias'] = df['Num_familias'].astype(str).str.replace(',', '.', regex=False)

# Converter para valores numéricos, substituindo valores inválidos por 0
df['Num_familias'] = pd.to_numeric(df['Num_familias'], errors='coerce').fillna(0)

# Atualizar os valores diretamente no banco
for index, row in df.iterrows():
    conn.execute(
        "UPDATE processos SET Num_familias = ? WHERE ID = ?",
        (row['Num_familias'], row['ID'])
    )

conn.commit()
conn.close()

# Carregar dados do banco
conn = sqlite3.connect('sisreq.db')
df = pd.read_sql_query("SELECT * FROM processos", conn)

# Garantir que todos os valores sejam strings antes de usar `.str.replace()`
df['Latitude'] = df['Latitude'].astype(str).str.replace(',', '.', regex=False)

# Converter para valores numéricos, substituindo valores inválidos por 0
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')

# Atualizar os valores diretamente no banco
for index, row in df.iterrows():
    # Se a latitude for NaN, atualize com NULL no banco de dados
    latitude_value = row['Latitude'] if not pd.isna(row['Latitude']) else None
    conn.execute(
        "UPDATE processos SET Latitude = ? WHERE ID = ?",
        (latitude_value, row['ID'])
    )

conn.commit()
conn.close()

# Carregar dados do banco
conn = sqlite3.connect('sisreq.db')
df = pd.read_sql_query("SELECT * FROM processos", conn)

# Garantir que todos os valores sejam strings antes de usar `.str.replace()`
df['Longitude'] = df['Longitude'].astype(str).str.replace(',', '.', regex=False)

# Converter para valores numéricos, substituindo valores inválidos por 0
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

# Atualizar os valores diretamente no banco
for index, row in df.iterrows():
    # Se a lotude for NaN, atualize com NULL no banco de dados
    longitude_value = row['Longitude'] if not pd.isna(row['Longitude']) else None
    conn.execute(
        "UPDATE processos SET longitude = ? WHERE ID = ?",
        (longitude_value, row['ID'])
    )

conn.commit()
conn.close()

# Tela de login
def tela_login():
    st.markdown(f"""
            <div style='display: flex; justify-content: center; align-items: center; margin-bottom: 20px;'>
                <h1 style='margin-right: -40px;'>Bem-vindo</h1>
                <img src="https://media.giphy.com/media/hvRJCLFzcasrR4ia7z/giphy.gif" style='vertical-align: middle;' width="45">
            </div>
        """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown('<h2 style="color: "#1f77b4";">Login</h2>', unsafe_allow_html=True)
        usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
        senha = st.text_input("Senha", placeholder="Digite sua senha", type="password")
    
        if st.button("Entrar"):
            if verificar_credenciais(usuario, senha):
                st.session_state['usuario_logado'] = usuario
                st.success(f"Bem-vindo, {usuario}!")
                st.rerun()
                #st.experimental_rerun()
            else:
                st.error("Credenciais inválidas.")

# Página inicial (após login)
def pagina_inicial():
    df = obter_todos_os_registros()
    pesquisar_comunidade()
    if not df.empty:
        if 'ID' in df.columns:
            df = df.drop(columns=['ID'])
            df.index = df.index + 1
            st.markdown('<h4 style="color: #1f77b5;">Controle de Processos</h4>', unsafe_allow_html=True)
            st.dataframe(df, height=500)

    if st.button("Exportar para Excel"):
        df.to_excel('processos.xlsx', index=False)
        st.success("Dados exportados com sucesso para processos.xlsx")
        with open("processos.xlsx", "rb") as file:
            st.download_button(
                label="Baixar Excel",
                data=file,
                file_name="processos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

def pesquisar_comunidade():
    df = obter_todos_os_registros()
    if not df.empty:
        if 'ID' in df.columns:
            df = df.drop(columns=['ID'])
            df.index = df.index + 1
    # Criar identificadores únicos de comunidade e município
    df['Comunidade_Municipio'] = df['Comunidade'] + " - " + df['Municipio']
    comunidades_disponiveis = df['Comunidade_Municipio'].unique().tolist()

    # Caixa de seleção para escolha da comunidade
    st.markdown('<h5 style="color: #1f77b4;">Selecione uma Comunidade ou Município:</h5>', unsafe_allow_html=True)
    comunidade_selecionada = st.selectbox(" ", options=comunidades_disponiveis)

    # Validar a seleção da comunidade
    if comunidade_selecionada:
        comunidade, municipio = comunidade_selecionada.split(" - ")
        registros_filtrados = df[(df['Comunidade'] == comunidade) & (df['Municipio'] == municipio)]

        if not registros_filtrados.empty:
            #st.markdown(f"<p style='color: #1f77b4;'><strong>Detalhes do Processo</strong></p>", unsafe_allow_html=True)

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
           
        else:
            st.warning("Comunidade não encontrada. Por favor, verifique o nome informado.")

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
    
# Função para Página Sobre
def pagina_about():
    st.subheader("Sobre o Projeto")
    st.write("""
        Sistema de registro de processos de regularização quilombola.
        Projeto experimental, em desenvolvimento. Focado em otimizar o registro, 
        visualização e consulta dos processos cadastrados. Inclui o Assistente Virtual, SISREQ_IA. 
    """)
    # Rodapé
    st.markdown(
        """
        <style>
        .rodape {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px 0;
            font-size: 12px;
            color: #666;
        }
        </style>
        <div class="rodape">
            © 2025 Desenvolvido por Michael J M Cardoso. Todos os direitos reservados.
        </div>
        """,
        unsafe_allow_html=True
    )

import sqlite3
import pandas as pd
import streamlit as st

def pagina_contatos():
    st.subheader("📞 Contatos")
    
    # Conexão com o banco de dados
    conn = sqlite3.connect('sisreq.db')
    cursor = conn.cursor()
    
    # 1. Verificar se a tabela existe e tem a estrutura correta
    try:
        cursor.execute("PRAGMA table_info(contatos)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Se a tabela não existe ou está incompleta, cria nova
        if not columns or 'comunidade' not in columns:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS contatos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comunidade TEXT NOT NULL,
                nome TEXT NOT NULL,
                contato TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            conn.commit()
    except:
        pass  # Tabela não existe ainda
        
    # 2. Formulário para adicionar novo contato
    with st.expander("➕ Adicionar Novo Contato", expanded=False):
        with st.form(key='form_novo_contato', clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                nova_comunidade = st.text_input("Comunidade/Povoado/Entidade*")
            with col2:
                novo_nome = st.text_input("Nome*")
            with col3:
                novo_contato = st.text_input("Número de Contato")
            
            if st.form_submit_button("Salvar Contato"):
                if nova_comunidade and novo_nome:
                    try:
                        cursor.execute(
                            "INSERT INTO contatos (comunidade, nome, contato) VALUES (?, ?, ?)",
                            (nova_comunidade, novo_nome, novo_contato)
                        )
                        conn.commit()
                        st.success("Contato adicionado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {str(e)}")
                else:
                    st.warning("Preencha os campos obrigatórios (*)!")
    
    # 3. Lista de contatos existentes
    st.markdown("---")
    st.subheader("📋 Lista de Contatos")
    
    try:
        df = pd.read_sql_query("SELECT * FROM contatos", conn)
        
        if not df.empty:
            # Converter a coluna de contato para string e remover formatação automática
            df['contato'] = df['contato'].astype(str).str.replace(r'\D', '', regex=True)
            
            # Mostrar tabela
            st.dataframe(
                df[['comunidade', 'nome', 'contato']],
                column_config={
                    'comunidade': 'Local',
                    'nome': 'Nome',
                    'contato': 'Contato'
                },
                hide_index=True,
                use_container_width=True
            )
            
            # 4. Opções de Edição/Exclusão
            with st.expander("⚙️ Gerenciar Contatos"):
                contato_id = st.selectbox(
                    "Selecione um contato para editar:",
                    options=df['id'],
                    format_func=lambda x: f"{df[df['id']==x]['nome'].iloc[0]} - {df[df['id']==x]['comunidade'].iloc[0]}"
                )
                
                if contato_id:
                    dados = df[df['id'] == contato_id].iloc[0]
                    
                    with st.form(key='form_editar_contato'):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            edit_comunidade = st.text_input("Local*", value=dados['comunidade'])
                        with col2:
                            edit_nome = st.text_input("Nome*", value=dados['nome'])
                        with col3:
                            edit_contato = st.text_input("Contato", value=dados['contato'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("✅ Atualizar"):
                                if edit_comunidade and edit_nome:
                                    cursor.execute(
                                        '''UPDATE contatos SET
                                        comunidade = ?,
                                        nome = ?,
                                        contato = ?
                                        WHERE id = ?''',
                                        (edit_comunidade, edit_nome, edit_contato, contato_id)
                                    )
                                    conn.commit()
                                    st.success("Atualizado!")
                                    st.rerun()
                                else:
                                    st.warning("Preencha os campos obrigatórios!")
                        with col2:
                            if st.form_submit_button("❌ Excluir"):
                                cursor.execute("DELETE FROM contatos WHERE id = ?", (contato_id,))
                                conn.commit()
                                st.success("Excluído!")
                                st.rerun()
        else:
            st.info("Nenhum contato cadastrado ainda.")
            
    except Exception as e:
        st.error(f"Erro ao carregar contatos: {str(e)}")
    
    conn.close()
    

# Adicionar novos usuários ao banco de dados
def adicionar_usuario(usuario, senha):
    try:
        conn = sqlite3.connect('sisreq.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO usuarios (usuario, senha) VALUES (?, ?)', 
                       (usuario, hash_senha(senha)))
        conn.commit()
        conn.close()
        return True, f"Usuário '{usuario}' adicionado com sucesso!"
    except sqlite3.IntegrityError:
        return False, f"Usuário '{usuario}' já existe."
    except Exception as e:
        return False, f"Erro ao adicionar usuário: {str(e)}"


if 'usuario_logado' not in st.session_state:
    tela_login()

else:
    # Menu de navegação
    st.sidebar.title(f"SISREQ - Sistema de Regularização Quilombola\nBem-vindo, {st.session_state['usuario_logado']}")
    
    # Botão para sair
    if st.sidebar.button("Sair"):
        del st.session_state['usuario_logado']
        st.rerun()
        #st.experimental_rerun()

    # Definir páginas disponíveis com base no tipo de usuário
    opcoes_paginas = ["📁Controle de Processos", "📥Iniciar Processo", "📝Editar Processo", "🔍Pesquisa", "📊Dashboard", "✨SISREQ_IA", "☎️Contatos", "ℹ️Sobre"]
    
    if st.session_state['usuario_logado'] == "admin":
        opcoes_paginas.insert(6, "👨‍💻Gerenciar Usuários")  # Adicionar "Gerenciar Usuários" antes de "Sobre"
    elif st.session_state['usuario_logado'] == "visitante":
        opcoes_paginas = [pagina for pagina in opcoes_paginas if pagina not in ["📝Editar Processo", "📥Iniciar Processo", "☎️Contatos"]]

    # Navegação principal
    pagina_selecionada = st.sidebar.radio("Selecione uma Página", opcoes_paginas)

    # Função para gerenciar usuários (apenas para admin)
    def gerenciar_usuarios():
        st.subheader("Adicionar Novo Usuário")

        col1, col2 = st.columns(2)
        with col1:
            novo_usuario = st.text_input("Novo Usuário")
        with col2:
            nova_senha = st.text_input("Senha", type="password")

        if st.button("Adicionar Usuário"):
            if novo_usuario and nova_senha:
                sucesso, mensagem = adicionar_usuario(novo_usuario, nova_senha)
                if sucesso:
                    st.success(mensagem)
                else:
                    st.error(mensagem)
            else:
                st.warning("Por favor, preencha todos os campos.")

        st.subheader("Controle de Usuários")
        conn = sqlite3.connect('sisreq.db')
        usuarios = pd.read_sql_query("SELECT id, usuario FROM usuarios", conn)
        conn.close()

        if not usuarios.empty:
            usuarios = usuarios.rename(columns={"id": "ID", "usuario": "Usuário"})
            st.dataframe(usuarios, use_container_width=True, height=490)

    # Redirecionamento de páginas
    if pagina_selecionada == "📁Controle de Processos":
        pagina_inicial()
    elif pagina_selecionada == "🔍Pesquisa":
        criar_submenu()
    elif pagina_selecionada == "📥Iniciar Processo":
        tela_de_cadastro()
    elif pagina_selecionada == "📝Editar Processo":
        pagina_editar()
    elif pagina_selecionada == "📊Dashboard":
        dashboard(False)
    elif pagina_selecionada == "👨‍💻Gerenciar Usuários":
        if st.session_state['usuario_logado'] == "admin":
            gerenciar_usuarios()
        else:
            st.error("Você não tem permissão para acessar esta página.")
    elif pagina_selecionada == "✨SISREQ_IA":
        iniciar_chat()
    elif pagina_selecionada == "ℹ️Sobre":
        pagina_about()
    elif pagina_selecionada == "☎️Contatos":
        pagina_contatos()

    st.sidebar.markdown('''
    ---
    Created with ❤️ by [Michael](https://github.com/michaeljmcardoso).
    ''')  