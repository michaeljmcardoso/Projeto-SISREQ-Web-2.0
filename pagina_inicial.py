import streamlit as st
from obter_todos_registros import obter_todos_os_registros
from pagina_pesquisa import pesquisar_comunidade

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