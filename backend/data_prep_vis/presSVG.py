import pandas as pd
import networkx as nx
import plotly.graph_objects as go

# 1. Charger les données
df = pd.read_csv('cleaned_researcher_network_edgelist.csv')
G = nx.from_pandas_edgelist(df, 'Researcher_A', 'Researcher_B', ['Co_Publications'])

# 2. Calculer les positions (Spring layout)
pos = nx.spring_layout(G, k=0.6, seed=42)

# 3. Préparer les arrêtes (Edges)
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=1, color='#888'),
    hoverinfo='none',
    mode='lines')

# 4. Préparer les nœuds (Nodes)
node_x = []
node_y = []
node_text = []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(f"Chercheur: {node}")

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    text=[n for n in G.nodes()], # Affiche les noms
    textposition="top center",
    hoverinfo='text',
    hovertext=node_text,
    marker=dict(size=15, color='#10b981', line_width=2))

# 5. Créer la figure dynamique
fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='Réseau dynamique des chercheurs',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=0, l=0, r=0, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

# Affichage interactif
fig.show()

# Pour exporter en image SVG statique de haute qualité si besoin :
fig.write_image("graphe.svg")