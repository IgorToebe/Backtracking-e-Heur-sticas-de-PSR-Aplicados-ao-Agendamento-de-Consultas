"""Interface de linha de comando. Ver README.md para exemplos de uso."""

import argparse
import sys

from algoritmos import backtracking_aprimorado, backtracking_simples
from avaliacao.experimentos import comparar as comparar_instancias
from avaliacao.experimentos import salvar_csv
from dados.geracao import TAMANHOS, gerar_instancia_por_tamanho
from dados.serializacao import carregar_instancia, salvar_instancia, validar_instancia
from interface.apresentacao import (
    imprimir_metricas,
    imprimir_por_cliente,
    imprimir_por_horario,
    imprimir_por_profissional,
)
from modelo.erros import InstanciaInvalidaError
from modelo.restricoes import validar_solucao

METODOS = {"simples": backtracking_simples, "aprimorado": backtracking_aprimorado}
LIMITE_NOS_PADRAO = 200_000


def _cmd_gerar_instancia(args: argparse.Namespace) -> None:
    instancia = gerar_instancia_por_tamanho(args.tamanho, args.seed)
    salvar_instancia(instancia, args.saida)
    print(f"instância '{args.tamanho}' (seed={args.seed}) salva em {args.saida} "
          f"({len(instancia.atendimentos)} atendimentos)")


def _cmd_resolver(args: argparse.Namespace) -> None:
    instancia = carregar_instancia(args.instancia)
    problemas = validar_instancia(instancia)
    for p in problemas:
        print(p)
    if any(p.startswith("ERRO") for p in problemas):
        print("\ninstância inválida: corrija os erros acima antes de resolver")
        sys.exit(1)

    solucao, metricas = METODOS[args.metodo].resolver(instancia, limite_nos=args.limite_nos, rastrear=args.rastrear)
    if solucao is None:
        motivo = " (limite de nós atingido)" if metricas.interrompida_por_limite else ""
        print(f"\nnenhuma solução encontrada{motivo}")
        imprimir_metricas(metricas)
        sys.exit(1)

    imprimir_por_profissional(instancia, solucao)
    imprimir_por_horario(instancia, solucao)
    imprimir_por_cliente(instancia, solucao)
    imprimir_metricas(metricas)

    violacoes = validar_solucao(instancia, solucao)
    print(f"\nconflitos na solução: {len(violacoes)}")
    for v in violacoes:
        print(f"  - {v}")


def _cmd_comparar(args: argparse.Namespace) -> None:
    instancias = {caminho: carregar_instancia(caminho) for caminho in args.instancias}
    linhas = comparar_instancias(instancias, limite_nos=args.limite_nos)
    salvar_csv(linhas, args.saida)
    print(f"{len(linhas)} resultados salvos em {args.saida}\n")
    cabecalho = f"{'instancia':30s} {'metodo':10s} {'n':>4s} {'tempo(s)':>10s} {'atrib.':>8s} {'backtr.':>8s} {'nos':>8s}"
    print(cabecalho)
    for linha in linhas:
        print(
            f"{linha['instancia']:30s} {linha['metodo']:10s} {linha['n_atendimentos']:4d} "
            f"{linha['tempo_segundos']:10.4f} {linha['atribuicoes']:8d} {linha['backtracks']:8d} "
            f"{linha['nos_explorados']:8d}"
        )


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass  # streams sem reconfigure (ex.: redirecionadas em alguns ambientes) — segue sem forçar utf-8

    parser = argparse.ArgumentParser(prog="main.py", description="Agendamento de consultas/atendimentos (PSR) — Tema 9")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    p_gerar = subparsers.add_parser("gerar-instancia", help="gera e salva uma instância sintética")
    p_gerar.add_argument("--tamanho", choices=list(TAMANHOS), required=True)
    p_gerar.add_argument("--seed", type=int, default=42)
    p_gerar.add_argument("--saida", required=True)
    p_gerar.set_defaults(func=_cmd_gerar_instancia)

    p_resolver = subparsers.add_parser("resolver", help="resolve uma instância e mostra a agenda resultante")
    p_resolver.add_argument("--instancia", required=True)
    p_resolver.add_argument("--metodo", choices=list(METODOS), required=True)
    p_resolver.add_argument("--limite-nos", type=int, default=LIMITE_NOS_PADRAO, dest="limite_nos")
    p_resolver.add_argument("--rastrear", action="store_true", help="imprime cada tentativa/retrocesso da busca")
    p_resolver.set_defaults(func=_cmd_resolver)

    p_comparar = subparsers.add_parser("comparar", help="roda as 2 versões em várias instâncias e salva um CSV comparativo")
    p_comparar.add_argument("--instancias", nargs="+", required=True)
    p_comparar.add_argument("--limite-nos", type=int, default=LIMITE_NOS_PADRAO, dest="limite_nos")
    p_comparar.add_argument("--saida", default="avaliacao/resultados/comparacao.csv")
    p_comparar.set_defaults(func=_cmd_comparar)

    args = parser.parse_args()
    try:
        args.func(args)
    except InstanciaInvalidaError as e:
        print(f"erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
