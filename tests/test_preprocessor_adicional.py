
from src.preprocessor import preprocessar


def test_preprocessamento_repetido():
    texto = "CONFIGURAÇÃO DE CÂMERA!!!"

    primeira = preprocessar(texto)
    segunda = preprocessar(primeira)

    assert primeira == segunda


def test_variacoes_da_mesma_pergunta():
    perguntas = [
        "Como configurar uma câmera?",
        "COMO CONFIGURAR UMA CAMERA!!!",
        "  Como configurar uma câmera?  ",
    ]

    resultados = [preprocessar(p) for p in perguntas]

    assert len(set(resultados)) == 1


def test_texto_normalizado():
    entrada = "camera hikvision offline"

    assert preprocessar(entrada) == entrada
