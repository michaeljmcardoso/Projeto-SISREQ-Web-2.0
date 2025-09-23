import streamlit as st
import sqlite3
import pandas as pd

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