import unittest

from analisador import analisar_linhas, interpretar_linha


class TestAnalisador(unittest.TestCase):
    def test_interpreta_linha_valida(self):
        registro = interpretar_linha(
            "2026-08-13 08:10:15 | 192.168.1.10 | LOGIN_SUCESSO | nicolas"
        )

        self.assertEqual(registro["endereco_ip"], "192.168.1.10")
        self.assertEqual(registro["evento"], "LOGIN_SUCESSO")
        self.assertEqual(registro["usuario"], "nicolas")

    def test_ignora_linha_incompleta_com_aviso(self):
        resultado = analisar_linhas(["linha sem separadores"])

        self.assertEqual(len(resultado["avisos"]), 1)
        self.assertEqual(resultado["total_sucessos"], 0)
        self.assertEqual(resultado["total_falhas"], 0)

    def test_ignora_data_invalida_com_aviso(self):
        resultado = analisar_linhas(
            ["DATA_ERRADA | 192.168.1.10 | LOGIN_FALHA | admin"]
        )

        self.assertEqual(len(resultado["avisos"]), 1)
        self.assertIn("data inválida", resultado["avisos"][0])

    def test_conta_sucessos_falhas_e_ips(self):
        linhas = [
            "2026-08-13 08:10:00 | 192.168.1.10 | LOGIN_SUCESSO | nicolas",
            "2026-08-13 08:11:00 | 192.168.1.25 | LOGIN_FALHA | admin",
            "2026-08-13 08:12:00 | 192.168.1.25 | LOGIN_FALHA | admin",
        ]

        resultado = analisar_linhas(linhas)

        self.assertEqual(resultado["total_sucessos"], 1)
        self.assertEqual(resultado["total_falhas"], 2)
        self.assertEqual(resultado["falhas_por_ip"], {"192.168.1.25": 2})

    def test_detecta_tres_falhas_dentro_da_janela(self):
        linhas = [
            "2026-08-13 08:12:03 | 192.168.1.25 | LOGIN_FALHA | admin",
            "2026-08-13 08:12:10 | 192.168.1.25 | LOGIN_FALHA | admin",
            "2026-08-13 08:12:18 | 192.168.1.25 | LOGIN_FALHA | admin",
        ]

        resultado = analisar_linhas(linhas)

        self.assertEqual(len(resultado["alertas"]), 1)
        self.assertEqual(resultado["alertas"][0]["ip"], "192.168.1.25")
        self.assertEqual(resultado["alertas"][0]["intervalo_segundos"], 15.0)

    def test_nao_alerta_falhas_fora_da_janela(self):
        linhas = [
            "2026-08-13 08:10:00 | 192.168.1.25 | LOGIN_FALHA | admin",
            "2026-08-13 08:12:00 | 192.168.1.25 | LOGIN_FALHA | admin",
            "2026-08-13 08:14:00 | 192.168.1.25 | LOGIN_FALHA | admin",
        ]

        resultado = analisar_linhas(linhas)

        self.assertEqual(resultado["alertas"], [])


if __name__ == "__main__":
    unittest.main()

