
import json
from collections import Counter
from pathlib import Path

import pytest

from src.preprocessor import preprocessar


CAMINHO_BASE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "base_conhecimento.json"
)

INTENCOES = {"configuracao", "erros", "senhas"}
CAMPOS = {"id", "intencao", "pergunta", "resposta", "referencia"}


@pytest.fixture(scope="module")
def base():
    with CAMINHO_BASE.open(encoding="utf-8-sig") as arquivo:
        return json.load(arquivo)


def test_base_existe():
    assert CAMINHO_BASE.is_file()


def test_base_possui_registros(base):
    assert isinstance(base, list)
    assert len(base) >= 12


def test_campos_obrigatorios(base):
    for registro in base:
        assert isinstance(registro, dict)
        assert CAMPOS.issubset(registro.keys())


def test_ids_validos_e_unicos(base):
    ids = [registro["id"] for registro in base]

    assert all(type(id_) is int and id_ > 0 for id_ in ids)
    assert len(ids) == len(set(ids))


def test_intencoes_validas(base):
    categorias = {registro["intencao"] for registro in base}

    assert categorias == INTENCOES


def test_todas_intencoes_tem_perguntas(base):
    contagem = Counter(item["intencao"] for item in base)

    for intencao in INTENCOES:
        assert contagem[intencao] >= 1


def test_campos_textuais_preenchidos(base):
    for registro in base:
        for campo in ("pergunta", "resposta", "referencia"):
            valor = registro[campo]

            assert isinstance(valor, str)
            assert valor.strip() != ""


def test_perguntas_nao_duplicadas(base):
    perguntas = [
        preprocessar(registro["pergunta"])
        for registro in base
    ]

    assert all(perguntas)
    assert len(perguntas) == len(set(perguntas))
