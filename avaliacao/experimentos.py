"""Execução dos experimentos comparativos entre as duas versões do backtracking."""

import csv

from algoritmos import backtracking_aprimorado, backtracking_simples
from modelo.entidades import Instancia
from modelo.restricoes import validar_solucao

METODOS = {"simples": backtracking_simples, "aprimorado": backtracking_aprimorado}

CAMPOS = [
    "instancia", "metodo", "n_atendimentos", "tempo_segundos",
    "atribuicoes", "backtracks", "nos_explorados", "resolvida", "interrompida_por_limite",
]


def executar(nome_instancia: str, instancia: Instancia, metodo: str, limite_nos: int | None = None) -> dict:
    if metodo not in METODOS:
        raise ValueError(f"metodo deve ser um de {list(METODOS)}, recebido {metodo!r}")

    solucao, metricas = METODOS[metodo].resolver(instancia, limite_nos=limite_nos)
    if solucao is not None:
        assert validar_solucao(instancia, solucao) == [], "solução encontrada viola alguma restrição"

    return {
        "instancia": nome_instancia,
        "metodo": metodo,
        "n_atendimentos": len(instancia.atendimentos),
        "tempo_segundos": round(metricas.tempo_segundos, 4),
        "atribuicoes": metricas.atribuicoes,
        "backtracks": metricas.backtracks,
        "nos_explorados": metricas.nos_explorados,
        "resolvida": solucao is not None,
        "interrompida_por_limite": metricas.interrompida_por_limite,
    }


def comparar(instancias: dict[str, Instancia], limite_nos: int | None = None) -> list[dict]:
    """Roda as 2 versões em cada instância fornecida. Serve tanto para a
    tabela principal (3 tamanhos) quanto para o experimento de densidade
    (mesmo tamanho, disponibilidade variando) — só muda o dict de entrada."""
    linhas = []
    for nome, instancia in instancias.items():
        for metodo in METODOS:
            linhas.append(executar(nome, instancia, metodo, limite_nos=limite_nos))
    return linhas


def salvar_csv(linhas: list[dict], caminho: str) -> None:
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(linhas)
