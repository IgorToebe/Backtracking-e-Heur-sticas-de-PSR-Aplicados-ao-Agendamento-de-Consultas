from dataclasses import replace

from modelo.dominio import gerar_dominio, slots_livres
from modelo.entidades import Valor


def test_slots_livres():
    disponibilidade = frozenset({0, 1, 2})
    assert slots_livres(disponibilidade, 0, 2) is True
    assert slots_livres(disponibilidade, 1, 2) is True
    assert slots_livres(disponibilidade, 2, 2) is False  # exigiria o slot 3, que não está disponível


def test_gerar_dominio_instancia_minima(instancia_minima):
    a1, a2, a3 = instancia_minima.atendimentos

    # A1: só o slot 0 é possível (disponibilidade do cliente C1), e só P1
    # está disponível nesse slot -> domínio com um único valor
    assert gerar_dominio(instancia_minima, a1) == [Valor("P1", 0, "S1")]

    # A2 e A3: só um slot possível cada, mas P1 e P2 disponíveis -> 2 valores
    assert gerar_dominio(instancia_minima, a2) == [Valor("P1", 1, "S1"), Valor("P2", 1, "S1")]
    assert gerar_dominio(instancia_minima, a3) == [Valor("P1", 2, "S1"), Valor("P2", 2, "S1")]


def test_gerar_dominio_vazio_quando_nenhum_profissional_tem_a_especialidade(instancia_minima):
    instancia_minima.clientes["C1"] = replace(instancia_minima.clientes["C1"], servico_necessario="odontologia")
    a1 = instancia_minima.atendimentos[0]
    assert gerar_dominio(instancia_minima, a1) == []
