import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

#charger les donnees
df = pd.read_csv('cleaned_researcher_network_edgelist.csv')

#creation du graphe
G = nx.Graph()

#ajout des noeuds et des aretes
for index, row in df.iterrows():
    G.add_edge(row['Researcher_A'],
               row['Researcher_B'],
               weight=row['Co_Publications'])

#visualisation du graphe
plt.figure(figsize=(12, 8), facecolor='#f7f7f7')
ax = plt.gca()
ax.set_facecolor('#f7f7f7')

#calcul de la position des noeuds ***V.A.
pos = nx.spring_layout(G, k=0.6, seed=42)

# Dessin des composants du graphe
nx.draw_networkx_nodes(G, pos, node_size=800, node_color='#10b981', alpha=0.9)
weights = [G[u][v]['weight'] for u, v in G.edges()]
nx.draw_networkx_edges(G, pos, width=weights, edge_color='black', alpha=0.4)
nx.draw_networkx_labels(G, pos, font_size=9, font_color='black')

plt.title("Visualisation du Réseau des chercheurs", color='red', pad=30)
plt.axis('off')

# Sauvegarde du résultat
plt.savefig('graphe_chercheurs.png', facecolor='white')
plt.show()