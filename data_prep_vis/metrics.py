import logging
from typing import Tuple, Dict, Any, Optional
import warnings

import numpy as np
import pandas as pd
import networkx as nx
from networkx import NetworkXError

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _build_weighted_graph(
    df_edges: pd.DataFrame,
    source_col: str = 'Researcher_A',
    target_col: str = 'Researcher_B',
    weight_col: str = 'Co_Publications'
) -> nx.Graph:
    """
    Construit un graphe pondéré non-orienté à partir d'un DataFrame.
    Calcule également une métrique de 'distance' inverse pour les algos de plus court chemin.
    """
    # Validation des entrées
    required_cols = {source_col, target_col, weight_col}
    if not required_cols.issubset(df_edges.columns):
        missing = required_cols - set(df_edges.columns)
        raise ValueError(f"Colonnes manquantes: {missing}")

    if df_edges.empty:
        raise ValueError("DataFrame des arêtes est vide")

    logger.info(f"Construction du graphe avec {len(df_edges)} arêtes")

    # Nettoyage rapide des poids invalides avant conversion
    df_filtered = df_edges[df_edges[weight_col] > 0].copy()
    if len(df_filtered) < len(df_edges):
        logger.warning(f"{len(df_edges) - len(df_filtered)} arêtes avec des poids invalides (<=0) ont été ignorées.")

    # CALCUL DE LA DISTANCE INVERSE : plus il y a de co-publications, plus la distance est faible
    df_filtered['distance'] = 1.0 / df_filtered[weight_col]

    # Création du graphe ultra-rapide sans iterrows()
    G = nx.from_pandas_edgelist(
        df_filtered,
        source=source_col,
        target=target_col,
        edge_attr=[weight_col, 'distance'],
        create_using=nx.Graph()
    )

    logger.info(
        f"Graphe construit: {G.number_of_nodes()} nœuds, "
        f"{G.number_of_edges()} arêtes"
    )

    return G


def _compute_degree_centrality(G: nx.Graph) -> Dict[Any, float]:
    """ Calcule la centralité de degré pondéré (Poids fort = Centralité forte) """
    logger.debug("Calcul de la centralité de degré")

    # .degree(weight='...') calcule la somme des poids (strength), ce que vous cherchiez à faire
    weighted_degrees = dict(G.degree(weight='Co_Publications'))
    
    max_weighted_degree = max(weighted_degrees.values()) if weighted_degrees else 1

    degree_centrality = {
        node: (deg / max_weighted_degree if max_weighted_degree > 0 else 0)
        for node, deg in weighted_degrees.items()
    }

    return degree_centrality


def _compute_betweenness_centrality(
    G: nx.Graph,
    normalized: bool = True,
    k: Optional[int] = None
) -> Dict[Any, float]:
    """ Calcule la centralité d'intermédiarité en utilisant l'attribut 'distance' """
    logger.debug("Calcul de la centralité d'intermédiarité")

    n_nodes = G.number_of_nodes()
    if k is None and n_nodes > 5000:
        k = min(int(np.sqrt(n_nodes)), 500)
        logger.info(f"Approximation betweenness avec k={k} nœuds ({n_nodes} nœuds total)")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # CORRECTION : Utilisation de 'distance' au lieu de 'weight'
        betweenness = nx.betweenness_centrality(
            G, weight='distance', normalized=normalized, k=k
        )

    return betweenness


def _compute_closeness_centrality(G: nx.Graph) -> Dict[Any, float]:
    """ Calcule la centralité de proximité en utilisant l'attribut 'distance' """
    logger.debug("Calcul de la centralité de proximité")

    # Gestion des graphes non connexes
    if not nx.is_connected(G):
        logger.warning(f"Graphe non connexe ({nx.number_connected_components(G)} composantes). Calcul par composante.")
        largest_cc = max(nx.connected_components(G), key=len)
        G_largest = G.subgraph(largest_cc).copy()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # CORRECTION : Utilisation de distance='distance'
            closeness_largest = nx.closeness_centrality(G_largest, distance='distance')

        closeness = {node: closeness_largest.get(node, 0) for node in G.nodes()}
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # CORRECTION : Utilisation de distance='distance'
            closeness = nx.closeness_centrality(G, distance='distance')

    return closeness


def _compute_pagerank(
    G: nx.Graph,
    alpha: float = 0.85,
    max_iter: int = 100,
    tol: float = 1e-6
) -> Dict[Any, float]:
    """ Calcule PageRank (PageRank utilise nativement le poids : poids fort = forte importance) """
    logger.debug("Calcul du PageRank")

    try:
        # PageRank gère correctement les gros poids comme une forte probabilité de transition
        pagerank = nx.pagerank(
            G.to_directed(),
            alpha=alpha,
            max_iter=max_iter,
            tol=tol,
            weight='Co_Publications'
        )
    except NetworkXError as e:
        logger.error(f"Erreur PageRank: {e}")
        n = G.number_of_nodes()
        pagerank = {node: 1.0 / n for node in G.nodes()}

    return pagerank


def compute_centrality_metrics(
    df_cleaned: pd.DataFrame,
    source_col: str = 'Researcher_A',
    target_col: str = 'Researcher_B',
    weight_col: str = 'Co_Publications'
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """ Calcule les 4 métriques de centralité principale pour un réseau social. """
    logger.info("Début du calcul des métriques de centralité")

    if not isinstance(df_cleaned, pd.DataFrame):
        raise TypeError("df_cleaned doit être un pandas DataFrame")

    if df_cleaned.empty:
        raise ValueError("DataFrame est vide")

    # Construction du graphe
    G = _build_weighted_graph(
        df_cleaned,
        source_col=source_col,
        target_col=target_col,
        weight_col=weight_col
    )

    # Calcul des métriques
    logger.info("Calcul des 4 métriques de centralité")
    degree = _compute_degree_centrality(G)
    betweenness = _compute_betweenness_centrality(G)
    closeness = _compute_closeness_centrality(G)
    pagerank = _compute_pagerank(G)

    # Construction du DataFrame résultat
    results = {
        'researcher': list(G.nodes()),
        'degree': [degree.get(node, 0) for node in G.nodes()],
        'betweenness': [betweenness.get(node, 0) for node in G.nodes()],
        'closeness': [closeness.get(node, 0) for node in G.nodes()],
        'pagerank': [pagerank.get(node, 0) for node in G.nodes()]
    }

    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('pagerank', ascending=False).reset_index(drop=True)

    # Statistiques du réseau (Utilise Co_Publications pour la force des liens)
    stats = {
        'num_nodes': G.number_of_nodes(),
        'num_edges': G.number_of_edges(),
        'density': nx.density(G),
        'avg_degree': np.mean([d for _, d in G.degree(weight='Co_Publications')]),
        'is_connected': nx.is_connected(G),
        'num_components': nx.number_connected_components(G),
        'avg_clustering': nx.average_clustering(G, weight='Co_Publications') if G.number_of_nodes() > 2 else 0.0,
    }

    logger.info(
        f"Métriques calculées: {stats['num_nodes']} nœuds, "
        f"densité={stats['density']:.4f}, "
        f"clustering={stats['avg_clustering']:.4f}"
    )

    return df_results, stats


def save_metrics(
    df_metrics: pd.DataFrame,
    filepath: str,
    file_format: str = 'csv',
    **kwargs
) -> None:
    """ Sauvegarde les résultats des métriques en fichier. """
    if file_format.lower() == 'csv':
        output_path = filepath if filepath.endswith('.csv') else f"{filepath}.csv"
        try:
            df_metrics.to_csv(output_path, index=False, **kwargs)
            logger.info(f"Métriques sauvegardées en CSV: {output_path}")
        except IOError as e:
            logger.error(f"Erreur sauvegarde CSV: {e}")
            raise

    elif file_format.lower() == 'pickle':
        output_path = filepath if filepath.endswith('.pkl') else f"{filepath}.pkl"
        try:
            df_metrics.to_pickle(output_path, **kwargs)
            logger.info(f"Métriques sauvegardées en Pickle: {output_path}")
        except IOError as e:
            logger.error(f"Erreur sauvegarde Pickle: {e}")
            raise
    else:
        raise ValueError(f"Format non supporté: {file_format}. Utilisez 'csv' ou 'pickle'")
    


####test_metrics.py
import pandas as pd
import numpy as np

# On suppose que le code corrigé précédent est enregistré dans un fichier nommé `centrality_analysis.py`
# ou inséré juste au-dessus de ce bloc de test.
# Si vous l'avez mis dans un fichier séparé, décommentez la ligne suivante :
# from centrality_analysis import compute_centrality_metrics, save_metrics

if __name__ == "__main__":
    df = pd.read_csv("cleaned_researcher_network_edgelist.csv")
    print("\n=== 2. EXÉCUTION DU CALCUL DES MÉTRIQUES ===")
    try:
        # Exécution de la fonction principale
        metrics_df, network_stats = compute_centrality_metrics(
            df,
            source_col='Researcher_A',
            target_col='Researcher_B',
            weight_col='Co_Publications'
        )
        
        print("\nCalcul réussi !")
    except Exception as e:
        print(f"Erreur lors du calcul : {e}")
        raise e

    print("-" * 50)
    print("\n=== 3. ANALYSE DES RÉSULTATS ===")
    # On arrondit pour une lecture plus propre
    print(metrics_df.round(4))
    
    print("\n=== 4. STATISTIQUES GLOBALES DU RÉSEAU ===")
    for key, value in network_stats.items():
        print(f"- {key}: {value}")

    print("-" * 50)
    print("\n=== 5. VÉRIFICATION DES LOGIQUES DE VOS ALGORITHMES ===")
    top_researcher = metrics_df.iloc[0]['researcher']
    print(f"» Chercheur le plus influent (PageRank maximum) : {top_researcher}")
    
    # Vérification 2 : Les chercheurs isolés doivent avoir une closeness à 0 
    # car ils ne sont pas dans la composante principale.
    isolated_researcher = metrics_df[metrics_df['researcher'] == 'Chercheur_Isole_1']
    if not isolated_researcher.empty:
        isole_closeness = isolated_researcher['closeness'].values[0]
        print(f"» Closeness de 'Chercheur_Isole_1' (hors composante principale) : {isole_closeness} (Attendu : 0.0)")
    else:
        print("» 'Chercheur_Isole_1' n'existe pas dans les données - Vérification ignorée")

    # Vérification 3 :
    print("\n=== 6. TEST DE LA SAUVEGARDE ===")
    save_metrics(metrics_df, filepath="metrics_results", file_format="csv")
    print("Fichier 'metrics_results.csv' créé avec succès.")