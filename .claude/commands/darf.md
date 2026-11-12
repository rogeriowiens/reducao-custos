---
description: Calcula o DARF (código 6015) de venda de FII, Fiagro, ações, BDR e FI-Infra, com texto pronto para WhatsApp
---

Rode a calculadora de DARF em `trabalho/darf/`. Regras e fontes: `trabalho/regras.md`.

1. Pergunte ao usuário, em português, só o que faltar (use apelido do cliente; nunca nome, CPF ou conta):
   - prejuízo acumulado por grupo (ações/BDR/units, day trade, FII/Fiagro) e IR retido ainda não abatido;
   - posição que o cliente já tinha antes da primeira operação (ativo, tipo, quantidade, preço médio);
   - cada compra, venda ou herança: data, ativo, tipo (ação, unit, BDR, FII, Fiagro, FI-Infra), quantidade,
     preço unitário, custos da nota e IR retido; na herança, o preço é o valor da partilha;
   - data de pagamento do DARF, se já venceu.
2. Grave os dados em `trabalho/dados/<apelido>.json` (pasta ignorada pelo git), no formato de
   `trabalho/darf/exemplo.json`.
3. Rode `python3 trabalho/darf trabalho/dados/<apelido>.json` e mostre a saída inteira, inclusive o
   bloco "TEXTO PARA WHATSAPP" e os avisos.
4. Se a calculadora parar com erro (venda maior que o estoque, Selic ausente), mostre a mensagem e
   peça o dado que falta. Não estime nada.

Argumentos do usuário, se houver: $ARGUMENTS
