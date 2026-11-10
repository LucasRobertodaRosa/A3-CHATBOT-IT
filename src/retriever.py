
import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.preprocessor import preprocessar


# Localização da base de conhecimento
CAMINHO_BASE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "base_conhecimento.json"
)


class Retriever:
    """
    Motor de recuperação de respostas usando
    TF-IDF e similaridade de cosseno.
    """

    def __init__(self, caminho_base=CAMINHO_BASE):
        self.caminho_base = Path(caminho_base)
        self.base = self.carregar_base()
        self.vectorizer = TfidfVectorizer()

        # Preparar as perguntas cadastradas
        self.perguntas = [
            preprocessar(item["pergunta"])
            for item in self.base
        ]

        if not any(self.perguntas):
            raise ValueError(
                "A base não possui perguntas válidas."
            )

        # Vetorizar as perguntas
        self.matriz_tfidf = self.vectorizer.fit_transform(
            self.perguntas
        )

    def carregar_base(self):
        """Carrega e valida os registros do JSON."""

        with open(
            self.caminho_base,
            "r",
            encoding="utf-8"
        ) as arquivo:
            dados = json.load(arquivo)

        if not isinstance(dados, list) or not dados:
            raise ValueError(
                "A base deve ser uma lista não vazia."
            )

        for indice, item in enumerate(dados):
            if not isinstance(item, dict):
                raise ValueError(
                    f"Registro {indice} inválido."
                )

            for campo in ("pergunta", "resposta", "intencao"):
                valor = item.get(campo)

                if not isinstance(valor, str) or not valor.strip():
                    raise ValueError(
                        f"Registro {indice}: campo '{campo}' inválido."
                    )

        return dados

    def buscar(self, pergunta):
        """
        Retorna a melhor correspondência da base.

        A decisão de aceitar ou rejeitar a resposta
        pertence ao engine (Pessoa 3).
        """

        pergunta_normalizada = preprocessar(pergunta)

        if not pergunta_normalizada:
            return None

        # Vetorizar a pergunta recebida
        vetor_pergunta = self.vectorizer.transform(
            [pergunta_normalizada]
        )

        # Comparar a pergunta com a base
        similaridades = cosine_similarity(
            vetor_pergunta,
            self.matriz_tfidf
        )[0]

        # Encontrar a maior similaridade
        indice_melhor = int(similaridades.argmax())
        maior_similaridade = float(
            similaridades[indice_melhor]
        )

        registro = self.base[indice_melhor]

        return {
            "id": registro.get("id"),
            "pergunta": registro["pergunta"],
            "resposta": registro["resposta"],
            "intencao": registro["intencao"],
            "similaridade": maior_similaridade
        }


# Interface simples para a Pessoa 3 utilizar
def buscar_resposta(pergunta):
    retriever = Retriever()
    return retriever.buscar(pergunta)
