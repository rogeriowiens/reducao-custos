# /darf — casos de teste

Três casos calculados à mão, antes de qualquer código. Depois de aprovados, viram testes automáticos: a ferramenta só está pronta quando reproduzir estes números ao centavo. As regras citadas estão em `trabalho/regras.md`.

Tickers fictícios, sem cliente real.

---

## Caso 1 — Exemplo oficial da Receita (ação, com custos e IR retido)

**O que testa:** custo com taxas, limite de R$ 20 mil estourado, alíquota de 15%, abatimento do IR retido, vencimento em mês com feriado.

É o exemplo publicado pela própria Receita na página "Cálculo e Pagamento do Imposto" (fonte F3). Se a ferramenta não der o número da Receita, está errada.

**Entrada**

| Data | Operação | Ativo | Tipo | Quantidade | Preço | Custos |
|---|---|---|---|---|---|---|
| 10/01/2024 | Compra | WXYZ3 | Ação | 1.000 | R$ 50,00 | R$ 15,00 |
| 26/02/2024 | Venda | WXYZ3 | Ação | 1.000 | R$ 60,00 | R$ 18,00 |

IR retido na venda, informado da nota: R$ 3,00. Prejuízo acumulado: zero.

**Conta**

| Passo | Valor |
|---|---|
| Custo total da compra | R$ 50.000,00 + R$ 15,00 = R$ 50.015,00 |
| Preço médio | R$ 50,015 por ação |
| Vendas de ações em fevereiro/2024 | R$ 60.000,00, acima de R$ 20.000,00: sem isenção |
| Valor líquido da venda | R$ 60.000,00 − R$ 18,00 = R$ 59.982,00 |
| Ganho | R$ 59.982,00 − R$ 50.015,00 = R$ 9.967,00 |
| Imposto a 15% | R$ 1.495,05 |
| IR retido | − R$ 3,00 |

**Resultado esperado**

| Campo | Valor |
|---|---|
| DARF | **R$ 1.492,05** |
| Código | 6015 |
| Período de apuração | 02/2024 |
| Vencimento | **28/03/2024** (dia 29 foi Sexta-feira Santa; a Agenda Tributária da Receita lista o 6015 no dia 28) |

**Texto esperado para WhatsApp**

```
Oi, [nome]! Fechei a conta da sua venda de WXYZ3 em fevereiro/2024.

• Venda: 1.000 ações a R$ 60,00 = R$ 60.000,00
• Preço médio de compra: R$ 50,02 (já com as taxas)
• Lucro: R$ 9.967,00
• Imposto (15%): R$ 1.495,05
• IR já retido na venda: R$ 3,00

*DARF a pagar: R$ 1.492,05*
Código 6015 | vencimento 28/03/2024

Não entrou na isenção porque as vendas de ações no mês passaram de R$ 20 mil.
```

---

## Caso 2 — Cinco tipos de ativo no mesmo mês

**O que testa:** isenção de R$ 20 mil só para ações, BDR sem isenção, prejuízo acumulado, FII e Fiagro no mesmo grupo, FI-Infra a 0%, e a lista do que não compensa.

**Entrada**

Posição comprada em 2025, custos zero:

| Data | Ativo | Tipo | Quantidade | Preço | Total |
|---|---|---|---|---|---|
| 10/02/2025 | ACAO3 | Ação | 500 | R$ 30,00 | R$ 15.000,00 |
| 12/02/2025 | BDRX34 | BDR | 200 | R$ 50,00 | R$ 10.000,00 |
| 14/02/2025 | FIIX11 | FII | 100 | R$ 160,00 | R$ 16.000,00 |
| 17/02/2025 | FAGR11 | Fiagro | 1.000 | R$ 9,00 | R$ 9.000,00 |
| 19/02/2025 | INFR11 | FI-Infra | 100 | R$ 100,00 | R$ 10.000,00 |

Vendas em março/2026, custos zero:

| Data | Ativo | Quantidade | Preço | Total |
|---|---|---|---|---|
| 05/03/2026 | ACAO3 | 500 | R$ 36,00 | R$ 18.000,00 |
| 10/03/2026 | BDRX34 | 200 | R$ 57,50 | R$ 11.500,00 |
| 12/03/2026 | FIIX11 | 100 | R$ 152,00 | R$ 15.200,00 |
| 16/03/2026 | FAGR11 | 1.000 | R$ 10,20 | R$ 10.200,00 |
| 18/03/2026 | INFR11 | 100 | R$ 95,00 | R$ 9.500,00 |

Prejuízo acumulado até fevereiro/2026: R$ 1.000,00 no grupo Geral (operações comuns); zero em FII/Fiagro. IR retido: não informado.

**Conta**

| Cesta | Resultado da venda | Tratamento | Imposto |
|---|---|---|---|
| Ação (ACAO3) | + R$ 3.000,00 | Vendas de ações no mês: R$ 18.000,00, até R$ 20.000,00. **Isento.** Não consome o prejuízo acumulado. | R$ 0,00 |
| BDR (BDRX34) | + R$ 1.500,00 | Sem isenção. Abate o prejuízo acumulado de R$ 1.000,00. Base: R$ 500,00 a 15%. | R$ 75,00 |
| FII (FIIX11) | − R$ 800,00 | Mesmo grupo do Fiagro. | |
| Fiagro (FAGR11) | + R$ 1.200,00 | Base do grupo: R$ 1.200,00 − R$ 800,00 = R$ 400,00 a 20%. | R$ 80,00 |
| FI-Infra (INFR11) | − R$ 500,00 | Alíquota zero. Não compensa e não acumula. | R$ 0,00 |

**Resultado esperado**

| Campo | Valor |
|---|---|
| DARF | **R$ 155,00** (R$ 75,00 + R$ 80,00) |
| Código | 6015 |
| Período de apuração | 03/2026 |
| Vencimento | **30/04/2026** |
| Prejuízo acumulado que sobra | Geral: R$ 0,00. FII/Fiagro: R$ 0,00. |

**O que não pôde ser compensado, e por quê**

| Item | Motivo |
|---|---|
| Prejuízo de R$ 500,00 em FI-Infra | Fundo de infraestrutura tem alíquota zero para pessoa física e fica fora da apuração; a perda não abate ganho de outro grupo nem fica guardada. |
| Prejuízo de R$ 800,00 em FII contra o ganho em BDR | FII e Fiagro só compensam entre si. Aqui foi todo usado contra o ganho do Fiagro. |
| Prejuízo acumulado de R$ 1.000,00 contra o ganho de R$ 3.000,00 em ações | O ganho é isento e fica fora da apuração. O prejuízo foi usado contra o ganho do BDR. |

**Texto esperado para WhatsApp**

```
Oi, [nome]! Fechei a conta das suas vendas de março/2026.

• ACAO3 (ação): lucro de R$ 3.000,00, isento. Você vendeu R$ 18.000,00 em ações no mês, dentro do limite de R$ 20 mil.
• BDRX34 (BDR): lucro de R$ 1.500,00. BDR não tem isenção. Usei seu prejuízo acumulado de R$ 1.000,00 e sobraram R$ 500,00 tributados a 15% = R$ 75,00.
• FIIX11 (FII) e FAGR11 (Fiagro): prejuízo de R$ 800,00 e lucro de R$ 1.200,00. Os dois se compensam: R$ 400,00 a 20% = R$ 80,00.
• INFR11 (FI-Infra): prejuízo de R$ 500,00. Esse tipo de fundo tem alíquota zero de IR para pessoa física, então a perda não abate imposto de outros ativos.

*DARF a pagar: R$ 155,00*
Código 6015 | vencimento 30/04/2026

Seu prejuízo acumulado zerou.
```

---

## Caso 3 — Herança, preço médio em três lotes e DARF pago em atraso

**O que testa:** custo pelo valor da partilha, preço médio ponderado, prejuízo do falecido que não se aproveita, multa abaixo do teto e juros Selic.

**Entrada**

| Data | Operação | Ativo | Tipo | Quantidade | Preço | Total |
|---|---|---|---|---|---|---|
| 05/02/2024 | Compra | ACAO3 | Ação | 100 | R$ 31,00 | R$ 3.100,00 |
| 16/06/2025 | Herança (valor de transferência na partilha) | ACAO3 | Ação | 300 | R$ 25,00 | R$ 7.500,00 |
| 20/10/2025 | Compra | ACAO3 | Ação | 100 | R$ 29,00 | R$ 2.900,00 |
| 15/01/2026 | Venda | ACAO3 | Ação | 500 | R$ 43,00 | R$ 21.500,00 |

Custos zero. IR retido: não informado. Prejuízo acumulado do herdeiro: zero. O falecido tinha R$ 4.000,00 de prejuízo acumulado em ações. Data do pagamento do DARF: 10/04/2026.

**Conta do imposto**

| Passo | Valor |
|---|---|
| Custo total | R$ 3.100,00 + R$ 7.500,00 + R$ 2.900,00 = R$ 13.500,00 |
| Preço médio | R$ 13.500,00 ÷ 500 = R$ 27,00 |
| Vendas de ações em janeiro/2026 | R$ 21.500,00, acima de R$ 20.000,00: sem isenção |
| Ganho | R$ 21.500,00 − R$ 13.500,00 = R$ 8.000,00 |
| Prejuízo do falecido | Não entra (Solução de Consulta Cosit nº 182/2024) |
| Imposto a 15% | R$ 1.200,00 |

**Conta do atraso**

| Passo | Valor |
|---|---|
| Vencimento | 27/02/2026, último dia útil de fevereiro |
| Início da contagem da multa | 02/03/2026, primeiro dia útil depois do vencimento |
| Dias de atraso até 10/04/2026 | 30 em março + 10 em abril = 40 dias |
| Multa | 40 × 0,33% = 13,20% (abaixo do teto de 20%) = R$ 158,40 |
| Juros | Selic de março/2026 (1,21%) + 1% do mês do pagamento = 2,21% = R$ 26,52 |

O percentual de 2,21% é o que o Sicalc da Receita devolve para vencimento em 02/2026 e pagamento em 04/2026, consultado em 12/11/2026.

**Resultado esperado**

| Campo | Valor |
|---|---|
| Imposto | R$ 1.200,00 |
| Multa | R$ 158,40 |
| Juros | R$ 26,52 |
| DARF pago em 10/04/2026 | **R$ 1.384,92** |
| Código | 6015 |
| Período de apuração | 01/2026 |
| Vencimento original | 27/02/2026 |

**O que não pôde ser compensado, e por quê**

| Item | Motivo |
|---|---|
| Prejuízo de R$ 4.000,00 do falecido | Prejuízo acumulado não passa para o herdeiro junto com as ações. |

**Texto esperado para WhatsApp**

```
Oi, [nome]! Fechei a conta da sua venda de ACAO3 em janeiro/2026.

• Venda: 500 ações a R$ 43,00 = R$ 21.500,00
• Preço médio: R$ 27,00. As 300 ações da herança entram pelo valor da partilha (R$ 25,00) e as outras 200 pelo que você pagou.
• Lucro: R$ 8.000,00
• Imposto (15%): R$ 1.200,00

O DARF venceu em 27/02/2026. Pagando em 10/04/2026:
• Multa (40 dias de atraso, 13,20%): R$ 158,40
• Juros (2,21%): R$ 26,52

*DARF a pagar: R$ 1.384,92*
Código 6015 | período 01/2026

O prejuízo que constava na declaração do falecido não pode ser usado por você: ele não se transfere com as ações.
```

---

## Casos que entram na suíte além destes três

| # | Caso | Resultado que o teste cobra |
|---|---|---|
| 4 | Imposto do mês abaixo de R$ 10,00 | Não gera DARF; soma no mês seguinte até passar de R$ 10,00 |
| 5 | Ações com prejuízo em mês de vendas até R$ 20 mil | Prejuízo fica guardado e abate ganho tributado depois |
| 6 | Venda parcial depois de duas compras | Preço médio não muda com a venda |
| 7 | Prejuízo de FII maior que o ganho do mês | Saldo segue para o mês seguinte, só para FII/Fiagro |
| 8 | Compra e venda do mesmo ativo no mesmo dia | Day trade a 20%, sem isenção, prejuízo separado |
| 9 | Ganho de novembro | Vencimento em 30/12, não 31/12 |
| 10 | Atraso longo | Multa travada em 20% |
| 11 | Pagamento em atraso com Selic de dois meses | 3,30% para vencimento 02/2026 e pagamento 05/2026, igual ao Sicalc |
| 12 | Venda de mais cotas do que há em estoque | Ferramenta para e avisa, não calcula |
