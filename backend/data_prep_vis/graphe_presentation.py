import pandas as pd
import networkx as nx
from pyvis.network import Network
import math

# ==========================================
# 1. CHARGEMENT DES DONNÉES
# ==========================================
df_edges = pd.read_csv('cleaned_researcher_network_edgelist.csv')
df_nodes = pd.read_csv('metrics_with_clusters.csv')

top_researcher = df_nodes.loc[df_nodes['pagerank'].idxmax(), 'researcher']

# ==========================================
# 2. CRÉATION DU GRAPHE NETWORKX
# ==========================================
G = nx.from_pandas_edgelist(
    df_edges,
    source='Researcher_A',
    target='Researcher_B',
    edge_attr=['Co_Publications'],
    create_using=nx.Graph()
)

# ==========================================
# 3. PALETTE DE COULEURS INFINIE (HSL)
# ==========================================
classes_uniques = list(df_nodes['classe'].unique())
num_classes = len(classes_uniques)

color_map = {}
for i, cls in enumerate(classes_uniques):
    hue = int((i * 360) / num_classes) if num_classes > 0 else 0
    color_map[cls] = f"hsl({hue}, 75%, 50%)"

# ==========================================
# 4. NORMALISATION AMPLIFIÉE DES TAILLES
# ==========================================
MIN_NODE_SIZE = 12
MAX_NODE_SIZE = 70

pr_min = df_nodes['pagerank'].min()
pr_max = df_nodes['pagerank'].max()

def obtenir_taille_accentuee(pr_val):
    if pr_max == pr_min:
        return MIN_NODE_SIZE
    linear_norm = (pr_val - pr_min) / (pr_max - pr_min)
    accentuated_norm = math.pow(linear_norm, 2)
    return MIN_NODE_SIZE + (accentuated_norm * (MAX_NODE_SIZE - MIN_NODE_SIZE))

# ==========================================
# 5. INITIALISATION PYVIS
# ==========================================
net = Network(height="700px", width="100%", bgcolor="#100f0f", font_color="white")

# On active le filtre physics
net.show_buttons(filter_=['physics'])

net.from_nx(G)

# ==========================================
# 6. INJECTION DES DONNÉES VISUELLES
# ==========================================
nodes_dict = df_nodes.set_index('researcher').to_dict('index')

for node in net.nodes:
    node_name = node['id']
    if node_name in nodes_dict:
        metrics = nodes_dict[node_name]
        node_class = metrics['classe']
        
        node['color'] = color_map[node_class]
        node['size'] = obtenir_taille_accentuee(metrics['pagerank'])
        
        is_top_str = " 👑 (PLUS INFLUENT)" if node_name == top_researcher else ""
        node['title'] = (
            f"<b>Chercheur :</b> {node_name}{is_top_str}<br>"
            f"<b>Classe :</b> {node_class}<br>"
            f"<b>PageRank :</b> {metrics['pagerank']:.6f}"
        )
        
        if node_name == top_researcher:
            node['label'] = f"⭐ {node_name} ⭐"
            node['borderWidth'] = 5
            node['borderColor'] = "#ffffff"
            node['size'] = MAX_NODE_SIZE + 15

# ==========================================
# 7. FORCE DU STYLE CSS POUR RENDRE LE PANNEAU VISIBLE
# ==========================================
net.toggle_physics(True)
net.barnes_hut(
    gravity=-12000,
    central_gravity=0.2, 
    spring_length=120,
    spring_strength=0.04
)

# Génération temporaire du HTML en mémoire pour modifier son CSS
html_filename = "reseau_dynamique.html"
net.save_graph(html_filename)

# --- Injection CSS Magique ---
# Nous allons lire le fichier généré et forcer le panneau d'options à s'afficher 
# proprement en bas avec un texte noir très lisible et un fond gris clair.
with open(html_filename, 'r', encoding='utf-8') as file:
    html_content = file.read()

# CSS personnalisé pour écraser le conflit de couleur de Pyvis
custom_css = """
<style>
    /* Force le conteneur des boutons à avoir un fond gris clair et du texte noir */
    #config {
        background-color: #f4f6f9 !important;
        color: #333333 !important;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    /* Force les textes des labels à être noirs et bien visibles */
    .vis-configuration-wrapper, .vis-config-item, .vis-config-label {
        color: #111111 !important;
        font-weight: bold !important;
    }
</style>
</head>
"""

# On insère notre CSS juste avant la fin de la balise </head>
html_content = html_content.replace("</head>", custom_css)

# Réécriture du fichier corrigé
with open(html_filename, 'w', encoding='utf-8') as file:
    file.write(html_content)

print(f"Fichier '{html_filename}' généré avec un panneau de contrôle de la physique hautement visible !")