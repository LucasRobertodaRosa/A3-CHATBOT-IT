"""Leitura e validação da base de conhecimento do A3 Chatbot IT.

Contrato para outras partes do projeto:
    from validar_base import carregar_base
    registros = carregar_base()

Cada registro contém: id (int), intencao (str), pergunta (str), resposta (str).
"""

import json
import unicodedata
from pathlib import Path

CAMINHO_BASE = Path(__file__).resolve().parent / "data" / "base_conhecimento.json"

INTENCOES_VALIDAS = {"configuracao", "erros", "senhas"}
CAMPOS_OBRIGATORIOS = {"id", "intencao", "pergunta", "resposta"}


def _normalizar_pergunta(pergunta):
    """Normaliza texto para detectar perguntas duplicadas."""
    texto = unicodedata.normalize("NFKD", pergunta.casefold())
    texto = "".join(letra for letra in texto if not unicodedata.combining(letra))
    return " ".join(texto.split())


def validar_registros(dados):
    """Retorna uma lista de erros. Lista vazia significa base válida."""
    if not isinstance(dados, list):
        return ["A raiz do JSON deve ser uma lista."]
    if not dados:
        return ["A base de conhecimento está vazia."]

    erros = []
    ids = set()
    perguntas = set()

    for posicao, item in enumerate(dados, start=1):
        prefixo = f"Registro {posicao}"
        if not isinstance(item, dict):
            erros.append(f"{prefixo}: deve ser um objeto JSON.")
            continue

        faltantes = CAMPOS_OBRIGATORIOS - item.keys()
        if faltantes:
            erros.append(
                f"{prefixo}: faltam campos: {', '.join(sorted(faltantes))}."
            )
            continue

        identificador = item["id"]
        if (not isinstance(identificador, int)
                or isinstance(identificador, bool)
                or identificador <= 0):
            erros.append(f"{prefixo}: 'id' deve ser um inteiro positivo.")
        elif identificador in ids:
            erros.append(f"{prefixo}: ID duplicado: {identificador}.")
        else:
            ids.add(identificador)

        intencao = item["intencao"]
        if not isinstance(intencao, str) or intencao not in INTENCOES_VALIDAS:
            erros.append(f"{prefixo}: intenção inválida: {intencao!r}.")

        for campo in ("pergunta", "resposta"):
            valor = item[campo]
            if not isinstance(valor, str) or not valor.strip():
                erros.append(f"{prefixo}: '{campo}' deve ser texto não vazio.")

        pergunta = item["pergunta"]
        if isinstance(pergunta, str) and pergunta.strip():
            pergunta_normalizada = _normalizar_pergunta(pergunta)
            if pergunta_normalizada in perguntas:
                erros.append(f"{prefixo}: pergunta duplicada: {pergunta!r}.")
            else:
                perguntas.add(pergunta_normalizada)

    return erros


def carregar_base(caminho=None):
    """Lê JSON e retorna registros válidos; lança erro se houver problema.

    `caminho` é opcional para facilitar testes e cargas alternativas.
    """
    arquivo = Path(caminho) if caminho is not None else CAMINHO_BASE
    with arquivo.open("r", encoding="utf-8-sig") as origem:
        dados = json.load(origem)

    erros = validar_registros(dados)
    if erros:
        detalhes = "\n".join(f"- {erro}" for erro in erros)
        raise ValueError(f"Base de conhecimento inválida:\n{detalhes}")
    return dados


def validar_base(caminho=None):
    """Mantém a função original: imprime diagnóstico e retorna True/False."""
    try:
        dados = carregar_base(caminho)
    except (OSError, UnicodeError, ValueError) as erro:
        print(f"ERRO: {erro}")
        return False

    print(f"Base válida! Total de registros: {len(dados)}")
    for intencao in sorted(INTENCOES_VALIDAS):
        quantidade = sum(item["intencao"] == intencao for item in dados)
        print(f"- {intencao}: {quantidade} {'registro' if quantidade == 1 else 'registros'}")
    return True


if __name__ == "__main__":
    if not validar_base():
        raise SystemExit(1)
