"""Geração do domínio de cada variável (atendimento) do PSR."""

from modelo.entidades import Atendimento, Instancia, Valor


def slots_livres(disponibilidade: frozenset[int], inicio: int, duracao: int) -> bool:
    """True se todos os slots [inicio, inicio + duracao) estão em `disponibilidade`."""
    return all((inicio + i) in disponibilidade for i in range(duracao))


def gerar_dominio(instancia: Instancia, atendimento: Atendimento) -> list[Valor]:
    """Combina profissional (Restrição 1: especialidade) x horário x sala,
    filtrando apenas pela disponibilidade ESTÁTICA de cada um (Restrição 5).

    Não verifica conflito com outros atendimentos (Restrições 2/3/4): isso é
    dinâmico e é checado durante a busca, em modelo.restricoes.consistente.
    """
    cliente = instancia.clientes[atendimento.cliente_id]
    duracao = cliente.duracao_slots
    total_slots = instancia.grade.total_slots

    profissionais_aptos = [
        p for p in instancia.profissionais.values() if cliente.servico_necessario in p.especialidades
    ]

    dominio = []
    for profissional in profissionais_aptos:
        for slot_inicio in range(total_slots - duracao + 1):
            if not slots_livres(profissional.horarios_disponiveis, slot_inicio, duracao):
                continue
            if not slots_livres(cliente.horarios_disponiveis, slot_inicio, duracao):
                continue
            for sala in instancia.salas.values():
                if slots_livres(sala.horarios_disponiveis, slot_inicio, duracao):
                    dominio.append(Valor(profissional.id, slot_inicio, sala.id))
    return dominio
