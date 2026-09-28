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


def carregar_instancia(caminho: str) -> Instancia:
    try:
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError:
        raise InstanciaInvalidaError(f"arquivo de instância não encontrado: {caminho}")
    except json.JSONDecodeError as e:
        raise InstanciaInvalidaError(f"JSON inválido em {caminho}: {e}")

    try:
        grade = GradeHoraria(**dados["grade"])
        profissionais = {
            p["id"]: Profissional(
                p["id"], p["nome"], frozenset(p["especialidades"]), frozenset(p["horarios_disponiveis"])
            )
            for p in dados["profissionais"]
        }
        clientes = {
            c["id"]: Cliente(
                c["id"], c["nome"], c["servico_necessario"],
                frozenset(c["horarios_disponiveis"]), c["duracao_slots"],
            )
            for c in dados["clientes"]
        }
        salas = {
            s["id"]: Sala(s["id"], s.get("tipo"), frozenset(s["horarios_disponiveis"]))
            for s in dados["salas"]
        }
        atendimentos = [Atendimento(a["id"], a["cliente_id"]) for a in dados["atendimentos"]]
    except (KeyError, TypeError) as e:
        raise InstanciaInvalidaError(f"estrutura inválida em {caminho}: campo ausente ou tipo incorreto ({e})")

    if len(profissionais) != len(dados["profissionais"]):
        raise InstanciaInvalidaError("IDs de profissionais duplicados na instância")
    if len(clientes) != len(dados["clientes"]):
        raise InstanciaInvalidaError("IDs de clientes duplicados na instância")
    if len(salas) != len(dados["salas"]):
        raise InstanciaInvalidaError("IDs de salas duplicados na instância")

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
