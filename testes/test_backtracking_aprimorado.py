from algoritmos.backtracking_aprimorado import resolver as resolver_aprimorado
from algoritmos.backtracking_simples import resolver as resolver_simples
from modelo.restricoes import validar_solucao


def test_resolve_instancia_minima(instancia_minima):
    solucao, metricas = resolver_aprimorado(instancia_minima)
    assert solucao is not None
    assert validar_solucao(instancia_minima, solucao) == []


def test_nao_precisa_de_retrocesso_na_instancia_conflituosa(instancia_conflituosa):
    """MRV escolhe o atendimento de domínio menor primeiro, evitando o erro
    que força o Backtracking simples a retroceder (ver conftest.py)."""
    solucao, metricas = resolver_aprimorado(instancia_conflituosa)
    assert solucao is not None
    assert validar_solucao(instancia_conflituosa, solucao) == []
    assert metricas.backtracks == 0


def test_aprimorado_explora_no_maximo_tantos_nos_quanto_o_simples(instancia_conflituosa):
    _, m_simples = resolver_simples(instancia_conflituosa)
    _, m_aprimorado = resolver_aprimorado(instancia_conflituosa)
    assert m_aprimorado.nos_explorados <= m_simples.nos_explorados
    assert m_aprimorado.backtracks <= m_simples.backtracks
