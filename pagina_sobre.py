import streamlit as st


# Função para Página Sobre
def pagina_about():
    st.subheader("Sobre o Projeto")
    st.write("""
        O SISREQ é um sistema de gerenciamento de registros para a regularização quilombola, 
        desenvolvido para facilitar o controle, acompanhamento e análise de processos. 
        Ele utiliza tecnologias modernas para oferecer uma experiência intuitiva e eficiente,
        tanto em ambientes desktop quanto mobile. O sistema conta com um assistente virtual chamado Oráculo, 
        que utiliza a API `google.generativeai` para fornecer suporte e informações em tempo real. 
        Além disso, o projeto possui controle de acesso de usuários, garantindo segurança e privacidade dos dados.
        Projeto experimental. Focado em otimizar o registro, visualização e consulta dos processos cadastrados. 
        Inclui o Assistente Virtual, Oráculo.
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
            © 2026 Desenvolvido por Michael J M Cardoso, Antropólogo e Programador. Todos os direitos reservados.
        </div>
        """,
        unsafe_allow_html=True
    )