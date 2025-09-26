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

    # Configuração do modelo e da sessão de chat
    generation_config = {
        "temperature": 0.3,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 1500,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction=(
            "Você é o assistente virtual Oráculo especialista em processos de regularização fundiária de territórios quilombolas "
            "do Instituto Nacional de Colonização e Reforma Agrária. Responda conforme for perguntado. Mantenha-se no contexto "
            "da regularização quilombola. Se for perguntado fora desse contexto, informe que não pode ajudar. "
            "O tom da conversa deve ser amigável, utilize emojis nas respostas."
            "Você tem acesso aos dados reais e atuais dos processos de regularização quilombola do INCRA no Maranhão."
        ),
    )
    st.warning('Temporariamente indisponível.')
    # def fetch_data_from_db(db_path):
    #     """Conecta ao banco de dados SQLite e retorna um DataFrame com os dados."""
    #     conn = sqlite3.connect(db_path)
    #     query = "SELECT * FROM processos"
    #     df = pd.read_sql_query(query, conn)
    #     conn.close()
    #     return df

    # def save_dataframe_to_csv(df, csv_path):
    #     """Salva um DataFrame em um arquivo CSV."""
    #     df.to_csv(csv_path, index=False)

    # def upload_to_gemini(path, mime_type=None):
    #     """Faz upload do arquivo especificado para o Gemini."""
    #     try:
    #         file = genai.upload_file(path, mime_type=mime_type)
    #         return file
    #     except Exception as e:
    #         st.error(f"Erro no upload do arquivo: {e}")
    #         return None

    # def wait_for_files_active(files):
    #     """Aguarda até que os arquivos estejam ativos para uso."""
    #     try:
    #         for name in (file.name for file in files if file):
    #             file = genai.get_file(name)
    #             while file.state.name == "PROCESSING":
    #                 time.sleep(10)
    #                 file = genai.get_file(name)
    #             if file.state.name != "ACTIVE":
    #                 st.error(f"Arquivo {file.name} falhou no processamento.")
    #                 return False
    #         return True
    #     except Exception as e:
    #         st.error(f"Erro ao aguardar o processamento do arquivo: {e}")
    #         return False

    # # Inicializa as variáveis de estado para manter o status do upload e dos arquivos
    # if "upload_successful" not in st.session_state:
    #     st.session_state["upload_successful"] = False
    # if "files" not in st.session_state:
    #     st.session_state["files"] = None

    # # Cria a Interface
    # st.subheader("Converse com o Óraculo✨")


    # db_path = "sisreq.db"

    # if os.path.exists(db_path):
    #     df = fetch_data_from_db(db_path)
    #     csv_path = "temp_data.csv"
    #     save_dataframe_to_csv(df, csv_path)

    #     if not st.session_state["upload_successful"]:
    #         placeholder = st.empty()  # Cria um espaço para a mensagem temporária

    #         with placeholder:
    #             st.info("Conectado ao banco de dados. Iniciando upload...")

    #         gemini_file = upload_to_gemini(csv_path, mime_type="text/csv")
            
    #         if gemini_file:
    #             st.session_state["files"] = [gemini_file]
    #             if wait_for_files_active(st.session_state["files"]):
    #                 # Remove a mensagem temporária e exibe a mensagem de sucesso apenas uma vez
    #                 time.sleep(2)
    #                 placeholder.empty()
    #                 st.session_state["upload_successful"] = True
    #                 st.success("Dados processados e prontos para interação!")

    #                 # Inicia a sessão de chat
    #                 chat_session = model.start_chat(history=[{"role": "user", "parts": [st.session_state["files"][0]]}])

    #                 # Loop de interação com o usuário
    #                 user_input = st.text_input("Digite sua pergunta:")
    #                 if user_input:
    #                     response = chat_session.send_message(user_input)
    #                     st.write("Resposta:", response.text)
    #             else:
    #                 st.error("Falha ao processar os dados. Verifique e tente novamente.")
    #         else:
    #             st.error("Falha no upload dos dados para o Gemini.")
    #     elif st.session_state["upload_successful"]:
    #         st.success("Dados processados e prontos para interação!")
    #         # Recupera a sessão de chat caso os dados já tenham sido processados
    #         chat_session = model.start_chat(history=[{"role": "user", "parts": [st.session_state["files"][0]]}])
    #         user_input = st.text_input("Digite sua pergunta:")
    #         if user_input:
    #             response = chat_session.send_message(user_input)
    #             st.write("Resposta:", response.text)

    # else:
    #     st.error("Banco de dados não encontrado. Verifique o caminho do arquivo.")