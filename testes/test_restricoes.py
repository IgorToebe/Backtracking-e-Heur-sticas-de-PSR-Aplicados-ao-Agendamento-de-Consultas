from modelo.entidades import Atendimento, Valor
from modelo.restricoes import (
    consistente,
    disponibilidade_respeitada,
    especialidade_compativel,
    sem_conflito_cliente,
    sem_conflito_profissional,
    sem_conflito_sala,
    sobrepoe,
    validar_solucao,
)


def test_sobrepoe_casos_basicos():
    assert sobrepoe(0, 1, 0, 1) is True     # mesmo slot
    assert sobrepoe(0, 2, 1, 1) is True     # sobreposição parcial
    assert sobrepoe(0, 1, 1, 1) is False    # slots adjacentes, sem sobreposição
    assert sobrepoe(2, 1, 0, 1) is False


def test_especialidade_compativel(instancia_minima):
    a1 = instancia_minima.atendimentos[0]  # cliente C1 precisa de "juridico"
    assert especialidade_compativel(a1, Valor("P1", 0, "S1"), instancia_minima) is True

    from dataclasses import replace
    instancia_minima.clientes["C1"] = replace(instancia_minima.clientes["C1"], servico_necessario="odontologia")
    assert especialidade_compativel(a1, Valor("P1", 0, "S1"), instancia_minima) is False


def test_disponibilidade_respeitada(instancia_minima):
    a1 = instancia_minima.atendimentos[0]
    assert disponibilidade_respeitada(a1, Valor("P1", 0, "S1"), instancia_minima) is True
    assert disponibilidade_respeitada(a1, Valor("P2", 0, "S1"), instancia_minima) is False  # P2 indisponível no slot 0


def test_sem_conflito_profissional(instancia_minima):
    a2, a3 = instancia_minima.atendimentos[1], instancia_minima.atendimentos[2]
    atribuicoes = {"A2": (a2, Valor("P1", 1, "S1"))}
    assert sem_conflito_profissional(a3, Valor("P1", 2, "S1"), atribuicoes, instancia_minima) is True
    assert sem_conflito_profissional(a3, Valor("P1", 1, "S1"), atribuicoes, instancia_minima) is False


def test_sem_conflito_cliente(instancia_minima):
    a2 = instancia_minima.atendimentos[1]
    outro_atendimento_mesmo_cliente = Atendimento("A2b", "C2")
    atribuicoes = {"A2": (a2, Valor("P1", 1, "S1"))}
    assert sem_conflito_cliente(outro_atendimento_mesmo_cliente, Valor("P2", 1, "S1"), atribuicoes, instancia_minima) is False
    assert sem_conflito_cliente(outro_atendimento_mesmo_cliente, Valor("P2", 2, "S1"), atribuicoes, instancia_minima) is True


def test_sem_conflito_sala(instancia_minima):
    a2, a3 = instancia_minima.atendimentos[1], instancia_minima.atendimentos[2]
    atribuicoes = {"A2": (a2, Valor("P1", 1, "S1"))}
    assert sem_conflito_sala(a3, Valor("P2", 1, "S1"), atribuicoes, instancia_minima) is False
    assert sem_conflito_sala(a3, Valor("P2", 2, "S1"), atribuicoes, instancia_minima) is True


def test_consistente_agrega_as_5_restricoes(instancia_minima):
    a1 = instancia_minima.atendimentos[0]
    assert consistente(instancia_minima, a1, Valor("P1", 0, "S1"), {}) is True
    assert consistente(instancia_minima, a1, Valor("P2", 0, "S1"), {}) is False  # R5: P2 indisponível no slot 0


def test_validar_solucao_detecta_conflito_injetado(instancia_minima):
    solucao_valida = {"A1": Valor("P1", 0, "S1"), "A2": Valor("P1", 1, "S1"), "A3": Valor("P2", 2, "S1")}
    assert validar_solucao(instancia_minima, solucao_valida) == []

    solucao_invalida = dict(solucao_valida)
    solucao_invalida["A3"] = Valor("P1", 1, "S1")  # mesmo profissional e slot de A2
    assert validar_solucao(instancia_minima, solucao_invalida) != []
