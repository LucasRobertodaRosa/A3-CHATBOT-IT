
import re
import unicodedata


def remover_acentos(texto):
    """
    Remove os acentos do texto.

    Exemplo:
    configuração -> configuracao
    câmera -> camera
    """

    texto_normalizado = unicodedata.normalize(
        "NFD",
        texto
    )

    return "".join(
        caractere
        for caractere in texto_normalizado
        if unicodedata.category(caractere) != "Mn"
    )


def preprocessar(texto):
    """
    Prepara uma pergunta para o mecanismo
    de busca do chatbot Hikvision.

    Etapas:
    1. Trata entradas vazias.
    2. Converte letras para minúsculas.
    3. Remove acentos.
    4. Remove pontuação e caracteres especiais.
    5. Remove espaços excedentes.

    Retorna uma string normalizada.
    """

    # Verificar entrada nula
    if texto is None:
        return ""

    # Converter entrada para texto
    texto = str(texto)

    # Remover espaços nas extremidades
    texto = texto.strip()

    # Verificar entrada vazia
    if not texto:
        return ""

    # Converter para letras minúsculas
    texto = texto.lower()

    # Remover acentuação
    texto = remover_acentos(texto)

    # Remover caracteres especiais
    # Preservar letras, números e espaços
    texto = re.sub(
        r"[^a-z0-9\s]",
        " ",
        texto
    )

    # Substituir espaços repetidos por um único
    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    # Retornar texto final
    return texto.strip()
