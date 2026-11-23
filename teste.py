import networkx as nx

grafo = nx.Graph()


grafo.add_edges_from([
    ("A", "B"),
    ("A", "D"),
    ("B", "C"),
    ("B", "E"),
    ("C", "F"),
    ("D", "E"),
    ("E", "F")
])

somas=dict()
for node in grafo.nodes:
    somas.setdefault(node, 0)

for node in grafo.nodes:
    somas[node]=sum(j for j in nx.single_source_shortest_path_length(grafo, node).values())

menor=min(somas.values())

menor_node=[]

for i in somas.keys():
    if somas[i]==menor:
        menor_node.append(i)
print(menor_node)    

    
    