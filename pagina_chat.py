import os
import time
import sqlite3
import pandas as pd
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

def rate_limited_request(func, *args, **kwargs):
    """Implementa rate limiting para evitar erro 429"""
    if "last_request_time" not in st.session_state:
        st.session_state.last_request_time = 0
    
    current_time = time.time()
    time_since_last_request = current_time - st.session_state.last_request_time
    
    # Espera pelo menos 3 segundos entre requisições (20 req/min)
    min_interval = 3.0
    if time_since_last_request < min_interval:
        sleep_time = min_interval - time_since_last_request
        time.sleep(sleep_time)
    
    st.session_state.last_request_time = time.time()
    return func(*args, **kwargs)

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
        st.session_state.chat_initialized = False
    if "data_context" not in st.session_state:
        st.session_state.data_context = ""
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = None
    if "df" not in st.session_state:
        st.session_state.df = None

    # Cria a Interface
    st.subheader("Converse com o Óraculo✨")

    db_path = "sisreq.db"

    if os.path.exists(db_path):
        # Busca dados do banco apenas uma vez
        if st.session_state.df is None:
            with st.spinner("Carregando dados do banco..."):
                st.session_state.df = fetch_data_from_db(db_path)
                
                # Cria um resumo dos dados para incluir no contexto
                data_summary = f"""
                Dados dos processos de regularização fundiária quilombola:
                - Total de processos: {len(st.session_state.df)}
                - Colunas disponíveis: {', '.join(st.session_state.df.columns)}
                - Amostra dos dados (primeiras 3 linhas):
                {st.session_state.df.head(3).to_string()}
                """
                st.session_state.data_context = data_summary
                
                # Inicializa a sessão de chat
                try:
                    st.session_state.chat_session = model.start_chat(history=[])
                    st.session_state.chat_initialized = True
                    st.success("✅ Dados carregados e prontos para interação!")
                except Exception as e:
                    st.error(f"Erro ao inicializar chat: {e}")
                    return

        # Se o chat foi inicializado com sucesso, mostra o input
        if st.session_state.chat_initialized and st.session_state.chat_session is not None:
            user_input = st.text_input("Digite sua pergunta sobre os processos quilombolas:")
            
            if user_input and user_input.strip():
                with st.spinner("🔍 Consultando o Oráculo..."):
                    try:
                        # Combina o contexto dos dados com a pergunta do usuário
                        full_prompt = f"""
                        CONTEXTO DOS DADOS DISPONÍVEIS:
                        {st.session_state.data_context}

                        PERGUNTA DO USUÁRIO: {user_input}

                        INSTRUÇÕES:
                        - Responda com base nos dados fornecidos sobre processos de regularização fundiária quilombola
                        - Seja amigável e use emojis quando apropriado
                        - Se a informação não estiver nos dados, informe que não possui essa informação específica
                        - Mantenha o foco no contexto de regularização quilombola
                        """
                        
                        # Usa rate limiting para evitar erro 429
                        response = rate_limited_request(
                            st.session_state.chat_session.send_message,
                            full_prompt
                        )
                        
                        st.markdown("### 💬 Resposta:")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg:
                            st.error("""
                            ⚠️ **Limite de requisições atingido!**
                            
                            Aguarde 20-30 segundos antes de fazer outra pergunta.
                            Isso é um limite temporário da API do Google.
                            """)
                            st.info("💡 **Dica:** Espere um pouco e tente novamente.")
                        elif "'NoneType' object has no attribute 'send_message'" in error_msg:
                            st.error("""
                            🔄 **Sessão reinicializada!**
                            
                            Recarregando a conversa...
                            """)
                            # Tenta reinicializar a sessão
                            try:
                                st.session_state.chat_session = model.start_chat(history=[])
                                st.rerun()
                            except:
                                st.error("Erro ao reinicializar. Recarregue a página.")
                        else:
                            st.error(f"Erro na consulta: {error_msg}")

        else:
            st.warning("⏳ Inicializando o chat...")

    else:
        st.error("❌ Banco de dados não encontrado. Verifique se o arquivo 'sisreq.db' está no diretório correto.")

# Botão para resetar a conversa
if st.button("🔄 Reiniciar Conversa"):
    for key in list(st.session_state.keys()):
        if key != "df":  # Mantém os dados carregados
            del st.session_state[key]
    st.rerun()