"""
Interface Streamlit do Chatbot de Suporte Técnico Hikvision.

Commit 5 - Tratamento de erros da interface:
pergunta vazia, base ausente, JSON inválido e erro ao carregar os módulos.
"""

import json
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Chatbot Duvidas Técnicas gerais para equipamentos Hikvision",
    page_icon="🤖",
    layout="centered",
)

CAMINHO_BASE = Path(__file__).parent / "data" / "base_conhecimento.json"
THRESHOLD = 0.40  # mesmo valor padrão do engine

MENSAGEM_FALLBACK = (
    "Não encontrei uma resposta com confiança suficiente para a sua pergunta. "
    "Vou encaminhar você para o **suporte técnico humano**, que poderá ajudar melhor."
)


# ---------------------------------------------------------------------------
# Verificações de ambiente
# ---------------------------------------------------------------------------
def verificar_base():
    """Retorna None se a base estiver ok, ou uma mensagem de erro."""
    if not CAMINHO_BASE.exists():
        return f"Base de conhecimento não encontrada em `{CAMINHO_BASE.relative_to(Path(__file__).parent)}`."
    try:
        with open(CAMINHO_BASE, encoding="utf-8") as arquivo:
            json.load(arquivo)
    except json.JSONDecodeError as erro:
        return f"A base de conhecimento possui JSON inválido (linha {erro.lineno}, coluna {erro.colno})."
    except OSError as erro:
        return f"Não foi possível ler a base de conhecimento: {erro}"
    return None


@st.cache_resource
def carregar_engine():
    """Importa o engine uma vez só. Retorna (função, erro)."""
    try:
        from src.engine import processar_pergunta
        return processar_pergunta, None
    except Exception as erro:  # ImportError, erro ao montar o TF-IDF etc.
        return None, f"Erro ao carregar os módulos do chatbot: {erro}"


# ---------------------------------------------------------------------------
# Resposta do engine
# ---------------------------------------------------------------------------
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


def responder(processar_pergunta, pergunta):
    """Chama o engine sem deixar a interface quebrar."""
    try:
        return normalizar_resultado(processar_pergunta(pergunta))
    except Exception as erro:
        return {
            "resposta": f"Ocorreu um erro ao processar sua pergunta ({erro}). {MENSAGEM_FALLBACK}",
            "confianca": None,
            "categoria": None,
            "fallback": True,
        }


def mostrar_resposta(dados):
    """Mostra a resposta do chatbot, o fallback e a confiança."""
    if dados["fallback"]:
        st.warning(dados["resposta"] or MENSAGEM_FALLBACK)
        st.caption(
    "⚠️ Resposta não identificada. "
    "Consulte a documentação oficial ou um profissional qualificado."
)
    else:
        st.markdown(dados["resposta"] or MENSAGEM_FALLBACK)
        if dados["categoria"]:
            st.caption(f"Categoria: {dados['categoria']}")

    if dados["confianca"] is not None:
        try:
            confianca = min(max(float(dados["confianca"]), 0.0), 1.0)
            st.caption(f"Nível de confiança: {confianca:.0%}"
                           "Dica: descreva o equipamento e o problema em cada "
    "pergunta. O chatbot ainda não interpreta o contexto "
    "de mensagens anteriores.")
            st.progress(confianca)
        except (TypeError, ValueError):
            pass


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------
st.title("🤖 Chatbot de Dúvidas Técnicas Hikvision")

st.markdown(
       """
    Olá! Sou um assistente virtual desenvolvido para fins
    acadêmicos, destinado a esclarecer dúvidas técnicas sobre
    equipamentos de segurança eletrônica.

    Posso auxiliar com dúvidas sobre:

    - **Configuração e instalação**
    - **Identificação de erros e falhas**
    - **Segurança, senhas e acesso**

    As respostas são obtidas de uma base de conhecimento
    limitada e podem não contemplar todos os equipamentos
    ou situações.
    """
)

st.caption(
    "⚠️ Protótipo acadêmico independente, não oficial "
    "e não homologado por fabricantes."
)

if st.sidebar.button("Limpar conversa"):
    st.session_state.historico = []

st.divider()

erro_base = verificar_base()
if erro_base:
    st.error(f"⚠️ {erro_base}")
    st.stop()

processar_pergunta, erro_engine = carregar_engine()
if erro_engine:
    st.error(f"⚠️ {erro_engine}")
    st.stop()

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

        dados = responder(processar_pergunta, pergunta)

        st.session_state.historico.append({"papel": "assistant", "dados": dados})
        with st.chat_message("assistant"):
            mostrar_resposta(dados)
    else:
        st.warning("Digite uma pergunta antes de enviar.")
