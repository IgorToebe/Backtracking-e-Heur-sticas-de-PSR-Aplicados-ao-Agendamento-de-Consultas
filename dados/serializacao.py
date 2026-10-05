"""Leitura, escrita e validação de instâncias em JSON."""

import json

from modelo.entidades import Atendimento, Cliente, GradeHoraria, Instancia, Profissional, Sala
from modelo.erros import InstanciaInvalidaError


def salvar_instancia(instancia: Instancia, caminho: str) -> None:
    dados = {
        "grade": {
            "dias": instancia.grade.dias,
            "slots_por_dia": instancia.grade.slots_por_dia,
            "minutos_por_slot": instancia.grade.minutos_por_slot,
        },
        "profissionais": [
            {
                "id": p.id, "nome": p.nome,
                "especialidades": sorted(p.especialidades),
                "horarios_disponiveis": sorted(p.horarios_disponiveis),
            }
            for p in instancia.profissionais.values()
        ],
        "clientes": [
            {
                "id": c.id, "nome": c.nome, "servico_necessario": c.servico_necessario,
                "horarios_disponiveis": sorted(c.horarios_disponiveis),
                "duracao_slots": c.duracao_slots,
            }
            for c in instancia.clientes.values()
        ],
        "salas": [
            {"id": s.id, "tipo": s.tipo, "horarios_disponiveis": sorted(s.horarios_disponiveis)}
            for s in instancia.salas.values()
        ],
        "atendimentos": [{"id": a.id, "cliente_id": a.cliente_id} for a in instancia.atendimentos],
    }
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def _inteiro_positivo(valor, campo: str) -> int:
    # bool é subclasse de int em Python: sem esse cuidado, `true` no JSON viraria 1
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise InstanciaInvalidaError(f"{campo} deve ser um inteiro positivo, recebido {valor!r}")
    return valor


def _texto(valor, campo: str) -> str:
    if not isinstance(valor, str) or not valor:
        raise InstanciaInvalidaError(f"{campo} deve ser um texto não vazio, recebido {valor!r}")
    return valor


def _horarios(valor, campo: str) -> frozenset[int]:
    if not isinstance(valor, list) or any(isinstance(s, bool) or not isinstance(s, int) for s in valor):
        raise InstanciaInvalidaError(f"{campo} deve ser uma lista de inteiros (índices de slot), recebido {valor!r}")
    return frozenset(valor)


def _especialidades(valor, campo: str) -> frozenset[str]:
    # uma string solta ("juridico") seria aceita por frozenset() e viraria um conjunto de letras
    if not isinstance(valor, list) or not all(isinstance(e, str) and e for e in valor):
        raise InstanciaInvalidaError(f"{campo} deve ser uma lista de textos, recebido {valor!r}")
    return frozenset(valor)


def carregar_instancia(caminho: str) -> Instancia:
    try:
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError:
        raise InstanciaInvalidaError(f"arquivo de instância não encontrado: {caminho}")
    except json.JSONDecodeError as e:
        raise InstanciaInvalidaError(f"JSON inválido em {caminho}: {e}")
    except UnicodeDecodeError:
        raise InstanciaInvalidaError(f"{caminho} não está codificado em UTF-8")
    except OSError as e:
        raise InstanciaInvalidaError(f"não foi possível ler {caminho}: {e.strerror}")

    try:
        g = dados["grade"]
        grade = GradeHoraria(
            _inteiro_positivo(g["dias"], "grade.dias"),
            _inteiro_positivo(g["slots_por_dia"], "grade.slots_por_dia"),
            _inteiro_positivo(g["minutos_por_slot"], "grade.minutos_por_slot"),
        )
        profissionais = {
            p["id"]: Profissional(
                _texto(p["id"], "profissional.id"), p["nome"],
                _especialidades(p["especialidades"], f"profissional {p['id']}: especialidades"),
                _horarios(p["horarios_disponiveis"], f"profissional {p['id']}: horarios_disponiveis"),
            )
            for p in dados["profissionais"]
        }
        clientes = {
            c["id"]: Cliente(
                _texto(c["id"], "cliente.id"), c["nome"],
                _texto(c["servico_necessario"], f"cliente {c['id']}: servico_necessario"),
                _horarios(c["horarios_disponiveis"], f"cliente {c['id']}: horarios_disponiveis"),
                _inteiro_positivo(c["duracao_slots"], f"cliente {c['id']}: duracao_slots"),
            )
            for c in dados["clientes"]
        }
        salas = {
            s["id"]: Sala(
                _texto(s["id"], "sala.id"), s.get("tipo"),
                _horarios(s["horarios_disponiveis"], f"sala {s['id']}: horarios_disponiveis"),
            )
            for s in dados["salas"]
        }
        atendimentos = [
            Atendimento(_texto(a["id"], "atendimento.id"), _texto(a["cliente_id"], f"atendimento {a['id']}: cliente_id"))
            for a in dados["atendimentos"]
        ]
    except (KeyError, TypeError, AttributeError) as e:
        raise InstanciaInvalidaError(f"estrutura inválida em {caminho}: campo ausente ou tipo incorreto ({e})")

    if len(profissionais) != len(dados["profissionais"]):
        raise InstanciaInvalidaError("IDs de profissionais duplicados na instância")
    if len(clientes) != len(dados["clientes"]):
        raise InstanciaInvalidaError("IDs de clientes duplicados na instância")
    if len(salas) != len(dados["salas"]):
        raise InstanciaInvalidaError("IDs de salas duplicados na instância")
    if len({a.id for a in atendimentos}) != len(atendimentos):
        raise InstanciaInvalidaError("IDs de atendimentos duplicados na instância")

    return Instancia(grade, profissionais, clientes, salas, atendimentos)


def validar_instancia(instancia: Instancia) -> list[str]:
    """Validação semântica (além da estrutural feita por carregar_instancia).

    Mensagens começam com 'ERRO' (a instância não pode ser resolvida como
    está) ou 'AVISO' (a instância é válida, mas algo pode ficar sem solução
    — ex. domínio vazio para algum atendimento).
    """
    problemas: list[str] = []
    total_slots = instancia.grade.total_slots

    for a in instancia.atendimentos:
        if a.cliente_id not in instancia.clientes:
            problemas.append(f"ERRO: atendimento {a.id} referencia cliente inexistente '{a.cliente_id}'")

    grupos = (
        ("profissional", instancia.profissionais.values()),
        ("cliente", instancia.clientes.values()),
        ("sala", instancia.salas.values()),
    )
    for nome_grupo, entidades in grupos:
        for e in entidades:
            fora = sorted(s for s in e.horarios_disponiveis if s < 0 or s >= total_slots)
            if fora:
                problemas.append(f"ERRO: {nome_grupo} {e.id} tem horário(s) fora da grade: {fora}")
            if not e.horarios_disponiveis:
                problemas.append(f"AVISO: {nome_grupo} {e.id} não tem nenhum horário disponível")

    especialidades_ofertadas = {esp for p in instancia.profissionais.values() for esp in p.especialidades}
    for c in instancia.clientes.values():
        if c.servico_necessario not in especialidades_ofertadas:
            problemas.append(
                f"AVISO: nenhum profissional oferece '{c.servico_necessario}', necessário "
                f"para o cliente {c.id} — atendimento(s) desse cliente ficarão sem solução"
            )

    return problemas
