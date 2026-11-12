"""Selic mensal para juros de mora (regras.md, item 11). Nunca estima: se faltar mês, para."""
import json
import os
import urllib.request
from decimal import Decimal

_ARQ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados_ref", "selic.json")
_URL = "https://sicalc.receita.fazenda.gov.br/sicalc/api/selic/acumulada/{ini}/{fim}"


class SelicIndisponivel(Exception):
    pass


def carregar():
    with open(_ARQ, encoding="utf-8") as f:
        return {k: Decimal(v) for k, v in json.load(f)["selic_mensal_percentual"].items()}


def _proximo_mes(ano, mes, n=1):
    i = ano * 12 + (mes - 1) + n
    return i // 12, i % 12 + 1


def juros_mora_percentual(vencimento, pagamento, tabela=None):
    """Soma da Selic do mês seguinte ao do vencimento até o mês anterior ao do pagamento,
    mais 1% no mês do pagamento. Pagamento no mês do vencimento (ou antes): sem juros."""
    if (pagamento.year, pagamento.month) <= (vencimento.year, vencimento.month):
        return Decimal(0)
    tabela = tabela if tabela is not None else carregar()
    total = Decimal(1)
    a, m = _proximo_mes(vencimento.year, vencimento.month)
    while (a, m) < (pagamento.year, pagamento.month):
        chave = f"{a:04d}-{m:02d}"
        if chave not in tabela:
            raise SelicIndisponivel(
                f"Falta a Selic de {m:02d}/{a}. Rode: python3 trabalho/darf --atualizar-selic"
            )
        total += tabela[chave]
        a, m = _proximo_mes(a, m)
    return total


def atualizar():
    """Baixa a Selic acumulada do Sicalc (Receita) e regrava dados_ref/selic.json."""
    with open(_ARQ, encoding="utf-8") as f:
        dados = json.load(f)
    ultimo = max(dados["selic_mensal_percentual"])
    a, m = int(ultimo[:4]), int(ultimo[5:])
    ini = f"{a:04d}-{m:02d}-01"
    fa, fm = _proximo_mes(*_hoje_ym(), 1)
    fim = f"{fa:04d}-{fm:02d}-01"
    with urllib.request.urlopen(_URL.format(ini=ini, fim=fim), timeout=60) as r:
        serie = json.load(r)
    acc = {x["data"][:7]: Decimal(x["valor"]) for x in serie}
    meses = sorted(acc)
    novos = 0
    for anterior, mes in zip(meses, meses[1:]):
        if mes == meses[-1]:
            continue  # o último mês só traz o 1% do mês de pagamento
        if mes not in dados["selic_mensal_percentual"]:
            dados["selic_mensal_percentual"][mes] = str(acc[anterior] - acc[mes])
            novos += 1
    import datetime as dt
    dados["consultado"] = dt.date.today().isoformat()
    with open(_ARQ, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=1)
    return novos, max(dados["selic_mensal_percentual"])


def _hoje_ym():
    import datetime as dt
    h = dt.date.today()
    return h.year, h.month
