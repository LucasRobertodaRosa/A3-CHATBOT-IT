
import csv
from pathlib import Path

from src.engine import processar_pergunta


CAMINHO_TESTES = Path(__file__).resolve().parent.parent / "data" / "test_cases.csv"


def avaliar_resposta(esperada, resultado):
    """
    Verifica se o chatbot apresentou o comportamento esperado.
    """
    if esperada.startswith("fallback:"):
        motivo_esperado = esperada.split(":", 1)[1]

        return (
            resultado["fallback"] is True
            and resultado["motivo"] == motivo_esperado
        )

    return (
        resultado["fallback"] is False
        and resultado["intencao"] == esperada
    )


def executar_testes():
    """
    Executa os casos de teste e calcula as métricas.
    """
    total = 0
    acertos = 0
    falsos_positivos = 0
    falsos_negativos = 0
    abstencoes = 0

    resultados = []

    with open(CAMINHO_TESTES, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)

        for caso in leitor:
            total += 1

            resultado = processar_pergunta(caso["pergunta"])
            esperada = caso["resposta_esperada"].strip()
            acertou = avaliar_resposta(esperada, resultado)

            if acertou:
                acertos += 1

            fallback_esperado = esperada.startswith("fallback:")
            fallback_obtido = resultado["fallback"]

            if fallback_obtido:
                abstencoes += 1

            # Respondeu quando deveria ter utilizado fallback.
            if fallback_esperado and not fallback_obtido:
                falsos_positivos += 1

            # Utilizou fallback quando deveria ter respondido.
            if not fallback_esperado and fallback_obtido:
                falsos_negativos += 1

            resultados.append({
                "id": caso["id"],
                "pergunta": caso["pergunta"],
                "esperado": esperada,
                "obtido": (
                    f"fallback:{resultado['motivo']}"
                    if fallback_obtido
                    else resultado["intencao"]
                ),
                "confianca": resultado["confianca"],
                "acertou": acertou,
            })

    erros = total - acertos
    acuracia = (acertos / total * 100) if total else 0
    taxa_abstencao = (abstencoes / total * 100) if total else 0

    print("\n===== RELATORIO DE METRICAS =====")
    print(f"Total de testes: {total}")
    print(f"Acertos: {acertos}")
    print(f"Erros: {erros}")
    print(f"Acuracia: {acuracia:.2f}%")
    print(f"Falsos positivos: {falsos_positivos}")
    print(f"Falsos negativos: {falsos_negativos}")
    print(f"Abstencoes: {abstencoes}")
    print(f"Taxa de abstencao: {taxa_abstencao:.2f}%")

    print("\n===== RESULTADOS INDIVIDUAIS =====")

    for item in resultados:
        status = "ACERTO" if item["acertou"] else "ERRO"

        print(
            f"Teste {item['id']}: {status} | "
            f"Esperado: {item['esperado']} | "
            f"Obtido: {item['obtido']} | "
            f"Confianca: {item['confianca']:.2f}"
        )

    return {
        "total": total,
        "acertos": acertos,
        "erros": erros,
        "acuracia": acuracia,
        "falsos_positivos": falsos_positivos,
        "falsos_negativos": falsos_negativos,
        "abstencoes": abstencoes,
        "resultados": resultados,
    }


if __name__ == "__main__":
    executar_testes()
