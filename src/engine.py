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

Abstenção: abaixo do limiar o engine não inventa resposta. Devolve a
mensagem padrão de encaminhamento ao suporte humano, com fallback=True.
"""

LIMIAR_CONFIANCA = 0.40

MENSAGEM_FALLBACK = (
    "Não encontrei uma resposta confiável para essa pergunta na base de "
    "conhecimento. Para evitar uma orientação incorreta, recomendo "
    "encaminhar sua dúvida ao suporte técnico humano."
)

MENSAGEM_PERGUNTA_VAZIA = (
    "Digite sua pergunta sobre equipamentos Hikvision "
    "(configuração, erros ou senhas)."
)


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


def _fallback(confianca, motivo):
    """Abstenção: não inventa resposta e encaminha ao suporte humano."""
    return _resultado(
        resposta=MENSAGEM_FALLBACK,
        confianca=confianca,
        fallback=True,
        motivo=motivo,
    )


def _pergunta_vazia():
    """Pergunta sem conteúdo: pede ao usuário que digite, sem acionar fallback."""
    return _resultado(resposta=MENSAGEM_PERGUNTA_VAZIA, motivo="vazia")


def processar_pergunta(pergunta, limiar=LIMIAR_CONFIANCA):
    """Recebe a pergunta do usuário e devolve o resultado padronizado.

    `limiar` é opcional e permite testar outros valores sem alterar o código.
    """
    if not isinstance(pergunta, str) or not pergunta.strip():
        return _pergunta_vazia()

    texto = _preprocessar(pergunta)
    if not texto.strip():
        # Ex.: pergunta composta só por símbolos ou emojis.
        return _pergunta_vazia()

    melhor = _buscar_melhor(texto)
    confianca = float(melhor["similaridade"])

    if not _confianca_suficiente(confianca, limiar):
        return _fallback(confianca, "baixa_confianca")

    return _resultado(
        resposta=melhor["resposta"],
        intencao=melhor["intencao"],
        confianca=confianca,
    )
