"""Backtracking aprimorado (Versão 2): MRV + Forward Checking + LCV.

Mesma casca do Backtracking simples (algoritmos/backtracking_simples.py),
trocando a ordem fixa de variáveis e valores por duas heurísticas e
acrescentando forward checking após cada atribuição. Isso cobre o mínimo
exigido pela especificação (MRV + FC obrigatórios) mais uma estratégia
extra (LCV).
"""

import time

from algoritmos.metricas import Metricas
from modelo.dominio import gerar_dominio
from modelo.entidades import Atendimento, Instancia, Valor
from modelo.restricoes import consistente, incompativel


def _escolher_variavel(nao_atribuidos: list[Atendimento], dominios: dict[str, list[Valor]]) -> Atendimento:
    """MRV: atendimento não-atribuído com o menor domínio restante."""
    return min(nao_atribuidos, key=lambda a: len(dominios[a.id]))


def _ordenar_por_lcv(
    atendimento: Atendimento,
    valores: list[Valor],
    outros: list[Atendimento],
    dominios: dict[str, list[Valor]],
    instancia: Instancia,
) -> list[Valor]:
    """LCV: tenta primeiro o valor que elimina menos opções dos domínios dos
    demais atendimentos não-atribuídos (least constraining value)."""

    def custo(valor: Valor) -> int:
        return sum(
            incompativel(atendimento, valor, outro, outro_valor, instancia)
            for outro in outros
            for outro_valor in dominios[outro.id]
        )

    return sorted(valores, key=custo)


def _forward_check(
    atendimento: Atendimento,
    valor: Valor,
    outros: list[Atendimento],
    dominios: dict[str, list[Valor]],
    instancia: Instancia,
) -> tuple[dict[str, list[Valor]], bool]:
    """Remove dos domínios dos não-atribuídos os valores que ficaram
    inconsistentes com a nova atribuição. Devolve o que foi removido (para
    ser restaurado no retrocesso) e se algum domínio ficou vazio (poda)."""
    removidos: dict[str, list[Valor]] = {}
    sucesso = True
    for outro in outros:
        eliminados = [v for v in dominios[outro.id] if incompativel(atendimento, valor, outro, v, instancia)]
        if eliminados:
            removidos[outro.id] = eliminados
            dominios[outro.id] = [v for v in dominios[outro.id] if v not in eliminados]
        if not dominios[outro.id]:
            sucesso = False
            break
    return removidos, sucesso


def resolver(
    instancia: Instancia, limite_nos: int | None = None, rastrear: bool = False
) -> tuple[dict[str, Valor] | None, Metricas]:
    dominios: dict[str, list[Valor]] = {a.id: gerar_dominio(instancia, a) for a in instancia.atendimentos}
    metricas = Metricas()

    def backtrack(
        atribuicoes: dict[str, tuple[Atendimento, Valor]], nao_atribuidos: list[Atendimento]
    ) -> dict[str, tuple[Atendimento, Valor]] | None:
        if metricas.interrompida_por_limite:
            return None
        metricas.nos_explorados += 1
        if limite_nos is not None and metricas.nos_explorados >= limite_nos:
            metricas.interrompida_por_limite = True
            return None
        if not nao_atribuidos:
            return atribuicoes

        atendimento = _escolher_variavel(nao_atribuidos, dominios)
        outros = [a for a in nao_atribuidos if a.id != atendimento.id]
        valores_ordenados = _ordenar_por_lcv(atendimento, dominios[atendimento.id], outros, dominios, instancia)

        for valor in valores_ordenados:
            if not consistente(instancia, atendimento, valor, atribuicoes):
                continue
            atribuicoes[atendimento.id] = (atendimento, valor)
            metricas.atribuicoes += 1
            if rastrear:
                print(f"  {atendimento.id} -> ({valor.descrever(instancia.grade)})  OK")

            removidos, sucesso = _forward_check(atendimento, valor, outros, dominios, instancia)
            resultado = backtrack(atribuicoes, outros) if sucesso else None
            if resultado is not None:
                return resultado

            for outro_id, valores_removidos in removidos.items():
                dominios[outro_id].extend(valores_removidos)
            del atribuicoes[atendimento.id]
            if metricas.interrompida_por_limite:
                return None  # busca abortada: não conta retrocesso nem tenta os demais valores
            metricas.backtracks += 1
            if rastrear:
                motivo = "retrocede" if sucesso else "poda (forward checking)"
                print(f"  {atendimento.id} -> ({valor.descrever(instancia.grade)})  FALHOU, {motivo}")
        return None

    inicio = time.perf_counter()
    resultado = backtrack({}, list(instancia.atendimentos))
    metricas.tempo_segundos = time.perf_counter() - inicio

    solucao = {aid: valor for aid, (_, valor) in resultado.items()} if resultado is not None else None
    return solucao, metricas
