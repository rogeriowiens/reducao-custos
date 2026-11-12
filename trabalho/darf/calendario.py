"""Dias úteis e vencimento do DARF (fonte: trabalho/regras.md, itens 9 e 10)."""
import calendar
import datetime as dt
import json
import os

_ARQ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados_ref", "feriados.json")
_cache = {}


class ErroCalendario(Exception):
    pass


def _feriados():
    if "f" not in _cache:
        with open(_ARQ, encoding="utf-8") as f:
            dados = json.load(f)["feriados"]
        _cache["f"] = {dt.date.fromisoformat(k) for k in dados}
        _cache["max"] = max(_cache["f"]).year
    return _cache["f"]


def eh_util(d):
    feriados = _feriados()
    if d.year > _cache["max"]:
        raise ErroCalendario(f"Sem tabela de feriados para {d.year}.")
    return d.weekday() < 5 and d not in feriados


def proximo_dia_util(d):
    """Primeiro dia útil depois de d."""
    d += dt.timedelta(days=1)
    while not eh_util(d):
        d += dt.timedelta(days=1)
    return d


def ultimo_dia_util(ano, mes):
    """Último dia útil do mês. Em dezembro, o último dia útil do ano não tem
    atendimento bancário ao público e vale o dia útil anterior (nota 3 da Anbima)."""
    d = dt.date(ano, mes, calendar.monthrange(ano, mes)[1])
    while not eh_util(d):
        d -= dt.timedelta(days=1)
    if mes == 12:
        d -= dt.timedelta(days=1)
        while not eh_util(d):
            d -= dt.timedelta(days=1)
    return d


def vencimento_darf(ano, mes):
    """Ganho apurado em (ano, mes) vence no último dia útil do mês seguinte."""
    if mes == 12:
        return ultimo_dia_util(ano + 1, 1)
    return ultimo_dia_util(ano, mes + 1)
