import streamlit as st


# Função para Página Sobre
def pagina_about():
    st.subheader("Sobre o Projeto")
    st.write("""
        Sistema de registro de processos de regularização quilombola.
        Projeto experimental. Focado em otimizar o registro, 
        visualização e consulta dos processos cadastrados. Inclui o Assistente Virtual, Oráculo. 
        Para atualizar a página aperte "R".
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
            © 2025 Desenvolvido por Michael J M Cardoso, Antropólogo e Programador. Todos os direitos reservados.
        </div>
        """,
        unsafe_allow_html=True
    )