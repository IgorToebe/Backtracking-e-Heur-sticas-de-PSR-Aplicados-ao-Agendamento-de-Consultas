# Agendamento de Consultas/Atendimentos — PSR (Tema 9)

Trabalho da disciplina de Introdução a IA. Modela o agendamento de
atendimentos (clientes × profissionais × salas × horários) como um
**Problema de Satisfação de Restrições (PSR)** e resolve com duas versões
de backtracking:

- **Backtracking simples** (`algoritmos/backtracking_simples.py`): busca
  com retrocesso, ordem de variáveis e valores fixa, sem heurísticas.
- **Backtracking aprimorado** (`algoritmos/backtracking_aprimorado.py`):
  MRV (Minimum Remaining Values) + Forward Checking + LCV (Least
  Constraining Value).

## Modelagem do PSR

- **Variáveis**: cada atendimento solicitado.
- **Domínio**: combinações válidas de `(profissional, horário, sala)` —
  filtradas pela especialidade do profissional e pela disponibilidade
  estática de cada um.
- **Restrições** (`modelo/restricoes.py`):
  1. o profissional deve ter a especialidade exigida pelo cliente;
  2. um profissional não atende duas pessoas ao mesmo tempo;
  3. um cliente não tem dois atendimentos ao mesmo tempo;
  4. uma sala não é usada por dois atendimentos ao mesmo tempo;
  5. a disponibilidade de profissional, cliente e sala é respeitada.

O tempo é discretizado em slots atômicos (`dias × slots_por_dia`); um
atendimento ocupa `duracao_slots` slots consecutivos.

## Instalação

```
python -m pip install -r requirements.txt
```

Requer Python 3.11+ (usa `X | None` e `dict[str, X]` na anotação de tipos).

## Menu interativo (usado na apresentação)

```
python main.py
```

Sem argumentos, o programa abre um menu numerado no terminal:

```
1 - Escolher instância
2 - Ver dados de entrada
3 - Executar backtracking simples (sem otimização)
4 - Executar backtracking aprimorado (com otimização)
5 - Executar os dois juntos e comparar
6 - Ver resultados
7 - Alterar instância
8 - Rodar testes
0 - Sair
```

A instância `dados/instancias/demo.json` já vem carregada. Em "Alterar
instância" dá para acrescentar cliente, mudar a disponibilidade de um
profissional, adicionar/remover sala e salvar em arquivo; depois é só
executar os algoritmos de novo para recalcular.

Os subcomandos abaixo continuam disponíveis para uso direto.

## Uso

Gerar uma instância sintética (3 tamanhos disponíveis — Seção 9 da
especificação: pequena ≥10, média ≥30, grande ≥60 atendimentos):

```
python main.py gerar-instancia --tamanho pequena --seed 42 --saida dados/instancias/pequena.json
python main.py gerar-instancia --tamanho media   --seed 42 --saida dados/instancias/media.json
python main.py gerar-instancia --tamanho grande  --seed 42 --saida dados/instancias/grande.json
```

Resolver uma instância e ver a agenda resultante (por profissional, por
horário e por cliente) e as métricas de desempenho:

```
python main.py resolver --instancia dados/instancias/pequena.json --metodo aprimorado
python main.py resolver --instancia dados/instancias/pequena.json --metodo simples --rastrear
```

`--rastrear` imprime cada tentativa de atribuição e retrocesso da busca —
útil para acompanhar visualmente o funcionamento do algoritmo na
instância pequena. `--limite-nos N` (padrão 200000) interrompe a busca
após N nós, para instâncias em que a versão simples não converge em
tempo hábil (ver `avaliacao/resultados/comparacao.csv`).

Comparar as duas versões numa bateria de instâncias e salvar um CSV:

```
python main.py comparar --instancias dados/instancias/pequena.json dados/instancias/media.json dados/instancias/grande.json --saida avaliacao/resultados/comparacao.csv
```

Experimento extra de densidade de restrições (tamanho fixo, disponibilidade variando):

```
python -m avaliacao.experimento_densidade
```

## Demonstração ao vivo (parâmetro alterado durante a apresentação)

`dados/instancias/demo.json` é uma instância comum, sem nenhuma solução
pré-calculada em qualquer lugar do código. Para alterar um parâmetro
durante a demonstração, edite o JSON diretamente (é só um arquivo texto)
e rode `resolver` de novo — o programa recalcula do zero:

- **acrescentar um cliente/atendimento**: adicionar um objeto em
  `"clientes"` e/ou `"atendimentos"`;
- **alterar uma indisponibilidade**: adicionar ou remover um número de
  `"horarios_disponiveis"` de um profissional/cliente/sala;
- **modificar a capacidade**: adicionar ou remover uma sala de `"salas"`.

```
python main.py resolver --instancia dados/instancias/demo.json --metodo aprimorado
```

Edições que só **adicionam** disponibilidade (nunca removem) preservam a
solução anterior — são as mais seguras para garantir que a demo continue
solúvel. Edições que removem disponibilidade ou adicionam demanda podem
tornar a instância inviável; nesse caso o programa reporta "nenhuma
solução encontrada" com as métricas da busca, em vez de travar ou falhar
silenciosamente.

## Testes

```
python -m pytest testes/ -v
```

Cobrem: as 5 restrições isoladamente, geração de domínio, geração de
dados (reprodutibilidade da seed e ausência de erros estruturais),
entradas inválidas (JSON malformado, referências inexistentes,
especialidade sem profissional compatível) e as duas versões do
backtracking sobre instâncias pequenas com solução verificável à mão.

## Estrutura do projeto

```
dados/          geração sintética e leitura/escrita/validação de instâncias
modelo/         entidades do PSR, geração de domínio, restrições
algoritmos/     as duas versões do backtracking + métricas
avaliacao/      experimentos comparativos (avaliacao/resultados/*.csv)
interface/      CLI e impressão das agendas no terminal
testes/         suíte pytest
entrega/        relatório técnico e slides
```

## Decisões de projeto relevantes

- **Geração de dados**: não existe base pública para este problema
  específico (atribuição profissional+horário+sala com disponibilidades),
  então as instâncias são sintéticas, com seed fixa para reprodutibilidade.
  O gerador planta uma solução válida antes de sortear as disponibilidades
  (cada disponibilidade sempre inclui os horários da solução plantada,
  mais folga aleatória) — isso garante que toda instância gerada tem pelo
  menos uma solução, o que é necessário para a comparação de desempenho
  da Seção 8 fazer sentido.
- **Tipo de sala**: a especificação trata "tipo de sala" como opcional
  ("quando necessário") e não está entre as 5 restrições obrigatórias do
  Tema 9, então não foi modelado — todas as salas são intercambiáveis.
- **Sem bibliotecas de resolução de PSR/otimização**: as duas versões do
  backtracking, MRV, Forward Checking e LCV são implementação própria,
  usando apenas a biblioteca padrão do Python, conforme exigido na
  Seção 18 da especificação.
