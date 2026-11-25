"""
Interface Streamlit do Chatbot de Suporte Técnico Hikvision.

Commit 3 - Histórico de conversa durante a sessão.
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

if st.sidebar.button("Limpar conversa"):
    st.session_state.historico = []

st.divider()

# Histórico guardado na sessão do Streamlit
if "historico" not in st.session_state:
    st.session_state.historico = []

for mensagem in st.session_state.historico:
    with st.chat_message(mensagem["papel"]):
        st.markdown(mensagem["texto"])

pergunta = st.chat_input("Digite sua pergunta. Ex.: Como redefinir a senha do meu DVR?")

if pergunta is not None:
    if pergunta.strip():
        st.session_state.historico.append({"papel": "user", "texto": pergunta})
        with st.chat_message("user"):
            st.markdown(pergunta)

        resposta = extrair_resposta(processar_pergunta(pergunta))

        st.session_state.historico.append({"papel": "assistant", "texto": resposta})
        with st.chat_message("assistant"):
            st.markdown(resposta)
    else:
        st.warning("Digite uma pergunta antes de enviar.")
