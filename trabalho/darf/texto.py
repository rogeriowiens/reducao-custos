"""Relatório do mês e texto pronto para WhatsApp (com [nome] no lugar do cliente)."""
from fractions import Fraction

from calculadora import CLASSES, cent

MESES = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def brl(x):
    v = cent(Fraction(x)) if not hasattr(x, "quantize") else x
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if v < 0 else "") + "R$ " + s


def pct(x):
    x = Fraction(x)
    s = f"{float(x):.2f}".replace(".", ",")
    return s + "%"


def _nome_classe(c):
    return CLASSES[c][1]


def _lucro_ou_prejuizo(r):
    return ("lucro de " + brl(r)) if r >= 0 else ("prejuízo de " + brl(-r))


NAO_COMPENSA = {
    "fiinfra": "FI-Infra: o fundo tem alíquota zero para pessoa física e fica fora da apuração; o prejuízo não abate imposto de outros ativos nem fica guardado.",
    "fii_contra_geral": "Prejuízo em FII/Fiagro não abate ganho de ação ou BDR: FII e Fiagro só compensam entre si.",
    "geral_contra_fii": "Prejuízo em ação ou BDR não abate ganho de FII ou Fiagro: os grupos são separados.",
    "dt_contra_comum": "Prejuízo de day trade só compensa com ganho de day trade, não com operação comum.",
    "comum_contra_dt": "Prejuízo de operação comum não compensa ganho de day trade.",
    "isento_nao_usa_prejuizo": "O ganho em ações é isento e fica fora da apuração, então não consome o prejuízo acumulado, que segue guardado.",
    "heranca_prejuizo_falecido": "Prejuízo acumulado que o falecido tinha não passa para o herdeiro junto com as ações.",
}


def relatorio_mes(r):
    L = []
    t = f"{r['mes']:02d}/{r['ano']}"
    L.append(f"=== Apuração de {t} ===")
    for v in r["vendas"]:
        tag = " (day trade)" if v["dt"] else ""
        L.append(f"  {v['ativo']} [{_nome_classe(v['classe'])}]{tag}: {_lucro_ou_prejuizo(v['resultado'])}"
                 + ("" if v["dt"] else f", vendeu {brl(v['bruto'])}"))
    if r["vendas_acoes"]:
        L.append(f"  Vendas de ações no mês: {brl(r['vendas_acoes'])} -> "
                 + ("isenção de R$ 20 mil vale para o ganho" if r["isento"] else "sem isenção"))
    ia = r["imposto_bruto"]
    L.append(f"  Geral (comum, 15%): resultado {brl(r['res_geral'])}; prejuízo usado {brl(r['usado']['geral'])}; "
             f"base {brl(r['base']['geral'])}; imposto {brl(ia['geral'])}")
    if r["res_dt"] or ia["dt"]:
        L.append(f"  Geral (day trade, 20%): resultado {brl(r['res_dt'])}; prejuízo usado {brl(r['usado']['dt'])}; "
                 f"base {brl(r['base']['dt'])}; imposto {brl(ia['dt'])}")
    if r["res_fii"] or ia["fii"]:
        L.append(f"  FII/Fiagro (20%): resultado {brl(r['res_fii'])}; prejuízo usado {brl(r['usado']['fii'])}; "
                 f"base {brl(r['base']['fii'])}; imposto {brl(ia['fii'])}")
    if r["res_infra"]:
        L.append(f"  FI-Infra (0%): resultado {brl(r['res_infra'])}, sem imposto")
    if r["irrf_deduzido"]:
        L.append(f"  IR retido abatido: {brl(r['irrf_deduzido'])}")
    L.append(f"  Prejuízo acumulado que sobra: Geral comum {brl(r['carry_fim']['geral_comum'])}; "
             f"day trade {brl(r['carry_fim']['geral_dt'])}; FII/Fiagro {brl(r['carry_fim']['fii'])}")
    if r["abaixo_de_10_acumulado"]:
        L.append(f"  Imposto de {brl(r['abaixo_de_10_acumulado'])} é menor que R$ 10,00: não gera DARF; "
                 "soma no mês seguinte até chegar a R$ 10,00.")
    elif r["darf"]:
        L.append(f"  DARF: {brl(r['darf'])} | código {r['codigo']} | vencimento {r['vencimento']:%d/%m/%Y}")
        if r["atraso"]:
            at = r["atraso"]
            L.append(f"  Pago em {at['pagamento']:%d/%m/%Y}: {at['dias']} dias de atraso, multa {pct(at['pct_multa'])} "
                     f"= {brl(at['multa'])}; juros {pct(at['pct_juros'])} = {brl(at['juros'])}; "
                     f"TOTAL {brl(at['total'])}")
    else:
        L.append("  Sem imposto a pagar neste mês.")
    for kind, _ in r["nao_compensa"]:
        L.append("  Não compensa: " + NAO_COMPENSA[kind])
    for a in dict.fromkeys(r["avisos"]):
        L.append("  Aviso: " + a)
    return "\n".join(L)


def whatsapp_mes(r):
    mes = f"{MESES[r['mes']]}/{r['ano']}"
    L = [f"Oi, [nome]! Fechei a conta das suas vendas de {mes}.", ""]
    for v in r["vendas"]:
        c = v["classe"]
        nome = _nome_classe(c)
        if v["dt"]:
            L.append(f"• {v['ativo']} ({nome}, day trade): {_lucro_ou_prejuizo(v['resultado'])}. "
                     "Day trade é tributado a 20% e não tem isenção.")
        elif c == "acao":
            if r["isento"] and v["resultado"] > 0:
                L.append(f"• {v['ativo']} ({nome}): {_lucro_ou_prejuizo(v['resultado'])}, isento. Você vendeu "
                         f"{brl(r['vendas_acoes'])} em ações no mês, dentro do limite de R$ 20 mil.")
            elif v["resultado"] > 0:
                L.append(f"• {v['ativo']} ({nome}): {_lucro_ou_prejuizo(v['resultado'])}. As vendas de ações no mês "
                         f"somaram {brl(r['vendas_acoes'])}, acima de R$ 20 mil, então não há isenção.")
            else:
                L.append(f"• {v['ativo']} ({nome}): {_lucro_ou_prejuizo(v['resultado'])}.")
        elif c in ("bdr", "unit"):
            L.append(f"• {v['ativo']} ({nome}): {_lucro_ou_prejuizo(v['resultado'])}. "
                     f"{'BDR' if c == 'bdr' else 'Unit'} não tem a isenção de R$ 20 mil.")
        elif c in ("fii", "fiagro"):
            L.append(f"• {v['ativo']} ({nome}): {_lucro_ou_prejuizo(v['resultado'])}. FII e Fiagro são tributados a 20% "
                     "e não têm isenção.")
        else:
            L.append(f"• {v['ativo']} ({nome}): {_lucro_ou_prejuizo(v['resultado'])}. Esse tipo de fundo tem "
                     "alíquota zero de IR para pessoa física.")
    L.append("")
    ia = r["imposto_bruto"]
    if r["usado"]["geral"]:
        L.append(f"Usei {brl(r['usado']['geral'])} do seu prejuízo acumulado em ações/BDR; base tributada "
                 f"{brl(r['base']['geral'])} a 15% = {brl(ia['geral'])}.")
    elif ia["geral"]:
        L.append(f"Ações/BDR: {brl(r['base']['geral'])} a 15% = {brl(ia['geral'])}.")
    if r["usado"]["dt"]:
        L.append(f"Day trade: usei {brl(r['usado']['dt'])} de prejuízo acumulado.")
    if ia["dt"]:
        L.append(f"Day trade: {brl(r['base']['dt'])} a 20% = {brl(ia['dt'])}.")
    if r["usado"]["fii"]:
        L.append(f"FII/Fiagro: usei {brl(r['usado']['fii'])} de prejuízo (FII e Fiagro se compensam).")
    if ia["fii"]:
        L.append(f"FII/Fiagro: {brl(r['base']['fii'])} a 20% = {brl(ia['fii'])}.")
    if r["irrf_deduzido"]:
        L.append(f"IR já retido nas vendas: {brl(r['irrf_deduzido'])}.")
    L.append("")
    if r["abaixo_de_10_acumulado"]:
        L.append(f"O imposto deste mês ({brl(r['abaixo_de_10_acumulado'])}) é menor que R$ 10,00 e não gera DARF. "
                 "Ele soma no mês seguinte, até passar de R$ 10,00.")
    elif r["darf"]:
        if r["atraso"]:
            at = r["atraso"]
            L.append(f"O DARF venceu em {r['vencimento']:%d/%m/%Y}. Pagando em {at['pagamento']:%d/%m/%Y}:")
            L.append(f"• Imposto: {brl(r['darf'])}")
            L.append(f"• Multa ({at['dias']} dias de atraso, {pct(at['pct_multa'])}): {brl(at['multa'])}")
            L.append(f"• Juros ({pct(at['pct_juros'])}): {brl(at['juros'])}")
            L.append("")
            L.append(f"*DARF a pagar: {brl(at['total'])}*")
            L.append(f"Código {r['codigo']} | período {r['mes']:02d}/{r['ano']}")
        else:
            L.append(f"*DARF a pagar: {brl(r['darf'])}*")
            L.append(f"Código {r['codigo']} | vencimento {r['vencimento']:%d/%m/%Y}")
    else:
        L.append("Neste mês não há imposto a pagar.")
    saldo = r["carry_fim"]
    guardado = []
    if saldo["geral_comum"] > 0:
        guardado.append(f"ações/BDR {brl(saldo['geral_comum'])}")
    if saldo["geral_dt"] > 0:
        guardado.append(f"day trade {brl(saldo['geral_dt'])}")
    if saldo["fii"] > 0:
        guardado.append(f"FII/Fiagro {brl(saldo['fii'])}")
    if guardado:
        L.append("")
        L.append("Prejuízo que segue guardado para meses futuros: " + "; ".join(guardado) + ".")
    elif r["usado"]["geral"] or r["usado"]["fii"] or r["usado"]["dt"]:
        L.append("")
        L.append("Seu prejuízo acumulado zerou.")
    notas = [NAO_COMPENSA[k] for k, _ in r["nao_compensa"]]
    if notas:
        L.append("")
        L.extend(notas)
    return "\n".join(L).strip() + "\n"
