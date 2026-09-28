from dados.geracao import TAMANHOS, gerar_instancia_por_tamanho
from dados.serializacao import validar_instancia


def test_mesma_seed_gera_instancia_identica():
    i1 = gerar_instancia_por_tamanho("pequena", seed=42)
    i2 = gerar_instancia_por_tamanho("pequena", seed=42)
    assert i1 == i2


def test_seeds_diferentes_geram_instancias_diferentes():
    i1 = gerar_instancia_por_tamanho("pequena", seed=1)
    i2 = gerar_instancia_por_tamanho("pequena", seed=2)
    assert i1 != i2


def test_tamanhos_minimos_respeitados():
    minimos = {"pequena": 10, "media": 30, "grande": 60}
    for tamanho, minimo in minimos.items():
        instancia = gerar_instancia_por_tamanho(tamanho, seed=42)
        assert len(instancia.atendimentos) >= minimo


def test_instancias_geradas_nao_tem_erros_estruturais():
    for tamanho in TAMANHOS:
        instancia = gerar_instancia_por_tamanho(tamanho, seed=42)
        erros = [p for p in validar_instancia(instancia) if p.startswith("ERRO")]
        assert erros == []
