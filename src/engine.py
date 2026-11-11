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
    motivo    (str)         "ok" | "vazia" | "baixa_confianca" (o motivo
                            de escopo entra em um commit seguinte)

Regra de confiança: a resposta só é aceita quando a similaridade do melhor
resultado é maior ou igual ao limiar. O valor inicial é 0.40, conforme a
especificação, e pode ser trocado por chamada (ex.: pelas métricas).
"""

LIMIAR_CONFIANCA = 0.40


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


def _confianca_suficiente(confianca, limiar):
    """True se a similaridade atinge o limiar (valor igual ao limiar passa)."""
    return confianca >= limiar


def processar_pergunta(pergunta, limiar=LIMIAR_CONFIANCA):
    """Recebe a pergunta do usuário e devolve o resultado padronizado.

    `limiar` é opcional e permite testar outros valores sem alterar o código.
    """
    if not isinstance(pergunta, str) or not pergunta.strip():
        return _resultado(motivo="vazia")

    texto = _preprocessar(pergunta)
    if not texto.strip():
        # Ex.: pergunta composta só por símbolos ou emojis.
        return _resultado(motivo="vazia")

    melhor = _buscar_melhor(texto)
    confianca = float(melhor["similaridade"])

    if not _confianca_suficiente(confianca, limiar):
        # A mensagem de encaminhamento ao suporte humano entra no
        # próximo commit; aqui só registramos a decisão e a confiança.
        return _resultado(
            confianca=confianca,
            fallback=True,
            motivo="baixa_confianca",
        )

    return _resultado(
        resposta=melhor["resposta"],
        intencao=melhor["intencao"],
        confianca=confianca,
    )
