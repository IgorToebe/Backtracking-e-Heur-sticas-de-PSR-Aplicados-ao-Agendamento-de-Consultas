from dataclasses import dataclass


@dataclass
class Metricas:
    """Contadores de desempenho, idênticos para as duas versões do
    backtracking (essencial para uma comparação justa entre elas):

    - nos_explorados: +1 a cada chamada da função recursiva de busca.
    - atribuicoes: +1 quando um valor passa em `consistente(...)` e é fixado.
    - backtracks: +1 sempre que uma atribuição precisa ser desfeita.
    """

    tempo_segundos: float = 0.0
    atribuicoes: int = 0
    backtracks: int = 0
    nos_explorados: int = 0
    interrompida_por_limite: bool = False
