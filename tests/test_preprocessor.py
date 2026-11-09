
from src.preprocessor import (
    preprocessar,
    remover_acentos
)


def test_conversao_minusculas():
    """
    Verifica conversão para letras minúsculas.
    """

    entrada = "CAMERA HIKVISION"

    resultado = preprocessar(entrada)

    assert resultado == "camera hikvision"


def test_remocao_acentos():
    """
    Verifica remoção de acentuação.
    """

    entrada = "Configuração de Câmera"

    resultado = preprocessar(entrada)

    assert resultado == "configuracao de camera"


def test_remover_acentos_diretamente():
    """
    Testa a função auxiliar remover_acentos.
    """

    resultado = remover_acentos(
        "Segurança e instalação"
    )

    assert resultado == "Seguranca e instalacao"


def test_remocao_pontuacao():
    """
    Verifica remoção de pontuação.
    """

    entrada = "Minha câmera está offline!!!"

    resultado = preprocessar(entrada)

    assert resultado == "minha camera esta offline"


def test_caracteres_especiais():
    """
    Verifica remoção de caracteres especiais.
    """

    entrada = "Senha@123 #Hikvision"

    resultado = preprocessar(entrada)

    assert resultado == "senha 123 hikvision"


def test_espacos_excedentes():
    """
    Verifica normalização dos espaços.
    """

    entrada = "  camera    sem    imagem  "

    resultado = preprocessar(entrada)

    assert resultado == "camera sem imagem"


def test_entrada_vazia():
    """
    Verifica tratamento de string vazia.
    """

    resultado = preprocessar("")

    assert resultado == ""


def test_apenas_espacos():
    """
    Verifica entrada somente com espaços.
    """

    resultado = preprocessar("     ")

    assert resultado == ""


def test_entrada_none():
    """
    Verifica tratamento de valor nulo.
    """

    resultado = preprocessar(None)

    assert resultado == ""


def test_preservacao_numeros():
    """
    Verifica preservação de números de modelos.
    """

    entrada = "DS-2CD 1234"

    resultado = preprocessar(entrada)

    assert resultado == "ds 2cd 1234"


def test_normalizacao_completa():
    """
    Testa todas as normalizações juntas.
    """

    entrada = "  CONFIGURAÇÃO!!! CÂMERA #01  "

    resultado = preprocessar(entrada)

    assert resultado == "configuracao camera 01"


def test_resultado_consistente():
    """
    Perguntas com diferenças de caixa,
    acentuação e pontuação devem produzir
    o mesmo texto normalizado.
    """

    pergunta1 = "Como configurar uma câmera?"

    pergunta2 = "COMO CONFIGURAR UMA CAMERA!!!"

    resultado1 = preprocessar(pergunta1)
    resultado2 = preprocessar(pergunta2)

    assert resultado1 == resultado2
