import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modelo.entidades import Atendimento, Cliente, GradeHoraria, Instancia, Profissional, Sala


@pytest.fixture
def instancia_minima() -> Instancia:
    """3 atendimentos, cada um forçado a um slot único por disponibilidade do
    cliente — dá para calcular o domínio e a solução esperada à mão.

    A1 (cliente C1, disponível só no slot 0) só pode ir com P1 (P2 não está
    disponível no slot 0). A2 e A3 podem ir com P1 ou P2, mas em slots
    diferentes de A1, então nunca há conflito de profissional/sala.
    """
    grade = GradeHoraria(dias=1, slots_por_dia=4, minutos_por_slot=60)
    profissionais = {
        "P1": Profissional("P1", "Prof. 1", frozenset({"juridico"}), frozenset({0, 1, 2})),
        "P2": Profissional("P2", "Prof. 2", frozenset({"juridico"}), frozenset({1, 2, 3})),
    }
    clientes = {
        "C1": Cliente("C1", "Cliente 1", "juridico", frozenset({0}), 1),
        "C2": Cliente("C2", "Cliente 2", "juridico", frozenset({1}), 1),
        "C3": Cliente("C3", "Cliente 3", "juridico", frozenset({2}), 1),
    }
    salas = {"S1": Sala("S1", None, frozenset({0, 1, 2, 3}))}
    atendimentos = [
        Atendimento("A1", "C1"),
        Atendimento("A2", "C2"),
        Atendimento("A3", "C3"),
    ]
    return Instancia(grade, profissionais, clientes, salas, atendimentos)


@pytest.fixture
def instancia_conflituosa() -> Instancia:
    """2 atendimentos com 1 único profissional e 1 única sala.

    A1 (cliente "largo", disponível nos slots 0 e 1) vem antes de A2
    (cliente "estreito", só disponível no slot 0) na ordem de entrada.
    O Backtracking simples tenta A1 no slot 0 primeiro (ordem fixa do
    domínio), o que deixa A2 sem opção e força 1 retrocesso. O Backtracking
    aprimorado escolhe A2 primeiro (MRV, domínio menor) e nunca erra.
    """
    grade = GradeHoraria(dias=1, slots_por_dia=2, minutos_por_slot=60)
    profissionais = {
        "P1": Profissional("P1", "Prof. 1", frozenset({"juridico"}), frozenset({0, 1})),
    }
    clientes = {
        "CW": Cliente("CW", "Cliente largo", "juridico", frozenset({0, 1}), 1),
        "CN": Cliente("CN", "Cliente estreito", "juridico", frozenset({0}), 1),
    }
    salas = {"S1": Sala("S1", None, frozenset({0, 1}))}
    atendimentos = [Atendimento("A1", "CW"), Atendimento("A2", "CN")]
    return Instancia(grade, profissionais, clientes, salas, atendimentos)
