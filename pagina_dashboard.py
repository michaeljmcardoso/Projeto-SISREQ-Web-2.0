import streamlit as st
import proc_por_fase
from graficos import exibir_grafico_fases_processo
from proc_por_municipio import exibir_processos_por_municipio

def dashboard(fase):
    st.title("Dashboard SISREQ")
    exibir_processos_por_municipio()
    proc_por_fase.processso_por_fase()
    exibir_grafico_fases_processo()
