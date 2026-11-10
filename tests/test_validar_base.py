
"""Testes unitários exclusivos da base e do validador (Pessoa 1)."""

import json
import io
import tempfile
from contextlib import redirect_stdout
import unittest
from pathlib import Path

from validar_base import carregar_base, validar_base, validar_registros


class TestBaseConhecimento(unittest.TestCase):

    def setUp(self):
        self.registros = [
            {
                "id": 1,
                "intencao": "configuracao",
                "pergunta": "Como configurar a camera?",
                "resposta": "Consulte o manual do modelo.",
                "referencia": "Manual Hikvision"
            },
            {
                "id": 2,
                "intencao": "erros",
                "pergunta": "Por que o NVR nao grava?",
                "resposta": "Verifique o armazenamento e o agendamento.",
                "referencia": "Manual NVR Hikvision"
            },
        ]

    def test_base_original_carrega(self):
        registros = carregar_base()
        self.assertGreaterEqual(len(registros), 12)
        self.assertEqual(validar_registros(registros), [])

    def test_registros_validos(self):
        self.assertEqual(validar_registros(self.registros), [])

    def test_lista_vazia(self):
        self.assertTrue(validar_registros([]))

    def test_raiz_invalida(self):
        self.assertTrue(
            validar_registros({"registros": self.registros})
        )

    def test_campo_ausente(self):
        self.registros[0].pop("resposta")
        self.assertIn(
            "faltam campos",
            str(validar_registros(self.registros))
        )

    def test_id_duplicado(self):
        self.registros[1]["id"] = 1
        self.assertIn(
            "ID duplicado",
            str(validar_registros(self.registros))
        )

    def test_id_booleano_rejeitado(self):
        self.registros[0]["id"] = True
        self.assertIn(
            "inteiro positivo",
            str(validar_registros(self.registros))
        )

    def test_pergunta_repetida_mesmo_com_acentos(self):
        self.registros[1]["pergunta"] = (
            "  COMO   CONFIGURAR A CÂMERA?  "
        )
        self.assertIn(
            "pergunta duplicada",
            str(validar_registros(self.registros))
        )

    def test_intencao_com_tipo_incorreto(self):
        self.registros[0]["intencao"] = ["configuracao"]
        self.assertIn(
            "intenção inválida",
            str(validar_registros(self.registros))
        )

    def test_resposta_vazia(self):
        self.registros[0]["resposta"] = "   "
        self.assertIn(
            "texto não vazio",
            str(validar_registros(self.registros))
        )

    def test_carrega_base_alternativa(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "exemplo.json"

            caminho.write_text(
                json.dumps(self.registros),
                encoding="utf-8"
            )

            self.assertEqual(
                carregar_base(caminho),
                self.registros
            )

            with redirect_stdout(io.StringIO()):
                self.assertTrue(validar_base(caminho))

    def test_json_invalido(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "invalido.json"

            caminho.write_text(
                "{json incompleto",
                encoding="utf-8"
            )

            with self.assertRaises(ValueError):
                carregar_base(caminho)

            with redirect_stdout(io.StringIO()):
                self.assertFalse(validar_base(caminho))

    def test_arquivo_inexistente(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "nao_existe.json"

            # O carregador converte erros de leitura
            # em ValueError, conforme a implementação atual.
            with self.assertRaises(ValueError):
                carregar_base(caminho)

            with redirect_stdout(io.StringIO()):
                self.assertFalse(validar_base(caminho))


if __name__ == "__main__":
    unittest.main()
