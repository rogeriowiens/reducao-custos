"""Testes do /darf. Rode: python3 -m unittest discover -s trabalho/darf -v

Os números esperados dos casos 1 a 3 foram calculados à mão em casos-de-teste.md
antes de existir código; os demais vêm da tabela "Casos que entram na suíte".
"""
import datetime as dt
import os
import sys
import unittest
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import calculadora as calc  # noqa: E402
import calendario  # noqa: E402
import selic  # noqa: E402
import texto  # noqa: E402

D = Decimal
HOJE = dt.date(2026, 11, 12)


def op(data, tipo, ativo, classe, qtd, preco, custos="0", irrf="0", corretora=""):
    return {"data": data, "tipo": tipo, "ativo": ativo, "classe": classe, "quantidade": qtd,
            "preco": preco, "custos": custos, "irrf": irrf, "corretora": corretora}


def mes(res, ano, m):
    for r in res["meses"]:
        if (r["ano"], r["mes"]) == (ano, m):
            return r
    raise AssertionError(f"mês {m}/{ano} não está no resultado")


class Caso1ExemploOficialReceita(unittest.TestCase):
    def setUp(self):
        self.res = calc.apurar({"operacoes": [
            op("2024-01-10", "compra", "WXYZ3", "acao", 1000, "50", "15"),
            op("2024-02-26", "venda", "WXYZ3", "acao", 1000, "60", "18", "3"),
        ]}, HOJE)
        self.r = mes(self.res, 2024, 2)

    def test_numeros(self):
        self.assertEqual(calc.cent(self.r["vendas"][0]["resultado"]), D("9967.00"))
        self.assertFalse(self.r["isento"])
        self.assertEqual(calc.cent(self.r["imposto_bruto"]["geral"]), D("1495.05"))
        self.assertEqual(calc.cent(self.r["darf"]), D("1492.05"))
        self.assertEqual(self.r["codigo"], "6015")
        self.assertEqual(self.r["vencimento"], dt.date(2024, 3, 28))

    def test_whatsapp(self):
        t = texto.whatsapp_mes(self.r)
        self.assertIn("[nome]", t)
        self.assertIn("R$ 1.492,05", t)
        self.assertIn("28/03/2024", t)
        self.assertIn("R$ 9.967,00", t)


class Caso2CincoTiposNoMesmoMes(unittest.TestCase):
    def setUp(self):
        ops = [
            op("2025-02-10", "compra", "ACAO3", "acao", 500, "30"),
            op("2025-02-12", "compra", "BDRX34", "bdr", 200, "50"),
            op("2025-02-14", "compra", "FIIX11", "fii", 100, "160"),
            op("2025-02-17", "compra", "FAGR11", "fiagro", 1000, "9"),
            op("2025-02-19", "compra", "INFR11", "fiinfra", 100, "100"),
            op("2026-03-05", "venda", "ACAO3", "acao", 500, "36"),
            op("2026-03-10", "venda", "BDRX34", "bdr", 200, "57.5"),
            op("2026-03-12", "venda", "FIIX11", "fii", 100, "152"),
            op("2026-03-16", "venda", "FAGR11", "fiagro", 1000, "10.2"),
            op("2026-03-18", "venda", "INFR11", "fiinfra", 100, "95"),
        ]
        self.res = calc.apurar({"saldos_iniciais": {"prejuizo_geral_comum": "1000"}, "operacoes": ops}, HOJE)
        self.r = mes(self.res, 2026, 3)

    def test_numeros(self):
        r = self.r
        self.assertTrue(r["isento"])
        self.assertEqual(calc.cent(r["vendas_acoes"]), D("18000.00"))
        self.assertEqual(calc.cent(r["base"]["geral"]), D("500.00"))
        self.assertEqual(calc.cent(r["imposto_bruto"]["geral"]), D("75.00"))
        self.assertEqual(calc.cent(r["base"]["fii"]), D("400.00"))
        self.assertEqual(calc.cent(r["imposto_bruto"]["fii"]), D("80.00"))
        self.assertEqual(calc.cent(r["res_infra"]), D("-500.00"))
        self.assertEqual(calc.cent(r["darf"]), D("155.00"))
        self.assertEqual(r["vencimento"], dt.date(2026, 4, 30))
        self.assertEqual(r["carry_fim"]["geral_comum"], 0)
        self.assertEqual(r["carry_fim"]["fii"], 0)

    def test_nao_compensa_e_texto(self):
        tipos = [k for k, _ in self.r["nao_compensa"]]
        self.assertIn("fiinfra", tipos)
        self.assertIn("fii_contra_geral", tipos)
        t = texto.whatsapp_mes(self.r)
        self.assertIn("R$ 155,00", t)
        self.assertIn("30/04/2026", t)
        self.assertIn("[nome]", t)


class Caso3HerancaEAtraso(unittest.TestCase):
    def setUp(self):
        ops = [
            op("2024-02-05", "compra", "ACAO3", "acao", 100, "31"),
            op("2025-06-16", "heranca", "ACAO3", "acao", 300, "25"),
            op("2025-10-20", "compra", "ACAO3", "acao", 100, "29"),
            op("2026-01-15", "venda", "ACAO3", "acao", 500, "43"),
        ]
        self.res = calc.apurar({"operacoes": ops, "pagamentos": {"2026-01": "2026-04-10"}}, HOJE)
        self.r = mes(self.res, 2026, 1)

    def test_numeros(self):
        r = self.r
        self.assertEqual(calc.cent(r["vendas"][0]["resultado"]), D("8000.00"))
        self.assertFalse(r["isento"])
        self.assertEqual(calc.cent(r["darf"]), D("1200.00"))
        self.assertEqual(r["vencimento"], dt.date(2026, 2, 27))
        at = r["atraso"]
        self.assertEqual(at["dias"], 40)
        self.assertEqual(calc.cent(at["pct_multa"]), D("13.20"))
        self.assertEqual(calc.cent(at["multa"]), D("158.40"))
        self.assertEqual(calc.cent(at["pct_juros"]), D("2.21"))
        self.assertEqual(calc.cent(at["juros"]), D("26.52"))
        self.assertEqual(calc.cent(at["total"]), D("1384.92"))

    def test_prejuizo_do_falecido_nao_passa(self):
        self.assertIn("heranca_prejuizo_falecido", [k for k, _ in self.r["nao_compensa"]])
        t = texto.whatsapp_mes(self.r)
        self.assertIn("R$ 1.384,92", t)
        self.assertIn("falecido", t)


class OutrosCasosDaSuite(unittest.TestCase):
    def test_04_imposto_abaixo_de_10_acumula(self):
        ops = [op("2026-01-05", "compra", "BDRX34", "bdr", 100, "10"),
               op("2026-02-10", "venda", "BDRX34", "bdr", 50, "11"),    # ganho 50 -> 7,50
               op("2026-03-10", "venda", "BDRX34", "bdr", 50, "10.4")]  # ganho 20 -> 3,00
        res = calc.apurar({"operacoes": ops}, HOJE)
        fev = mes(res, 2026, 2)
        self.assertEqual(fev["darf"], 0)
        self.assertEqual(calc.cent(fev["abaixo_de_10_acumulado"]), D("7.50"))
        mar = mes(res, 2026, 3)
        self.assertEqual(calc.cent(mar["darf"]), D("10.50"))
        self.assertEqual(mar["vencimento"], dt.date(2026, 4, 30))

    def test_05_prejuizo_em_mes_de_acoes_ate_20_mil_fica_guardado(self):
        ops = [op("2026-01-05", "compra", "ACAO3", "acao", 1000, "20"),
               op("2026-01-06", "compra", "BDRX34", "bdr", 100, "10"),
               op("2026-02-10", "venda", "ACAO3", "acao", 500, "19"),    # prejuízo 500, vendas 9.500
               op("2026-03-10", "venda", "BDRX34", "bdr", 100, "20")]    # ganho 1.000
        res = calc.apurar({"operacoes": ops}, HOJE)
        fev = mes(res, 2026, 2)
        self.assertEqual(fev["darf"], 0)
        self.assertEqual(calc.cent(fev["carry_fim"]["geral_comum"]), D("500.00"))
        mar = mes(res, 2026, 3)
        self.assertEqual(calc.cent(mar["usado"]["geral"]), D("500.00"))
        self.assertEqual(calc.cent(mar["darf"]), D("75.00"))

    def test_06_preco_medio_nao_muda_com_venda(self):
        ops = [op("2026-01-05", "compra", "BDRX34", "bdr", 100, "10"),
               op("2026-01-06", "compra", "BDRX34", "bdr", 100, "20"),   # PM 15
               op("2026-02-10", "venda", "BDRX34", "bdr", 50, "18"),     # ganho 150
               op("2026-03-10", "venda", "BDRX34", "bdr", 50, "18")]     # ganho 150
        res = calc.apurar({"operacoes": ops}, HOJE)
        for m in (2, 3):
            r = mes(res, 2026, m)
            self.assertEqual(calc.cent(r["vendas"][0]["resultado"]), D("150.00"))
            self.assertEqual(calc.cent(r["darf"]), D("22.50"))

    def test_07_prejuizo_de_fii_segue_para_fiagro_e_proximos_meses(self):
        ops = [op("2026-01-05", "compra", "FIIX11", "fii", 100, "100"),
               op("2026-01-06", "compra", "FAGR11", "fiagro", 100, "10"),
               op("2026-02-10", "venda", "FIIX11", "fii", 100, "90"),      # -1.000
               op("2026-03-10", "venda", "FAGR11", "fiagro", 100, "14"),   # +400
               op("2026-01-07", "compra", "FIIY11", "fii", 100, "100"),
               op("2026-04-10", "venda", "FIIY11", "fii", 100, "110")]     # +1.000
        res = calc.apurar({"operacoes": ops}, HOJE)
        fev = mes(res, 2026, 2)
        self.assertEqual(calc.cent(fev["carry_fim"]["fii"]), D("1000.00"))
        mar = mes(res, 2026, 3)
        self.assertEqual(mar["darf"], 0)
        self.assertEqual(calc.cent(mar["carry_fim"]["fii"]), D("600.00"))
        abr = mes(res, 2026, 4)
        self.assertEqual(calc.cent(abr["base"]["fii"]), D("400.00"))
        self.assertEqual(calc.cent(abr["darf"]), D("80.00"))

    def test_08_day_trade_20_por_cento_sem_isencao(self):
        ops = [op("2026-03-10", "compra", "ACAO3", "acao", 100, "10", irrf="0"),
               op("2026-03-10", "venda", "ACAO3", "acao", 100, "11", irrf="1", corretora="")]
        res = calc.apurar({"operacoes": ops}, HOJE)
        r = mes(res, 2026, 3)
        self.assertEqual(calc.cent(r["res_dt"]), D("100.00"))
        self.assertEqual(calc.cent(r["imposto_bruto"]["dt"]), D("20.00"))
        self.assertEqual(calc.cent(r["irrf_deduzido"]), D("1.00"))
        self.assertEqual(calc.cent(r["darf"]), D("19.00"))
        self.assertEqual(r["vendas_acoes"], 0)  # day trade não entrou nos R$ 20 mil

    def test_08b_prejuizo_day_trade_nao_abate_comum(self):
        ops = [op("2026-03-02", "compra", "BDRX34", "bdr", 100, "10"),
               op("2026-03-10", "compra", "ACAO3", "acao", 100, "10"),
               op("2026-03-10", "venda", "ACAO3", "acao", 100, "9"),       # day trade -100
               op("2026-03-20", "venda", "BDRX34", "bdr", 100, "20")]      # comum +1.000
        r = mes(calc.apurar({"operacoes": ops}, HOJE), 2026, 3)
        self.assertEqual(calc.cent(r["darf"]), D("150.00"))
        self.assertEqual(calc.cent(r["carry_fim"]["geral_dt"]), D("100.00"))
        self.assertIn("dt_contra_comum", [k for k, _ in r["nao_compensa"]])

    def test_09_ganho_de_novembro_vence_em_30_12(self):
        self.assertEqual(calendario.vencimento_darf(2026, 11), dt.date(2026, 12, 30))
        self.assertEqual(calendario.vencimento_darf(2025, 11), dt.date(2025, 12, 30))

    def test_10_atraso_longo_trava_multa_em_20(self):
        ops = [op("2026-01-05", "compra", "BDRX34", "bdr", 100, "10"),
               op("2026-01-20", "venda", "BDRX34", "bdr", 100, "30")]      # ganho 2.000 -> 300
        res = calc.apurar({"operacoes": ops, "pagamentos": {"2026-01": "2026-06-30"}}, HOJE)
        at = mes(res, 2026, 1)["atraso"]
        self.assertEqual(calc.cent(at["pct_multa"]), D("20.00"))
        self.assertEqual(calc.cent(at["multa"]), D("60.00"))

    def test_11_selic_de_dois_meses_igual_ao_sicalc(self):
        pct = selic.juros_mora_percentual(dt.date(2026, 2, 27), dt.date(2026, 5, 4))
        self.assertEqual(pct, D("3.30"))
        self.assertEqual(selic.juros_mora_percentual(dt.date(2026, 2, 27), dt.date(2026, 4, 10)), D("2.21"))
        self.assertEqual(selic.juros_mora_percentual(dt.date(2026, 2, 27), dt.date(2026, 3, 9)), D("1"))
        self.assertEqual(selic.juros_mora_percentual(dt.date(2026, 2, 27), dt.date(2026, 2, 27)), D("0"))

    def test_11b_selic_ausente_para_com_erro_em_vez_de_estimar(self):
        with self.assertRaises(selic.SelicIndisponivel):
            selic.juros_mora_percentual(dt.date(2026, 10, 30), dt.date(2027, 3, 1))

    def test_12_venda_maior_que_estoque_para(self):
        ops = [op("2026-01-05", "compra", "ACAO3", "acao", 100, "10"),
               op("2026-02-10", "venda", "ACAO3", "acao", 200, "12")]
        with self.assertRaises(calc.ErroCalculo) as e:
            calc.apurar({"operacoes": ops}, HOJE)
        self.assertIn("estoque", str(e.exception))

    def test_unit_nao_tem_isenção(self):
        ops = [op("2026-01-05", "compra", "UNTX11", "unit", 100, "10"),
               op("2026-02-10", "venda", "UNTX11", "unit", 100, "12")]     # ganho 200, vendas 1.200
        r = mes(calc.apurar({"operacoes": ops}, HOJE), 2026, 2)
        self.assertEqual(calc.cent(r["imposto_bruto"]["geral"]), D("30.00"))
        self.assertTrue(any("Unit" in a for a in r["avisos"]))

    def test_irrf_sobrando_passa_para_o_proximo_mes(self):
        ops = [op("2026-01-05", "compra", "ACAO3", "acao", 1000, "10"),
               op("2026-02-10", "venda", "ACAO3", "acao", 500, "10", irrf="2"),   # empate: sem imposto
               op("2026-03-10", "compra", "BDRX34", "bdr", 100, "10"),
               op("2026-04-10", "venda", "BDRX34", "bdr", 100, "30", irrf="1")]   # ganho 2.000 -> 300
        r = mes(calc.apurar({"operacoes": ops}, HOJE), 2026, 4)
        self.assertEqual(calc.cent(r["irrf_deduzido"]), D("3.00"))
        self.assertEqual(calc.cent(r["darf"]), D("297.00"))

    def test_fiinfra_nao_gera_imposto_nem_compensa(self):
        ops = [op("2026-01-05", "compra", "INFR11", "fiinfra", 100, "100"),
               op("2026-02-10", "venda", "INFR11", "fiinfra", 100, "150")]
        r = mes(calc.apurar({"operacoes": ops}, HOJE), 2026, 2)
        self.assertEqual(r["darf"], 0)
        self.assertEqual(r["imposto"], 0)


class CalendarioContraAgendaDaReceita(unittest.TestCase):
    """Datas em que a Agenda Tributária da Receita lista o código 6015 (conferidas em 12/11/2026)."""

    def test_vencimentos(self):
        esperado = {
            (2024, 2): dt.date(2024, 3, 28), (2024, 4): dt.date(2024, 5, 31), (2024, 11): dt.date(2024, 12, 30),
            (2024, 12): dt.date(2025, 1, 31), (2025, 1): dt.date(2025, 2, 28), (2025, 2): dt.date(2025, 3, 31),
            (2025, 3): dt.date(2025, 4, 30), (2025, 4): dt.date(2025, 5, 30), (2025, 5): dt.date(2025, 6, 30),
            (2025, 6): dt.date(2025, 7, 31), (2025, 7): dt.date(2025, 8, 29), (2025, 8): dt.date(2025, 9, 30),
            (2025, 9): dt.date(2025, 10, 31), (2025, 11): dt.date(2025, 12, 30), (2025, 12): dt.date(2026, 1, 30),
            (2026, 1): dt.date(2026, 2, 27), (2026, 2): dt.date(2026, 3, 31), (2026, 3): dt.date(2026, 4, 30),
            (2026, 4): dt.date(2026, 5, 29), (2026, 5): dt.date(2026, 6, 30), (2026, 6): dt.date(2026, 7, 31),
        }
        for (a, m), d in esperado.items():
            self.assertEqual(calendario.vencimento_darf(a, m), d, f"{m:02d}/{a}")


if __name__ == "__main__":
    unittest.main()
