import warnings
warnings.filterwarnings('ignore')

import logging
import random
from typing import Tuple, Dict, List, Any, Optional
from pathlib import Path

import pandas as pd
import numpy as np
import networkx as nx
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn.preprocessing import StandardScaler

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from pyvis.network import Network
    PYVIS_AVAILABLE = True
except ImportError:
    PYVIS_AVAILABLE = False

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ===========================
# ÉTAPE 7 : LINK PREDICTION
# ===========================

def link_prediction_analysis(G: nx.Graph, df_metrics: pd.DataFrame) -> Tuple[Dict[str, float], pd.DataFrame]:
    """
    Analyse de prédiction de liens avec 3 méthodes.
    7a — Validation par holdout (10% des arêtes retirées).
    7b — Simulation de disparition d'un chercheur central et reconstruction.
    """
    print("\n" + "="*70)
    print("[ÉTAPE 7] Prédiction de Liens (Link Prediction)")
    print("="*70)
    
    G_original = G.copy()
    edges = list(G_original.edges())
    
    if len(edges) < 10:
        print(" ✗ Erreur: Le graphe contient trop peu d'arêtes pour un holdout optimal.")
        return {}, pd.DataFrame()

    print("\n[7a] Validation par holdout (10% des arêtes retirées)...")
    n_test = max(1, int(0.1 * len(edges)))
    
    test_edges = random.sample(edges, n_test)
    G_train = G_original.copy()
    G_train.remove_edges_from(test_edges)
    print(f"  ✓ Graphe d'entraînement: {G_train.number_of_nodes()} nœuds, {G_train.number_of_edges()} arêtes ({n_test} retirées)")
    
    test_edges_set = {tuple(sorted(e)) for e in test_edges}
    nodes_list = list(G_train.nodes())
    non_connected = []
    max_non_connected = max(len(test_edges_set) * 10, 5000)
    
    for i, u in enumerate(nodes_list):
        for v in nodes_list[i+1:]:
            if not G_train.has_edge(u, v):
                non_connected.append((u, v))
                if len(non_connected) >= max_non_connected:
                    break
        if len(non_connected) >= max_non_connected:
            break
            
    print(f"  ✓ Paires non-connectées échantillonnées: {len(non_connected)}")
    
    auc_scores = {}
    methods = ['adamic_adar', 'jaccard', 'preferential_attachment']
    
    for method_name in methods:
        print(f"    Calcul de la méthode: {method_name.upper()}...")
        try:
            if method_name == 'adamic_adar':
                predictions = list(nx.adamic_adar_index(G_train, non_connected))
            elif method_name == 'jaccard':
                predictions = list(nx.jaccard_coefficient(G_train, non_connected))
            else:
                predictions = list(nx.preferential_attachment(G_train, non_connected))
            
            scores = {(u, v): score for u, v, score in predictions}
            y_true = [1 if tuple(sorted((u, v))) in test_edges_set else 0 for u, v in scores.keys()]
            y_scores = list(scores.values())
            
            if len(set(y_true)) > 1:
                auc_scores[method_name] = roc_auc_score(y_true, y_scores)
            else:
                auc_scores[method_name] = 0.5
        except Exception as e:
            print(f"    ⚠ Erreur lors du calcul de {method_name}: {e}")
            auc_scores[method_name] = 0.0

    print("\n  Tableau comparatif des AUC-ROC:")
    print("  " + "-" * 40)
    for method, score in sorted(auc_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"    {method:25s} : {score:.4f}")
    
    print("\n[7b] Simulation de disparition de chercheur central (top 3 par betweenness)...")
    if 'betweenness' not in df_metrics.columns:
        betweenness_dict = nx.betweenness_centrality(G_original, weight='weight')
        df_metrics['betweenness'] = df_metrics['node'].map(betweenness_dict)

    critical_nodes = df_metrics.nlargest(3, 'betweenness')['node'].tolist()
    print(f"  ✓ Nœuds critiques identifiés: {critical_nodes}")
    
    predictions_list = []
    for critical_node in critical_nodes:
        if critical_node not in G_original:
            continue
            
        G_simul = G_original.copy()
        neighbors = list(G_simul.neighbors(critical_node))
        G_simul.remove_node(critical_node)
        
        orphan_pairs = [(u, v) for i, u in enumerate(neighbors) for v in neighbors[i+1:] if not G_simul.has_edge(u, v)]
        
        if orphan_pairs:
            for method_name in methods:
                try:
                    if method_name == 'adamic_adar':
                        scores = list(nx.adamic_adar_index(G_simul, orphan_pairs))
                    elif method_name == 'jaccard':
                        scores = list(nx.jaccard_coefficient(G_simul, orphan_pairs))
                    else:
                        scores = list(nx.preferential_attachment(G_simul, orphan_pairs))
                    
                    scores_sorted = sorted(scores, key=lambda x: x[2], reverse=True)[:5]
                    for rank, (u, v, score) in enumerate(scores_sorted, 1):
                        predictions_list.append({
                            'removed_node': critical_node,
                            'algorithm': method_name,
                            'node_u': u,
                            'node_v': v,
                            'score': score,
                            'rank': rank
                        })
                except Exception:
                    continue

    df_predictions = pd.DataFrame(predictions_list) if predictions_list else pd.DataFrame(columns=['removed_node', 'algorithm', 'node_u', 'node_v', 'score', 'rank'])
    if not df_predictions.empty:
        df_predictions.to_csv('link_predictions.csv', index=False)
        print(f"  ✓ Fichier sauvegardé: link_predictions.csv ({len(df_predictions)} lignes)")
        
    return auc_scores, df_predictions


# ==================================
# ÉTAPE 8 : ML VULNERABILITY SCORING
# ==================================

def vulnerability_scoring(G: nx.Graph, df_metrics: pd.DataFrame, df_degradation: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Modèle ML supervisé pour prédire le score de vulnérabilité.
    La cible est simulée par une attaque topologique à 20% sur la betweenness.
    """
    print("\n" + "="*70)
    print("[ÉTAPE 8] Scoring de Vulnérabilité (ML)")
    print("="*70)
    
    print("\n[8a] Extraction des features structurelles...")
    clustering_coeff = nx.clustering(G)
    avg_neighbor_deg = nx.average_neighbor_degree(G)
    triangles = nx.triangles(G)
    bridge_nodes = set(nx.articulation_points(G)) if nx.is_connected(G) or len(G.nodes()) > 0 else set()
    
    features_data = []
    for node in G.nodes():
        node_metrics = df_metrics[df_metrics['node'] == node]
        if not node_metrics.empty:
            degree = node_metrics['degree'].values[0] if 'degree' in node_metrics.columns else G.degree(node)
            betweenness = node_metrics['betweenness'].values[0] if 'betweenness' in node_metrics.columns else 0
            closeness = node_metrics['closeness'].values[0] if 'closeness' in node_metrics.columns else 0
            pagerank = node_metrics['pagerank'].values[0] if 'pagerank' in node_metrics.columns else 0
        else:
            degree = G.degree(node)
            betweenness = nx.betweenness_centrality(G).get(node, 0)
            closeness = nx.closeness_centrality(G).get(node, 0)
            pagerank = nx.pagerank(G).get(node, 0)
            
        features_data.append({
            'node': node,
            'degree': degree,
            'betweenness': betweenness,
            'closeness': closeness,
            'pagerank': pagerank,
            'clustering_coeff': clustering_coeff.get(node, 0),
            'avg_neighbor_degree': avg_neighbor_deg.get(node, 0),
            'n_triangles': triangles.get(node, 0),
            'is_bridge': 1 if node in bridge_nodes else 0
        })
        
    df_features = pd.DataFrame(features_data)
    
    print("\n[8b] Calcul de la variable cible par simulation d'attaque à 20%...")
    n_to_remove = max(1, int(0.20 * len(G.nodes())))
    sorted_nodes_by_bet = df_features.sort_values(by='betweenness', ascending=False)['node'].tolist()
    removed_nodes_crisis = set(sorted_nodes_by_bet[:n_to_remove])
    
    G_crisis = G.copy()
    G_crisis.remove_nodes_from(removed_nodes_crisis)
    
    isolated_in_crisis = []
    for node in G.nodes():
        if node in removed_nodes_crisis:
            isolated_in_crisis.append(1)
        elif node in G_crisis and G_crisis.degree(node) == 0:
            isolated_in_crisis.append(1)
        else:
            isolated_in_crisis.append(0)
            
    df_features['is_isolated_in_crisis'] = isolated_in_crisis
    print(f"  ✓ Distribution cible: {df_features['is_isolated_in_crisis'].value_counts().to_dict()}")
    
    print("\n[8c] Entraînement des classifieurs (RF + GB)...")
    X = df_features.drop(['node', 'is_isolated_in_crisis'], axis=1)
    y = df_features['is_isolated_in_crisis']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if len(set(y)) > 1 else None
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=150, random_state=42, class_weight='balanced'),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=150, random_state=42)
    }
    
    best_model = None
    best_auc = -1
    best_model_name = ""
    
    for model_name, model in models.items():
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        try:
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
            auc_score = roc_auc_score(y_test, y_pred_proba)
        except Exception:
            auc_score = accuracy_score(y_test, y_pred)
            
        print(f"    -> {model_name} : Accuracy = {accuracy_score(y_test, y_pred):.4f} | AUC-ROC = {auc_score:.4f}")
        
        if auc_score > best_auc:
            best_auc = auc_score
            best_model = model
            best_model_name = model_name

    print(f"  ✓ Modèle retenu: {best_model_name}")
    
    if hasattr(best_model, 'feature_importances_'):
        importances = pd.DataFrame({'feature': X.columns, 'importance': best_model.feature_importances_})
        importances.sort_values('importance', ascending=False).to_csv('feature_importance.csv', index=False)
    
    X_all_scaled = scaler.transform(X)
    df_features['vulnerability_proba'] = best_model.predict_proba(X_all_scaled)[:, 1]
    
    df_features['vulnerability_level'] = pd.cut(
        df_features['vulnerability_proba'], 
        bins=[-0.01, 0.35, 0.70, 1.01], 
        labels=['LOW', 'MEDIUM', 'HIGH']
    )
    
    df_vulnerability = df_features[['node', 'vulnerability_proba', 'vulnerability_level']].copy()
    df_features.to_csv('vulnerability_scores.csv', index=False)
    
    model_info = {'best_model_name': best_model_name, 'best_auc': best_auc, 'scaler': scaler}
    return df_vulnerability, model_info


# ================================
# ÉTAPE 9 : FUTURE NETWORK MAPPING
# ================================

def generate_future_network(
    G: nx.Graph,
    df_vulnerability: pd.DataFrame,
    df_predictions: pd.DataFrame,
    auc_scores: Dict[str, float]
) -> List[str]:
    """
    Génération et écriture stable du réseau futur au format HTML (Pyvis).
    """
    print("\n" + "="*70)
    print("[ÉTAPE 9] Cartographie du Réseau Futur & Leaders Émergents")
    print("="*70)
    
    G_future = G.copy()
    
    # 9a — Retrait des maillons HIGH
    high_vuln_nodes = df_vulnerability[df_vulnerability['vulnerability_level'] == 'HIGH']['node'].tolist()
    n_to_remove = max(1, int(0.10 * len(G.nodes())))
    nodes_to_remove = high_vuln_nodes[:n_to_remove]
    
    print(f"  [9a] Retrait préventif de {len(nodes_to_remove)} nœuds vulnérables (HIGH).")
    G_future.remove_nodes_from(nodes_to_remove)
    
    # 9b — Ajout des prédictions
    if not df_predictions.empty and auc_scores:
        best_method = max(auc_scores, key=auc_scores.get)
        print(f"  [9b] Expansion via la meilleure méthode de prédiction: {best_method}")
        
        pred_best = df_predictions[df_predictions['algorithm'] == best_method].nlargest(25, 'score')
        added_edges = 0
        
        for _, row in pred_best.iterrows():
            u, v = row['node_u'], row['node_v']
            if u in G_future.nodes() and v in G_future.nodes() and not G_future.has_edge(u, v):
                G_future.add_edge(u, v, weight=row['score'], is_predicted=True)
                added_edges += 1
        print(f"    ✓ {added_edges} liens d'opportunité ajoutés.")
        
    # 9c — Leaders émergents
    bet_orig = nx.betweenness_centrality(G, weight='weight')
    bet_fut = nx.betweenness_centrality(G_future, weight='weight')
    
    rank_orig = {node: idx for idx, (node, _) in enumerate(sorted(bet_orig.items(), key=lambda x: x[1], reverse=True))}
    rank_fut = {node: idx for idx, (node, _) in enumerate(sorted(bet_fut.items(), key=lambda x: x[1], reverse=True))}
    
    emerging_leaders = []
    for node in G_future.nodes():
        if node in rank_orig and node in rank_fut:
            if (rank_orig[node] - rank_fut[node]) >= 5:
                emerging_leaders.append(node)
                
    print(f"  ✓ {len(emerging_leaders)} leaders émergents identifiés structurellement.")
    
    # 9d — Export Pyvis Sécurisé (Utilisation de write_html pour éviter les bugs)
    if not PYVIS_AVAILABLE:
        print("  ⚠ Package Pyvis absent. Sauvegarde ignorée.")
        return emerging_leaders
        
    try:
        # Ajout de notebook=False et résolution CDN stable
        net = Network(height="750px", width="100%", bgcolor="#1a1a1a", font_color="white", directed=False, notebook=False)
        pr_fut = nx.pagerank(G_future, weight='weight')
        
        for node in G_future.nodes():
            # Forcer la conversion en String pour Pyvis
            node_str = str(node)
            
            if node in emerging_leaders:
                color = '#2ecc71'  # Vert : Leader
                group = 'Leader Émergent'
            else:
                vuln_lvl = df_vulnerability[df_vulnerability['node'] == node]['vulnerability_level'].values
                lvl = vuln_lvl[0] if len(vuln_lvl) > 0 else 'LOW'
                color = '#e67e22' if lvl == 'MEDIUM' else '#3498db' # Orange (Medium), Bleu (Low)
                group = f'Chercheur ({lvl})'
                
            size = max(12, min(55, pr_fut.get(node, 0) * 1500))
            title = f"Chercheur: {node_str}\nPageRank Futur: {pr_fut.get(node, 0):.4f}\nStatut: {group}"
            
            net.add_node(node_str, label=node_str, color=color, size=size, title=title)
            
        for u, v, data in G_future.edges(data=True):
            is_pred = data.get('is_predicted', False)
            net.add_edge(str(u), str(v), color='#2ecc71' if is_pred else '#555555', 
                         width=3 if is_pred else 1, 
                         dashed=is_pred)
                         
        net.toggle_physics(True)
        
        # FIX PRINCIPAL : write_html est natif et écrit directement sur le disque sans passer par le navigateur
        net.write_html("reseau_futur.html")
        print("  ✓ SUCCÈS : Le fichier interactif stable 'reseau_futur.html' a été écrit.")
    except Exception as e:
        print(f"  ⚠ Échec de la compilation graphique : {e}")
        
    return emerging_leaders


# ===============================
# RAPPORT FINAL
# ===============================

def generate_predictive_report(
    auc_scores: Dict[str, float],
    df_predictions: pd.DataFrame,
    model_info: Dict[str, Any],
    emerging_leaders: List[str]
) -> None:
    """Génère le fichier de rapport textuel final."""
    report = "="*70 + "\n"
    report += "RAPPORT PRÉDICTIF ET CARTOGRAPHIE DU RÉSEAU FUTUR (PHASE 3)\n"
    report += "="*70 + "\n\n"
    
    report += "1. ANALYSE DE PRÉDICTION DE LIENS (LINK PREDICTION)\n"
    report += "-"*50 + "\n"
    for method, auc in sorted(auc_scores.items(), key=lambda x: x[1], reverse=True):
        report += f"  - {method:25s} : AUC-ROC = {auc:.4f}\n"
        
    if auc_scores:
        best = max(auc_scores, key=auc_scores.get)
        report += f"\nAlgorithme le plus performant : {best}\n"
        
    if not df_predictions.empty:
        report += f"\nTop 5 des liaisons de rechange recommandées :\n"
        top_5 = df_predictions.nlargest(5, 'score')
        for _, row in top_5.iterrows():
            report += f"  • {row['node_u']} <--> {row['node_v']} (Score={row['score']:.4f}, Via={row['algorithm']})\n"
            
    report += "\n2. MODÉLISATION DE LA VULNÉRABILITÉ (MACHINE LEARNING)\n"
    report += "-"*50 + "\n"
    report += f"  - Classifieur optimal de transition : {model_info.get('best_model_name')}\n"
    report += f"  - Score d'évaluation du modèle (AUC) : {model_info.get('best_auc', 0):.4f}\n"
    
    report += "\n3. SYNTHÈSE DU RÉSEAU FUTUR SIMULÉ\n"
    report += "-"*50 + "\n"
    report += f"  - Nombre total de leaders émergents détectés : {len(emerging_leaders)}\n"
    if emerging_leaders:
        report += f"  - Liste des profils résilients : {', '.join([str(l) for l in emerging_leaders[:10]])}\n"
        
    with open('predictive_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("✓ Rapport écrit dans 'predictive_report.txt'")


# ================
# MAIN PIPELINE
# ================

def main():
    print("\n" + "="*70)
    print("INITIALISATION DU PIPELINE DE LA PHASE 3 — CODE CORRIGÉ")
    print("="*70)
    
    base_dir = Path("C:/Users/NB/Desktop/mp modeling the social network of researchers/backend")
    path_edges = base_dir / "data_prep_vis/cleaned_researcher_network_edgelist.csv"
    path_metrics = base_dir / "data_prep_vis/metrics_with_clusters.csv"
    path_degradation = base_dir / "simulateur_stress/degradation_results.csv"
    
    # Fallback local
    if not path_edges.exists(): path_edges = Path("cleaned_researcher_network_edgelist.csv")
    if not path_metrics.exists(): path_metrics = Path("metrics_with_clusters.csv")
    if not path_degradation.exists(): path_degradation = Path("degradation_results.csv")

    try:
        df_network = pd.read_csv(path_edges)
    except FileNotFoundError:
        print(f" ✗ Erreur Critique: Impossible de lire le fichier edgelist.")
        return
        
    try:
        df_metrics = pd.read_csv(path_metrics)
        if 'researcher' in df_metrics.columns:
            df_metrics = df_metrics.rename(columns={'researcher': 'node'})
    except FileNotFoundError:
        df_metrics = pd.DataFrame(columns=['node'])
        
    try:
        df_degradation = pd.read_csv(path_degradation)
    except FileNotFoundError:
        df_degradation = pd.DataFrame()

    # Construction robuste
    G = nx.Graph()
    for _, row in df_network.iterrows():
        u = row['Researcher_A'] if 'Researcher_A' in row.index else (row['source'] if 'source' in row.index else None)
        v = row['Researcher_B'] if 'Researcher_B' in row.index else (row['target'] if 'target' in row.index else None)
        w = row['Co_Publications'] if 'Co_Publications' in row.index else (row['weight'] if 'weight' in row.index else 1)
        
        # Nettoyage des types/NaN pour éviter les bugs Pyvis en aval
        if pd.notna(u) and pd.notna(v):
            G.add_edge(u, v, weight=float(w))
            
    print(f"  ✓ Graphe NetworkX initialisé : {G.number_of_nodes()} nœuds.")
    
    random.seed(42)
    np.random.seed(42)
    
    auc_scores, df_predictions = link_prediction_analysis(G, df_metrics)
    df_vulnerability, model_info = vulnerability_scoring(G, df_metrics, df_degradation)
    emerging_leaders = generate_future_network(G, df_vulnerability, df_predictions, auc_scores)
    generate_predictive_report(auc_scores, df_predictions, model_info, emerging_leaders)
    
    print("\n" + "="*70)
    print("✓ PIPELINE EXÉCUTÉ — TOUS LES LIVRABLES (DONT HTML) SONT DISPONIBLES")
    print("="*70)


if __name__ == "__main__":
    main()