"""As 5 restrições obrigatórias do Tema 9, como funções puras e testáveis.

`atribuicoes` é um dict {atendimento_id: (Atendimento, Valor)} com os
atendimentos já fixados durante a busca — guardar o Atendimento junto do
Valor evita ter que procurá-lo de volta em instancia.atendimentos a cada
checagem de restrição.
"""

from modelo.dominio import slots_livres
from modelo.entidades import Atendimento, Instancia, Valor

Atribuicoes = dict[str, tuple[Atendimento, Valor]]


def especialidade_compativel(atendimento: Atendimento, valor: Valor, instancia: Instancia) -> bool:
    """Restrição 1: o profissional escolhido deve ter a especialidade que o cliente precisa."""
    cliente = instancia.clientes[atendimento.cliente_id]
    profissional = instancia.profissionais[valor.profissional_id]
    return cliente.servico_necessario in profissional.especialidades


def sobrepoe(inicio_a: int, duracao_a: int, inicio_b: int, duracao_b: int) -> bool:
    """True se os intervalos [inicio_a, inicio_a+duracao_a) e [inicio_b, inicio_b+duracao_b) se sobrepõem."""
    return inicio_a < inicio_b + duracao_b and inicio_b < inicio_a + duracao_a


def duracao_de(atendimento: Atendimento, instancia: Instancia) -> int:
    return instancia.clientes[atendimento.cliente_id].duracao_slots


def sem_conflito_profissional(atendimento: Atendimento, valor: Valor, atribuicoes: Atribuicoes, instancia: Instancia) -> bool:
    """Restrição 2: um profissional não pode atender duas pessoas ao mesmo tempo."""
    duracao = duracao_de(atendimento, instancia)
    for outro, outro_valor in atribuicoes.values():
        if outro_valor.profissional_id == valor.profissional_id and sobrepoe(
            valor.slot_inicio, duracao, outro_valor.slot_inicio, duracao_de(outro, instancia)
        ):
            return False
    return True


def sem_conflito_cliente(atendimento: Atendimento, valor: Valor, atribuicoes: Atribuicoes, instancia: Instancia) -> bool:
    """Restrição 3: um cliente não pode ter dois atendimentos ao mesmo tempo."""
    duracao = duracao_de(atendimento, instancia)
    for outro, outro_valor in atribuicoes.values():
        if outro.cliente_id == atendimento.cliente_id and sobrepoe(
            valor.slot_inicio, duracao, outro_valor.slot_inicio, duracao_de(outro, instancia)
        ):
            return False
    return True


def sem_conflito_sala(atendimento: Atendimento, valor: Valor, atribuicoes: Atribuicoes, instancia: Instancia) -> bool:
    """Restrição 4: uma sala não pode ser usada por dois atendimentos ao mesmo tempo."""
    duracao = duracao_de(atendimento, instancia)
    for outro, outro_valor in atribuicoes.values():
        if outro_valor.sala_id == valor.sala_id and sobrepoe(
            valor.slot_inicio, duracao, outro_valor.slot_inicio, duracao_de(outro, instancia)
        ):
            return False
    return True


def disponibilidade_respeitada(atendimento: Atendimento, valor: Valor, instancia: Instancia) -> bool:
    """Restrição 5: profissional, cliente e sala precisam estar livres em todos os slots ocupados."""
    cliente = instancia.clientes[atendimento.cliente_id]
    profissional = instancia.profissionais[valor.profissional_id]
    sala = instancia.salas[valor.sala_id]
    duracao = cliente.duracao_slots
    return (
        slots_livres(profissional.horarios_disponiveis, valor.slot_inicio, duracao)
        and slots_livres(cliente.horarios_disponiveis, valor.slot_inicio, duracao)
        and slots_livres(sala.horarios_disponiveis, valor.slot_inicio, duracao)
    )


def consistente(instancia: Instancia, atendimento: Atendimento, valor: Valor, atribuicoes: Atribuicoes) -> bool:
    """Agrega as 5 restrições — chamada a cada tentativa de atribuição no backtracking."""
    return (
        especialidade_compativel(atendimento, valor, instancia)
        and disponibilidade_respeitada(atendimento, valor, instancia)
        and sem_conflito_profissional(atendimento, valor, atribuicoes, instancia)
        and sem_conflito_cliente(atendimento, valor, atribuicoes, instancia)
        and sem_conflito_sala(atendimento, valor, atribuicoes, instancia)
    )


def incompativel(a1: Atendimento, v1: Valor, a2: Atendimento, v2: Valor, instancia: Instancia) -> bool:
    """True se (a1,v1) e (a2,v2) não podem coexistir na mesma solução, por
    violarem R2 (profissional), R3 (cliente) ou R4 (sala). Usada pelo
    Backtracking aprimorado (forward checking e LCV) para avaliar o efeito
    de uma atribuição hipotética sobre outro atendimento não-atribuído."""
    hipotese: Atribuicoes = {a1.id: (a1, v1)}
    return not (
        sem_conflito_profissional(a2, v2, hipotese, instancia)
        and sem_conflito_cliente(a2, v2, hipotese, instancia)
        and sem_conflito_sala(a2, v2, hipotese, instancia)
    )


def validar_solucao(instancia: Instancia, solucao: dict[str, Valor]) -> list[str]:
    """Recheca as 5 restrições numa solução completa, de forma independente do
    solver que a produziu. Lista de violações vazia = solução válida."""
    violacoes: list[str] = []
    atribuicoes: Atribuicoes = {}
    for atendimento in instancia.atendimentos:
        valor = solucao.get(atendimento.id)
        if valor is None:
            violacoes.append(f"atendimento {atendimento.id} sem valor atribuído")
            continue
        if not consistente(instancia, atendimento, valor, atribuicoes):
            violacoes.append(f"atendimento {atendimento.id} viola alguma restrição com {valor}")
        atribuicoes[atendimento.id] = (atendimento, valor)
    return violacoes
