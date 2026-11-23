def estrategia(grafo):
    livres = [
        v for v in grafo.nodes
        if grafo.nodes[v]["time"] == 0
    ]

    return max(
        livres,
        key=lambda v: grafo.nodes[v]["peso"]
    )
