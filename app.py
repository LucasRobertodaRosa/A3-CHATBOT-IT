"""
Interface Streamlit do Chatbot de Suporte Técnico Hikvision.

Commit 4 - Exibição do fallback e do nível de confiança.
"""

import streamlit as st

from src.engine import processar_pergunta

st.set_page_config(
    page_title="Chatbot Suporte Técnico Hikvision",
    page_icon="🤖",
    layout="centered",
)

THRESHOLD = 0.40  # mesmo valor padrão do engine

MENSAGEM_FALLBACK = (
    "Não encontrei uma resposta com confiança suficiente para a sua pergunta. "
    "Vou encaminhar você para o **suporte técnico humano**, que poderá ajudar melhor."
)


def normalizar_resultado(resultado):
    """
    Converte o retorno do engine em um dict padrão:
    {"resposta": str, "confianca": float | None, "categoria": str | None, "fallback": bool}
    """
    if isinstance(resultado, dict):
        confianca = resultado.get("confianca", resultado.get("similaridade"))
        fallback = resultado.get("fallback")
        if fallback is None:
            fallback = confianca is not None and confianca < THRESHOLD
        return {
            "resposta": resultado.get("resposta", ""),
            "confianca": confianca,
            "categoria": resultado.get("categoria", resultado.get("intencao")),
            "fallback": bool(fallback),
        }
    return {"resposta": str(resultado), "confianca": None, "categoria": None, "fallback": False}


def mostrar_resposta(dados):
    """Mostra a resposta do chatbot, o fallback e a confiança."""
    if dados["fallback"]:
        st.warning(dados["resposta"] or MENSAGEM_FALLBACK)
        st.caption("🔁 Encaminhado para suporte humano")
    else:
        st.markdown(dados["resposta"])
        if dados["categoria"]:
            st.caption(f"Categoria: {dados['categoria']}")

    if dados["confianca"] is not None:
        st.caption(f"Nível de confiança: {dados['confianca']:.0%}")
        st.progress(min(max(float(dados["confianca"]), 0.0), 1.0))


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

if "historico" not in st.session_state:
    st.session_state.historico = []

for mensagem in st.session_state.historico:
    with st.chat_message(mensagem["papel"]):
        if mensagem["papel"] == "assistant":
            mostrar_resposta(mensagem["dados"])
        else:
            st.markdown(mensagem["texto"])

pergunta = st.chat_input("Digite sua pergunta. Ex.: Como redefinir a senha do meu DVR?")

if pergunta is not None:
    if pergunta.strip():
        st.session_state.historico.append({"papel": "user", "texto": pergunta})
        with st.chat_message("user"):
            st.markdown(pergunta)

        dados = normalizar_resultado(processar_pergunta(pergunta))

        st.session_state.historico.append({"papel": "assistant", "dados": dados})
        with st.chat_message("assistant"):
            mostrar_resposta(dados)
    else:
        st.warning("Digite uma pergunta antes de enviar.")
