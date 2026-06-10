import logging
from typing import Tuple, Dict, Set, Any, Optional, List
import warnings

import numpy as np
import pandas as pd
import networkx as nx

try:
    import community as community_louvain
    LOUVAIN_AVAILABLE = True
except ImportError:
    LOUVAIN_AVAILABLE = False

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _apply_louvain(
    G: nx.Graph,
    weight: str = 'weight',
    seed: int = 42
) -> Dict[Any, int]:
    """ Applique l'algorithme Louvain de détection de communautés. """
    if not LOUVAIN_AVAILABLE:
        raise ImportError(
            "python-louvain est requis. Installez avec: pip install python-louvain"
        )

    if G.number_of_nodes() == 0:
        raise ValueError("Graphe vide")

    logger.info("Application de l'algorithme Louvain")

    try:
        partition = community_louvain.best_partition(
            G,
            weight=weight,
            random_state=seed
        )
        logger.info(f"Louvain terminé: {len(set(partition.values()))} communautés détectées")
        return partition
    except Exception as e:
        logger.error(f"Erreur lors de l'application de Louvain: {e}")
        raise


def _apply_greedy_modularity(G: nx.Graph, weight: str = 'weight') -> Dict[Any, int]:
    """ Applique l'algorithme greedy d'optimisation de modularité. """
    if G.number_of_nodes() == 0:
        raise ValueError("Graphe vide")

    logger.info("Application de l'algorithme Greedy Modularity")

    try:
        communities = nx.community.greedy_modularity_communities(G, weight=weight)

        partition = {}
        for community_id, community_set in enumerate(communities):
            for node in community_set:
                partition[node] = community_id

        logger.info(f"Greedy Modularity terminé: {len(communities)} communautés détectées")
        return partition
    except Exception as e:
        logger.error(f"Erreur lors du greedy modularity: {e}")
        raise


def _calculate_modularity(
    G: nx.Graph,
    partition: Dict[Any, int],
    weight: str = 'weight'
) -> float:
    """
    Calcule le score de modularité exact pour une partition donnée.
    Utilise python-louvain si disponible, sinon applique la formule mathématique exacte.
    """
    if not partition:
        raise ValueError("Partition vide")

    logger.debug("Calcul de la modularité")

    try:
        if LOUVAIN_AVAILABLE:
            return float(community_louvain.modularity(partition, G, weight=weight))
        
        # --- CORRECTION DU CALCUL MANUEL (Formule de Newman pour graphe pondéré) ---
        # 1. Calcul de 2m (somme de tous les poids de toutes les arêtes du graphe)
        twice_m = sum(data.get(weight, 1.0) for _, _, data in G.edges(data=True)) * 2.0
        if organizer_total_weight := twice_m == 0:
            return 0.0

        # 2. Calcul du degré pondéré (strength) pour chaque nœud
        degrees = dict(G.degree(weight=weight))

        # 3. Calcul de la modularité en itérant sur les arêtes
        # Pour éviter le biais directionnel, on applique la formule sur les arêtes non-orientées
        # Q = (1/2m) * sum_over_edges_uv (2 * A_uv - (2 * k_u * k_v)/2m)  quand c_u == c_v
        controlled_sum = 0.0
        for u, v, data in G.edges(data=True):
            if partition[u] == partition[v]:
                edge_weight = data.get(weight, 1.0)
                # k_u * k_v / 2m
                null_model = (degrees[u] * degrees[v]) / twice_m
                # Multiplié par 2 car l'arête (u,v) représente (u,v) et (v,u) dans la matrice
                controlled_sum += 2.0 * (edge_weight - null_model)

        # On n'oublie pas de diviser la somme totale par 2m
        modularity = controlled_sum / twice_m

    except Exception as e:
        logger.error(f"Erreur lors du calcul de modularité: {e}")
        modularity = 0.0

    return float(modularity)


def _build_community_dataframe(
    partition: Dict[Any, int],
    G: nx.Graph
) -> pd.DataFrame:
    """ Construit un DataFrame à partir d'une partition de communautés. """
    if not partition:
        raise ValueError("Partition vide")

    logger.debug("Construction du DataFrame de communautés")

    # Utilisation de Pandas pour calculer les tailles de clusters de manière vectorisée
    df = pd.DataFrame(list(partition.items()), columns=['node_id', 'cluster_id'])
    
    # Calcul des tailles
    cluster_sizes = df['cluster_id'].value_counts().to_dict()
    df['cluster_size'] = df['cluster_id'].map(cluster_sizes)

    # Trier par cluster_id, puis par node_id
    df = df.sort_values(['cluster_id', 'node_id']).reset_index(drop=True)

    logger.info(f"DataFrame construit: {len(df)} nœuds dans {len(cluster_sizes)} communautés")
    return df


def detect_communities(
    G: nx.Graph,
    method: str = 'louvain',
    weight: str = 'weight'
) -> Tuple[pd.DataFrame, float, Dict[str, Any]]:
    """
    Détecte les communautés dans un graphe pondéré non-orienté.
    
    CORRECTION DOCSTRING: Retourne un tuple de 3 éléments.
    >>> communities_df, modularity, stats = detect_communities(G, method='louvain')
    """
    logger.info(f"Début de la détection de communautés (méthode: {method})")

    if not isinstance(G, nx.Graph):
        raise TypeError("G doit être un graphe NetworkX")

    if G.number_of_nodes() == 0:
        raise ValueError("Graphe vide")

    logger.info(f"Graphe: {G.number_of_nodes()} nœuds, {G.number_of_edges()} arêtes")

    method = method.lower()
    if method == 'louvain':
        if not LOUVAIN_AVAILABLE:
            logger.warning("Louvain non disponible, utilisation de greedy_modularity")
            method = 'greedy_modularity'
            partition = _apply_greedy_modularity(G, weight=weight)
        else:
            partition = _apply_louvain(G, weight=weight)
    elif method == 'greedy_modularity':
        partition = _apply_greedy_modularity(G, weight=weight)
    else:
        raise ValueError(f"Méthode inconnue: {method}. Utilisez 'louvain' ou 'greedy_modularity'")

    # Calculer la modularité exacte
    modularity = _calculate_modularity(G, partition, weight=weight)
    logger.info(f"Modularité: {modularity:.4f}")

    # Construire le DataFrame
    df_communities = _build_community_dataframe(partition, G)

    # Calculer les statistiques
    community_ids = set(partition.values())

    stats = {
        'num_communities': len(community_ids),
        'avg_community_size': float(df_communities['cluster_size'].mean()),
        'largest_community': int(df_communities['cluster_size'].max()),
        'smallest_community': int(df_communities['cluster_size'].min()),
        'modularity': modularity,
        'method': method,
    }

    logger.info(f"Détection terminée: {stats['num_communities']} communautés, modularité={modularity:.4f}")
    return df_communities, modularity, stats


def save_communities(
    df_communities: pd.DataFrame,
    filepath: str,
    file_format: str = 'csv',  # CORRECTION: Évite d'écraser le mot-clé 'format'
    include_stats: bool = True,
    stats: Optional[Dict[str, Any]] = None,
    **kwargs
) -> None:
    """ Sauvegarde les résultats de détection de communautés en fichier. """
    logger.info(f"Sauvegarde des communautés en {file_format}")

    if file_format.lower() == 'csv':
        output_path = filepath if filepath.endswith('.csv') else f"{filepath}.csv"
        try:
            df_communities.to_csv(output_path, index=False, **kwargs)
            logger.info(f"Communautés sauvegardées: {output_path}")

            if include_stats and stats:
                stats_path = output_path.replace('.csv', '_stats.csv')
                df_stats = pd.DataFrame([stats])
                df_stats.to_csv(stats_path, index=False)
                logger.info(f"Statistiques sauvegardées: {stats_path}")
        except IOError as e:
            logger.error(f"Erreur sauvegarde CSV: {e}")
            raise

    elif file_format.lower() == 'pickle':
        output_path = filepath if filepath.endswith('.pkl') else f"{filepath}.pkl"
        try:
            df_communities.to_pickle(output_path, **kwargs)
            logger.info(f"Communautés sauvegardées: {output_path}")

            if include_stats and stats:
                stats_path = output_path.replace('.pkl', '_stats.pkl')
                pd.Series(stats).to_pickle(stats_path)
                logger.info(f"Statistiques sauvegardées: {stats_path}")
        except IOError as e:
            logger.error(f"Erreur sauvegarde Pickle: {e}")
            raise
    else:
        raise ValueError(f"Format non supporté: {file_format}. Utilisez 'csv' ou 'pickle'")


def get_community_subgraph(G: nx.Graph, partition: Dict[Any, int], community_id: int) -> nx.Graph:
    """ Extrait le sous-graphe d'une communauté spécifique. """
    nodes_in_community = [node for node, comm_id in partition.items() if comm_id == community_id]
    return G.subgraph(nodes_in_community).copy()


def analyze_community_structure(G: nx.Graph, partition: Dict[Any, int], weight: str = 'weight') -> pd.DataFrame:
    """ Analyse la structure interne de chaque communauté. """
    results = []

    for community_id in set(partition.values()):
        subgraph = get_community_subgraph(G, partition, community_id)

        results.append({
            'community_id': community_id,
            'num_nodes': subgraph.number_of_nodes(),
            'num_edges': subgraph.number_of_edges(),
            'density': nx.density(subgraph) if subgraph.number_of_nodes() > 1 else 0,
            'avg_degree': (
                np.mean([d for _, d in subgraph.degree(weight=weight)])
                if subgraph.number_of_nodes() > 0
                else 0
            ),
        })

    df_analysis = pd.DataFrame(results)
    return df_analysis.sort_values('num_nodes', ascending=False).reset_index(drop=True)

#============================================================
import pandas as pd
import networkx as nx
import logging

logging.basicConfig(level=logging.INFO)

def main():
    """
    Main workflow:
    1. Load cleaned_researcher_network_edgelist.csv
    2. Detect communities using Louvain algorithm
    3. Load metrics_results.csv
    4. Merge clusters with metrics
    5. Save merged results to CSV
    """
    
    print("=" * 70)
    print("=== DÉTECTION DE COMMUNAUTÉS ET FUSION AVEC MÉTRIQUES ===")
    print("=" * 70)
    
    # Step 1: Load network data
    print("\n[Step 1] Chargement du réseau depuis 'cleaned_researcher_network_edgelist.csv'...")
    try:
        df_network = pd.read_csv('cleaned_researcher_network_edgelist.csv')
        print(f"✓ Réseau chargé: {len(df_network)} arêtes")
    except FileNotFoundError:
        print("✗ ERREUR: Fichier 'cleaned_researcher_network_edgelist.csv' non trouvé")
        return
    
    # Step 2: Build NetworkX graph
    print("\n[Step 2] Construction du graphe NetworkX...")
    try:
        G = nx.Graph()
        for _, row in df_network.iterrows():
            source = row['Researcher_A']
            target = row['Researcher_B']
            weight = row['Co_Publications']
            G.add_edge(source, target, weight=weight)
        
        print(f"✓ Graphe construit: {G.number_of_nodes()} nœuds, {G.number_of_edges()} arêtes")
    except Exception as e:
        print(f"✗ ERREUR lors de la construction du graphe: {e}")
        return
    
    # Step 3: Detect communities
    print("\n[Step 3] Détection des communautés (algorithme Louvain)...")
    try:
        df_communities, modularity, stats = detect_communities(G, method='louvain', weight='weight')
        print(f"✓ Communautés détectées:")
        print(f"  - Nombre de communautés: {stats['num_communities']}")
        print(f"  - Modularité: {modularity:.4f}")
        print(f"  - Densité intra-communauté: {stats.get('avg_density', 'N/A')}")
    except Exception as e:
        print(f"✗ ERREUR lors de la détection: {e}")
        return
    
    # Step 4: Load metrics results
    print("\n[Step 4] Chargement des métriques depuis 'metrics_results.csv'...")
    try:
        df_metrics = pd.read_csv('metrics_results.csv')
        print(f"✓ Métriques chargées: {len(df_metrics)} chercheurs")
    except FileNotFoundError:
        print("✗ ERREUR: Fichier 'metrics_results.csv' non trouvé")
        return
    
    # Step 5: Prepare data for merging
    print("\n[Step 5] Préparation de la fusion...")
    
    # Rename columns to match
    df_communities_renamed = df_communities.rename(columns={'node_id': 'researcher', 'cluster_id': 'classe'})
    
    # Check column names in metrics
    if 'researcher' in df_metrics.columns:
        pass
    elif 'node_id' in df_metrics.columns:
        df_metrics = df_metrics.rename(columns={'node_id': 'researcher'})
    else:
        print("✗ ERREUR: Colonne 'researcher' ou 'node_id' non trouvée dans metrics_results.csv")
        print(f"Colonnes disponibles: {list(df_metrics.columns)}")
        return
    
    # Step 6: Merge dataframes
    print("\n[Step 6] Fusion des données...")
    try:
        df_merged = pd.merge(
            df_metrics,
            df_communities_renamed[['researcher', 'classe']],
            on='researcher',
            how='left'
        )
        
        # Count researchers without community assignment
        missing_clusters = df_merged['classe'].isna().sum()
        if missing_clusters > 0:
            print(f"⚠ {missing_clusters} chercheurs n'ont pas d'assignation de communauté (isolated nodes)")
            df_merged['classe'] = df_merged['classe'].fillna(-1).astype(int)
        
        print(f"✓ Fusion réussie: {len(df_merged)} chercheurs")
        print(f"  Colonnes résultantes: {list(df_merged.columns)}")
    except Exception as e:
        print(f"✗ ERREUR lors de la fusion: {e}")
        return
    
    # Step 7: Save merged results
    print("\n[Step 7] Sauvegarde des résultats fusionnés...")
    output_filename = "metrics_with_clusters.csv"
    try:
        df_merged.to_csv(output_filename, index=False)
        print(f"✓ Fichier sauvegardé: {output_filename}")
        print(f"  Taille: {len(df_merged)} lignes, {len(df_merged.columns)} colonnes")
    except Exception as e:
        print(f"✗ ERREUR lors de la sauvegarde: {e}")
        return
    
    # Step 8: Display summary
    print("\n" + "=" * 70)
    print("=== RÉSUMÉ DES RÉSULTATS ===")
    print("=" * 70)
    print(f"\nTop 10 chercheurs par PageRank:")
    print(df_merged[['researcher', 'pagerank', 'classe']].head(10).to_string(index=False))
    
    print(f"\n\nDistribution par communauté:")
    community_dist = df_merged['classe'].value_counts().sort_index()
    for classe, count in community_dist.items():
        classe_label = f"Communauté {classe}" if classe != -1 else "Non assigné"
        print(f"  {classe_label}: {count} chercheurs")
    
    print("\n" + "=" * 70)
    print("✓ Traitement terminé avec succès!")
    print("=" * 70)


if __name__ == "__main__":
    main()