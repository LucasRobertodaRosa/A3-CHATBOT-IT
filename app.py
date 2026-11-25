"""
Interface Streamlit do Chatbot de Suporte Técnico Hikvision.

Commit 2 - Integração da interface com o engine (processar_pergunta).
"""

import streamlit as st

from src.engine import processar_pergunta

st.set_page_config(
    page_title="Chatbot Suporte Técnico Hikvision",
    page_icon="🤖",
    layout="centered",
)


def extrair_resposta(resultado):
    """Aceita retorno do engine como dict ou como texto simples."""
    if isinstance(resultado, dict):
        return resultado.get("resposta", "")
    return str(resultado)


st.title("🤖 Chatbot de Suporte Técnico Hikvision")

st.markdown(
    """
    Olá! Sou o assistente virtual de suporte técnico para equipamentos **Hikvision**.

    Posso ajudar com dúvidas sobre:
    - **Configuração / Instalação**
    - **Erros / Falhas**
    - **Segurança / Senhas**

    Quando não tiver confiança suficiente na resposta, vou encaminhar você
    para o suporte humano em vez de inventar uma solução.
    """
)

st.divider()

pergunta = st.text_input(
    "Digite sua pergunta:",
    placeholder="Ex.: Como redefinir a senha do meu DVR?",
)

if st.button("Enviar"):
    if pergunta.strip():
        resultado = processar_pergunta(pergunta)
        st.success(extrair_resposta(resultado))
    else:
        st.warning("Digite uma pergunta antes de enviar.")
