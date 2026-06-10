import pandas as pd
import networkx as nx
from pyvis.network import Network
import math

# ==========================================
# 1. CHARGEMENT DES DONNÉES
# ==========================================
df_edges = pd.read_csv('cleaned_researcher_network_edgelist.csv')
df_nodes = pd.read_csv('metrics_with_clusters.csv')

# Trouver la star du réseau
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
# 3. PALETTE DE COULEURS INFINIE (GÉNÉRATEUR HSL)
# ==========================================
classes_uniques = list(df_nodes['classe'].unique())
num_classes = len(classes_uniques)

color_map = {}
for i, cls in enumerate(classes_uniques):
    # On divise le cercle chromatique (360 degrés) équitablement par le nombre de classes
    hue = int((i * 360) / num_classes) if num_classes > 0 else 0
    # Saturation à 75% et Luminosité à 50% pour des couleurs vives sur fond sombre
    color_map[cls] = f"hsl({hue}, 75%, 50%)"

# ==========================================
# 4. NORMALISATION AMPLIFIÉE DES TAILLES (Min-Max + Puissance)
# ==========================================
# Définir les bornes de tailles souhaitées dans l'interface Pyvis
MIN_NODE_SIZE = 12
MAX_NODE_SIZE = 70

# On récupère les valeurs min et max réelles du PageRank pour calibrer l'échelle
pr_min = df_nodes['pagerank'].min()
pr_max = df_nodes['pagerank'].max()

def obtenir_taille_accentuee(pr_val):
    """ Calcule une taille fortement contrastée grâce à une échelle de puissance """
    if pr_max == pr_min:
        return MIN_NODE_SIZE
    
    # 1. Normalisation linéaire entre 0 et 1
    linear_norm = (pr_val - pr_min) / (pr_max - pr_min)
    
    # 2. Application d'une puissance (ex: au carré ou cube) 
    # Cela écrase les petites valeurs et fait exploser les valeurs dominantes
    accentuated_norm = math.pow(linear_norm, 2)  # Changez le '2' en '3' pour encore plus de contraste
    
    # 3. Projection sur notre plage de tailles Pyvis (MIN_NODE_SIZE à MAX_NODE_SIZE)
    return MIN_NODE_SIZE + (accentuated_norm * (MAX_NODE_SIZE - MIN_NODE_SIZE))

# ==========================================
# 5. INITIALISATION ET INJECTION PYVIS
# ==========================================
net = Network(height="750px", width="100%", bgcolor="#100f0fff", font_color="white")
net.from_nx(G)

nodes_dict = df_nodes.set_index('researcher').to_dict('index')

for node in net.nodes:
    node_name = node['id']
    
    if node_name in nodes_dict:
        metrics = nodes_dict[node_name]
        node_class = metrics['classe']
        
        # A. Couleur HSL dynamique unique
        node['color'] = color_map[node_class]
        
        # B. Taille fortement accentuée
        node['size'] = obtenir_taille_accentuee(metrics['pagerank'])
        
        # C. Infobulle au survol
        is_top_str = " 👑 (PLUS INFLUENT)" if node_name == top_researcher else ""
        node['title'] = (
            f"<b>Chercheur :</b> {node_name}{is_top_str}<br>"
            f"<b>Classe :</b> {node_class}<br>"
            f"<b>PageRank :</b> {metrics['pagerank']:.6f}"
        )
        
        # D. Traitement spécial pour le leader (Mise en valeur extrême)
        if node_name == top_researcher:
            node['label'] = f"⭐ {node_name} ⭐"
            node['borderWidth'] = 5
            node['borderColor'] = "#ffffff"
            node['size'] = MAX_NODE_SIZE + 15  # Forcer le leader à dépasser le plafond maximum

# ==========================================
# 6. CONFIGURATION PHYSIQUE DU RENDU
# ==========================================
net.toggle_physics(True)

# Important : On ajuste la physique pour éviter que les très gros nœuds ne chevauchent les petits
net.barnes_hut(
    gravity=-12000,          # Répulsion plus forte pour espacer les nœuds
    central_gravity=0.2, 
    spring_length=120,        # Ressorts légèrement plus longs pour aérer le graphe
    spring_strength=0.04
)


# CETTE LIGNE AJOUTE LE PANNEAU DE CONFIGURATION SUR L'INTERFACE INTERACTIVE
# On cible spécifiquement la section "physics" pour permettre d'activer/désactiver le mouvement
net.show_buttons(filter_=['physics'])

# Génération du fichier
net.show("reseau_dynamique.html", notebook=False)