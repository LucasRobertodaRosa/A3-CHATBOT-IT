
import csv
from pathlib import Path

from src.engine import processar_pergunta


BASE = Path(__file__).resolve().parent

ENTRADA = BASE / "data" / "test_cases.csv"

SAIDA = (
    BASE / "docs" / "evidencias"
    / "resultados_20_testes.csv"
)

ROTULOS = {
    "configuracao",
    "erros",
    "senhas",
    "fallback:baixa_confianca",
    "fallback:fora_escopo",
}

SAIDA.parent.mkdir(parents=True, exist_ok=True)

with ENTRADA.open(
    "r", encoding="utf-8-sig", newline=""
) as arquivo:
    linhas = (linha for linha in arquivo if linha.strip())
    leitor = csv.DictReader(linhas)
    casos = list(leitor)
    colunas_originais = list(leitor.fieldnames or [])

colunas_novas = [
    "categoria_obtida",
    "confianca",
    "motivo",
    "resultado_automatico",
]

resultados = []

for caso in casos:
    resultado = processar_pergunta(caso["pergunta"])

    if resultado.get("fallback"):
        categoria_obtida = (
            "fallback:"
            + str(resultado.get("motivo", ""))
        )
    else:
        categoria_obtida = str(
            resultado.get("intencao") or ""
        )

    esperado = str(
        caso.get("resposta_esperada") or ""
    ).strip()

    if esperado not in ROTULOS:
        esperado = str(
            caso.get("categoria") or ""
        ).strip()

    if esperado in ROTULOS:
        avaliacao = (
            "ACERTO"
            if esperado == categoria_obtida
            else "ERRO"
        )
    else:
        avaliacao = "REVISAR"

    registro = dict(caso)

    registro.update({
        "resposta_obtida": resultado.get(
            "resposta", ""
        ),
        "categoria_obtida": categoria_obtida,
        "confianca": resultado.get(
            "confianca", 0
        ),
        "motivo": resultado.get(
            "motivo", ""
        ),
        "resultado_automatico": avaliacao,
    })

    resultados.append(registro)

colunas = list(dict.fromkeys(
    colunas_originais + colunas_novas
))

with SAIDA.open(
    "w", encoding="utf-8-sig", newline=""
) as arquivo:
    escritor = csv.DictWriter(
        arquivo, fieldnames=colunas
    )
    escritor.writeheader()
    escritor.writerows(resultados)

print(f"Total de casos: {len(resultados)}")
print(f"Resultados salvos em: {SAIDA}")
print("Revise os resultados e compare com metrics.py.")
