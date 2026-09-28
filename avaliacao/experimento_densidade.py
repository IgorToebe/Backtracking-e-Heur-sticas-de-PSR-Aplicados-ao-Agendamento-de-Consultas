"""Experimento extra: tamanho de instância fixo (médio), variando só a
disponibilidade (prob_disponibilidade) — isola o efeito do "aperto" das
restrições do efeito do tamanho da instância, para responder à pergunta 6
da Seção 11 da especificação ("como o aumento do número de restrições
afetou o problema?"). A tabela principal (comparacao.csv) varia tamanho E
disponibilidade ao mesmo tempo, então não separa essas duas causas.

Uso (a partir da raiz do projeto): python -m avaliacao.experimento_densidade
"""

from dados.geracao import TAMANHOS, gerar_instancia
from avaliacao.experimentos import comparar, salvar_csv

BASE = {k: v for k, v in TAMANHOS["media"].items() if k != "prob_disponibilidade"}
PROBABILIDADES = [0.55, 0.40, 0.25, 0.15]
SEED = 42
SAIDA = "avaliacao/resultados/densidade.csv"
LIMITE_NOS = 200_000


def main() -> None:
    instancias = {
        f"media_disp={p:.2f}": gerar_instancia(seed=SEED, prob_disponibilidade=p, **BASE)
        for p in PROBABILIDADES
    }
    linhas = comparar(instancias, limite_nos=LIMITE_NOS)
    salvar_csv(linhas, SAIDA)
    print(f"{len(linhas)} resultados salvos em {SAIDA}")
    for linha in linhas:
        print(linha)


if __name__ == "__main__":
    main()
