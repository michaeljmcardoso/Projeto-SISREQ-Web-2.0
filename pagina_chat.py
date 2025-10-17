import os
import time
import sqlite3
import pandas as pd
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

def iniciar_chat():
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()

    # Configuração da API Gemini
    genai.configure(api_key=os.environ["CHAVE_API"])

    # Configuração do modelo
    generation_config = {
        "temperature": 0.3,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 800,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config,
        system_instruction=(
            "Você é o assistente virtual Oráculo especialista em processos de regularização fundiária de territórios quilombolas "
            "do Instituto Nacional de Colonização e Reforma Agrária. Responda conforme for perguntado. Mantenha-se no contexto "
            "da regularização quilombola. Se for perguntado fora desse contexto, informe que não pode ajudar. "
            "O tom da conversa deve ser amigável, utilize emojis nas respostas."
            "Você tem acesso aos dados reais e atuais dos processos de regularização quilombola do INCRA no Maranhão."
        ),
    )

    def fetch_data_from_db(db_path):
        """Conecta ao banco de dados SQLite e retorna um DataFrame com os dados."""
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM processos"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    # Inicializa as variáveis de estado
    if "chat_initialized" not in st.session_state:
        st.session_state["chat_initialized"] = False
    if "data_context" not in st.session_state:
        st.session_state["data_context"] = ""

    # Cria a Interface
    st.subheader("Converse com o Óraculo✨")

    db_path = "sisreq.db"

    if os.path.exists(db_path):
        # Busca dados do banco
        df = fetch_data_from_db(db_path)
        
        # Prepara o contexto com os dados
        if not st.session_state["chat_initialized"]:
            # Cria um resumo dos dados para incluir no contexto
            data_summary = f"""
            Dados dos processos de regularização fundiária quilombola:
            - Total de processos: {len(df)}
            - Colunas disponíveis: {', '.join(df.columns)}
            - Primeiras linhas dos dados:
            {df.head().to_string()}
            """
            st.session_state["data_context"] = data_summary
            st.session_state["chat_initialized"] = True
            st.success("Dados carregados e prontos para interação!")

        # Inicia a sessão de chat
        chat_session = model.start_chat(history=[])

        # Adiciona o contexto dos dados na primeira mensagem se for a primeira interação
        user_input = st.text_input("Digite sua pergunta:")
        
        if user_input:
            # Combina o contexto dos dados com a pergunta do usuário
            full_prompt = f"""
            Contexto dos dados disponíveis:
            {st.session_state["data_context"]}
            
            Pergunta do usuário: {user_input}
            
            Responda com base nos dados fornecidos sobre processos de regularização fundiária quilombola.
            """
            
            response = chat_session.send_message(full_prompt)
            st.write("Resposta:", response.text)

    else:
        st.error("Banco de dados não encontrado. Verifique o caminho do arquivo.")