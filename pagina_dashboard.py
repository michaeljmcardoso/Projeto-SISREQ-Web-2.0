import streamlit as st
from dashboard import processos_por_fase, processos_por_municipio, grafico_processos_por_fase

def dashboard(fase):
    st.markdown('<h2 style="color: #1f77b4;">Dashboard SISREQ</h2>', unsafe_allow_html=True)
    processos_por_municipio()
    processos_por_fase()
    grafico_processos_por_fase()
