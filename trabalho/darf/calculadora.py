"""Calculadora de DARF de renda variável (código 6015).

Regras: trabalho/regras.md (decisões D1 a D7 aprovadas como propostas).
Tudo em Fraction (exato); arredonda ao centavo (meia para cima) só no imposto,
na multa e nos juros (D5).
"""
import datetime as dt
from decimal import Decimal, ROUND_HALF_UP, getcontext
from fractions import Fraction

import calendario
import selic as mod_selic

getcontext().prec = 60

CLASSES = {
    "acao": ("Geral", "ação"),
    "unit": ("Geral", "unit"),
    "bdr": ("Geral", "BDR"),
    "fii": ("FII/Fiagro", "FII"),
    "fiagro": ("FII/Fiagro", "Fiagro"),
    "fiinfra": ("Infra", "FI-Infra"),
}
LIMITE_ISENCAO = Fraction(20000)
ALIQ = {"geral_comum": Fraction(15, 100), "geral_dt": Fraction(20, 100), "fii": Fraction(20, 100)}
MINIMO_DARF = Fraction(10)
CODIGO = "6015"


class ErroCalculo(Exception):
    pass


# ---------------------------------------------------------------- números
def frac(v):
    if isinstance(v, Fraction):
        return v
    if v is None or v == "":
        return Fraction(0)
    try:
        return Fraction(str(v).replace(",", "."))
    except (ValueError, ZeroDivisionError):
        raise ErroCalculo(f"Número inválido: {v!r}")


def cent(x):
    """Fraction -> Decimal com 2 casas, meia para cima."""
    x = Fraction(x)
    return (Decimal(x.numerator) / Decimal(x.denominator)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def cent_f(x):
    return Fraction(cent(x))


def data(v):
    if isinstance(v, dt.date):
        return v
    try:
        return dt.date.fromisoformat(v)
    except (TypeError, ValueError):
        raise ErroCalculo(f"Data inválida: {v!r} (use AAAA-MM-DD)")


def ym(d):
    return (d.year, d.month)


def chave(a, m):
    return f"{a:04d}-{m:02d}"


# ---------------------------------------------------------------- operações
def _normalizar(entrada):
    ops = []
    for i, o in enumerate(entrada.get("operacoes", [])):
        tipo = o.get("tipo")
        classe = o.get("classe")
        if tipo not in ("compra", "venda", "heranca"):
            raise ErroCalculo(f"Operação {i + 1}: tipo deve ser compra, venda ou heranca.")
        if classe not in CLASSES:
            raise ErroCalculo(f"Operação {i + 1}: classe deve ser uma de {', '.join(CLASSES)}.")
        qtd = frac(o.get("quantidade"))
        if qtd <= 0:
            raise ErroCalculo(f"Operação {i + 1}: quantidade deve ser positiva.")
        ops.append({
            "idx": i, "data": data(o.get("data")), "tipo": tipo, "ativo": str(o.get("ativo", "")).upper(),
            "classe": classe, "qtd": qtd, "preco": frac(o.get("preco")),
            "custos": Fraction(0) if tipo == "heranca" else frac(o.get("custos")),
            "irrf": frac(o.get("irrf")), "corretora": o.get("corretora") or "",
        })
    ops.sort(key=lambda o: (o["data"], o["idx"]))
    return ops


def _separar_daytrade(ops_dia, avisos):
    """Day trade: mesmo dia, mesmo ativo, mesma corretora; 1ª compra com 1ª venda (IN 1.585, art. 65, §3º).
    Devolve (partes_normais, resultados_daytrade)."""
    grupos = {}
    for o in ops_dia:
        if o["tipo"] in ("compra", "venda"):
            grupos.setdefault((o["ativo"], o["corretora"]), []).append(o)
    dt_res = []
    consumo = {}  # idx -> quantidade que virou day trade
    for (ativo, corretora), lst in grupos.items():
        compras = [o for o in lst if o["tipo"] == "compra"]
        vendas = [o for o in lst if o["tipo"] == "venda"]
        q = min(sum(o["qtd"] for o in compras), sum(o["qtd"] for o in vendas))
        if q == 0:
            continue
        if not corretora:
            avisos.append(f"{ativo}: comprou e vendeu no mesmo dia ({lst[0]['data']:%d/%m/%Y}). "
                          "Tratei como day trade supondo a mesma corretora; se foram corretoras diferentes, "
                          "informe o campo 'corretora' nas operações.")
        pend_c, pend_v = q, q
        custo = Fraction(0)
        receita = Fraction(0)
        irrf = Fraction(0)
        for o in compras:
            if pend_c == 0:
                break
            u = min(o["qtd"], pend_c)
            pend_c -= u
            custo += u * o["preco"] + o["custos"] * u / o["qtd"]
            consumo[o["idx"]] = consumo.get(o["idx"], 0) + u
        for o in vendas:
            if pend_v == 0:
                break
            u = min(o["qtd"], pend_v)
            pend_v -= u
            receita += u * o["preco"] - o["custos"] * u / o["qtd"]
            irrf += o["irrf"] * u / o["qtd"]
            consumo[o["idx"]] = consumo.get(o["idx"], 0) + u
        dt_res.append({"ativo": ativo, "classe": lst[0]["classe"], "resultado": receita - custo,
                       "irrf": irrf, "quantidade": q, "data": lst[0]["data"]})
        if irrf == 0 and any(o["irrf"] for o in vendas):
            pass
    normais = []
    for o in ops_dia:
        u = consumo.get(o["idx"], 0)
        resta = o["qtd"] - u
        if resta == 0:
            continue
        p = dict(o)
        p["qtd"] = resta
        p["custos"] = o["custos"] * resta / o["qtd"]
        p["irrf"] = o["irrf"] * resta / o["qtd"]
        normais.append(p)
    return normais, dt_res


# ---------------------------------------------------------------- apuração
def apurar(entrada, hoje=None):
    """Devolve dict com 'meses' (lista de resultados mensais) e 'avisos' gerais."""
    hoje = hoje or dt.date.today()
    ops = _normalizar(entrada)
    if not ops:
        raise ErroCalculo("Nenhuma operação informada.")
    avisos = []
    saldos = entrada.get("saldos_iniciais", {}) or {}
    car = {
        "geral_comum": frac(saldos.get("prejuizo_geral_comum")),
        "geral_dt": frac(saldos.get("prejuizo_geral_daytrade")),
        "fii": frac(saldos.get("prejuizo_fii_fiagro")),
    }
    irrf_c = frac(saldos.get("irrf_comum"))
    irrf_d = frac(saldos.get("irrf_daytrade"))
    abaixo10 = frac(saldos.get("imposto_abaixo_de_10"))
    for nome, v in list(car.items()) + [("irrf_comum", irrf_c), ("irrf_daytrade", irrf_d), ("imposto_abaixo_de_10", abaixo10)]:
        if v < 0:
            raise ErroCalculo(f"Saldo inicial '{nome}' não pode ser negativo.")

    estoque = {}  # ativo -> [qtd, custo_total]
    heranca = set()
    for p in entrada.get("posicoes_iniciais", []) or []:
        q = frac(p.get("quantidade"))
        estoque[str(p["ativo"]).upper()] = [q, q * frac(p.get("preco_medio"))]
    pagamentos = {k: data(v) for k, v in (entrada.get("pagamentos") or {}).items()}

    inicio = ym(ops[0]["data"])
    fim = ym(ops[-1]["data"])
    meses_resultado = []
    a, m = inicio
    ultimo_dt_aviso = set()
    while (a, m) <= fim:
        if m == 1:
            irrf_d = Fraction(0)  # IRRF de day trade só compensa até dezembro do mesmo ano
        ops_mes = [o for o in ops if ym(o["data"]) == (a, m)]
        avisos_mes = []
        vendas = []   # dicts: ativo, classe, bruto, resultado, irrf, dt
        dias = sorted({o["data"] for o in ops_mes})
        for dia in dias:
            normais, dts = _separar_daytrade([o for o in ops_mes if o["data"] == dia], avisos_mes)
            for r in dts:
                vendas.append({"ativo": r["ativo"], "classe": r["classe"], "bruto": Fraction(0),
                               "resultado": r["resultado"], "irrf": r["irrf"], "dt": True, "data": dia})
            for o in normais:
                pos = estoque.setdefault(o["ativo"], [Fraction(0), Fraction(0)])
                if o["tipo"] in ("compra", "heranca"):
                    pos[0] += o["qtd"]
                    pos[1] += o["qtd"] * o["preco"] + o["custos"]
                    if o["tipo"] == "heranca":
                        heranca.add(o["ativo"])
                else:
                    if o["qtd"] > pos[0]:
                        raise ErroCalculo(
                            f"{o['ativo']}: venda de {_n(o['qtd'])} em {dia:%d/%m/%Y}, mas o estoque é "
                            f"{_n(pos[0])}. Faltam compras ou a posição inicial. Não calculei.")
                    custo = pos[1] * o["qtd"] / pos[0]
                    pos[0] -= o["qtd"]
                    pos[1] -= custo
                    liquido = o["qtd"] * o["preco"] - o["custos"]
                    vendas.append({"ativo": o["ativo"], "classe": o["classe"], "bruto": o["qtd"] * o["preco"],
                                   "resultado": liquido - custo, "irrf": o["irrf"], "dt": False, "data": dia,
                                   "heranca": o["ativo"] in heranca})
        meses_resultado.append(_fechar_mes(a, m, vendas, car, avisos_mes, pagamentos, hoje,
                                           state := {"irrf_c": irrf_c, "irrf_d": irrf_d, "abaixo10": abaixo10}))
        irrf_c, irrf_d, abaixo10 = state["irrf_c"], state["irrf_d"], state["abaixo10"]
        a, m = (a, m + 1) if m < 12 else (a + 1, 1)
    sem_venda = [r for r in meses_resultado if not r["vendas"]]
    return {"meses": [r for r in meses_resultado if r["vendas"] or r["darf"] or r["abaixo_de_10_acumulado"]],
            "avisos": avisos, "saldos_finais": {k: cent(v) for k, v in car.items()},
            "irrf_comum_saldo": cent(irrf_c), "irrf_daytrade_saldo": cent(irrf_d),
            "imposto_abaixo_de_10": cent(abaixo10), "ignorados": len(sem_venda)}


def _n(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else str(float(x))


def _bucket(res, carry, aliquota):
    """Aplica o resultado do mês a um grupo. Devolve (base, imposto, carry_novo, usado)."""
    if res >= 0:
        usado = min(carry, res)
        base = res - usado
        return base, cent_f(base * aliquota), carry - usado, usado
    return Fraction(0), Fraction(0), carry - res, Fraction(0)


def _fechar_mes(a, m, vendas, car, avisos, pagamentos, hoje, st):
    geral = [v for v in vendas if CLASSES[v["classe"]][0] == "Geral" and not v["dt"]]
    geral_dt = [v for v in vendas if CLASSES[v["classe"]][0] == "Geral" and v["dt"]]
    fii = [v for v in vendas if CLASSES[v["classe"]][0] == "FII/Fiagro"]
    infra = [v for v in vendas if CLASSES[v["classe"]][0] == "Infra"]

    # --- grupo Geral, operação comum, com a isenção de R$ 20 mil só para ações
    acoes = [v for v in geral if v["classe"] == "acao"]
    vendas_acoes = sum((v["bruto"] for v in acoes), Fraction(0))
    res_acoes = sum((v["resultado"] for v in acoes), Fraction(0))
    isento = bool(acoes) and vendas_acoes <= LIMITE_ISENCAO and res_acoes > 0
    res_outros = sum((v["resultado"] for v in geral if v["classe"] != "acao"), Fraction(0))
    res_geral = res_outros + (Fraction(0) if isento else res_acoes)
    carry_geral_ini = car["geral_comum"]
    base_g, imp_g, car["geral_comum"], usado_g = _bucket(res_geral, car["geral_comum"], ALIQ["geral_comum"])

    res_dt = sum((v["resultado"] for v in geral_dt), Fraction(0))
    base_d, imp_d, car["geral_dt"], usado_d = _bucket(res_dt, car["geral_dt"], ALIQ["geral_dt"])

    res_fii = sum((v["resultado"] for v in fii), Fraction(0))
    base_f, imp_f, car["fii"], usado_f = _bucket(res_fii, car["fii"], ALIQ["fii"])

    res_infra = sum((v["resultado"] for v in infra), Fraction(0))

    # --- IRRF informado (comum: 0,005%; day trade: 1%)
    st["irrf_c"] += sum((v["irrf"] for v in vendas if not v["dt"] and v["classe"] != "fiinfra"), Fraction(0))
    st["irrf_d"] += sum((v["irrf"] for v in vendas if v["dt"]), Fraction(0))
    ded_c = min(st["irrf_c"], imp_g + imp_f)
    st["irrf_c"] -= ded_c
    ded_d = min(st["irrf_d"], imp_d)
    st["irrf_d"] -= ded_d

    imposto = (imp_g + imp_f - ded_c) + (imp_d - ded_d)
    total = imposto + st["abaixo10"]
    darf = Fraction(0)
    acumulado = Fraction(0)
    if total >= MINIMO_DARF:
        darf = total
        st["abaixo10"] = Fraction(0)
    elif total > 0:
        acumulado = total
        st["abaixo10"] = total
    venc = calendario.vencimento_darf(a, m)

    # --- pagamento em atraso
    atraso = None
    pag = pagamentos.get(chave(a, m))
    if darf > 0 and pag and pag > venc:
        ini = calendario.proximo_dia_util(venc)
        dias = max(1, (pag - ini).days + 1)
        pct_multa = min(Fraction(33, 100) * dias, Fraction(20))
        pct_juros = Fraction(mod_selic.juros_mora_percentual(venc, pag))
        multa = cent_f(darf * pct_multa / 100)
        juros = cent_f(darf * pct_juros / 100)
        atraso = {"pagamento": pag, "dias": dias, "pct_multa": pct_multa, "multa": multa,
                  "pct_juros": pct_juros, "juros": juros, "total": darf + multa + juros}
    elif darf > 0 and not pag and venc < hoje:
        avisos.append(f"O DARF de {m:02d}/{a} venceu em {venc:%d/%m/%Y}. Informe a data de pagamento para "
                      "calcular multa e juros.")

    # --- avisos e o que não compensa
    nao_comp = []
    if infra:
        nao_comp.append(("fiinfra", res_infra))
    if any(v["resultado"] < 0 for v in fii) and res_geral > 0:
        nao_comp.append(("fii_contra_geral", None))
    if any(v["resultado"] < 0 for v in geral) and res_fii > 0:
        nao_comp.append(("geral_contra_fii", None))
    if res_dt < 0 and res_geral > 0:
        nao_comp.append(("dt_contra_comum", None))
    if res_geral < 0 and res_dt > 0:
        nao_comp.append(("comum_contra_dt", None))
    if isento and carry_geral_ini > 0:
        nao_comp.append(("isento_nao_usa_prejuizo", carry_geral_ini))
    if any(v.get("heranca") for v in vendas):
        nao_comp.append(("heranca_prejuizo_falecido", None))

    if any(v["classe"] == "unit" for v in vendas):
        avisos.append("Unit: não achei posição oficial sobre a isenção de R$ 20 mil; tratei como SEM isenção (D1).")
    if infra:
        avisos.append("FI-Infra: a alíquota zero vale para fundo que cumpre a Lei 12.431 (art. 3º); "
                      "não verifiquei o regulamento do fundo.")
    ult = [v for v in vendas if not v["dt"] and v["data"] >= _antepenultimo_util(a, m)]
    if ult:
        avisos.append("Há venda nos 2 últimos pregões do mês. Se a corretora liquidar no mês seguinte, a Receita "
                      "(Perguntas e Respostas IRPF 2026, pergunta 745) conta o prazo da liquidação; usei o mês do pregão, "
                      "que vence antes (D3).")
    if acoes and geral_dt and any(v["classe"] == "acao" for v in geral_dt):
        avisos.append("Mês com day trade e venda comum de ações: não achei regra dizendo se o day trade conta nos "
                      "R$ 20 mil; não contei.")
    if m == 12 and st["irrf_d"] > 0:
        avisos.append(f"Sobrou IRRF de day trade de {cent(st['irrf_d'])}: só compensa até dezembro; pode pedir restituição.")
    if darf > 0 or imposto > 0:
        avisos.append("Valores arredondados ao centavo; o Sicalc pode diferir em R$ 0,01 (D5).")

    return {
        "ano": a, "mes": m, "vendas": vendas, "vendas_acoes": vendas_acoes, "isento": isento,
        "res_acoes": res_acoes, "res_geral": res_geral, "res_dt": res_dt, "res_fii": res_fii, "res_infra": res_infra,
        "carry_ini_geral": carry_geral_ini, "usado": {"geral": usado_g, "dt": usado_d, "fii": usado_f},
        "base": {"geral": base_g, "dt": base_d, "fii": base_f},
        "imposto_bruto": {"geral": imp_g, "dt": imp_d, "fii": imp_f},
        "irrf_deduzido": ded_c + ded_d, "imposto": imposto, "darf": darf,
        "abaixo_de_10_acumulado": acumulado, "vencimento": venc, "atraso": atraso,
        "carry_fim": dict(car), "nao_compensa": nao_comp, "avisos": avisos,
        "codigo": CODIGO,
    }


def _antepenultimo_util(a, m):
    """Data do penúltimo pregão do mês (limite para o aviso D3)."""
    import calendar
    d = dt.date(a, m, calendar.monthrange(a, m)[1])
    n = 0
    while True:
        if calendario.eh_util(d):
            n += 1
            if n == 2:
                return d
        d -= dt.timedelta(days=1)
