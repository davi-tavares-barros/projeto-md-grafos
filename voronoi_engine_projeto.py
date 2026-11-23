"""
Game Engine - Jogo de Voronoi em Grafos

Interface da estratégia:
    def estrategia(grafo):
        ...
        return vertice

Atributos dos vértices:
    grafo.nodes[v]["peso"]
    grafo.nodes[v]["time"]

time (visão entregue à estratégia):
    0 = livre
    1 = centro do PRÓPRIO time
    2 = centro do ADVERSÁRIO

A engine mantém internamente rótulos fixos (1 = Equipe 1, 2 = Equipe 2),
mas a cada jogada entrega à estratégia uma CÓPIA do grafo já normalizada
para a perspectiva de quem está jogando. Assim, o aluno sempre pode ler
1 como "meu" e 2 como "do oponente", exatamente como no documento, e
qualquer alteração que ele faça na cópia não afeta o tabuleiro real.

A engine executa 6 rodadas, com 3 centros por equipe.
Cada confronto possui duas partidas, alternando quem começa.
"""

import copy
import importlib.util
import random
from pathlib import Path
import networkx as nx

CENTROS_POR_EQUIPE = 3
RODADAS = 2 * CENTROS_POR_EQUIPE


def carregar_estrategia(caminho):
    caminho = Path(caminho)
    spec = importlib.util.spec_from_file_location(caminho.stem, caminho)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar {caminho}")

    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

    if not hasattr(modulo, "estrategia"):
        raise AttributeError(
            f"{caminho} deve possuir uma função estrategia(grafo)."
        )

    estrategia = modulo.estrategia

    if not callable(estrategia):
        raise TypeError(f"estrategia em {caminho} não é uma função.")

    return estrategia


def validar_grafo(grafo):
    if not isinstance(grafo, nx.Graph):
        raise TypeError("O argumento deve ser um networkx.Graph.")

    if grafo.is_directed():
        raise ValueError("O grafo deve ser não direcionado.")

    for v, dados in grafo.nodes(data=True):
        if "peso" not in dados:
            raise ValueError(f"O vértice {v!r} não possui 'peso'.")
        if "time" not in dados:
            raise ValueError(f"O vértice {v!r} não possui 'time'.")
        if dados["time"] not in (0, 1, 2):
            raise ValueError(f"Time inválido no vértice {v!r}.")


def preparar_grafo(grafo):
    validar_grafo(grafo)
    estado = copy.deepcopy(grafo)

    for v in estado.nodes:
        estado.nodes[v]["time"] = 0

    return estado

def preparar_visao(grafo, time):

    visao = copy.deepcopy(grafo)

    # O time 2 enxerga o tabuleiro espelhado.
    if time == 2:
        for v in visao.nodes:
            t = visao.nodes[v]["time"]
            if t == 1:
                visao.nodes[v]["time"] = 2
            elif t == 2:
                visao.nodes[v]["time"] = 1

    return visao


def validar_escolha(grafo, escolha):
    if escolha not in grafo:
        raise ValueError(
            f"A estratégia retornou {escolha!r}, que não existe no grafo."
        )

    if grafo.nodes[escolha]["time"] != 0:
        raise ValueError(
            f"A estratégia escolheu {escolha!r}, que já foi escolhido."
        )


def calcular_distancias(grafo):
    # A matriz de distâncias é interna à engine e nunca é passada à estratégia.
    return dict(nx.all_pairs_shortest_path_length(grafo))


def pontuar(grafo, centros_1, centros_2):
    dist = calcular_distancias(grafo)

    score_1 = 0.0
    score_2 = 0.0
    empatados = []

    for v in grafo.nodes:
        d1 = min(dist[v][c] for c in centros_1)
        d2 = min(dist[v][c] for c in centros_2)
        peso = grafo.nodes[v]["peso"]

        if d1 < d2:
            score_1 += peso
        elif d2 < d1:
            score_2 += peso
        else:
            score_1 += peso / 2
            score_2 += peso / 2
            empatados.append(v)

    return score_1, score_2, empatados


def jogar_partida(grafo_base, estrategia_1, estrategia_2, primeiro):
    grafo = preparar_grafo(grafo_base)

    centros_1 = []
    centros_2 = []

    estrategias = {
        1: estrategia_1,
        2: estrategia_2,
    }

    for rodada in range(RODADAS):
        if primeiro == 1:
            time = 1 if rodada % 2 == 0 else 2
        else:
            time = 2 if rodada % 2 == 0 else 1

        visao = preparar_visao(grafo, time)
        escolha = estrategias[time](visao)

        validar_escolha(grafo, escolha)

        grafo.nodes[escolha]["time"] = time

        if time == 1:
            centros_1.append(escolha)
        else:
            centros_2.append(escolha)

    score_1, score_2, empatados = pontuar(
        grafo, centros_1, centros_2
    )

    return {
        "grafo_final": grafo,
        "centros_time1": centros_1,
        "centros_time2": centros_2,
        "score_time1": score_1,
        "score_time2": score_2,
        "vertices_empatados": empatados,
        "primeiro": primeiro,
    }


def competir(grafo, estrategia_1, estrategia_2):
    """
    Um confronto possui duas partidas:
    1. Equipe 1 começa.
    2. Equipe 2 começa.

    O placar final é a soma das duas partidas.
    """
    partida_1 = jogar_partida(
        grafo, estrategia_1, estrategia_2, primeiro=1
    )

    partida_2 = jogar_partida(
        grafo, estrategia_1, estrategia_2, primeiro=2
    )

    total_1 = partida_1["score_time1"] + partida_2["score_time1"]
    total_2 = partida_1["score_time2"] + partida_2["score_time2"]

    if total_1 > total_2:
        resultado = "Equipe 1"
    elif total_2 > total_1:
        resultado = "Equipe 2"
    else:
        resultado = "Empate"

    return {
        "partida_1": partida_1,
        "partida_2": partida_2,
        "total_time1": total_1,
        "total_time2": total_2,
        "resultado": resultado,
    }


def criar_grafo_exemplo():
    grafo = nx.Graph()

    grafo.add_edges_from([
        ("A", "B"), ("A", "D"), ("B", "C"), ("B", "E"), ("C", "F"),
        ("D", "E"), ("D", "G"), ("E", "F"), ("E", "H"), ("F", "I"),
        ("G", "H"), ("G", "J"), ("H", "I"), ("H", "K"), ("I", "L"),
        ("J", "K"), ("K", "L"), ("L", "M"), ("K", "M")
    ])


    pesos = {
        "A": 2, "B": 5, "C": 3, "D": 4, "E": 1, "F": 2,
        "G": 6, "H": 8, "I": 3, "J": 5, "K": 7, "L": 4, "M": 2
    }

    for v in grafo.nodes:
        grafo.nodes[v]["peso"] = pesos[v]
        grafo.nodes[v]["time"] = 0

    return grafo


if __name__ == "__main__":
    grafo = criar_grafo_exemplo()

    estrategia_1 = carregar_estrategia("aluno_1.py")
    estrategia_2 = carregar_estrategia("aluno_2.py")

    resultado = competir(grafo, estrategia_1, estrategia_2)

    print("Partida 1:", resultado["partida_1"]["centros_time1"],
          resultado["partida_1"]["centros_time2"])
    print("Partida 2:", resultado["partida_2"]["centros_time1"],
          resultado["partida_2"]["centros_time2"])
    print("Placar final:", resultado["total_time1"],
          "x", resultado["total_time2"])
    print("Resultado:", resultado["resultado"])
