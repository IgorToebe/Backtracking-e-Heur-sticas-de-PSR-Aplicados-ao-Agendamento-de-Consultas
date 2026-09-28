from algoritmos.backtracking_simples import resolver
from modelo.restricoes import validar_solucao


def test_resolve_instancia_minima(instancia_minima):
    solucao, metricas = resolver(instancia_minima)
    assert solucao is not None
    assert validar_solucao(instancia_minima, solucao) == []
    assert solucao["A1"].profissional_id == "P1"  # único profissional possível no slot 0
    assert solucao["A1"].slot_inicio == 0


def test_precisa_de_um_retrocesso_na_instancia_conflituosa(instancia_conflituosa):
    solucao, metricas = resolver(instancia_conflituosa)
    assert solucao is not None
    assert validar_solucao(instancia_conflituosa, solucao) == []
    assert metricas.backtracks == 1


def test_limite_de_nos_interrompe_sem_travar(instancia_minima):
    solucao, metricas = resolver(instancia_minima, limite_nos=1)
    assert solucao is None
    assert metricas.interrompida_por_limite is True
    assert metricas.nos_explorados == 1
