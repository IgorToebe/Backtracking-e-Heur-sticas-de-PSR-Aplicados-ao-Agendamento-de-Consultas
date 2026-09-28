import json
from dataclasses import replace

import pytest

from dados.serializacao import carregar_instancia, validar_instancia
from modelo.dominio import gerar_dominio
from modelo.entidades import Atendimento
from modelo.erros import InstanciaInvalidaError


def test_json_invalido_gera_erro_amigavel(tmp_path):
    caminho = tmp_path / "quebrado.json"
    caminho.write_text("{ isso nao e json valido ]", encoding="utf-8")
    with pytest.raises(InstanciaInvalidaError):
        carregar_instancia(str(caminho))


def test_arquivo_inexistente_gera_erro_amigavel(tmp_path):
    with pytest.raises(InstanciaInvalidaError):
        carregar_instancia(str(tmp_path / "nao_existe.json"))


def test_campo_obrigatorio_ausente_gera_erro(tmp_path):
    dados = {
        "grade": {"dias": 1, "slots_por_dia": 4, "minutos_por_slot": 60},
        "profissionais": [{"id": "P1", "nome": "P1"}],  # faltam especialidades e horarios_disponiveis
        "clientes": [],
        "salas": [],
        "atendimentos": [],
    }
    caminho = tmp_path / "incompleto.json"
    caminho.write_text(json.dumps(dados), encoding="utf-8")
    with pytest.raises(InstanciaInvalidaError):
        carregar_instancia(str(caminho))


def test_cliente_id_inexistente_e_detectado_sem_crash(instancia_minima):
    instancia_minima.atendimentos.append(Atendimento("A4", "C_NAO_EXISTE"))
    problemas = validar_instancia(instancia_minima)
    assert any("A4" in p and p.startswith("ERRO") for p in problemas)


def test_especialidade_sem_profissional_gera_dominio_vazio_sem_crash(instancia_minima):
    instancia_minima.clientes["C1"] = replace(instancia_minima.clientes["C1"], servico_necessario="odontologia")
    a1 = instancia_minima.atendimentos[0]

    assert gerar_dominio(instancia_minima, a1) == []
    problemas = validar_instancia(instancia_minima)
    assert any(p.startswith("AVISO") and "odontologia" in p for p in problemas)
