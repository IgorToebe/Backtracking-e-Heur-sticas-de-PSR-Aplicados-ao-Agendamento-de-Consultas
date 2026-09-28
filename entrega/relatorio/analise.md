# Análise dos resultados

Dados: `avaliacao/resultados/comparacao.csv` (3 tamanhos × 2 métodos, seed=42,
limite de 200.000 nós) e `avaliacao/resultados/densidade.csv` (tamanho fixo
= 30 atendimentos, variando só a disponibilidade extra).

## Tabela principal

| Instância | Método     | Tempo (s) | Atribuições | Backtracks | Nós explorados | Resolvida |
|-----------|------------|-----------|-------------|------------|-----------------|-----------|
| Pequena (10) | Simples    | 0,0002 | 10     | 0       | 11     | Sim |
| Pequena (10) | Aprimorado | 0,0032 | 10     | 0       | 11     | Sim |
| Média (30)   | Simples    | 5,76   | 200.100 | 200.100 | 200.000 (limite) | **Não** |
| Média (30)   | Aprimorado | 0,03   | 30     | 0       | 31     | Sim |
| Grande (60)  | Simples    | 8,37   | 200.471 | 200.471 | 200.000 (limite) | **Não** |
| Grande (60)  | Aprimorado | 0,21   | 66     | 6       | 62     | Sim |

## 1. O Backtracking simples conseguiu resolver todas as instâncias?

Não. Resolveu apenas a instância pequena (11 nós, instantâneo). Nas
instâncias média e grande, não encontrou solução dentro do limite de
200.000 nós. Para confirmar que não era só um limite artificialmente
baixo, a instância média foi testada à parte com um limite de 3.000.000
de nós: em 76 segundos, ainda não havia solução — evidência de explosão
combinatória real, não de um teto de segurança mal calibrado.

## 2. Quantos retrocessos foram necessários?

Pequena: 0 em ambas as versões (instância folgada o bastante para não
exigir nenhum). Média e grande: o simples atinge o teto de ~200.000
retrocessos sem convergir; o aprimorado precisa de **0** retrocessos na
média e apenas **6** na grande.

## 3. MRV reduziu o espaço de busca?

Sim, de forma decisiva. Na instância grande, nós explorados caíram de
mais de 200.000 (sem solução) para 62 (com solução). No experimento de
densidade, o aprimorado (MRV+FC+LCV) manteve exatamente 31 nós e 0
retrocessos nas 4 disponibilidades testadas (0,55 a 0,15), enquanto o
simples só resolveu a disponibilidade mais folgada (0,55) e não convergiu
nas outras três, mesmo com o mesmo teto de nós.

## 4. Forward Checking produziu melhoria?

Sim. No cenário controlado dos testes automatizados
(`instancia_conflituosa`, ver `testes/conftest.py`), construído
propositalmente para expor a diferença: o simples precisa de exatamente
**1** retrocesso porque atribui um atendimento "largo" antes de descobrir
que isso inviabiliza um atendimento "estreito"; o aprimorado, com forward
checking, elimina esse valor do domínio do atendimento largo assim que o
estreito é escolhido primeiro (via MRV) — 0 retrocessos. Esse mesmo efeito,
em escala maior, explica os 6 retrocessos (contra >200.000) na instância
grande real.

## 5. Qual foi a diferença entre as versões?

O simples tenta valores em ordem fixa e só percebe um conflito quando
chega ao atendimento afetado, retrocedendo por uma cadeia de decisões já
tomadas — custo que cresce rapidamente com o tamanho da instância. O
aprimorado escolhe primeiro os atendimentos mais restritos (MRV), evita
valores que eliminam mais opções dos demais (LCV) e, a cada atribuição,
já poda os domínios futuros (Forward Checking), descobrindo becos sem
saída muito mais cedo. Na prática: mesmo resultado (agenda válida) com
3 a mais de 3000 vezes menos nós/retrocessos.

Uma diferença adicional aparece no *tempo* (não no número de nós): no
experimento de densidade, o aprimorado gastou 0,83s com disponibilidade
0,55 mas só 0,01–0,21s nas disponibilidades menores, apesar de explorar
sempre os mesmos 31 nós. Isso ocorre porque domínios maiores (mais
disponibilidade) tornam MRV/Forward Checking/LCV mais caros de calcular
em cada nó, mesmo quando o número de nós não muda — ou seja, heurísticas
que olham à frente reduzem o espaço de busca, mas têm um custo por nó que
cresce com o tamanho do domínio.

## 6. Como o aumento do número de restrições afetou o problema?

O experimento de densidade (tamanho fixo, só a disponibilidade variando)
isola esse efeito: reduzir a disponibilidade de 0,55 para 0,40 já é
suficiente para o backtracking simples deixar de convergir em 200.000
nós (de 31 nós/0,002s para o limite/~6,6s sem solução) — uma transição
abrupta de "trivial" para "intratável no orçamento de nós". O aprimorado,
no mesmo intervalo, permanece com 31 nós e 0 retrocessos nas 4
disponibilidades testadas: as restrições ficaram mais apertadas, mas as
heurísticas de antecipação absorveram esse aperto sem precisar explorar
mais estados. Isso confirma o resultado da tabela principal (grande ×
média × pequena) sem confundir "mais restrições" com "mais atendimentos":
aqui o tamanho da instância é o mesmo, só a disponibilidade muda, e o
efeito sobre o simples já é dramático.
