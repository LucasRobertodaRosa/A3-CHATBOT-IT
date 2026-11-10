
from src.retriever import Retriever


def test_carregamento_base():
    retriever = Retriever()
    assert len(retriever.base) == 12


def test_vetorizacao_tfidf():
    retriever = Retriever()

    assert retriever.matriz_tfidf.shape[0] == len(
        retriever.base
    )


def test_pergunta_identica():
    retriever = Retriever()

    pergunta = retriever.base[0]["pergunta"]
    resultado = retriever.buscar(pergunta)

    assert resultado is not None
    assert resultado["similaridade"] > 0.99


def test_pergunta_vazia():
    retriever = Retriever()

    assert retriever.buscar("") is None
    assert retriever.buscar(None) is None


def test_sem_correspondencia():
    retriever = Retriever()

    resultado = retriever.buscar(
        "banana abacaxi melancia"
    )

    assert resultado is not None
    assert resultado["similaridade"] == 0.0

def test_pergunta_reformulada():
    retriever = Retriever()

    pergunta_original = retriever.base[0]["pergunta"]

    pergunta_reformulada = pergunta_original.upper()

    resultado = retriever.buscar(pergunta_reformulada)

    assert resultado is not None
    assert resultado["similaridade"] > 0.99