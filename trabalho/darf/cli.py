"""Interface em português: pergunta os dados ou lê um arquivo JSON."""
import datetime as dt
import json
import os
import re
import sys
from fractions import Fraction

import calculadora as calc
import texto

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DADOS = os.path.join(RAIZ, "trabalho", "dados")

CLASSES_MENU = [("acao", "ação"), ("unit", "unit"), ("bdr", "BDR"), ("fii", "FII"),
                ("fiagro", "Fiagro"), ("fiinfra", "FI-Infra")]
USO = """Uso:
  python3 trabalho/darf                      pergunta os dados em português
  python3 trabalho/darf arquivo.json         lê um arquivo (veja trabalho/darf/exemplo.json)
  python3 trabalho/darf arquivo.json --mes 2026-03   mostra só esse mês
  python3 trabalho/darf --atualizar-selic    baixa a Selic nova do Sicalc (Receita)
"""


def pergunta(msg, padrao=None):
    suf = f" [{padrao}]" if padrao is not None else ""
    try:
        r = input(f"{msg}{suf}: ").strip()
    except EOFError:
        print()
        sys.exit(1)
    return r if r else (padrao if padrao is not None else "")


def num_br(s):
    """Número digitado em português: 1.234,56 -> '1234.56'."""
    s = s.strip().replace("R$", "").replace(" ", "")
    if not s:
        return "0"
    s = s.replace(".", "").replace(",", ".")
    try:
        Fraction(s)
    except ValueError:
        raise ValueError(f"não entendi o número '{s}'")
    return s


def data_br(s):
    try:
        return dt.datetime.strptime(s.strip(), "%d/%m/%Y").date().isoformat()
    except ValueError:
        raise ValueError("use a data como dd/mm/aaaa")


def tentar(msg, conv, padrao=None):
    while True:
        r = pergunta(msg, padrao)
        try:
            return conv(r)
        except ValueError as e:
            print(f"  ! {e}")


def coletar():
    print("Calculadora de DARF de renda variável (código 6015)")
    print("Use só apelido, sem nome, CPF ou conta. Valores no formato 1.234,56. Enter deixa o padrão.\n")
    apelido = re.sub(r"[^a-z0-9_-]", "", pergunta("Apelido do cliente (ex.: cliente-a)", "cliente").lower()) or "cliente"
    entrada = {"apelido": apelido, "saldos_iniciais": {}, "posicoes_iniciais": [], "operacoes": [], "pagamentos": {}}

    print("\nPrejuízo acumulado de meses anteriores (informado na declaração do IR). Enter = 0.")
    s = entrada["saldos_iniciais"]
    s["prejuizo_geral_comum"] = tentar("  Ações/BDR/units, operação comum (R$)", num_br, "0")
    s["prejuizo_geral_daytrade"] = tentar("  Day trade (R$)", num_br, "0")
    s["prejuizo_fii_fiagro"] = tentar("  FII e Fiagro (R$)", num_br, "0")
    s["irrf_comum"] = tentar("  IR retido (0,005%) ainda não abatido (R$)", num_br, "0")

    print("\nPosição que o cliente já tinha antes da primeira operação abaixo (Enter no ativo para terminar).")
    while True:
        ativo = pergunta("  Ativo (ex.: ACAO3)").upper()
        if not ativo:
            break
        classe = escolher_classe()
        qtd = tentar("  Quantidade", num_br)
        pm = tentar("  Preço médio (R$)", num_br)
        entrada["posicoes_iniciais"].append({"ativo": ativo, "classe": classe, "quantidade": qtd, "preco_medio": pm})

    print("\nOperações em ordem. Tipo: c = compra, v = venda, h = herança (preço = valor da partilha).")
    print("Enter na data para terminar.")
    while True:
        d = pergunta("\n  Data (dd/mm/aaaa)")
        if not d:
            break
        try:
            d = data_br(d)
        except ValueError as e:
            print(f"  ! {e}")
            continue
        tipo = tentar("  Tipo (c/v/h)", lambda x: {"c": "compra", "v": "venda", "h": "heranca"}[x.lower()]
                      if x.lower() in ("c", "v", "h") else (_ for _ in ()).throw(ValueError("digite c, v ou h")))
        ativo = pergunta("  Ativo").upper()
        classe = escolher_classe()
        qtd = tentar("  Quantidade", num_br)
        preco = tentar("  Preço unitário (R$)" + (" - valor da partilha" if tipo == "heranca" else ""), num_br)
        custos = "0" if tipo == "heranca" else tentar("  Custos da nota: corretagem, emolumentos, taxas (R$)", num_br, "0")
        irrf = tentar("  IR retido na nota (R$)", num_br, "0") if tipo == "venda" else "0"
        corretora = pergunta("  Corretora (apelido; Enter = mesma de sempre)", "")
        entrada["operacoes"].append({"data": d, "tipo": tipo, "ativo": ativo, "classe": classe, "quantidade": qtd,
                                     "preco": preco, "custos": custos, "irrf": irrf, "corretora": corretora})
    return entrada


def escolher_classe():
    print("  Tipo de ativo: " + ", ".join(f"{i + 1}={n}" for i, (_, n) in enumerate(CLASSES_MENU)))
    return CLASSES_MENU[tentar("  Número", lambda x: int(x) - 1 if x.isdigit() and 1 <= int(x) <= len(CLASSES_MENU)
                               else (_ for _ in ()).throw(ValueError("escolha um número da lista")))][0]


def mostrar(res, so_mes=None):
    for r in res["meses"]:
        if so_mes and (r["ano"], r["mes"]) != so_mes:
            continue
        print(texto.relatorio_mes(r))
        print("\n--- TEXTO PARA WHATSAPP ---")
        print(texto.whatsapp_mes(r))
        print("--- FIM DO TEXTO ---\n")
    for a in res["avisos"]:
        print("Aviso:", a)


def main(argv):
    if "-h" in argv or "--help" in argv:
        print(USO)
        return 0
    if "--atualizar-selic" in argv:
        import selic
        n, ultimo = selic.atualizar()
        print(f"Selic atualizada: {n} mês(es) novo(s); última disponível {ultimo}.")
        return 0
    so_mes = None
    if "--mes" in argv:
        i = argv.index("--mes")
        a, m = argv[i + 1].split("-")
        so_mes = (int(a), int(m))
        argv = argv[:i] + argv[i + 2:]
    arquivos = [x for x in argv if not x.startswith("--")]
    try:
        if arquivos:
            with open(arquivos[0], encoding="utf-8") as f:
                entrada = json.load(f)
            res = calc.apurar(entrada)
            mostrar(res, so_mes)
            return 0
        entrada = coletar()
        if not entrada["operacoes"]:
            print("Nenhuma operação informada.")
            return 1
        res = calc.apurar(entrada)
        mostrar(res, so_mes)
        # pagamento em atraso: pergunta só dos meses com DARF vencido
        hoje = dt.date.today()
        mudou = False
        for r in res["meses"]:
            if r["darf"] and r["vencimento"] < hoje and not r["atraso"]:
                d = pergunta(f"O DARF de {r['mes']:02d}/{r['ano']} venceu em {r['vencimento']:%d/%m/%Y}. "
                             "Data do pagamento (dd/mm/aaaa; Enter = ainda não pagou/pagou no prazo)")
                if d:
                    try:
                        entrada["pagamentos"][f"{r['ano']:04d}-{r['mes']:02d}"] = data_br(d)
                        mudou = True
                    except ValueError as e:
                        print(f"  ! {e}")
        if mudou:
            print()
            mostrar(calc.apurar(entrada), so_mes)
        if pergunta("Salvar estes dados para reaproveitar (fica só nesta máquina, por apelido)? (s/n)", "n").lower() == "s":
            os.makedirs(DADOS, exist_ok=True)
            caminho = os.path.join(DADOS, entrada["apelido"] + ".json")
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(entrada, f, ensure_ascii=False, indent=1)
            print(f"Salvo em {caminho}")
        return 0
    except (calc.ErroCalculo, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Não consegui calcular: {e}")
        return 1
    except Exception as e:  # SelicIndisponivel, ErroCalendario
        print(f"Não consegui calcular: {e}")
        return 1
