"""Backtracking simples (Versão 1): busca com retrocesso, sem heurísticas.

Ordem de variáveis: ordem de entrada da instância (fixa).
Ordem de valores: ordem em que o domínio foi gerado (fixa).
"""

import time

from algoritmos.metricas import Metricas
from modelo.dominio import gerar_dominio
from modelo.entidades import Atendimento, Instancia, Valor
from modelo.restricoes import consistente


def resolver(
    instancia: Instancia, limite_nos: int | None = None, rastrear: bool = False
) -> tuple[dict[str, Valor] | None, Metricas]:
    dominios: dict[str, list[Valor]] = {a.id: gerar_dominio(instancia, a) for a in instancia.atendimentos}
    metricas = Metricas()

    def backtrack(
        atribuicoes: dict[str, tuple[Atendimento, Valor]], restantes: list[Atendimento]
    ) -> dict[str, tuple[Atendimento, Valor]] | None:
        if metricas.interrompida_por_limite:
            return None
        metricas.nos_explorados += 1
        if limite_nos is not None and metricas.nos_explorados >= limite_nos:
            metricas.interrompida_por_limite = True
            return None
        if not restantes:
            return atribuicoes

        atendimento, *proximos = restantes
        for valor in dominios[atendimento.id]:
            if not consistente(instancia, atendimento, valor, atribuicoes):
                continue
            atribuicoes[atendimento.id] = (atendimento, valor)
            metricas.atribuicoes += 1
            if rastrear:
                print(f"  {atendimento.id} -> ({valor.descrever(instancia.grade)})  OK")
            resultado = backtrack(atribuicoes, proximos)
            if resultado is not None:
                return resultado
            del atribuicoes[atendimento.id]
            if metricas.interrompida_por_limite:
                return None  # busca abortada: não conta retrocesso nem tenta os demais valores
            metricas.backtracks += 1
            if rastrear:
                print(f"  {atendimento.id} -> ({valor.descrever(instancia.grade)})  FALHOU, retrocede")
        return None

    inicio = time.perf_counter()
    resultado = backtrack({}, list(instancia.atendimentos))
    metricas.tempo_segundos = time.perf_counter() - inicio

    solucao = {aid: valor for aid, (_, valor) in resultado.items()} if resultado is not None else None
    return solucao, metricas
