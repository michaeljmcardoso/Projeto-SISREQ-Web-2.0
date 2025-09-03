import streamlit as st
from dashboard import processos_por_fase, processos_por_municipio, grafico_processos_por_fase, plotar_mapa_interativo, data_abertura, exibir_status_pnra, territorios_identificados

def dashboard(fase):
    st.markdown('<h2 style="color: #1f77b4;">Dashboard</h2>', unsafe_allow_html=True)
    st.markdown(
                    f"<p style='color: #FFFFFF; background-color: #1f77b4; padding: 1px; border-radius: 1px;'>",
                    unsafe_allow_html=True
                )
    
    processos_por_municipio()
    plotar_mapa_interativo()
    processos_por_fase()
    grafico_processos_por_fase()
    territorios_identificados()
    exibir_status_pnra()
    data_abertura()