"""Entidades do PSR de agendamento de consultas/atendimentos (Tema 9).

O tempo é discretizado em slots atômicos: cada entidade com "horários
disponíveis" guarda um conjunto de índices de slot dentro da grade
(0 .. dias * slots_por_dia - 1). Um atendimento ocupa `duracao_slots`
slots consecutivos a partir do slot escolhido.
"""

from dataclasses import dataclass

HORA_INICIO = 8  # dia útil começa às 08:00, usado só para exibição


@dataclass(frozen=True)
class GradeHoraria:
    dias: int
    slots_por_dia: int
    minutos_por_slot: int

    @property
    def total_slots(self) -> int:
        return self.dias * self.slots_por_dia

    def formatar_slot(self, slot_id: int) -> str:
        dia, slot_no_dia = divmod(slot_id, self.slots_por_dia)
        minutos_totais = HORA_INICIO * 60 + slot_no_dia * self.minutos_por_slot
        hora, minuto = divmod(minutos_totais, 60)
        return f"Dia{dia + 1} {hora:02d}:{minuto:02d}"


@dataclass(frozen=True)
class Profissional:
    id: str
    nome: str
    especialidades: frozenset[str]
    horarios_disponiveis: frozenset[int]


@dataclass(frozen=True)
class Cliente:
    id: str
    nome: str
    servico_necessario: str
    horarios_disponiveis: frozenset[int]
    duracao_slots: int


@dataclass(frozen=True)
class Sala:
    id: str
    tipo: str | None
    horarios_disponiveis: frozenset[int]


@dataclass(frozen=True)
class Atendimento:
    """Variável do PSR: um pedido de atendimento a ser alocado.

    Serviço, duração e disponibilidade do lado do cliente vêm do
    Cliente (via cliente_id) — não são duplicados aqui, para não abrir
    espaço para inconsistência entre Atendimento e Cliente.
    """

    id: str
    cliente_id: str


@dataclass(frozen=True)
class Valor:
    """Valor candidato do domínio de um Atendimento."""

    profissional_id: str
    slot_inicio: int
    sala_id: str


@dataclass
class Instancia:
    grade: GradeHoraria
    profissionais: dict[str, Profissional]
    clientes: dict[str, Cliente]
    salas: dict[str, Sala]
    atendimentos: list[Atendimento]
