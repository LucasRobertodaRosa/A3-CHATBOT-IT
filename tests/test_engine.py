"""Testes do engine: limiar de confiança, fallback, escopo e entrada vazia.

O preprocessador (Pessoa 1) e o retriever (Pessoa 2) são simulados, então
estes testes rodam sem depender das outras branches e validam apenas a lógica
de decisão do engine. A única exceção é TestBaseReal, que usa os módulos
reais e é ignorado enquanto eles não estiverem na main.

Execução, a partir da raiz do projeto:
    python -m unittest discover -s tests -v
ou, se o pytest estiver instalado:
    python -m pytest tests/test_engine.py -v
"""

import re
import sys
import unicodedata
import unittest
from pathlib import Path
from unittest import mock

# Garante que a raiz do projeto esteja no caminho de importação, mesmo
# quando os testes são executados de dentro da pasta tests/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import engine  # noqa: E402

RESPOSTA_DA_BASE = "Verifique a alimentação elétrica e os cabos de rede."


def _preprocessar_falso(texto):
    """Imita o preprocessar() previsto: minúsculas, sem acento e sem símbolos."""
    texto = unicodedata.normalize("NFKD", texto.casefold())
    texto = "".join(letra for letra in texto if not unicodedata.combining(letra))
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", texto).split())


class EngineTestCase(unittest.TestCase):
    """Base: simula preprocessador e retriever e registra as chamadas."""

    def setUp(self):
        self.chamadas_retriever = []
        self.similaridade = 0.0
        for alvo, substituto in (
            ("_preprocessar", _preprocessar_falso),
            ("_buscar_melhor", self._retriever_falso),
        ):
            patcher = mock.patch.object(engine, alvo, substituto)
            patcher.start()
            self.addCleanup(patcher.stop)

    def _retriever_falso(self, texto):
        self.chamadas_retriever.append(texto)
        return {
            "id": 5,
            "intencao": "erros",
            "resposta": RESPOSTA_DA_BASE,
            "similaridade": self.similaridade,
        }

    def perguntar(self, pergunta, similaridade=0.9, **kwargs):
        """Chama o engine com o retriever devolvendo a similaridade dada."""
        self.similaridade = similaridade
        return engine.processar_pergunta(pergunta, **kwargs)

    def assertFallback(self, resultado, motivo):
        self.assertTrue(resultado["fallback"])
        self.assertEqual(resultado["motivo"], motivo)
        self.assertEqual(resultado["resposta"], engine.MENSAGEM_FALLBACK)
        self.assertNotIn(RESPOSTA_DA_BASE, resultado["resposta"])
        self.assertIsNone(resultado["intencao"])


class TestContrato(EngineTestCase):
    def test_resultado_sempre_tem_as_mesmas_chaves(self):
        esperadas = {"resposta", "intencao", "confianca", "fallback", "motivo"}
        casos = [
            ("Minha câmera está offline", 0.9),  # resposta
            ("Minha câmera está offline", 0.1),  # baixa confiança
            ("Qual a capital da França?", 0.9),  # fora do escopo
            ("", 0.9),                           # vazia
        ]
        for pergunta, similaridade in casos:
            with self.subTest(pergunta=pergunta, similaridade=similaridade):
                resultado = self.perguntar(pergunta, similaridade)
                self.assertEqual(set(resultado), esperadas)


class TestConfiancaAlta(EngineTestCase):
    def test_devolve_resposta_e_intencao_da_base(self):
        resultado = self.perguntar("Minha câmera Hikvision está offline", 0.85)
        self.assertFalse(resultado["fallback"])
        self.assertEqual(resultado["motivo"], "ok")
        self.assertEqual(resultado["resposta"], RESPOSTA_DA_BASE)
        self.assertEqual(resultado["intencao"], "erros")
        self.assertEqual(resultado["confianca"], 0.85)

    def test_retriever_recebe_o_texto_ja_preprocessado(self):
        self.perguntar("Minha CÂMERA Hikvision está OFFLINE!!!", 0.85)
        self.assertEqual(
            self.chamadas_retriever, ["minha camera hikvision esta offline"]
        )


class TestLimiar(EngineTestCase):
    def test_limiar_padrao_e_040(self):
        self.assertEqual(engine.LIMIAR_CONFIANCA, 0.40)

    def test_exatamente_no_limiar_ainda_responde(self):
        resultado = self.perguntar("Minha câmera está offline", 0.40)
        self.assertFalse(resultado["fallback"])
        self.assertEqual(resultado["motivo"], "ok")

    def test_logo_abaixo_do_limiar_cai_em_fallback(self):
        resultado = self.perguntar("Minha câmera está offline", 0.39)
        self.assertFallback(resultado, "baixa_confianca")

    def test_limiar_personalizado_muda_a_decisao(self):
        casos = [
            (0.50, 0.60, True),   # acima do padrão, abaixo do limiar novo
            (0.50, 0.30, False),  # acima do limiar novo
            (0.35, 0.30, False),  # abaixo do padrão, mas passa no novo
        ]
        for similaridade, limiar, deve_cair in casos:
            with self.subTest(similaridade=similaridade, limiar=limiar):
                resultado = self.perguntar(
                    "Minha câmera está offline", similaridade, limiar=limiar
                )
                self.assertEqual(resultado["fallback"], deve_cair)


class TestFallback(EngineTestCase):
    def test_baixa_confianca_usa_so_a_mensagem_padrao(self):
        resultado = self.perguntar("Minha câmera está offline", 0.10)
        self.assertFallback(resultado, "baixa_confianca")

    def test_fallback_preserva_a_confianca_real(self):
        resultado = self.perguntar("Minha câmera está offline", 0.25)
        self.assertEqual(resultado["confianca"], 0.25)

    def test_confianca_zero_tambem_e_fallback(self):
        resultado = self.perguntar("Minha câmera está offline", 0.0)
        self.assertFallback(resultado, "baixa_confianca")

    def test_mensagem_padrao_encaminha_ao_suporte_humano(self):
        self.assertIn("suporte técnico humano", engine.MENSAGEM_FALLBACK)


class TestEscopo(EngineTestCase):
    def test_fora_do_escopo_cai_em_fallback_sem_consultar_a_base(self):
        perguntas = [
            "Qual a capital da França?",
            "Como configurar o email no celular?",
            "Como recuperar a senha do Instagram?",
            "Qual o tipo de arquivo do vídeo do YouTube?",
        ]
        for pergunta in perguntas:
            with self.subTest(pergunta=pergunta):
                # Similaridade alta de propósito: o escopo deve vetar mesmo assim.
                resultado = self.perguntar(pergunta, 0.95)
                self.assertFallback(resultado, "fora_escopo")
                self.assertEqual(resultado["confianca"], 0.0)
        self.assertEqual(self.chamadas_retriever, [])

    def test_perguntas_do_dominio_seguem_para_o_retriever(self):
        perguntas = [
            "Como configurar o endereço IP de uma câmera Hikvision?",
            "O NVR não está gravando. Como resolver?",
            "Gravador DVR não grava",
            "Hik-Connect não abre",
            "Como instalar o iVMS-4200?",
            "O equipamento fica congelando",
            "Minhas câmeras ficaram offline",
        ]
        for pergunta in perguntas:
            with self.subTest(pergunta=pergunta):
                resultado = self.perguntar(pergunta, 0.9)
                self.assertFalse(resultado["fallback"])
                self.assertEqual(resultado["motivo"], "ok")

    def test_sigla_ip_exige_palavra_inteira(self):
        self.assertTrue(engine._dentro_do_escopo("qual o ip padrao"))
        self.assertFalse(engine._dentro_do_escopo("qual o tipo de arquivo"))


class TestPerguntasAmbiguas(EngineTestCase):
    def test_vaga_sem_termo_do_dominio_vira_fora_de_escopo(self):
        for pergunta in ("Não funciona", "Como faço isso?", "Preciso de ajuda"):
            with self.subTest(pergunta=pergunta):
                resultado = self.perguntar(pergunta, 0.9)
                self.assertFallback(resultado, "fora_escopo")

    def test_vaga_com_termo_do_dominio_e_baixa_similaridade_vira_fallback(self):
        for pergunta in ("Minha câmera", "Problema no NVR"):
            with self.subTest(pergunta=pergunta):
                resultado = self.perguntar(pergunta, 0.20)
                self.assertFallback(resultado, "baixa_confianca")


class TestEntradaVazia(EngineTestCase):
    def test_entradas_sem_conteudo_pedem_pergunta_sem_acionar_fallback(self):
        for entrada in ("", "   ", "\n\t", "???", "!!! ...", None, 123):
            with self.subTest(entrada=entrada):
                resultado = self.perguntar(entrada, 0.9)
                self.assertEqual(resultado["motivo"], "vazia")
                self.assertFalse(resultado["fallback"])
                self.assertEqual(
                    resultado["resposta"], engine.MENSAGEM_PERGUNTA_VAZIA
                )
        self.assertEqual(self.chamadas_retriever, [])


class TestBaseReal(unittest.TestCase):
    """Usa o preprocessador e a base reais. Ignorado até a integração."""

    def test_todas_as_perguntas_da_base_estao_no_escopo(self):
        try:
            from src.preprocessor import preprocessar
            from validar_base import carregar_base
        except ImportError:
            self.skipTest("preprocessor/validar_base ainda não estão na main")

        for registro in carregar_base():
            with self.subTest(id=registro["id"]):
                texto = preprocessar(registro["pergunta"])
                self.assertTrue(
                    engine._dentro_do_escopo(texto),
                    f"Pergunta da base fora do escopo: {registro['pergunta']!r}. "
                    "Inclua um termo do domínio em TERMOS_EXATOS ou RADICAIS.",
                )


if __name__ == "__main__":
    unittest.main()
