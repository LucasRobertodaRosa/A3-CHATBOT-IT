
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
    mesmo com diferenças de acentos ou pontuação.
    """

    texto = unicodedata.normalize(
        "NFKD",
        texto.lower().strip()
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    texto = re.sub(
        r"[^a-z0-9]+",
        " ",
        texto
    )

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def validar_base(caminho=CAMINHO_BASE):
    """
    Verifica a integridade da base de conhecimento.

    Valida:
    - Existência do arquivo
    - Formato JSON
    - Estrutura em lista
    - Campos obrigatórios
    - IDs únicos e válidos
    - Intenções permitidas
    - Textos não vazios
    - Perguntas duplicadas

    Retorna True quando válida e False caso contrário.
    """

    caminho = Path(caminho)

    # 1. Verificar existência do arquivo

    if not caminho.is_file():
        print(
            f"ERRO: arquivo não encontrado: {caminho}"
        )
        return False

    # 2. Carregar e validar o formato JSON

    try:
        with caminho.open(
            "r",
            encoding="utf-8"
        ) as arquivo:
            dados = json.load(arquivo)

    except (json.JSONDecodeError, UnicodeDecodeError) as erro:
        print(
            f"ERRO: JSON inválido ou codificação incorreta: {erro}"
        )
        return False

    except OSError as erro:
        print(
            f"ERRO: não foi possível ler a base: {erro}"
        )
        return False

    # 3. Validar a estrutura principal

    if not isinstance(dados, list):
        print(
            "ERRO: a raiz do JSON deve ser uma lista."
        )
        return False

    if not dados:
        print(
            "ERRO: a base de conhecimento está vazia."
        )
        return False

    # 4. Preparar estruturas de validação

    ids_vistos = set()
    perguntas_vistas = {}
    erros = []

    # 5. Percorrer cada registro

    for posicao, item in enumerate(
        dados,
        start=1
    ):

        if not isinstance(item, dict):
            erros.append(
                f"Registro {posicao}: deve ser um objeto JSON."
            )
            continue

        # 6. Verificar campos obrigatórios

        faltantes = CAMPOS_OBRIGATORIOS - item.keys()

        if faltantes:
            erros.append(
                f"Registro {posicao}: faltam os campos "
                f"{', '.join(sorted(faltantes))}."
            )

        # 7. Verificar o ID

        identificador = item.get("id")

        if (
            isinstance(identificador, bool)
            or not isinstance(identificador, int)
        ):
            erros.append(
                f"Registro {posicao}: "
                "'id' deve ser um número inteiro."
            )

        elif identificador <= 0:
            erros.append(
                f"Registro {posicao}: "
                "'id' deve ser maior que zero."
            )

        elif identificador in ids_vistos:
            erros.append(
                f"Registro {posicao}: "
                f"id duplicado {identificador}."
            )

        else:
            ids_vistos.add(identificador)

        # 8. Verificar a intenção

        intencao = item.get("intencao")

        if (
            not isinstance(intencao, str)
            or intencao not in INTENCOES_VALIDAS
        ):
            erros.append(
                f"Registro {posicao}: "
                f"intenção inválida: {intencao!r}."
            )

        # 9. Verificar textos obrigatórios

        for campo in (
            "pergunta",
            "resposta",
            "referencia"
        ):

            valor = item.get(campo)

            if (
                not isinstance(valor, str)
                or not valor.strip()
            ):
                erros.append(
                    f"Registro {posicao}: "
                    f"'{campo}' deve ser texto não vazio."
                )

        # 10. Detectar perguntas duplicadas

        pergunta = item.get("pergunta")

        if (
            isinstance(pergunta, str)
            and pergunta.strip()
        ):

            normalizada = normalizar_pergunta(
                pergunta
            )

            if normalizada in perguntas_vistas:
                anterior = perguntas_vistas[normalizada]

                erros.append(
                    f"Registro {posicao}: "
                    f"pergunta duplicada do registro {anterior}."
                )

            else:
                perguntas_vistas[normalizada] = posicao

    # 11. Exibir erros encontrados

    if erros:
        print("Foram encontrados problemas na base:")

        for erro in erros:
            print(f"- {erro}")

        return False

    # 12. Exibir resultado da validação

    print(
        f"Base válida! Total de registros: {len(dados)}"
    )

    for intencao in sorted(INTENCOES_VALIDAS):

        quantidade = sum(
            item["intencao"] == intencao
            for item in dados
        )

        print(
            f"- {intencao}: {quantidade} registros"
        )

    return True


if __name__ == "__main__":
    raise SystemExit(
        0 if validar_base() else 1
    )
