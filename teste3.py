import networkx as nx

grafo=nx.Graph()

def estrategia_md(grafo):
    nosso_turno=True
    for u in grafo.nodes:
        if grafo.nodes[u]["time"]==2: #adversário começa
            nosso_turno=False
            grafo.neighbors(u) #
        elif not nosso_turno:
            # mediana ponderada nx.single_source_shortest_path_length(grafo, i) #centro, nosso_turno

#def func_mediana(grafo):
#    for v in 
#               função MEDIANA(grafo)
#               para cada v com time(v) = 0
#               custo(v) ← Σ peso(u) · d(v, u)
#                   ▹ soma sobre todos os vértices u
#               devolva o v de menor custo(v)



