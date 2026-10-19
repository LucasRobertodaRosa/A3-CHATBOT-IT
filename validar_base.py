
import json
from pathlib import Path

CAMINHO_BASE = (
    Path(__file__).parent
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
}


def validar_base():
    if not CAMINHO_BASE.exists():
        print(f"ERRO: arquivo não encontrado: {CAMINHO_BASE}")
        return False

    try:
        with CAMINHO_BASE.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except json.JSONDecodeError as erro:
        print(f"ERRO: JSON inválido: {erro}")
        return False

    if not isinstance(dados, list):
        print("ERRO: a raiz do JSON deve ser uma lista.")
        return False

    if not dados:
        print("ERRO: a base de conhecimento está vazia.")
        return False

    ids = set()
    erros = []

    for posicao, item in enumerate(dados, start=1):
        if not isinstance(item, dict):
            erros.append(f"Registro {posicao}: deve ser um objeto.")
            continue

        faltantes = CAMPOS_OBRIGATORIOS - item.keys()

        if faltantes:
            erros.append(
                f"Registro {posicao}: faltam os campos "
                f"{', '.join(sorted(faltantes))}."
            )
            continue

        if not isinstance(item["id"], int) or isinstance(item["id"], bool):
            erros.append(f"Registro {posicao}: id deve ser inteiro.")
        elif item["id"] in ids:
            erros.append(f"Registro {posicao}: id duplicado {item['id']}.")
        else:
            ids.add(item["id"])

        if item["intencao"] not in INTENCOES_VALIDAS:
            erros.append(
                f"Registro {posicao}: intenção inválida "
                f"'{item['intencao']}'."
            )

        for campo in ("pergunta", "resposta"):
            valor = item[campo]
            if not isinstance(valor, str) or not valor.strip():
                erros.append(
                    f"Registro {posicao}: '{campo}' deve ser texto não vazio."
                )

    if erros:
        print("Foram encontrados problemas:")
        for erro in erros:
            print(f"- {erro}")
        return False

    print(f"Base válida! Total de registros: {len(dados)}")

    for intencao in sorted(INTENCOES_VALIDAS):
        quantidade = sum(
            item["intencao"] == intencao for item in dados
        )
        print(f"- {intencao}: {quantidade} registros")

    return True


if __name__ == "__main__":
    if not validar_base():
        raise SystemExit(1)