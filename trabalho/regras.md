# Regras fiscais e de produto

Este arquivo guarda as regras que as ferramentas de `trabalho/` aplicam. Cada regra traz a fonte oficial, o link e a data. Onde não achei fonte, está escrito **não achei**. Nenhuma ferramenta é programada antes de a seção dela ser aprovada aqui.

| Ferramenta | Situação |
|---|---|
| /darf | **Aguardando aprovação** (nada programado) |
| /ipca-curva, /regressiva, /comparar | Ainda não pesquisadas |

---

# /darf

Pesquisa feita em 11 e 12/11/2026. Vale para pessoa física residente no Brasil, em operações no mercado à vista da B3 com ação, BDR, FII, Fiagro e FI-Infra.

## 1. Resumo por tipo de ativo

| Tipo | Grupo de apuração | Alíquota sobre o ganho | Isenção de R$ 20 mil/mês | Prejuízo compensa com |
|---|---|---|---|---|
| Ação | Geral | 15% (day trade: 20%) | Sim, só em operação comum | ação e BDR, comum com comum e day trade com day trade |
| BDR | Geral | 15% (day trade: 20%) | Não | ação e BDR, comum com comum e day trade com day trade |
| FII | FII/Fiagro | 20% | Não | FII e Fiagro |
| Fiagro | FII/Fiagro | 20% | Não | FII e Fiagro |
| FI-Infra | Infraestrutura | 0% | Não se aplica | nada |

Os grupos são os mesmos da calculadora oficial da Receita (ReVar): Geral, FII/Fiagro, Fundos de Infraestrutura e Isentos [F4].

## 2. Preço médio e resultado

1. **Custo de aquisição** é a média ponderada dos custos unitários [F1, art. 58; F2, pergunta 719].
2. **Custos da operação** (corretagem, emolumentos, taxa de liquidação) somam ao preço na compra e diminuem o valor na venda [F2, pergunta 708; F3]. Taxa de custódia também é dedutível, informada à parte; juros de margem, ISS, plataformas e o imposto pago na herança não são [F4].
3. **Venda não altera o preço médio**; só compra altera [F4].
4. **Corretoras diferentes**: o preço médio é um só por ativo, somando todas as corretoras [F2, pergunta 720].
5. **Data que vale** é a do pregão, não a da liquidação [F2, pergunta 745; F4].
6. **Ganho líquido do mês** é a soma dos resultados das vendas do mês, por grupo [F1, art. 56, § 3º; F2, pergunta 704]. O imposto é apurado mês a mês e não entra no ajuste anual [F2, pergunta 731].

## 3. Ativo recebido por herança

1. O custo é o **valor pelo qual o ativo foi transferido** na partilha, ou seja, o que consta na coluna "Valor de Transferência" da Declaração Final de Espólio [F8, art. 23, § 4º; F2, perguntas 609 e 611; F1, art. 58, § 3º, I].
2. Esse valor pode ser o da última declaração do falecido ou o de mercado. A escolha é feita ativo por ativo e vale para todos os herdeiros daquele ativo. Se for a mercado, o espólio paga 15% sobre a diferença; isso é ganho de capital do espólio e **fica fora do /darf** [F8, art. 23, § 1º; F2, pergunta 609].
3. **Meação** do cônjuge sobrevivente não tem essa escolha: entra pelo valor da última declaração do falecido [F2, pergunta 610].
4. A data de aquisição é a do falecimento [F2, pergunta 609, d].
5. **Prejuízo acumulado do falecido não passa para o herdeiro** [F12].
6. Na ferramenta, a herança entra no preço médio como uma compra pelo valor de transferência, com custo operacional zero.

## 4. Alíquotas

1. Geral, operação comum: **15%** [F5, art. 2º, II; F1, art. 57].
2. Geral, day trade: **20%** [F5, art. 2º, I; F1, art. 65, § 11].
3. FII: **20%** [F6, art. 18; F1, art. 37]. Fiagro: **20%** [F6, art. 20-D]. Não há alíquota diferente para day trade nesse grupo [F4].
4. FI-Infra (fundo do art. 3º da Lei 12.431): **0%** para pessoa física, inclusive sobre o ganho na venda da cota [F7, art. 3º, § 1º, I, b, e § 2º-A; F1, art. 34, § 1º, I, e § 3º]. A alíquota zero depende de o fundo cumprir o enquadramento da lei (85% em ativos de infraestrutura); a ferramenta não verifica o regulamento, você informa o tipo.

## 5. Isenção de R$ 20.000 por mês

1. É isento o ganho líquido em **ações, no mercado à vista**, quando o **total das vendas de ações no mês** for igual ou inferior a R$ 20.000,00 [F5, art. 3º, I; F1, art. 59, I; F2, pergunta 707].
2. O limite olha o valor vendido, não o lucro, e soma todas as corretoras. Cônjuges apuram separado e cada um tem o seu limite [F1, art. 59, § 3º; F2, pergunta 737].
3. O mês é o do pregão [F2, pergunta 745].
4. **Não tem isenção**: day trade [F1, art. 59, § 2º, I]; BDR [F10]; FII e Fiagro (a isenção é só para ações) [F5, art. 3º, I]; ETF e bônus de subscrição, que também não entram na soma do limite [F11].
5. Venda de BDR, FII, Fiagro e FI-Infra **não conta** para os R$ 20 mil, porque o limite é "para o conjunto de ações" [F5, art. 3º, I].
6. **Ganho isento não consome prejuízo acumulado.** A norma dispensa informar as vendas isentas na apuração, "exceto no caso de pretender compensar as perdas apuradas" [F1, art. 59, § 1º; F2, pergunta 729], e o ReVar separa o grupo Isentos do grupo Geral [F4]. Ver item 12.4.
7. **Prejuízo em mês de vendas até R$ 20 mil é aproveitável**: compensa ganhos tributados do mesmo mês ou dos seguintes [F1, art. 59, § 1º].

## 6. Compensação de prejuízo

1. Geral, operação comum: compensa com ganho de operação comum do grupo Geral, no mesmo mês ou nos seguintes, sem prazo, inclusive em anos seguintes [F1, art. 64; F2, perguntas 709 e 711].
2. Day trade só compensa com day trade [F1, art. 64 e art. 65, § 10; F2, pergunta 709].
3. FII: "as perdas incorridas na alienação de cotas de fundo de investimento imobiliário só podem ser compensadas com ganhos auferidos na alienação de cotas de fundo da mesma espécie" [F1, art. 37, § 2º; F13].
4. FII e Fiagro ficam no **mesmo grupo de prejuízo** no ReVar, sem separar comum de day trade [F4]. Ver item 12.2.
5. FI-Infra: prejuízo não compensa nada e ganho não absorve prejuízo de ninguém. Ver item 12.3.
6. Prejuízo de um mês **não volta** para abater ganho de mês anterior [F2, pergunta 710].
7. Para usar prejuízo de anos anteriores, ele precisa estar informado na declaração anual, no mês em que ocorreu e nos seguintes [F2, pergunta 711]. A ferramenta pergunta o saldo por grupo e avisa disso.
8. Prejuízo de venda fora de bolsa não compensa ganho em bolsa [F2, pergunta 717].

### O que a ferramenta vai dizer que não pode ser compensado

| Situação | Motivo |
|---|---|
| Prejuízo em FII ou Fiagro contra ganho em ação ou BDR, e o contrário | Grupos diferentes [F1, art. 37, § 2º; F13] |
| Prejuízo em FI-Infra contra qualquer ganho | Alíquota zero, fora da apuração de ganho líquido [F4; F1, art. 34] |
| Prejuízo de day trade contra ganho de operação comum, e o contrário | Só com a mesma espécie [F1, art. 64] |
| Prejuízo acumulado contra ganho isento (ações até R$ 20 mil) | O ganho isento fica fora da apuração; o prejuízo segue inteiro [F1, art. 59, § 1º] |
| Prejuízo de hoje contra ganho de mês passado | Apuração é mensal [F2, pergunta 710] |
| Prejuízo do falecido usado pelo herdeiro | Vedado [F12] |

## 7. Day trade

1. É a operação iniciada e encerrada no mesmo dia, com o mesmo ativo, na mesma corretora [F1, art. 65, § 1º, I; F2, pergunta 705].
2. O resultado casa, pela ordem, a primeira compra com a primeira venda do dia, e assim por diante [F1, art. 65, § 3º].
3. O estoque de dias anteriores não entra na conta do day trade [F1, art. 65, § 2º] e o day trade não altera o estoque [F4].
4. Perdas de day trade do mesmo dia se compensam entre si [F1, art. 65, § 4º].
5. Tem retenção de 1% na fonte sobre o ganho, que pode ser abatida do imposto do mês ou dos meses seguintes, só até dezembro do mesmo ano [F1, art. 65, caput e § 8º; F2, perguntas 712, 714 e 715].

## 8. Imposto retido na fonte ("dedo-duro")

1. Operação comum: 0,005% sobre o valor da venda, dispensado quando for R$ 1,00 ou menos [F5, art. 2º, §§ 1º e 4º; F1, art. 63].
2. Pode ser abatido do imposto do mês, dos meses seguintes ou na declaração anual [F1, art. 63, § 8º].
3. Na ferramenta, o valor retido é **informado por você** a partir da nota de corretagem. Sem valor informado, nada é abatido e a saída avisa.

## 9. DARF

1. Código **6015** [F2, pergunta 730; F3; F16].
2. Vencimento: **último dia útil do mês seguinte** ao da apuração [F1, art. 56, § 5º; F2, pergunta 730; F3]. FII e Fiagro seguem o mesmo procedimento [F1, art. 37, § 1º, I; F6, arts. 18, II, e 20-D, II].
3. **Abaixo de R$ 10,00 não se paga**: o valor é somado ao imposto do mesmo código dos meses seguintes até chegar a R$ 10,00, e então vence no prazo do último mês [F9, art. 68; F4].
4. A ferramenta soma Geral e FII/Fiagro num DARF só por mês. Não achei frase oficial dizendo "um DARF só"; o que as fontes dão é o mesmo código, o mesmo vencimento e o mínimo de R$ 10,00 medido por código e por período [F9, art. 68, § 1º].
5. O cálculo serve para conferir e explicar. A emissão do documento continua sendo pelo Sicalc ou pelo ReVar.

## 10. Como a ferramenta acha o último dia útil

1. Tira sábados, domingos e os feriados nacionais da lista da Anbima [F17].
2. Em dezembro, tira também o último dia útil do ano, que não tem atendimento bancário ao público [F17, nota 3].
3. **Conferido contra a Agenda Tributária da Receita** [F16]: a regra deu a mesma data em que a Receita lista o código 6015 em 21 meses (03/2024, 05/2024, 12/2024, 01 a 10/2025, 12/2025 e 01 a 07/2026). Exemplos: 28/03/2024 (dia 29 foi Sexta-feira Santa), 30/12/2024 e 30/12/2025.
4. Feriado estadual ou municipal não está na lista. Não afeta nenhum fim de mês que eu tenha conferido.

## 11. Pagamento em atraso

1. **Multa de mora**: 0,33% por dia de atraso, limitada a 20% [F9, art. 61, caput e § 2º]. A contagem começa no primeiro dia útil depois do vencimento e termina no dia do pagamento [F14].
2. **Juros de mora**: soma da Selic mensal do mês seguinte ao do vencimento até o mês anterior ao do pagamento, mais 1% no mês do pagamento. Pago dentro do próprio mês do vencimento, não há juros [F9, art. 61, § 3º, e art. 5º, § 3º; F14].
3. Multa e juros incidem sobre o imposto devido, cada um separadamente [F14].
4. **Selic usada**: a do Sicalc, da própria Receita [F15]. Reserva, se o Sicalc estiver fora do ar: série 4390 do Banco Central [F15]. As duas coincidem nos 141 meses de 02/2015 a 10/2026 que comparei. Para períodos anteriores a 2015 a ferramenta só usa o Sicalc, porque a soma desde 1995 difere entre as duas (441,26 na Receita, 446,17 no Banco Central).

## 12. Não achei

1. **Units e a isenção de R$ 20 mil.** Não achei posição oficial. O que existe: a Receita lê a isenção ao pé da letra, só para "ativos da espécie ações" [F11], negou-a ao BDR por ser certificado de depósito [F10] e lista Units como categoria separada de ações no ReVar [F4]. Nenhuma dessas fontes fala de Unit e isenção.
2. **Prejuízo de FII contra ganho de Fiagro.** Não achei instrução normativa nem solução de consulta. A norma de FII fala em "fundo da mesma espécie" [F1, art. 37, § 2º] e é anterior ao Fiagro. O manual do ReVar manda informar os prejuízos de FII e de Fiagro no mesmo grupo [F4].
3. **Prejuízo em FI-Infra para pessoa física.** Não achei regra expressa. Para pessoa jurídica a norma veda a dedução [F1, art. 34, § 12]. O ReVar trata o grupo como alíquota zero e diz que os resultados "são mais gerenciais do que tributários", sem campo de prejuízo acumulado [F4].
4. **Ganho isento e prejuízo acumulado.** Não achei frase oficial dizendo, com todas as letras, que o ganho isento não abate o prejuízo acumulado. A regra do item 5.6 é a leitura do art. 59, § 1º, somada à separação de grupos do ReVar.
5. **Arredondamento** do imposto, da multa e dos juros em centavos. Não achei regra. Os três casos de teste fecham em centavos exatos.
6. **Prazo quando a venda é nos dois últimos pregões do mês.** As fontes divergem. A pergunta 745 diz que o prazo conta do mês da liquidação financeira [F2]. A página de cálculo e o ReVar contam do mês do pregão [F3; F4].
7. **Agenda Tributária de agosto a novembro de 2026.** Não localizei as páginas; os vencimentos desses meses saem da regra do item 10, sem conferência.
8. **Texto das leis no Planalto.** O site recusa acesso automatizado. Li as leis no texto atualizado da Câmara dos Deputados.

## 13. Decisões que são suas

| # | Decisão | O que proponho |
|---|---|---|
| D1 | Unit tem isenção de R$ 20 mil? | Tratar como **sem isenção** e avisar na saída. É a leitura que não deixa imposto por pagar. |
| D2 | Prejuízo de FII compensa ganho de Fiagro? | **Sim**, como faz o ReVar. |
| D3 | Venda nos dois últimos pregões do mês: prazo pelo pregão ou pela liquidação? | **Pelo pregão**, que vence antes, com aviso na saída citando a pergunta 745. |
| D4 | Day trade: calcular ou só detectar e parar? | **Calcular**, pela regra do item 7. A ferramenta pergunta se foi na mesma corretora. |
| D5 | Arredondamento | Ao centavo mais próximo, com aviso de que o Sicalc pode diferir em R$ 0,01. |
| D6 | Prejuízo em FI-Infra | **Não compensa e não acumula**, como no ReVar. |
| D7 | Ganho isento abate prejuízo acumulado? | **Não abate**, pela leitura do item 5.6. |

## 14. Fora do /darf nesta versão

Opções, termo, futuro, ouro, aluguel de ações, ETF, venda a descoberto, operações fora de bolsa, direitos e bônus de subscrição, bonificação, desdobramento, grupamento, amortização de cotas e FIP-IE. Em bonificação, desdobramento e afins, você informa a quantidade e o custo já ajustados.

## 15. Mudanças recentes que conferi

1. **MP 1.303/2025** (17,5% e limite trimestral): perdeu a vigência em 08/10/2025 sem votação e sem decreto legislativo. Não vale [F19].
2. **Lei 15.270/2025**: cria a tributação mínima anual para quem recebe mais de R$ 600 mil por ano, a partir do ano-calendário de 2026. Os ganhos líquidos de bolsa entram nessa base. Não muda o DARF mensal e fica fora da ferramenta [F18].
3. **Lei Complementar 224/2025** (corte de benefícios fiscais): alcança PIS/Cofins, IRPJ, CSLL, II, IPI e contribuição patronal. Não alcança o IR da pessoa física [F20].
4. **IN RFB 1.585/2015** segue vigente; a última alteração é de 2019 [F1]. Busquei no sistema de normas da Receita e não encontrei ato de 2026 mudando alíquota, isenção ou compensação em bolsa.

## 16. Fontes

| # | Fonte | Data do documento | Link |
|---|---|---|---|
| F1 | IN RFB nº 1.585/2015 | DOU 02/09/2015; alterada em 2016, 2017 e 2019; vigente | https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494 |
| F2 | Receita, Perguntas e Respostas IRPF 2026 (ano-calendário 2025), versão 1.0 | 23/04/2026 | https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/perguntas-e-respostas/dirpf/p-r-irpf-2026-v1-00-2026-04-23.pdf |
| F3 | Receita, "Cálculo e Pagamento do Imposto" (bolsa de valores) | Atualizada em 19/11/2025 | https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/bolsa-de-valores-1/calculo-e-pagamento-do-imposto |
| F4 | Receita, Manual de utilização do ReVar | Atualizado em 20/12/2024 | https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/manual |
| F5 | Lei 11.033/2004, arts. 2º e 3º (texto atualizado, Câmara) | 21/12/2004 | https://www2.camara.leg.br/legin/fed/lei/2004/lei-11033-21-dezembro-2004-535177-normaatualizada-pl.html |
| F6 | Lei 8.668/1993, arts. 18, 19, 20-C e 20-D (texto atualizado, Câmara) | 25/06/1993; Fiagro incluído pela Lei 14.130/2021 | https://www2.camara.leg.br/legin/fed/lei/1993/lei-8668-25-junho-1993-350597-normaatualizada-pl.html |
| F7 | Lei 12.431/2011, art. 3º (texto atualizado, Câmara) | 24/06/2011; alterada pela Lei 14.801/2024 | https://www2.camara.leg.br/legin/fed/lei/2011/lei-12431-24-junho-2011-610836-normaatualizada-pl.html |
| F8 | Lei 9.532/1997, art. 23 (texto atualizado, Câmara) | 10/12/1997 | https://www2.camara.leg.br/legin/fed/lei/1997/lei-9532-10-dezembro-1997-372088-normaatualizada-pl.html |
| F9 | Lei 9.430/1996, arts. 5º, § 3º, 61 e 68 (texto atualizado, Câmara) | 27/12/1996 | https://www2.camara.leg.br/legin/fed/lei/1996/lei-9430-27-dezembro-1996-367738-normaatualizada-pl.html |
| F10 | Solução de Consulta Cosit nº 39/2022 (BDR) | DOU 05/10/2022 | https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=126441 |
| F11 | Solução de Consulta Cosit nº 145/2021 (ETF e bônus de subscrição) | DOU 27/09/2021 | https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=120689 |
| F12 | Solução de Consulta Cosit nº 182/2024 (prejuízo do espólio) | DOU 26/06/2024 | https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=138932 |
| F13 | Solução de Consulta Cosit nº 223/2018 (FII) | DOU 19/12/2018 | https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=97453 |
| F14 | Receita, "Como calcular multa de mora" e "Como calcular juros de mora" | Atualizadas em 22/09/2020 e 22/10/2025 | https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/pagamentos-e-parcelamentos/pagamento-em-atraso |
| F15 | Receita, Sicalc, consulta de taxa Selic; Banco Central, SGS série 4390 | Consulta em 12/11/2026 (última Selic: 10/2026, 1,07%) | https://sicalc.receita.fazenda.gov.br/sicalc/selic/consulta e https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json |
| F16 | Receita, Agenda Tributária | Páginas diárias de 2024 a 2026 | https://www.gov.br/receitafederal/pt-br/assuntos/agenda-tributaria |
| F17 | Anbima, feriados nacionais 2001–2099 | Arquivo salvo em 22/12/2023 | https://www.anbima.com.br/feriados/arqs/feriados_nacionais.xls |
| F18 | Lei 15.270/2025, que inclui o art. 16-A na Lei 9.250/1995 (Câmara) | 26/11/2025 | https://www2.camara.leg.br/legin/fed/lei/2025/lei-15270-26-novembro-2025-798354-publicacaooriginal-177117-pl.html |
| F19 | Congresso Nacional, tramitação da MP 1.303/2025 | Vigência encerrada em 08/10/2025 | https://www.congressonacional.leg.br/materias/medidas-provisorias/-/mpv/169059 |
| F20 | Lei Complementar 224/2025 (Câmara) | 26/12/2025 | https://www2.camara.leg.br/legin/fed/leicom/2025/leicomplementar-224-26-dezembro-2025-798608-publicacaooriginal-177629-pl.html |

Todas as fontes foram abertas e lidas em 11 e 12/11/2026.
