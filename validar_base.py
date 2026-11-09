
"""
Leitura e validação da base de conhecimento do A3 Chatbot IT.

Contrato para outras partes do projeto:
    from validar_base import carregar_base
    registros = carregar_base()

Cada registro contém:
    id (int), intencao (str), pergunta (str),
    resposta (str), referencia (str).
"""

import json
import re
import unicodedata
from pathlib import Path


CAMINHO_BASE = (
    Path(__file__).resolve().parent
    / "data"
    / "base_conhecimento.json"
)

INTENCOES_VALIDAS = {
    "configuracao",
    "erros",
    "senhas",
}

CAMPOS_OBRIGATORIOS = {
    "id",
    "intencao",
    "pergunta",
    "resposta",
    "referencia",
}


def normalizar_pergunta(texto):
    """
    Normaliza perguntas para detectar duplicidades,
    ignorando diferenças de acentos, pontuação e espaços.
    """

    texto = unicodedata.normalize("NFKD", texto.casefold())

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    texto = re.sub(r"[^a-z0-9]+", " ", texto)

    return " ".join(texto.split())


def validar_registros(dados):
    """
    Valida os registros da base de conhecimento.

    Retorna uma lista de erros.
    Uma lista vazia significa que a base é válida.
    """

    if not isinstance(dados, list):
        return ["A raiz do JSON deve ser uma lista."]

    if not dados:
        return ["A base de conhecimento está vazia."]

    erros = []
    ids_vistos = set()
    perguntas_vistas = {}

    for posicao, item in enumerate(dados, start=1):
        prefixo = f"Registro {posicao}"

        if not isinstance(item, dict):
            erros.append(
                f"{prefixo}: deve ser um objeto JSON."
            )
            continue

        # Verificar campos obrigatórios
        faltantes = CAMPOS_OBRIGATORIOS - item.keys()

        if faltantes:
            erros.append(
                f"{prefixo}: faltam campos: "
                f"{', '.join(sorted(faltantes))}."
            )

        # Verificar ID
        identificador = item.get("id")

        if (
            isinstance(identificador, bool)
            or not isinstance(identificador, int)
            or identificador <= 0
        ):
            erros.append(
                f"{prefixo}: 'id' deve ser um inteiro positivo."
            )

        elif identificador in ids_vistos:
            erros.append(
                f"{prefixo}: ID duplicado: {identificador}."
            )

        else:
            ids_vistos.add(identificador)

        # Verificar intenção
        intencao = item.get("intencao")

        if (
            not isinstance(intencao, str)
            or intencao not in INTENCOES_VALIDAS
        ):
            erros.append(
                f"{prefixo}: intenção inválida: {intencao!r}."
            )

        # Verificar textos obrigatórios
        for campo in ("pergunta", "resposta", "referencia"):
            valor = item.get(campo)

            if not isinstance(valor, str) or not valor.strip():
                erros.append(
                    f"{prefixo}: '{campo}' deve ser texto não vazio."
                )

        # Detectar perguntas duplicadas
        pergunta = item.get("pergunta")

        if isinstance(pergunta, str) and pergunta.strip():
            normalizada = normalizar_pergunta(pergunta)

            if normalizada in perguntas_vistas:
                anterior = perguntas_vistas[normalizada]

                erros.append(
                    f"{prefixo}: pergunta duplicada "
                    f"do registro {anterior}."
                )
            else:
                perguntas_vistas[normalizada] = posicao

    return erros


def carregar_base(caminho=None):
    """
    Carrega a base de conhecimento e retorna os registros válidos.

    Pode receber um caminho alternativo para facilitar testes.
    Levanta ValueError quando a base contém erros.
    """

    arquivo = Path(caminho) if caminho is not None else CAMINHO_BASE

    try:
        with arquivo.open("r", encoding="utf-8-sig") as origem:
            dados = json.load(origem)

    except (OSError, UnicodeError, json.JSONDecodeError) as erro:
        raise ValueError(
            f"Não foi possível carregar a base de conhecimento: {erro}"
        ) from erro

    erros = validar_registros(dados)

    if erros:
        detalhes = "\n".join(f"- {erro}" for erro in erros)

        raise ValueError(
            f"Base de conhecimento inválida:\n{detalhes}"
        )

    return dados


def validar_base(caminho=None):
    """
    Mantém a função de validação original.

    Imprime o diagnóstico e retorna True ou False.
    """

    try:
        dados = carregar_base(caminho)

    except (OSError, UnicodeError, ValueError) as erro:
        print(f"ERRO: {erro}")
        return False

    print(
        f"Base válida! Total de registros: {len(dados)}"
    )

    for intencao in sorted(INTENCOES_VALIDAS):
        quantidade = sum(
            item["intencao"] == intencao
            for item in dados
        )

        print(
            f"- {intencao}: {quantidade} "
            f"{'registro' if quantidade == 1 else 'registros'}"
        )

    return True


if __name__ == "__main__":
    if not validar_base():
        raise SystemExit(1)
