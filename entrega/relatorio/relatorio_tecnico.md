# Agendamento de Consultas/Atendimentos como Problema de Satisfação de Restrições

**[PREENCHER] Universidade — Curso — Disciplina de Introdução a Inteligência Artificial**
**Integrantes:** [PREENCHER nomes e RAs]
**Professor:** [PREENCHER]
**Data:** [PREENCHER]

---

## 1. Introdução

Clínicas, escritórios de consultoria/advocacia, assistências técnicas e
serviços de atendimento acadêmico compartilham um mesmo problema
operacional: distribuir clientes entre profissionais, horários e salas
disponíveis, respeitando especialidades e evitando conflitos de agenda.
Esse problema (Tema 9 da especificação do trabalho) foi modelado como um
**Problema de Satisfação de Restrições (PSR)** e resolvido com duas
versões de um algoritmo de busca com retrocesso (*backtracking*): uma
versão simples, sem heurísticas, e uma versão aprimorada, com as
heurísticas MRV (Minimum Remaining Values), Forward Checking e LCV
(Least Constraining Value). Este relatório descreve o problema, a
modelagem, os algoritmos implementados, os experimentos realizados e a
análise dos resultados.

## 2. Descrição do problema real

Uma organização de atendimentos (clínica, consultoria, escritório
jurídico, assistência técnica ou atendimento acadêmico) recebe pedidos de
atendimento de clientes. Cada pedido exige um serviço específico, que só
pode ser realizado por profissionais com a especialidade correspondente,
em um horário compatível com a disponibilidade do cliente, do
profissional escolhido e de uma sala. O objetivo é encontrar uma
atribuição completa — profissional, horário e sala para cada atendimento
solicitado — que não viole nenhuma das restrições de disponibilidade nem
cause dois atendimentos simultâneos para o mesmo profissional, cliente ou
sala.

## 3. Modelagem como PSR

**PSR = Variáveis + Domínios + Restrições.**

- **Variáveis**: cada atendimento solicitado (`Atendimento`, identificado
  por um id e pelo cliente que o solicitou).
- **Domínios**: para cada atendimento, o conjunto de combinações
  `(profissional, horário de início, sala)` em que o profissional possui
  a especialidade exigida pelo cliente e profissional, cliente e sala
  estão disponíveis em todos os slots que o atendimento ocupará
  (`modelo/dominio.py::gerar_dominio`). O tempo é discretizado em slots
  atômicos (grade `dias × slots_por_dia`); um atendimento ocupa
  `duracao_slots` slots consecutivos.
- **Restrições** (`modelo/restricoes.py`), as 5 exigidas pela
  especificação do Tema 9:
  1. o profissional deve possuir a especialidade necessária;
  2. um profissional não atende duas pessoas simultaneamente;
  3. um cliente não tem dois atendimentos simultâneos;
  4. uma sala não é usada por dois atendimentos simultaneamente;
  5. a disponibilidade de profissional, cliente e sala é respeitada.

  As restrições 1 e 5 já são garantidas na própria geração do domínio
  (um valor inconsistente com elas nunca chega a ser gerado); as
  restrições 2, 3 e 4 são dinâmicas — dependem de quais outros
  atendimentos já foram atribuídos — e por isso são checadas a cada
  tentativa de atribuição, na função `consistente(...)`.

  "Tipo de sala" é tratado pela especificação como opcional ("quando
  necessário") e não está entre as 5 restrições obrigatórias, então não
  foi modelado como restrição adicional — todas as salas são
  intercambiáveis nesta implementação.

## 4. Algoritmos implementados

### 4.1 Backtracking simples (`algoritmos/backtracking_simples.py`)

Busca com retrocesso clássica: percorre os atendimentos na ordem em que
aparecem na instância (ordem fixa) e, para cada um, tenta os valores do
domínio na ordem em que foram gerados (ordem fixa). Quando um valor é
consistente com as atribuições já feitas, ele é fixado e a busca avança
recursivamente; quando nenhum valor do domínio funciona, a função
retorna sem solução e a atribuição anterior é desfeita (retrocesso). Não
usa nenhuma heurística de ordenação nem propagação de restrições.

### 4.2 Backtracking aprimorado (`algoritmos/backtracking_aprimorado.py`)

Mesma estrutura de busca, substituindo a ordem fixa por três técnicas:

- **MRV (Minimum Remaining Values)** — obrigatória: a cada passo, escolhe
  para atribuir o atendimento não-atribuído com o **menor domínio
  restante**, em vez de seguir a ordem de entrada. Intuição: atendimentos
  mais restritos têm mais chance de falhar, então é melhor descobrir isso
  cedo, antes de investir esforço em atendimentos mais flexíveis.
- **Forward Checking** — obrigatória: depois de cada atribuição, remove
  dos domínios dos atendimentos ainda não-atribuídos os valores que se
  tornaram inconsistentes com essa atribuição. Se algum domínio ficar
  vazio, o ramo é podado imediatamente, sem esperar chegar até aquele
  atendimento para descobrir a falha.
- **LCV (Least Constraining Value)** — estratégia extra escolhida (a
  especificação exige pelo menos uma entre Degree Heuristic, LCV e
  propagação adicional): ao escolher o valor para o atendimento
  selecionado, tenta primeiro o que **elimina menos opções** dos domínios
  dos demais atendimentos não-atribuídos, deixando a árvore de busca mais
  aberta para as decisões seguintes.

A função `incompativel(...)` (`modelo/restricoes.py`) é reaproveitada
tanto pelo Forward Checking quanto pelo cálculo do custo do LCV: ela
verifica, usando as mesmas restrições 2/3/4 já testadas isoladamente, se
duas atribuições hipotéticas para dois atendimentos diferentes podem
coexistir.

### 4.3 Métricas

Ambas as versões compartilham a mesma contabilidade
(`algoritmos/metricas.py`), essencial para uma comparação justa:
`nos_explorados` (uma chamada da função de busca), `atribuicoes` (um
valor aceito e fixado) e `backtracks` (uma atribuição desfeita). Um
parâmetro opcional `limite_nos` interrompe a busca após N nós — necessário
porque o backtracking simples não converge em tempo hábil nas instâncias
maiores (ver Seção 6).

## 5. Dados e instâncias de teste

Não existe uma base pública para "atribuição profissional+horário+sala
com disponibilidades" equivalente ao Tema 9, então os dados são gerados
sinteticamente (`dados/geracao.py`), com seed fixa para reprodutibilidade.
O gerador primeiro planta uma solução válida (aloca cada atendimento sem
conflitos) e só depois monta as disponibilidades de cada
profissional/cliente/sala como a união dos horários usados por essa
solução com uma folga aleatória — isso garante que toda instância gerada
tem pelo menos uma solução, condição necessária para a comparação de
desempenho da Seção 8 ter sentido (comparar "tempo até encontrar uma
solução" só é significativo quando ela existe).

Três tamanhos foram gerados (seed=42), respeitando os mínimos da
especificação:

| Instância | Atendimentos | Clientes | Profissionais | Salas | Grade |
|---|---|---|---|---|---|
| Pequena | 10 | 8 | 6 | 3 | 1 dia × 10 slots |
| Média | 30 | 22 | 8 | 4 | 3 dias × 10 slots |
| Grande | 60 | 45 | 11 | 4 | 5 dias × 10 slots |

A instância grande usa uma disponibilidade extra menor (mais "aperto")
que as demais, para pressionar o algoritmo por menor folga de recursos,
não só por ter mais atendimentos.

## 6. Experimentos e resultados

Cada instância foi resolvida pelas duas versões, com limite de 200.000
nós (`avaliacao/resultados/comparacao.csv`):

| Instância | Método | Tempo (s) | Atribuições | Backtracks | Nós explorados | Resolvida |
|---|---|---|---|---|---|---|
| Pequena (10) | Simples | 0,0002 | 10 | 0 | 11 | Sim |
| Pequena (10) | Aprimorado | 0,0032 | 10 | 0 | 11 | Sim |
| Média (30) | Simples | 5,76 | 200.100 | 200.100 | 200.000 (limite) | **Não** |
| Média (30) | Aprimorado | 0,03 | 30 | 0 | 31 | Sim |
| Grande (60) | Simples | 8,37 | 200.471 | 200.471 | 200.000 (limite) | **Não** |
| Grande (60) | Aprimorado | 0,21 | 66 | 6 | 62 | Sim |

Um segundo experimento (`avaliacao/experimento_densidade.py`,
`avaliacao/resultados/densidade.csv`) isola o efeito da disponibilidade
(densidade de restrições) do efeito do tamanho da instância: fixa o
tamanho em 30 atendimentos e varia só a probabilidade de disponibilidade
extra (0,55 → 0,40 → 0,25 → 0,15):

| Disponibilidade | Método | Tempo (s) | Backtracks | Nós | Resolvida |
|---|---|---|---|---|---|
| 0,55 | Simples | 0,002 | 0 | 31 | Sim |
| 0,55 | Aprimorado | 0,83 | 0 | 31 | Sim |
| 0,40 | Simples | 6,63 | 200.339 | 200.000 (limite) | **Não** |
| 0,40 | Aprimorado | 0,21 | 0 | 31 | Sim |
| 0,25 | Simples | 5,49 | 200.100 | 200.000 (limite) | **Não** |
| 0,25 | Aprimorado | 0,03 | 0 | 31 | Sim |
| 0,15 | Simples | 6,01 | 200.065 | 200.000 (limite) | **Não** |
| 0,15 | Aprimorado | 0,01 | 0 | 31 | Sim |

## 7. Discussão (respostas às perguntas da Seção 11)

**O backtracking simples conseguiu resolver todas as instâncias?** Não.
Resolveu só a pequena (11 nós, instantâneo). Nas instâncias média e
grande não convergiu em 200.000 nós; um teste à parte com 3.000.000 de
nós na instância média (76s) também não encontrou solução, o que indica
explosão combinatória real, não um limite mal calibrado.

**Quantos retrocessos foram necessários?** Pequena: 0 em ambas as
versões. Média e grande: o simples atinge o teto de ~200.000 retrocessos
sem convergir; o aprimorado precisa de 0 (média) e apenas 6 (grande).

**MRV reduziu o espaço de busca?** Sim, de forma decisiva: na grande, os
nós explorados caem de >200.000 (sem solução) para 62 (com solução). No
experimento de densidade, o aprimorado manteve exatamente 31 nós/0
retrocessos nas 4 disponibilidades testadas, enquanto o simples só
resolveu a mais folgada.

**Forward Checking produziu melhoria?** Sim. Um cenário controlado nos
testes automatizados (`testes/conftest.py::instancia_conflituosa`) isola
o efeito: o simples precisa de exatamente 1 retrocesso porque atribui um
atendimento "largo" antes de descobrir que isso inviabiliza um
atendimento "estreito"; o aprimorado, com forward checking, elimina esse
valor do domínio do largo assim que o estreito é escolhido primeiro (via
MRV) — 0 retrocessos.

**Qual foi a diferença entre as versões?** O simples só percebe um
conflito quando chega ao atendimento afetado, retrocedendo por uma
cadeia de decisões já tomadas — custo que cresce rapidamente com o
tamanho da instância. O aprimorado escolhe primeiro os atendimentos mais
restritos, evita valores mais restritivos e poda domínios futuros a cada
passo, descobrindo becos sem saída muito mais cedo: mesmo resultado com
3 a mais de 3000 vezes menos nós/retrocessos. Uma diferença adicional
aparece no tempo (não no número de nós): no experimento de densidade, o
aprimorado gastou 0,83s com disponibilidade 0,55 mas só 0,01–0,21s nas
disponibilidades menores, sempre explorando os mesmos 31 nós — domínios
maiores tornam MRV/Forward Checking/LCV mais caros de calcular por nó,
mesmo sem mudar o número de nós.

**Como o aumento do número de restrições afetou o problema?** O
experimento de densidade mostra uma transição abrupta para o simples:
baixar a disponibilidade de 0,55 para 0,40 já é suficiente para ele
deixar de convergir em 200.000 nós. O aprimorado, no mesmo intervalo,
manteve 31 nós/0 retrocessos nas 4 disponibilidades — as heurísticas de
antecipação absorveram o aperto das restrições sem precisar explorar mais
estados.

## 8. Limitações

- O backtracking simples é impraticável para instâncias médias/grandes
  dentro de um orçamento de nós razoável para demonstração — isso é
  esperado (é uma busca completa sem poda) e é justamente o que o
  experimento evidencia, mas significa que não há um "tempo de
  referência" real para o simples nessas instâncias, só o comportamento
  até o limite.
- O custo por nó do LCV cresce com o tamanho dos domínios (ver
  experimento de densidade), então em instâncias com disponibilidade
  muito alta e poucos atendimentos conflitantes o aprimorado pode gastar
  mais tempo de parede que um backtracking simples que "acerta de
  primeira" — o ganho do aprimorado está no número de nós/retrocessos,
  não incondicionalmente no tempo de parede em qualquer cenário.
- "Tipo de sala" não foi modelado como restrição (ver Seção 3).
- A geração de dados garante que existe pelo menos uma solução na
  instância original, mas edições manuais feitas durante a demonstração
  (Seção 15) podem tornar a instância inviável; o programa trata esse
  caso relatando "nenhuma solução encontrada" em vez de travar, mas isso
  não é o mesmo que garantir viabilidade após qualquer edição.

## 9. Conclusão

A modelagem do agendamento de atendimentos como PSR permitiu comparar
diretamente, com métricas objetivas, o efeito de heurísticas de busca
sobre um problema real de escalonamento. Os experimentos confirmam a
expectativa teórica: MRV, Forward Checking e LCV reduzem drasticamente o
espaço de busca explorado (de dezenas de milhares/centenas de milhares de
nós, sem solução, para dezenas de nós, com solução), tornando viável
resolver em frações de segundo instâncias que o backtracking simples não
consegue resolver dentro de um orçamento computacional razoável.
