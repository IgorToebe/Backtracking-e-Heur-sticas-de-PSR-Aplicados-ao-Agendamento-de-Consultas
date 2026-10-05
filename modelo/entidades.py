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

    def hora_do_slot(self, slot_no_dia: int) -> str:
        """Horário de início ("HH:MM") de um slot dentro do dia. slot_no_dia ==
        slots_por_dia dá o horário de fim do expediente."""
        hora, minuto = divmod(HORA_INICIO * 60 + slot_no_dia * self.minutos_por_slot, 60)
        return f"{hora:02d}:{minuto:02d}"

    def formatar_slot(self, slot_id: int) -> str:
        dia, slot_no_dia = divmod(slot_id, self.slots_por_dia)
        return f"Dia{dia + 1} {self.hora_do_slot(slot_no_dia)}"

    def formatar_horarios(self, slots) -> str:
        """{0,1,2,5} -> 'Dia1 08:00-11:00, 13:00-14:00' (slots consecutivos
        viram um intervalo; o fim é o término do último slot)."""
        por_dia: dict[int, list[int]] = {}
        for s in sorted(slots):
            dia, slot_no_dia = divmod(s, self.slots_por_dia)
            por_dia.setdefault(dia, []).append(slot_no_dia)
        if not por_dia:
            return "nenhum"
        partes = []
        for dia, lista in por_dia.items():
            intervalos, inicio, anterior = [], lista[0], lista[0]
            for s in lista[1:] + [None]:
                if s is not None and s == anterior + 1:
                    anterior = s
                    continue
                intervalos.append(f"{self.hora_do_slot(inicio)}-{self.hora_do_slot(anterior + 1)}")
                if s is not None:
                    inicio = anterior = s
            partes.append(f"Dia{dia + 1} " + ", ".join(intervalos))
        return " | ".join(partes)


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

    def descrever(self, grade: GradeHoraria) -> str:
        return f"{self.profissional_id}, {self.sala_id}, {grade.formatar_slot(self.slot_inicio)}"


@dataclass
class Instancia:
    grade: GradeHoraria
    profissionais: dict[str, Profissional]
    clientes: dict[str, Cliente]
    salas: dict[str, Sala]
    atendimentos: list[Atendimento]
