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
    if "CHAVE_API" not in os.environ:
        st.error("A CHAVE_API não está definida no arquivo .env.")
        return

    # 1. Inicializa a configuração da API
    genai.configure(api_key=os.environ["CHAVE_API"])
    
    # A inicialização do cliente não é mais necessária, pois removemos a API de arquivos.
    # try:
    #     client = genai.Client()
    # except Exception as e:
    #     st.error(f"Erro ao inicializar o cliente da Gemini API: {e}")
    #     return

    def fetch_data_from_db(db_path):
        """Conecta ao banco de dados SQLite e retorna um DataFrame com os dados."""
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM processos"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def save_dataframe_to_csv(df, csv_path):
        """Salva um DataFrame em um arquivo CSV."""
        df.to_csv(csv_path, index=False)

    # Funções de upload e espera removidas, pois passaremos os dados como texto.
    # def upload_to_gemini(...):
    # def wait_for_files_active(...):
    
    # ----------------------------------------------------------------------
    # 1. PREPARAÇÃO DE DADOS (FORA DA SESSÃO DE CHAT)
    # ----------------------------------------------------------------------
    db_path = "sisreq.db"
    data_content = ""
    
    if os.path.exists(db_path):
        try:
            df = fetch_data_from_db(db_path)
            # Converte o DataFrame para uma string CSV para passar ao modelo
            data_content = df.to_csv(index=False)
            st.session_state["data_loaded"] = True
            
            # Limpeza: Removemos o temp_data.csv, pois leremos diretamente o conteúdo.
            # O arquivo não será mais necessário para a API.
            
        except Exception as e:
            st.error(f"Erro ao carregar os dados do banco de dados: {e}")
            st.session_state["data_loaded"] = False
            return
    else:
        st.error("Banco de dados 'sisreq.db' não encontrado. Verifique o caminho do arquivo.")
        return

    # ----------------------------------------------------------------------
    # 2. CONFIGURAÇÃO E INÍCIO DO CHAT
    # ----------------------------------------------------------------------
    
    # Instrução de sistema aprimorada para incluir o contexto dos dados
    system_instruction_template = (
        "Você é o assistente virtual Oráculo especialista em processos de regularização fundiária de territórios quilombolas "
        "do Instituto Nacional de Colonização e Reforma Agrária. Responda conforme for perguntado. Mantenha-se no contexto "
        "da regularização quilombola. Se for perguntado fora desse contexto, informe que não pode ajudar. "
        "O tom da conversa deve ser amigável, utilize emojis nas respostas.\n\n"
        "INFORMAÇÕES DE CONTEXTO: Você tem acesso aos seguintes dados reais e atuais dos processos de regularização quilombola do INCRA no Maranhão. Utilize estes dados para responder a perguntas sobre processos, status, ou territórios:\n\n"
        "--- INÍCIO DOS DADOS ---\n"
        f"{data_content}\n"
        "--- FIM DOS DADOS ---\n"
    )

    generation_config = {
        "temperature": 0.3,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 1600,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config,
        system_instruction=system_instruction_template,
    )

    # ----------------------------------------------------------------------
    # 3. INTERFACE STREAMLIT
    # ----------------------------------------------------------------------
    
    # Inicializa o histórico de mensagens do Streamlit
    if "messages" not in st.session_state:
        # A instrução de sistema já contém o contexto de dados, então o histórico começa vazio
        st.session_state.messages = []

    # Cria a Interface
    st.subheader("Converse com o Óraculo✨")
    st.success("Dados carregados com sucesso e pronto para interação!")

    # Exibe o histórico de mensagens
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Loop de interação com o usuário (Chat UI padrão do Streamlit)
    user_input = st.chat_input("Digite sua pergunta:")

    if user_input:
        # Adiciona a mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("O Oráculo está pensando..."):
                
                # Prepara o histórico de mensagens para o Gemini (apenas mensagens de texto)
                gemini_history = [
                    {"role": "user", "parts": [msg["content"]]} 
                    if msg["role"] == "user" else 
                    {"role": "model", "parts": [msg["content"]]}
                    for msg in st.session_state.messages
                ]

                # Inicia/Continua a sessão de chat com o histórico
                # O contexto dos dados está em 'system_instruction'
                chat_session = model.start_chat(history=gemini_history)
                response = chat_session.send_message(user_input)

                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})