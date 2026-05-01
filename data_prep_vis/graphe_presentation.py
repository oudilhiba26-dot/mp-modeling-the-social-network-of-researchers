import pandas as pd
import networkx as nx
from pyvis.network import Network

# 1. Charger les données
df = pd.read_csv('cleaned_researcher_network_edgelist.csv')

# 2. Création du graphe NetworkX (votre logique actuelle)
G = nx.Graph()
for index, row in df.iterrows():
    G.add_edge(row['Researcher_A'],
               row['Researcher_B'],
               weight=row['Co_Publications'])

# 3. Conversion vers Pyvis pour la dynamique
# On crée une instance Network. 'height' et 'width' pour la taille, 
# 'bgcolor' pour le fond, et 'font_color' pour le texte.
net = Network(height="750px", width="100%", bgcolor="#100f0f", font_color="white")

# Importation du graphe NetworkX
net.from_nx(G)

# 4. Personnalisation esthétique (Optionnel mais recommandé)
for node in net.nodes:
    node['color'] = "#1056b9"
    node['size'] = 20  # Équivalent de node_size

# 5. Activation de la physique interactive
# Cela permet aux nœuds de bouger de façon fluide
net.toggle_physics(True)

# 6. Génération et ouverture du fichier interactif
net.show("reseau_dynamique.html", notebook=False)