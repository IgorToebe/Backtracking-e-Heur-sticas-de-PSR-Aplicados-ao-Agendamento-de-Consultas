"""Impressão dos resultados no terminal: agenda em 3 visões + métricas."""

from algoritmos.metricas import Metricas
from modelo.entidades import Instancia, Valor


def _atendimento_por_id(instancia: Instancia, atendimento_id: str):
    return next(a for a in instancia.atendimentos if a.id == atendimento_id)


def _linha(instancia: Instancia, atendimento_id: str, valor: Valor) -> str:
    atendimento = _atendimento_por_id(instancia, atendimento_id)
    cliente = instancia.clientes[atendimento.cliente_id]
    horario = instancia.grade.formatar_slot(valor.slot_inicio)
    return (
        f"{atendimento_id}: cliente={cliente.nome} profissional={valor.profissional_id} "
        f"sala={valor.sala_id} horario={horario}"
    )


def imprimir_por_profissional(instancia: Instancia, solucao: dict[str, Valor]) -> None:
    print("\n=== Agenda por profissional ===")
    por_profissional: dict[str, list[str]] = {}
    for aid, valor in solucao.items():
        por_profissional.setdefault(valor.profissional_id, []).append(aid)
    for pid in sorted(por_profissional):
        print(f"-- {pid} ({instancia.profissionais[pid].nome}) --")
        aids = sorted(por_profissional[pid], key=lambda aid: solucao[aid].slot_inicio)
        for aid in aids:
            print("   " + _linha(instancia, aid, solucao[aid]))


def imprimir_por_horario(instancia: Instancia, solucao: dict[str, Valor]) -> None:
    print("\n=== Agenda por horário ===")
    por_slot: dict[int, list[str]] = {}
    for aid, valor in solucao.items():
        por_slot.setdefault(valor.slot_inicio, []).append(aid)
    for slot in sorted(por_slot):
        print(f"-- {instancia.grade.formatar_slot(slot)} --")
        for aid in por_slot[slot]:
            print("   " + _linha(instancia, aid, solucao[aid]))


def imprimir_por_cliente(instancia: Instancia, solucao: dict[str, Valor]) -> None:
    print("\n=== Agenda por cliente ===")
    por_cliente: dict[str, list[str]] = {}
    for aid, valor in solucao.items():
        cliente_id = _atendimento_por_id(instancia, aid).cliente_id
        por_cliente.setdefault(cliente_id, []).append(aid)
    for cid in sorted(por_cliente):
        print(f"-- {cid} ({instancia.clientes[cid].nome}) --")
        aids = sorted(por_cliente[cid], key=lambda aid: solucao[aid].slot_inicio)
        for aid in aids:
            print("   " + _linha(instancia, aid, solucao[aid]))


def imprimir_metricas(metricas: Metricas) -> None:
    print("\n=== Métricas ===")
    print(f"tempo:           {metricas.tempo_segundos:.4f}s")
    print(f"atribuições:     {metricas.atribuicoes}")
    print(f"backtracks:      {metricas.backtracks}")
    print(f"nós explorados:  {metricas.nos_explorados}")
    if metricas.interrompida_por_limite:
        print("ATENÇÃO: busca interrompida pelo limite de nós")
