# Conteúdo dos slides

Estrutura pronta para colar em PowerPoint/Google Slides/Canva (1 seção =
1 ou mais slides). Preencher os campos entre [colchetes]. Tempo sugerido
total: 15 minutos (ver distribuição na especificação, Seção 16).

---

## Slide 1 — Capa

- [Universidade] — [Curso]
- Disciplina: Introdução a Inteligência Artificial
- Título: Agendamento de Consultas/Atendimentos como Problema de Satisfação de Restrições (Tema 9)
- Integrantes: [nomes e RAs]
- Professor: [nome]
- [Data]

---

## Slide 2-3 — Introdução (≈3 min)

**O problema real**

- Clínicas/consultorias/escritórios precisam distribuir clientes entre
  profissionais, horários e salas.
- Cada atendimento exige uma especialidade, um horário compatível com
  cliente/profissional/sala, sem conflitos simultâneos.

**Modelagem como PSR**

- Variáveis: cada atendimento solicitado.
- Domínio: cada atendimento tem o seu próprio domínio, formado pelas
  combinações (profissional, horário, sala) possíveis de acordo com as
  suas próprias restrições: especialidade exigida pelo cliente e
  disponibilidade do profissional, do cliente e da sala.
- Objetivo: o programa busca atribuir um valor a todos os atendimentos
  evitando conflitos entre eles. Há conflito quando dois atendimentos
  escolhem valores que se sobrepõem, isto é, usam o mesmo profissional,
  a mesma sala ou o mesmo cliente em horários que coincidem.
- 5 restrições obrigatórias: especialidade compatível; profissional sem
  conflito; cliente sem conflito; sala sem conflito; disponibilidade
  respeitada.
- (Diagrama sugerido: uma variável "Atendimento" com uma seta para seu
  domínio de tuplas (profissional, horário, sala), e ícones das 5
  restrições ao redor.)

**Tamanho das instâncias (quantidade de cada elemento)**

| Elemento                                | Pequena | Média | Grande |
| --------------------------------------- | ------- | ----- | ------ |
| Atendimentos (variáveis)                | 10      | 30    | 60     |
| Clientes                                | 8       | 22    | 45     |
| Profissionais                           | 6       | 8     | 11     |
| Salas                                   | 3       | 4     | 4      |
| Horários no total                       | 10      | 30    | 50     |
| Dias                                    | 1       | 3     | 5      |
| Horários por dia                        | 10      | 10    | 10     |
| Combinações geradas (soma dos domínios) | 83      | 371   | 1.111  |

| Tamanho da árvore (produto dos domínios, aprox.)
| 5,5 × 10⁸ | 6,1 × 10²⁸ | 3,0 × 10⁶² |

- 3 especialidades em todas as instâncias (clínica geral, jurídico,
  psicologia); duração de cada atendimento de 1 ou 2 horários (slots de
  60 min).

---

## Slide 4 — Materiais e métodos

- Linguagem: Python 3.11+ (biblioteca padrão apenas).
- Plataforma/SO/computador:
  CPU - Core I5 10a geração, 6 cores, 12 threads, 12MB L3 Cache, 2.9Ghz.
  RAM - DDR 4, 2x8Gb - dual channel, 2666Mhz, CL19.
- Técnicas de IA: busca com retrocesso (backtracking); heurísticas MRV,
  Forward Checking e LCV.
- Método de avaliação: tempo de execução, nº de atribuições, nº de
  retrocessos, nº de nós explorados — comparados entre as duas versões em
  3 tamanhos de instância + um experimento controlando só a densidade de
  restrições (número de horários disponíveis de cada dia).

---

## Slide 5-6 — Fundamentação: estratégias e heurísticas (≈4 min)

**Versão 1 — Backtracking simples**

- Ordem de variáveis e de valores fixa; sem heurísticas.
- Funcionamento na árvore de busca: cada nível da árvore é um
  atendimento e cada ramo é um valor do seu domínio (profissional,
  horário, sala).
  1. Desce um nível: atribui ao próximo atendimento o primeiro valor do
     domínio que não viola nenhuma restrição com o que já foi atribuído.
  2. Se todos os atendimentos foram atribuídos, achou a solução.
  3. Se nenhum valor do domínio serve, o ramo é um beco sem saída:
     retrocede (backtrack) ao nível anterior, desfaz aquela atribuição e
     tenta o próximo valor dali.
     Toda atribuição é uma tentativa, não uma decisão definitiva: só se
     confirma quando todos os atendimentos forem atribuídos.
     Exemplo: A1 recebe (P1, 10h, S1) provisoriamente. A2 só tem
     (P1, 10h, S2) no seu domínio, mas P1 já está ocupado às 10h por A1,
     então A2 esgota todos os seus valores sem sucesso. Como a causa é a
     escolha feita em A1, o algoritmo volta a ele (um nível por vez),
     desfaz (P1, 10h, S1) e tenta o próximo valor do seu domínio,
     (P2, 10h, S1). Agora A2 consegue usar (P1, 10h, S2) e a busca segue
     para A3.
  4. Se esgotar todos os valores do primeiro nível, não há solução.
- Memória: a árvore completa é teórica e nunca é construída. O algoritmo
  guarda só o caminho atual (as atribuições feitas da raiz até o nível
  onde está); ao retroceder, a atribuição desfeita é esquecida. Por isso
  a memória cresce com o número de atendimentos, não com o tamanho da
  árvore. O custo do backtracking é de tempo.
- Limitação: só descobre um erro ao esbarrar nele, então pode explorar
  muitos ramos inúteis antes de corrigir uma escolha ruim feita lá no
  início.

**Versão 2 — Backtracking aprimorado**

- MRV (Minimum Remaining Values): escolhe sempre o atendimento com menor
  domínio restante.
- Forward Checking: após cada atribuição, remove dos domínios futuros os
  valores que ficaram inconsistentes; poda o ramo se algum domínio
  esvaziar.
- LCV (Least Constraining Value): entre os valores possíveis, tenta
  primeiro o que menos restringe as opções dos demais atendimentos.
- Como resolve os problemas da Versão 1: o simples só descobre um erro
  ao esbarrar nele, bem abaixo na árvore; o aprimorado evita ou antecipa
  esse erro.
  - MRV: começa pelo atendimento que tem menos combinações válidas
    (profissional, horário, sala) no domínio, ou seja, o mais restrito e
    com maior chance de ficar sem opção. Assim os becos sem saída
    aparecem perto da raiz, e não no fundo da árvore.
  - Forward Checking: enxerga o erro assim que ele se torna inevitável
    (algum domínio fica vazio) e corta o ramo na hora, sem descer
    níveis inúteis.
  - LCV: escolhe valores que deixam mais opções para os demais,
    reduzindo a chance de precisar retroceder.
  - Resultado: menos ramos explorados e menos retrocessos.
  - Memória: além do caminho atual, guarda os valores que o Forward
    Checking removeu dos domínios, para devolvê-los ao retroceder.

(Sugestão: mostrar lado a lado uma árvore de busca pequena — a mesma do
teste `instancia_conflituosa` — comparando 1 retrocesso do simples contra
0 retrocessos do aprimorado.)

---

## Slide 7-8 — Desenvolvimento (parte de ≈4 min de "Algoritmos" + demonstração)

**Organização do código**

```
dados/        geração sintética + leitura/escrita/validação de instâncias
modelo/       entidades do PSR, domínio, restrições
algoritmos/   backtracking simples e aprimorado + métricas
avaliacao/    experimentos comparativos
interface/    CLI e impressão das agendas
testes/       suíte pytest
```

- `dados/`: gera instâncias de teste (sempre com solução, mesma seed =
  mesma instância), lê/grava JSON e valida a entrada.
- `modelo/`: entidades do problema (profissional, cliente, sala,
  atendimento), domínio de cada atendimento e as 5 restrições.
- `algoritmos/`: as duas versões do backtracking e as métricas (tempo,
  atribuições, retrocessos, nós), iguais nas duas para comparar com justiça.
- `avaliacao/`: roda as duas versões e salva os resultados em CSV.
- `interface/`: comandos `gerar-instancia`, `resolver` e `comparar`, e a
  agenda impressa por profissional, horário e cliente.
- `testes/`: testes automáticos do domínio, das restrições e dos algoritmos.

**Decisões de projeto**

- Cada restrição é uma função simples (responde sim/não) e é testada
  separadamente.
- As duas versões usam as mesmas restrições e o mesmo domínio: só muda a
  ordem da busca e o forward checking. Assim, a diferença de desempenho
  vem só das heurísticas.
- Especialidade e disponibilidade já filtram o domínio antes da busca; os
  conflitos entre atendimentos são checados durante a busca.
- Ao final, a solução é conferida de novo, de forma independente.

**Demonstração ao vivo (≈5 min, ver Seção 15 da especificação)**

1. Mostrar `dados/instancias/demo.json` (dados de entrada).
2. Rodar `python main.py resolver --instancia dados/instancias/demo.json --metodo aprimorado`.
3. Mostrar a agenda por profissional / por horário / por cliente e
   confirmar "conflitos na solução: 0".
4. Alterar um parâmetro simples pedido pelo professor (editar o JSON:
   adicionar cliente, remover disponibilidade, adicionar/remover sala).
5. Rodar `resolver` de novo e mostrar a nova agenda. Se não houver mais
   solução, o programa avisa.

---

## Slide 9-10 — Resultados e análise (≈3 min)

| Instância    | Método     | Tempo (s) | Backtracks | Nós              | Resolvida |
| ------------ | ---------- | --------- | ---------- | ---------------- | --------- |
| Pequena (10) | Simples    | 0,0002    | 0          | 11               | Sim       |
| Pequena (10) | Aprimorado | 0,0032    | 0          | 11               | Sim       |
| Média (30)   | Simples    | 5,76      | 200.100    | 200.000 (limite) | Não       |
| Média (30)   | Aprimorado | 0,03      | 0          | 31               | Sim       |
| Grande (60)  | Simples    | 8,37      | 200.471    | 200.000 (limite) | Não       |
| Grande (60)  | Aprimorado | 0,21      | 6          | 62               | Sim       |

- O simples só resolve a instância pequena; nas demais, nem 200 mil nós
  bastam.
- O aprimorado resolve todas em menos de 0,25s, com poucas dezenas de nós.
- Experimento extra (densidade fixa de restrições, tamanho constante):
  reduzir a disponibilidade já derruba o simples, mas o aprimorado
  mantém 31 nós/0 retrocessos nas 4 disponibilidades testadas.
- (Gráfico sugerido: barras de nós explorados, escala log, simples ×
  aprimorado, para as 3 instâncias.)

---

## Slide 11 — Conclusões

- MRV + Forward Checking + LCV reduzem drasticamente o espaço de busca
  explorado, tornando tratável um problema que o backtracking simples
  não resolve em tempo/orçamento razoável a partir de instâncias médias.
- O ganho é sobretudo em nós/retrocessos explorados; o custo por nó do
  aprimorado cresce com o tamanho dos domínios (ver limitações no
  relatório técnico).
- O sistema atende às 5 restrições do Tema 9 e permite verificar
  visualmente a ausência de conflitos nas 3 visões de agenda.

---

## Slide 12 — Referências bibliográficas

- [Russell, S.; Norvig, P. — Artificial Intelligence: A Modern Approach
  (capítulo de CSPs — MRV, Forward Checking, LCV).]
- [Especificação do trabalho — Introdução a Inteligência Artificial, Tema 9.]
- [Outras referências usadas pela equipe.]
