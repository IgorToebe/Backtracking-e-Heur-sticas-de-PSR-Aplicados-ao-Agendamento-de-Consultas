"""Geração sintética e reprodutível de instâncias do problema de agendamento.

Não existe base pública para "atribuição profissional+horário+sala com
disponibilidades" (Tema 9), então as instâncias são geradas por um gerador
próprio com seed fixa: mesma seed sempre produz a mesma instância, o que
permite reproduzir os experimentos.

O gerador primeiro planta uma solução válida (aloca cada atendimento a um
profissional/horário/sala sem conflitos) e só depois monta as
disponibilidades: cada disponibilidade sempre inclui os horários usados
pela solução plantada, mais horários extras aleatórios (a folga
`prob_disponibilidade`). Isso garante que a instância gerada é sempre
solúvel — geração puramente aleatória das disponibilidades, sem essa
garantia, frequentemente produz instâncias inviáveis mesmo com poucos
atendimentos, o que inviabilizaria a comparação de desempenho pedida
na Seção 8 da especificação.
"""

import random

from modelo.entidades import Atendimento, Cliente, GradeHoraria, Instancia, Profissional, Sala

ESPECIALIDADES = ["clinica_geral", "juridico", "psicologia"]
MINUTOS_POR_SLOT = 60
DURACAO_MIN_SLOTS = 1
DURACAO_MAX_SLOTS = 2
TENTATIVAS_PLANTIO = 30

# Parâmetros por tamanho de instância (Seção 9 da especificação).
# A instância "grande" pressiona o algoritmo por menor slack (menos
# recursos relativos e disponibilidade extra mais restrita), não só por
# ter mais atendimentos. n_profissionais é sempre múltiplo do número de
# especialidades, para garantir pelo menos um profissional por
# especialidade em cada grupo e reduzir o risco de a instância planejada
# não caber na grade (poucos slots + só 1 profissional por especialidade).
TAMANHOS = {
    "pequena": dict(
        n_atendimentos=10, n_clientes=8, n_profissionais=6, n_salas=3,
        dias=1, slots_por_dia=10, prob_disponibilidade=0.35,
    ),
    "media": dict(
        n_atendimentos=30, n_clientes=22, n_profissionais=8, n_salas=4,
        dias=3, slots_por_dia=10, prob_disponibilidade=0.25,
    ),
    "grande": dict(
        n_atendimentos=60, n_clientes=45, n_profissionais=11, n_salas=4,
        dias=5, slots_por_dia=10, prob_disponibilidade=0.15,
    ),
}


def _plantar_solucao(
    rng: random.Random,
    atendimentos_ids: list[str],
    cliente_por_atendimento: dict[str, str],
    servico_por_cliente: dict[str, str],
    duracao_por_cliente: dict[str, int],
    ids_profissionais: list[str],
    especialidade_por_profissional: dict[str, str],
    ids_salas: list[str],
    total_slots: int,
) -> tuple[dict[str, tuple[str, int, str]], dict[str, set[int]], dict[str, set[int]], dict[str, set[int]]]:
    """Constrói uma alocação válida (sem violar R1-R5) para todos os
    atendimentos, para garantir que a instância final tenha solução."""
    ordem = list(atendimentos_ids)
    for _ in range(TENTATIVAS_PLANTIO):
        rng.shuffle(ordem)
        planta: dict[str, tuple[str, int, str]] = {}
        ocupado_profissional = {pid: set() for pid in ids_profissionais}
        ocupado_sala = {sid: set() for sid in ids_salas}
        ocupado_cliente = {cid: set() for cid in cliente_por_atendimento.values()}
        sucesso = True

        for aid in ordem:
            cid = cliente_por_atendimento[aid]
            duracao = duracao_por_cliente[cid]
            candidatos_prof = [p for p in ids_profissionais if especialidade_por_profissional[p] == servico_por_cliente[cid]]
            rng.shuffle(candidatos_prof)
            posicoes = list(range(total_slots - duracao + 1))
            rng.shuffle(posicoes)

            escolhido = None
            for pid in candidatos_prof:
                for slot in posicoes:
                    janela = range(slot, slot + duracao)
                    if any(s in ocupado_profissional[pid] for s in janela):
                        continue
                    if any(s in ocupado_cliente[cid] for s in janela):
                        continue
                    sala = next((s for s in ids_salas if not any(t in ocupado_sala[s] for t in janela)), None)
                    if sala is None:
                        continue
                    escolhido = (pid, slot, sala)
                    break
                if escolhido:
                    break

            if escolhido is None:
                sucesso = False
                break  # não coube; tenta de novo com outra ordem/embaralhamento
            pid, slot, sala = escolhido
            for s in range(slot, slot + duracao):
                ocupado_profissional[pid].add(s)
                ocupado_cliente[cid].add(s)
                ocupado_sala[sala].add(s)
            planta[aid] = escolhido

        if sucesso:
            return planta, ocupado_profissional, ocupado_cliente, ocupado_sala

    raise RuntimeError(
        "não foi possível plantar uma solução válida com os parâmetros informados "
        "(muitos atendimentos para os recursos disponíveis) — aumente n_profissionais/"
        "n_salas/slots_por_dia ou reduza n_atendimentos"
    )


def _horarios_com_folga(base: set[int], total_slots: int, prob_extra: float, rng: random.Random) -> frozenset[int]:
    extra = {s for s in range(total_slots) if s not in base and rng.random() < prob_extra}
    return frozenset(base | extra)


def gerar_instancia(
    seed: int,
    n_atendimentos: int,
    n_clientes: int,
    n_profissionais: int,
    n_salas: int,
    dias: int,
    slots_por_dia: int,
    prob_disponibilidade: float,
    especialidades: list[str] = ESPECIALIDADES,
    minutos_por_slot: int = MINUTOS_POR_SLOT,
    duracao_min: int = DURACAO_MIN_SLOTS,
    duracao_max: int = DURACAO_MAX_SLOTS,
) -> Instancia:
    if n_clientes >= n_atendimentos:
        raise ValueError("n_clientes deve ser menor que n_atendimentos, para que "
                          "alguns clientes tenham mais de um atendimento (Restrição 3)")

    rng = random.Random(seed)
    grade = GradeHoraria(dias, slots_por_dia, minutos_por_slot)
    total_slots = grade.total_slots

    ids_profissionais = [f"P{i + 1}" for i in range(n_profissionais)]
    especialidade_por_profissional = {pid: especialidades[i % len(especialidades)] for i, pid in enumerate(ids_profissionais)}

    ids_clientes = [f"C{i + 1}" for i in range(n_clientes)]
    servico_por_cliente = {cid: rng.choice(especialidades) for cid in ids_clientes}
    duracao_por_cliente = {cid: rng.randint(duracao_min, duracao_max) for cid in ids_clientes}

    ids_salas = [f"S{i + 1}" for i in range(n_salas)]

    atendimentos_ids = [f"A{i + 1}" for i in range(n_atendimentos)]
    cliente_por_atendimento = {
        aid: (ids_clientes[i] if i < n_clientes else rng.choice(ids_clientes))
        for i, aid in enumerate(atendimentos_ids)
    }

    _planta, ocupado_prof, ocupado_cli, ocupado_sala = _plantar_solucao(
        rng, atendimentos_ids, cliente_por_atendimento, servico_por_cliente, duracao_por_cliente,
        ids_profissionais, especialidade_por_profissional, ids_salas, total_slots,
    )

    profissionais = {
        pid: Profissional(
            pid, f"Profissional {pid[1:]}", frozenset({especialidade_por_profissional[pid]}),
            _horarios_com_folga(ocupado_prof[pid], total_slots, prob_disponibilidade, rng),
        )
        for pid in ids_profissionais
    }
    clientes = {
        cid: Cliente(
            cid, f"Cliente {cid[1:]}", servico_por_cliente[cid],
            _horarios_com_folga(ocupado_cli[cid], total_slots, prob_disponibilidade, rng),
            duracao_por_cliente[cid],
        )
        for cid in ids_clientes
    }
    salas = {
        sid: Sala(sid, None, _horarios_com_folga(ocupado_sala[sid], total_slots, prob_disponibilidade, rng))
        for sid in ids_salas
    }
    atendimentos = [Atendimento(aid, cliente_por_atendimento[aid]) for aid in atendimentos_ids]
    rng.shuffle(atendimentos)

    return Instancia(grade, profissionais, clientes, salas, atendimentos)


def gerar_instancia_por_tamanho(tamanho: str, seed: int) -> Instancia:
    if tamanho not in TAMANHOS:
        raise ValueError(f"tamanho deve ser um de {list(TAMANHOS)}, recebido {tamanho!r}")
    return gerar_instancia(seed=seed, **TAMANHOS[tamanho])
