"""
Interface Streamlit do Chatbot de Suporte Técnico Hikvision.

Commit 1 - Interface inicial: título, apresentação e campo de pergunta.
A integração com o engine (processar_pergunta) entra no próximo commit.
"""

import streamlit as st

st.set_page_config(
    page_title="Chatbot Suporte Técnico Hikvision",
    page_icon="🤖",
    layout="centered",
)

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
        st.info(f"Pergunta recebida: {pergunta}")
    else:
        st.warning("Digite uma pergunta antes de enviar.")
