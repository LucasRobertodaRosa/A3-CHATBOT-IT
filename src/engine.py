"""Engine do chatbot de suporte técnico Hikvision (A3 Chatbot IT).

Fluxo: pergunta -> pré-processamento -> retriever -> resultado padronizado.

Contrato para a interface (app.py) e para as métricas (src/metrics.py):
    from src.engine import processar_pergunta
    resultado = processar_pergunta("Minha câmera está offline")

O resultado é sempre um dicionário com as chaves:
    resposta  (str)         texto a ser exibido ao usuário
    intencao  (str | None)  "configuracao" | "erros" | "senhas" | None
    confianca (float)       similaridade do melhor resultado (0.0 a 1.0)
    fallback  (bool)        True quando a pergunta deve ir para um humano
    motivo    (str)         "ok" | "vazia" (outros motivos entram nos
                            commits de limiar, fallback e escopo)
"""


def _preprocessar(texto):
    """Chama o pré-processador da Pessoa 1 (src/preprocessor.py)."""
    from src.preprocessor import preprocessar

    return preprocessar(texto)


def _buscar_melhor(texto):
    """Chama o retriever da Pessoa 2 (src/retriever.py).

    Espera um dicionário com as chaves: id, intencao, resposta, similaridade.
    Se o nome da função ou o formato de retorno mudar, só este ponto
    precisa ser ajustado.
    """
    from src.retriever import melhor_resposta

    return melhor_resposta(texto)


def _resultado(resposta="", intencao=None, confianca=0.0,
               fallback=False, motivo="ok"):
    """Monta o dicionário de retorno sempre com as mesmas chaves."""
    return {
        "resposta": resposta,
        "intencao": intencao,
        "confianca": confianca,
        "fallback": fallback,
        "motivo": motivo,
    }


def processar_pergunta(pergunta):
    """Recebe a pergunta do usuário e devolve o resultado padronizado."""
    if not isinstance(pergunta, str) or not pergunta.strip():
        return _resultado(motivo="vazia")

    texto = _preprocessar(pergunta)
    if not texto.strip():
        # Ex.: pergunta composta só por símbolos ou emojis.
        return _resultado(motivo="vazia")

    melhor = _buscar_melhor(texto)
    return _resultado(
        resposta=melhor["resposta"],
        intencao=melhor["intencao"],
        confianca=float(melhor["similaridade"]),
    )
