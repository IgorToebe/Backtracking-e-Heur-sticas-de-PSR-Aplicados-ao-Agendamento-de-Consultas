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
- Domínio: combinações (profissional, horário, sala) válidas quanto a
  especialidade e disponibilidade.
- 5 restrições obrigatórias: especialidade compatível; profissional sem
  conflito; cliente sem conflito; sala sem conflito; disponibilidade
  respeitada.
- (Diagrama sugerido: uma variável "Atendimento" com uma seta para seu
  domínio de tuplas (profissional, horário, sala), e ícones das 5
  restrições ao redor.)

---

## Slide 4 — Materiais e métodos

- Linguagem: Python 3.11+ (biblioteca padrão apenas).
- Plataforma/SO/computador: [preencher com a máquina usada na demo].
- Técnicas de IA: busca com retrocesso (backtracking); heurísticas MRV,
  Forward Checking e LCV.
- Método de avaliação: tempo de execução, nº de atribuições, nº de
  retrocessos, nº de nós explorados — comparados entre as duas versões em
  3 tamanhos de instância + um experimento controlando só a densidade de
  restrições.

---

## Slide 5-6 — Fundamentação: estratégias e heurísticas (≈4 min)

**Versão 1 — Backtracking simples**
- Ordem de variáveis e de valores fixa; sem heurísticas.

**Versão 2 — Backtracking aprimorado**
- MRV (Minimum Remaining Values): escolhe sempre o atendimento com menor
  domínio restante.
- Forward Checking: após cada atribuição, remove dos domínios futuros os
  valores que ficaram inconsistentes; poda o ramo se algum domínio
  esvaziar.
- LCV (Least Constraining Value): entre os valores possíveis, tenta
  primeiro o que menos restringe as opções dos demais atendimentos.

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
- Restrições isoladas em funções puras e testadas uma a uma.
- Backtracking simples e aprimorado reaproveitam as mesmas funções de
  restrição/domínio — só mudam a ordenação de variáveis/valores e a
  presença de forward checking.

**Demonstração ao vivo (≈5 min, ver Seção 15 da especificação)**
1. Mostrar `dados/instancias/demo.json` (dados de entrada).
2. Rodar `python main.py resolver --instancia dados/instancias/demo.json --metodo aprimorado`.
3. Mostrar a agenda por profissional / por horário / por cliente e
   confirmar "conflitos na solução: 0".
4. Alterar um parâmetro simples pedido pelo professor (editar o JSON:
   adicionar cliente, remover disponibilidade, adicionar/remover sala).
5. Rodar `resolver` de novo e mostrar a nova agenda recalculada.

---

## Slide 9-10 — Resultados e análise (≈3 min)

| Instância | Método | Tempo (s) | Backtracks | Nós | Resolvida |
|---|---|---|---|---|---|
| Pequena (10) | Simples | 0,0002 | 0 | 11 | Sim |
| Pequena (10) | Aprimorado | 0,0032 | 0 | 11 | Sim |
| Média (30) | Simples | 5,76 | 200.100 | 200.000 (limite) | Não |
| Média (30) | Aprimorado | 0,03 | 0 | 31 | Sim |
| Grande (60) | Simples | 8,37 | 200.471 | 200.000 (limite) | Não |
| Grande (60) | Aprimorado | 0,21 | 6 | 62 | Sim |

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
