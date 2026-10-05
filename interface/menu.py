"""Menu interativo usado na apresentação (python main.py, sem argumentos)."""

import glob
import subprocess
import sys
from dataclasses import replace

from algoritmos import backtracking_aprimorado, backtracking_simples
from dados.serializacao import carregar_instancia, salvar_instancia, validar_instancia
from interface.apresentacao import (
    imprimir_metricas,
    imprimir_por_cliente,
    imprimir_por_horario,
    imprimir_por_profissional,
)
from modelo.entidades import HORA_INICIO, Atendimento, Cliente, Sala
from modelo.erros import InstanciaInvalidaError
from modelo.restricoes import validar_solucao

METODOS = {
    "simples": ("Backtracking simples (sem otimização)", backtracking_simples),
    "aprimorado": ("Backtracking aprimorado (MRV + Forward Checking + LCV)", backtracking_aprimorado),
}
LIMITE_NOS = 200_000

instancia = None
caminho = None
resultados = {}  # metodo -> (solucao, metricas) da última execução


def ler_opcao(texto="Opção: "):
    return input(texto).strip()


def ler_numero(texto, padrao=None):
    while True:
        valor = input(texto).strip()
        if valor == "" and padrao is not None:
            return padrao
        if valor.isdigit():
            return int(valor)
        print("Digite um número.")


def hora_para_slot(grade, texto, fim=False):
    """'09:30' -> índice do slot dentro do dia (fim=True aceita o fim do expediente)."""
    hora, _, minuto = texto.partition(":")
    minutos = int(hora) * 60 + int(minuto or 0) - HORA_INICIO * 60
    slot, resto = divmod(minutos, grade.minutos_por_slot)
    limite = grade.slots_por_dia if fim else grade.slots_por_dia - 1
    if minutos < 0 or resto != 0 or slot > limite:
        raise ValueError(f"horário {texto} fora da grade")
    return slot


def ler_horarios(texto):
    """Lê horários como '08:00-12:00, 14:00-16:00' (vale para todos os dias)
    ou 'Dia2 08:00-12:00' (só aquele dia). 'todos' = grade inteira."""
    g = instancia.grade
    print(f"  (expediente das {g.hora_do_slot(0)} às {g.hora_do_slot(g.slots_por_dia)}, "
          f"de {g.minutos_por_slot} em {g.minutos_por_slot} min)")
    while True:
        valor = input(texto).strip().lower()
        if valor == "todos":
            return set(range(g.total_slots))
        try:
            horarios = set()
            for parte in valor.split(","):
                parte = parte.strip()
                if not parte:
                    continue
                dias = range(g.dias)
                if parte.startswith("dia"):
                    dia, parte = parte[3:].split(maxsplit=1)
                    if not 1 <= int(dia) <= g.dias:
                        raise ValueError(f"dia {dia} fora da grade")
                    dias = [int(dia) - 1]
                if "-" in parte:
                    a, b = parte.replace(" ", "").split("-")
                    slots = range(hora_para_slot(g, a), hora_para_slot(g, b, fim=True))
                else:
                    slots = [hora_para_slot(g, parte)]
                for d in dias:
                    horarios.update(d * g.slots_por_dia + s for s in slots)
            return horarios
        except ValueError as e:
            print(f"Formato inválido ({e}). Exemplo: 08:00-12:00, 14:00-16:00 ou Dia2 09:00-11:00")


def pausa():
    input("\nPressione Enter para continuar...")


# ------------------------------------------------------------------ instância

def escolher_instancia():
    global instancia, caminho
    arquivos = sorted(a.replace("\\", "/") for a in glob.glob("dados/instancias/*.json"))
    print("\nInstâncias disponíveis:")
    for i, arquivo in enumerate(arquivos, 1):
        print(f"  {i} - {arquivo}")
    n = ler_numero("Número da instância (0 para cancelar): ")
    if n < 1 or n > len(arquivos):
        return
    try:
        instancia = carregar_instancia(arquivos[n - 1])
    except InstanciaInvalidaError as e:
        print(f"Erro ao carregar: {e}")
        return
    caminho = arquivos[n - 1]
    resultados.clear()
    print(f"Instância {caminho} carregada ({len(instancia.atendimentos)} atendimentos).")
    for problema in validar_instancia(instancia):
        print(problema)


def mostrar_dados():
    g = instancia.grade
    print(f"\n--- Dados de entrada: {caminho} ---")
    print(f"Grade: {g.dias} dia(s), das {g.hora_do_slot(0)} às {g.hora_do_slot(g.slots_por_dia)}, "
          f"em horários de {g.minutos_por_slot} min")

    print("\nProfissionais:")
    for p in instancia.profissionais.values():
        print(f"  {p.id} - {', '.join(sorted(p.especialidades))} - horários {g.formatar_horarios(p.horarios_disponiveis)}")

    print("\nClientes:")
    for c in instancia.clientes.values():
        print(f"  {c.id} - {c.servico_necessario}, duração {c.duracao_slots * g.minutos_por_slot} min - "
              f"horários {g.formatar_horarios(c.horarios_disponiveis)}")

    print("\nSalas:")
    for s in instancia.salas.values():
        print(f"  {s.id} - horários {g.formatar_horarios(s.horarios_disponiveis)}")

    print("\nAtendimentos:")
    print("  " + ", ".join(f"{a.id}({a.cliente_id})" for a in instancia.atendimentos))


# ------------------------------------------------------------------ execução

def executar(metodo, rastrear=False):
    nome, algoritmo = METODOS[metodo]
    print(f"\n>>> Executando: {nome}")
    try:
        solucao, metricas = algoritmo.resolver(instancia, limite_nos=LIMITE_NOS, rastrear=rastrear)
    except KeyboardInterrupt:
        print("Execução interrompida.")
        return
    resultados[metodo] = (solucao, metricas)
    if solucao is None:
        motivo = "limite de nós atingido" if metricas.interrompida_por_limite else "instância sem solução"
        print(f"Nenhuma solução encontrada ({motivo}).")
    else:
        print(f"Solução encontrada! {len(solucao)} atendimentos agendados.")
    imprimir_metricas(metricas)


def executar_separado(metodo):
    rastrear = False
    if len(instancia.atendimentos) <= 15:
        rastrear = ler_opcao("Mostrar passo a passo da busca? (s/n): ").lower() == "s"
    executar(metodo, rastrear)
    if metodo in resultados and resultados[metodo][0] is not None:
        if ler_opcao("\nVer a agenda? (s/n): ").lower() == "s":
            mostrar_agenda(metodo)


def executar_juntos():
    for metodo in METODOS:
        executar(metodo)
    mostrar_comparacao()


def mostrar_comparacao():
    print("\n--- Comparação dos algoritmos ---")
    print(f"{'Algoritmo':12} {'Tempo (s)':>10} {'Atribuições':>12} {'Backtracks':>11} {'Nós':>8}  Resultado")
    for metodo, (solucao, m) in resultados.items():
        if solucao is not None:
            status = "resolveu"
        elif m.interrompida_por_limite:
            status = "parou no limite"
        else:
            status = "sem solução"
        print(f"{metodo:12} {m.tempo_segundos:10.4f} {m.atribuicoes:12} {m.backtracks:11} "
              f"{m.nos_explorados:8}  {status}")

    if len(resultados) == 2 and all(sol is not None for sol, _ in resultados.values()):
        s, a = resultados["simples"][1], resultados["aprimorado"][1]
        print(f"\nO aprimorado explorou {a.nos_explorados} nós contra {s.nos_explorados} do simples "
              f"e fez {a.backtracks} backtracks contra {s.backtracks}.")


# ------------------------------------------------------------------ resultados

def mostrar_agenda(metodo):
    solucao, metricas = resultados[metodo]
    if solucao is None:
        print("Esse algoritmo não encontrou solução.")
        imprimir_metricas(metricas)
        return
    imprimir_por_profissional(instancia, solucao)
    imprimir_por_horario(instancia, solucao)
    imprimir_por_cliente(instancia, solucao)
    imprimir_metricas(metricas)
    conflitos = validar_solucao(instancia, solucao)
    print(f"\nConflitos encontrados na verificação: {len(conflitos)}")
    for c in conflitos:
        print(f"  - {c}")


def ver_resultados():
    if not resultados:
        print("Nenhum algoritmo foi executado ainda.")
        return
    print("\n1 - Agenda do backtracking simples")
    print("2 - Agenda do backtracking aprimorado")
    print("3 - Tabela comparativa")
    op = ler_opcao()
    metodo = {"1": "simples", "2": "aprimorado"}.get(op)
    if metodo:
        if metodo in resultados:
            mostrar_agenda(metodo)
        else:
            print("Esse algoritmo ainda não foi executado.")
    elif op == "3":
        mostrar_comparacao()


# ------------------------------------------------------------------ alterações

def proximo_id(prefixo, existentes):
    n = 1
    while f"{prefixo}{n}" in existentes:
        n += 1
    return f"{prefixo}{n}"


def alterar_instancia():
    print("\n1 - Acrescentar cliente")
    print("2 - Alterar disponibilidade de um profissional")
    print("3 - Adicionar sala")
    print("4 - Remover sala")
    print("5 - Salvar instância em arquivo")
    print("0 - Voltar")
    op = ler_opcao()

    if op == "1":
        servicos = sorted({e for p in instancia.profissionais.values() for e in p.especialidades})
        print("Serviços: " + ", ".join(servicos))
        servico = input("Serviço necessário: ").strip()
        minutos = instancia.grade.minutos_por_slot
        duracao = ler_numero(f"Duração em minutos, múltiplo de {minutos} (Enter = {minutos}): ", minutos)
        if duracao % minutos:
            print(f"Duração arredondada para {max(1, -(-duracao // minutos)) * minutos} min.")
        duracao = max(1, -(-duracao // minutos))  # arredonda para cima em nº de horários
        horarios = ler_horarios("Horários disponíveis (ex: 08:00-12:00 ou todos): ")
        cid = proximo_id("C", instancia.clientes)
        aid = proximo_id("A", {a.id for a in instancia.atendimentos})
        instancia.clientes[cid] = Cliente(cid, f"Cliente {cid[1:]}", servico, frozenset(horarios), duracao)
        instancia.atendimentos.append(Atendimento(aid, cid))
        print(f"Cliente {cid} adicionado com o atendimento {aid}.")

    elif op == "2":
        pid = input(f"Profissional ({', '.join(instancia.profissionais)}): ").strip().upper()
        if pid not in instancia.profissionais:
            print("Profissional não encontrado.")
            return
        p = instancia.profissionais[pid]
        print(f"Horários atuais: {instancia.grade.formatar_horarios(p.horarios_disponiveis)}")
        horarios = ler_horarios("Novos horários disponíveis (ex: 08:00-12:00, 14:00-16:00): ")
        instancia.profissionais[pid] = replace(p, horarios_disponiveis=frozenset(horarios))
        print("Disponibilidade alterada.")

    elif op == "3":
        sid = proximo_id("S", instancia.salas)
        horarios = ler_horarios("Horários disponíveis da sala (ex: 08:00-18:00 ou todos): ")
        instancia.salas[sid] = Sala(sid, None, frozenset(horarios))
        print(f"Sala {sid} adicionada.")

    elif op == "4":
        sid = input(f"Sala a remover ({', '.join(instancia.salas)}): ").strip().upper()
        if sid not in instancia.salas:
            print("Sala não encontrada.")
            return
        del instancia.salas[sid]
        print(f"Sala {sid} removida.")

    elif op == "5":
        destino = input("Nome do arquivo (ex: dados/instancias/demo2.json): ").strip()
        if destino:
            try:
                salvar_instancia(instancia, destino)
                print(f"Salvo em {destino}.")
            except OSError as e:
                print(f"Erro ao salvar: {e.strerror}")
        return
    else:
        return

    resultados.clear()  # a instância mudou, os resultados antigos não valem mais
    for problema in validar_instancia(instancia):
        print(problema)
    print("Execute os algoritmos novamente para recalcular a solução.")


# ------------------------------------------------------------------ testes

def rodar_testes():
    print("\nRodando os testes (pytest)...\n")
    subprocess.call([sys.executable, "-m", "pytest", "testes", "-v"])


# ------------------------------------------------------------------ menu

def menu_principal():
    global instancia, caminho
    caminho = "dados/instancias/demo.json"
    try:
        instancia = carregar_instancia(caminho)
    except InstanciaInvalidaError:
        instancia = caminho = None

    while True:
        print("\n==========================================")
        print("   AGENDAMENTO DE ATENDIMENTOS - PSR")
        print("==========================================")
        print(f"Instância atual: {caminho or 'nenhuma'}")
        print("1 - Escolher instância")
        print("2 - Ver dados de entrada")
        print("3 - Executar backtracking simples (sem otimização)")
        print("4 - Executar backtracking aprimorado (com otimização)")
        print("5 - Executar os dois juntos e comparar")
        print("6 - Ver resultados")
        print("7 - Alterar instância")
        print("8 - Rodar testes")
        print("0 - Sair")
        op = ler_opcao()

        if op == "0":
            print("Saindo...")
            break
        if op == "1":
            escolher_instancia()
        elif op == "8":
            rodar_testes()
        elif op in ("2", "3", "4", "5", "6", "7"):
            if instancia is None:
                print("Escolha uma instância primeiro (opção 1).")
            elif op == "2":
                mostrar_dados()
            elif op == "3":
                executar_separado("simples")
            elif op == "4":
                executar_separado("aprimorado")
            elif op == "5":
                executar_juntos()
            elif op == "6":
                ver_resultados()
            elif op == "7":
                alterar_instancia()
        else:
            print("Opção inválida.")
            continue
        pausa()
