"""Leitura comum de configurações locais e Streamlit Cloud Secrets."""
import os

from dotenv import load_dotenv

load_dotenv()


def get_config(nome: str, padrao: str = '', section: str = None) -> str:
    """Retorna uma configuração do ambiente, secrets raiz ou seção indicada."""
    valor = os.getenv(nome)
    if valor is not None:
        return valor

    try:
        import streamlit as st
    except ImportError:
        return padrao

    try:
        if section:
            configuracoes = st.secrets.get(section, {})
            valor = configuracoes.get(nome)
        else:
            valor = st.secrets.get(nome)
    except (FileNotFoundError, KeyError):
        return padrao

    return str(valor) if valor is not None else padrao
