import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
from obter_todos_registros import obter_todos_os_registros
from tela_cadastro import tela_de_cadastro
from editar import pagina_editar

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
            Teor_Decisao_Prazo_Sentença TEXT,
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
    conn = sqlite3.connect('sisreq.db')  # Corrigido para usar o mesmo banco de dados
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE usuario = ? AND senha = ?', (usuario, hash_senha(senha)))
    dados = cursor.fetchone()
    conn.close()
    return dados is not None

# Inicializar banco de dados
iniciar_banco_de_dados()

# Tela de login
def tela_login():
    st.markdown('<h2 style="color: "#1f77b4";">Login</h2>', unsafe_allow_html=True)
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
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
    st.markdown('<h2 style="color: "#1f77b4";">SISREQ - Sistema de Regularização Quilombola</h2>', unsafe_allow_html=True)
    st.subheader("Registros Salvos")
    df = obter_todos_os_registros()
    if not df.empty:
        if 'ID' in df.columns:
            df = df.drop(columns=['ID'])
            df.index = df.index + 1
            st.dataframe(df, height=600)

    if st.button("Exportar para Excel"):
        df.to_excel('processos.xlsx', index=False)
        st.success("Dados exportados com sucesso para sisreq.xlsx")
        with open("processos.xlsx", "rb") as file:
            st.download_button(
                label="Baixar Excel",
                data=file,
                file_name="processos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
# Função para Página Sobre
def pagina_about():
    st.subheader("Sobre o Projeto")
    st.write("""
        Sistema de registro dos processos de regularização quilombola.
        Projeto experimental em desenvolvimento. Focado em otimizar o registro, 
        visualização e consulta dos processos cadastrados.
        Durante a fase de desenvolvimento, algumas funcionalidades podem não responder corretamente.
        Desenvolvido por **Michael JM Cardoso** - Antropólogo e Programador.
    """)

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
    st.sidebar.title(f"Bem-vindo, {st.session_state['usuario_logado']}")
    if st.sidebar.button("Sair"):
        del st.session_state['usuario_logado']
        st.rerun()
        #st.experimental_rerun()
    
    # Adicionar "Gerenciar Usuários" apenas para o admin
    opcoes_paginas = ["Página Inicial", "Editar Registro", "Tela de Cadastro", "Visualizações", "Sobre"]
    if st.session_state['usuario_logado'] == "admin":
        opcoes_paginas.insert(3, "Gerenciar Usuários")  # Insere antes da página "Sobre"

    pagina_selecionada = st.sidebar.radio("Selecione uma Página", opcoes_paginas)

    # Função para gerenciar usuários (acessível apenas pelo admin)
    def gerenciar_usuarios():
        st.header("Gerenciar Usuários")
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

        st.subheader("Usuários Cadastrados")
        conn = sqlite3.connect('sisreq.db')
        usuarios = pd.read_sql_query("SELECT id, usuario FROM usuarios", conn)
        conn.close()

        if not usuarios.empty:
            usuarios = usuarios.rename(columns={"id": "ID", "usuario": "Usuário"})
            st.dataframe(usuarios, use_container_width=True)

    # Redirecionamento de páginas
    if pagina_selecionada == "Página Inicial":
        pagina_inicial()
    elif pagina_selecionada == "Tela de Cadastro":
        tela_de_cadastro()
    elif pagina_selecionada == "Editar Registro":
        pagina_editar()
    # elif pagina_selecionada == "Visualizações":
    #     pagina_visualizacoes()
    elif pagina_selecionada == "Gerenciar Usuários":
        if st.session_state['usuario_logado'] == "admin":
            gerenciar_usuarios()
        else:
            st.error("Você não tem permissão para acessar esta página.")
    elif pagina_selecionada == "Sobre":
        pagina_about()
