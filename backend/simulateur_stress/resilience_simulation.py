"""
Phase 2 : Pipeline de simulation de résilience réseau

Ce script implémente un pipeline complet de simulation d'attaques et d'analyse
de résilience d'un réseau social de chercheurs. Trois stratégies d'attaque sont
testées : aléatoire, basée sur le degré, et basée sur l'intermédiarité.

Sorties :
    - degradation_results.csv : résultats détaillés des simulations
    - degradation_curves.html : visualisation interactive Plotly
    - degradation_curves.png : visualisation statique PNG
    - resilience_report.txt : rapport texte synthétique
"""

import logging
import warnings
from typing import Tuple, Dict, List, Any
from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx

# Tentative d'import de plotly (fallback matplotlib)
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    import matplotlib.pyplot as plt

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ignorer certains avertissements NetworkX
warnings.filterwarnings('ignore', category=DeprecationWarning)


# ============================================================================
# ÉTAPE 4 : PROTOCOLES D'ATTAQUE (3 stratégies)
# ============================================================================

def random_attack(G: nx.Graph, n: int) -> nx.Graph:
    """
    Attaque aléatoire : supprime n nœuds choisis aléatoirement.
    
    Simule les retraites, changements de carrière, etc.
    
    Args:
        G: Graphe NetworkX original
        n: Nombre de nœuds à supprimer
        
    Returns:
        Copie du graphe avec n nœuds supprimés aléatoirement
    """
    G_copy = G.copy()
    nodes_to_remove = np.random.choice(list(G_copy.nodes()), size=min(n, G_copy.number_of_nodes()), replace=False)
    G_copy.remove_nodes_from(nodes_to_remove)
    return G_copy


def degree_attack(G: nx.Graph, n: int) -> nx.Graph:
    """
    Attaque basée sur le degré : supprime les n nœuds avec le degré le plus élevé.
    
    Simule le recrutement des "stars" par des institutions concurrentes.
    
    Args:
        G: Graphe NetworkX original
        n: Nombre de nœuds à supprimer
        
    Returns:
        Copie du graphe avec les n nœuds de degré maximal supprimés
    """
    G_copy = G.copy()
    degrees = dict(G_copy.degree(weight='weight'))
    # Trier par degré décroissant
    sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
    nodes_to_remove = [node for node, _ in sorted_nodes[:min(n, len(sorted_nodes))]]
    G_copy.remove_nodes_from(nodes_to_remove)
    return G_copy


def betweenness_attack(G: nx.Graph, n: int) -> nx.Graph:
    """
    Attaque basée sur l'intermédiarité : supprime les n nœuds avec la plus haute betweenness.
    
    Simule une stratégie adversariale visant à fragmenter le réseau en coupant les ponts.
    
    Args:
        G: Graphe NetworkX original
        n: Nombre de nœuds à supprimer
        
    Returns:
        Copie du graphe avec les n nœuds de betweenness maximal supprimés
    """
    G_copy = G.copy()
    betweenness = nx.betweenness_centrality(G_copy, weight='weight')
    # Trier par betweenness décroissante
    sorted_nodes = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
    nodes_to_remove = [node for node, _ in sorted_nodes[:min(n, len(sorted_nodes))]]
    G_copy.remove_nodes_from(nodes_to_remove)
    return G_copy


# ============================================================================
# UTILITAIRES POUR LE CALCUL DES MÉTRIQUES
# ============================================================================

def get_giant_component(G: nx.Graph) -> nx.Graph:
    """
    Extrait la plus grande composante connexe (GCC) du graphe.
    
    Args:
        G: Graphe NetworkX
        
    Returns:
        Sous-graphe contenant la GCC
    """
    if G.number_of_nodes() == 0:
        return G.copy()
    
    largest_cc = max(nx.connected_components(G), key=len)
    return G.subgraph(largest_cc).copy()


def calculate_metrics(G: nx.Graph) -> Dict[str, Any]:
    """
    Calcule les 4 métriques de résilience pour un graphe.
    
    Args:
        G: Graphe NetworkX
        
    Returns:
        Dict avec clés : gcc_size, n_components, diameter, density
    """
    metrics = {}
    
    # 1. Taille de la composante géante
    if G.number_of_nodes() > 0:
        gcc = get_giant_component(G)
        metrics['gcc_size'] = gcc.number_of_nodes()
    else:
        metrics['gcc_size'] = 0
    
    # 2. Nombre de composantes connexes
    metrics['n_components'] = nx.number_connected_components(G) if G.number_of_nodes() > 0 else 0
    
    # 3. Diamètre (calculé sur la GCC pour éviter les erreurs)
    if metrics['gcc_size'] > 1:
        try:
            gcc = get_giant_component(G)
            metrics['diameter'] = nx.diameter(gcc)
        except Exception:
            metrics['diameter'] = np.inf
    else:
        metrics['diameter'] = 0 if metrics['gcc_size'] == 1 else np.nan
    
    # 4. Densité du graphe
    metrics['density'] = nx.density(G)
    
    return metrics


# ============================================================================
# ÉTAPE 5 : AUTOMATISATION DE LA DÉGRADATION PROGRESSIVE
# ============================================================================

def simulate_degradation(
    G: nx.Graph,
    attack_func,
    steps: List[int] = None,
    attack_name: str = "unknown"
) -> pd.DataFrame:
    """
    Simule la dégradation progressive du réseau via attaques itératives.
    
    Applique l'attaque de façon itérative en supprimant k% des nœuds du graphe
    courant à chaque étape. Recalcule les 4 métriques après chaque suppression.
    
    Args:
        G: Graphe NetworkX original
        attack_func: Fonction d'attaque (random_attack, degree_attack, ou betweenness_attack)
        steps: Liste des pourcentages à tester [1, 5, 10, 20, ...]
        attack_name: Nom de la stratégie d'attaque (pour logging/output)
        
    Returns:
        DataFrame avec colonnes : step, pct_removed, gcc_size, n_components, diameter, density, attack_type
    """
    if steps is None:
        steps = [1, 5, 10, 20]
    
    logger.info(f"Simulation de dégradation : {attack_name}")
    
    results = []
    G_current = G.copy()
    initial_nodes = G.number_of_nodes()
    
    # Étape 0 : état initial
    metrics_initial = calculate_metrics(G_current)
    results.append({
        'step': 0,
        'pct_removed': 0,
        'gcc_size': metrics_initial['gcc_size'],
        'n_components': metrics_initial['n_components'],
        'diameter': metrics_initial['diameter'],
        'density': metrics_initial['density'],
        'attack_type': attack_name
    })
    
    # Appliquer les attaques itérativement
    for pct in steps:
        # Calculer le nombre de nœuds à supprimer à cette étape
        n_to_remove = max(1, int(initial_nodes * pct / 100))
        
        # Appliquer l'attaque
        G_current = attack_func(G_current, n_to_remove)
        
        # Recalculer les métriques
        metrics = calculate_metrics(G_current)
        
        results.append({
            'step': len(results),
            'pct_removed': pct,
            'gcc_size': metrics['gcc_size'],
            'n_components': metrics['n_components'],
            'diameter': metrics['diameter'],
            'density': metrics['density'],
            'attack_type': attack_name
        })
        
        logger.info(f"  Step {pct}%: GCC={metrics['gcc_size']}, Components={metrics['n_components']}, Density={metrics['density']:.4f}")
    
    return pd.DataFrame(results)


# ============================================================================
# ÉTAPE 6 : SIGNAUX D'ALERTE, POINTS DE BASCULE ET RAPPORT
# ============================================================================

def detect_tipping_points(df_results: pd.DataFrame, threshold_pct: float = 0.20) -> Dict[str, int]:
    """
    Détecte le point de bascule pour chaque type d'attaque.
    
    Le point de bascule est le premier seuil où la taille de la GCC chute
    de plus de threshold_pct (20% par défaut) par rapport à l'étape précédente.
    
    Args:
        df_results: DataFrame des résultats de dégradation
        threshold_pct: Seuil de chute relative en pourcentage
        
    Returns:
        Dict mappant attack_type -> pct_removed au tipping point (ou -1 si absent)
    """
    tipping_points = {}
    
    for attack_type in df_results['attack_type'].unique():
        df_attack = df_results[df_results['attack_type'] == attack_type].sort_values('pct_removed')
        
        tipping_point = -1
        for i in range(1, len(df_attack)):
            prev_gcc = df_attack.iloc[i-1]['gcc_size']
            curr_gcc = df_attack.iloc[i]['gcc_size']
            
            if prev_gcc > 0:
                relative_drop = (prev_gcc - curr_gcc) / prev_gcc
                if relative_drop > threshold_pct:
                    tipping_point = df_attack.iloc[i]['pct_removed']
                    break
        
        tipping_points[attack_type] = tipping_point
    
    return tipping_points


def plot_degradation_curves(df_results: pd.DataFrame, output_html: str = "degradation_curves.html"):
    """
    Génère un graphique multi-courbes montrant l'évolution de la GCC.
    
    Utilise Plotly pour l'interactivité (fallback Matplotlib si Plotly indisponible).
    
    Args:
        df_results: DataFrame des résultats
        output_html: Chemin du fichier HTML de sortie
    """
    logger.info("Génération des courbes de dégradation")
    
    if PLOTLY_AVAILABLE:
        fig = go.Figure()
        
        for attack_type in df_results['attack_type'].unique():
            df_attack = df_results[df_results['attack_type'] == attack_type]
            df_attack = df_attack.sort_values('pct_removed')
            
            fig.add_trace(go.Scatter(
                x=df_attack['pct_removed'],
                y=df_attack['gcc_size'],
                mode='lines+markers',
                name=attack_type,
                line=dict(width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title="Résilience du réseau : Évolution de la composante géante",
            xaxis_title="Pourcentage de nœuds supprimés (%)",
            yaxis_title="Taille de la composante géante (nœuds)",
            hovermode='x unified',
            template='plotly_white',
            font=dict(size=12),
            height=600,
            width=1000
        )
        
        fig.write_html(output_html)
        logger.info(f"Graphique Plotly sauvegardé : {output_html}")
        
        # Génération PNG
        try:
            output_png = output_html.replace('.html', '.png')
            fig.write_image(output_png)
            logger.info(f"Graphique PNG sauvegardé : {output_png}")
        except Exception as e:
            logger.warning(f"Impossible de sauvegarder PNG : {e}")
    
    else:
        # Fallback matplotlib
        logger.warning("Plotly non disponible, utilisation de Matplotlib")
        plt.figure(figsize=(12, 7))
        
        for attack_type in df_results['attack_type'].unique():
            df_attack = df_results[df_results['attack_type'] == attack_type]
            df_attack = df_attack.sort_values('pct_removed')
            plt.plot(df_attack['pct_removed'], df_attack['gcc_size'], 
                    marker='o', linewidth=2, label=attack_type)
        
        plt.xlabel('Pourcentage de nœuds supprimés (%)', fontsize=12)
        plt.ylabel('Taille de la composante géante (nœuds)', fontsize=12)
        plt.title('Résilience du réseau : Évolution de la composante géante', fontsize=14)
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        
        output_png = "degradation_curves.png"
        plt.savefig(output_png, dpi=150, bbox_inches='tight')
        logger.info(f"Graphique Matplotlib sauvegardé : {output_png}")
        plt.close()


def generate_resilience_report(
    G_original: nx.Graph,
    df_results: pd.DataFrame,
    tipping_points: Dict[str, int],
    output_file: str = "resilience_report.txt"
):
    """
    Génère un rapport texte synthétique avant/après.
    
    Args:
        G_original: Graphe original (avant attaques)
        df_results: DataFrame des résultats
        tipping_points: Dict des points de bascule détectés
        output_file: Chemin du fichier rapport
    """
    logger.info(f"Génération du rapport : {output_file}")
    
    # Métriques initiales
    metrics_initial = calculate_metrics(G_original)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RAPPORT DE RÉSILIENCE RÉSEAU - PHASE 2\n")
        f.write("=" * 80 + "\n\n")
        
        # Section 1 : Métriques initiales
        f.write("1. MÉTRIQUES INITIALES DU RÉSEAU (AVANT ATTAQUE)\n")
        f.write("-" * 80 + "\n")
        f.write(f"  Nombre de nœuds         : {G_original.number_of_nodes()}\n")
        f.write(f"  Nombre d'arêtes         : {G_original.number_of_edges()}\n")
        f.write(f"  Densité                 : {metrics_initial['density']:.4f}\n")
        f.write(f"  Taille GCC              : {metrics_initial['gcc_size']} ({100*metrics_initial['gcc_size']/G_original.number_of_nodes():.1f}%)\n")
        f.write(f"  Nombre de composantes   : {metrics_initial['n_components']}\n")
        f.write(f"  Diamètre (GCC)          : {metrics_initial['diameter']}\n")
        f.write("\n")
        
        # Section 2 : Résultats par stratégie
        f.write("2. RÉSULTATS DÉTAILLÉS PAR STRATÉGIE D'ATTAQUE\n")
        f.write("-" * 80 + "\n\n")
        
        for attack_type in df_results['attack_type'].unique():
            df_attack = df_results[df_results['attack_type'] == attack_type]
            tipping = tipping_points.get(attack_type, -1)
            
            f.write(f"\n[{attack_type.upper()}]\n")
            f.write(f"{'Suppression':<15} {'GCC':<10} {'Composantes':<15} {'Diamètre':<12} {'Densité':<10}\n")
            f.write("-" * 65 + "\n")
            
            for _, row in df_attack.iterrows():
                pct = row['pct_removed']
                gcc = int(row['gcc_size'])
                comp = int(row['n_components'])
                diam = f"{row['diameter']:.1f}" if pd.notna(row['diameter']) and row['diameter'] != np.inf else "∞"
                dens = f"{row['density']:.4f}"
                
                marker = " <-- TIPPING POINT" if pct == tipping else ""
                f.write(f"{pct}%{'':<11} {gcc:<10} {comp:<15} {diam:<12} {dens:<10}{marker}\n")
            
            if tipping > 0:
                f.write(f"\n  ⚠ Point de bascule détecté : {tipping}% de suppression\n")
            else:
                f.write(f"\n  ℹ Aucun point de bascule détecté (chute < 20% à chaque étape)\n")
            f.write("\n")
        
        # Section 3 : Analyse comparative
        f.write("\n" + "=" * 80 + "\n")
        f.write("3. ANALYSE COMPARATIVE\n")
        f.write("-" * 80 + "\n\n")
        
        # Tableau résumé final (% suppression maximal)
        f.write("État du réseau à suppression maximale (avant disparition complète) :\n")
        f.write(f"{'Stratégie':<25} {'GCC':<10} {'Composantes':<15} {'Densité':<10}\n")
        f.write("-" * 60 + "\n")
        
        for attack_type in df_results['attack_type'].unique():
            df_attack = df_results[df_results['attack_type'] == attack_type]
            last_row = df_attack.iloc[-1]
            
            gcc = int(last_row['gcc_size'])
            comp = int(last_row['n_components'])
            dens = f"{last_row['density']:.4f}"
            
            f.write(f"{attack_type:<25} {gcc:<10} {comp:<15} {dens:<10}\n")
        
        # Conclusion
        f.write("\n" + "=" * 80 + "\n")
        f.write("4. CONCLUSION\n")
        f.write("-" * 80 + "\n")
        
        # Déterminer la stratégie la plus dévastatrice
        final_states = {}
        for attack_type in df_results['attack_type'].unique():
            df_attack = df_results[df_results['attack_type'] == attack_type]
            final_gcc = df_attack.iloc[-1]['gcc_size']
            final_states[attack_type] = final_gcc
        
        worst_attack = min(final_states, key=final_states.get)
        
        f.write(f"\nStratégie la plus dévastatrice : {worst_attack.upper()}\n\n")
        
        if "degree" in worst_attack.lower():
            f.write("  Analyse : L'attaque par degré est la plus efficace car elle cible\n")
            f.write("  directement les nœuds les plus connectés (hubs). En supprimant ces\n")
            f.write("  nœuds cruciaux, le réseau se fragmente rapidement, réduisant drastiquement\n")
            f.write("  la taille de la composante géante.\n")
        elif "betweenness" in worst_attack.lower():
            f.write("  Analyse : L'attaque par betweenness est la plus efficace car elle cible\n")
            f.write("  les nœuds qui servent de ponts entre communautés. Leur suppression\n")
            f.write("  isole rapidement les groupes et fragmente le réseau en petites composantes.\n")
        else:
            f.write("  Analyse : L'attaque aléatoire pose une menace homogène au réseau.\n")
            f.write("  Bien que moins ciblée que les autres stratégies, elle montre la\n")
            f.write("  robustesse globale du réseau face à des défaillances non-structurées.\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"Rapport généré le : {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n")
    
    logger.info(f"Rapport sauvegardé : {output_file}")


# ============================================================================
# BLOC PRINCIPAL
# ============================================================================

def main():
    """
    Exécute le pipeline complet de simulation de résilience.
    """
    print("=" * 80)
    print("PHASE 2 : PIPELINE DE SIMULATION DE RÉSILIENCE RÉSEAU")
    print("=" * 80)
    
    # ========== Étape 1 : Chargement des données ==========
    print("\n[Étape 1] Chargement des données...")
    
    try:
        df_network = pd.read_csv(r"C:\Users\NB\Desktop\mp modeling the social network of researchers\backend\data_prep_vis\cleaned_researcher_network_edgelist.csv")
        print(f"✓ Réseau chargé : {len(df_network)} arêtes")
    except FileNotFoundError:
        print("✗ ERREUR : Fichier 'cleaned_researcher_network_edgelist.csv' non trouvé")
        return
    
    # ========== Étape 2 : Construction du graphe ==========
    print("\n[Étape 2] Construction du graphe NetworkX...")
    # renommer les colonnes pour plus de clarté
    source_col, target_col = 'Researcher_A', 'Researcher_B'

    weight_col = 'Co_Publications'
    
    
    # methode optimale pour construire le graphe à partir d'un DataFrame de taille grande
    G = nx.from_pandas_edgelist(
    df_network,
    source=source_col,
    target=target_col,
    edge_attr=[weight_col],
    create_using=nx.Graph()
)
    
    print(f"✓ Graphe construit : {G.number_of_nodes()} nœuds, {G.number_of_edges()} arêtes")
    
    # ========== Étape 3 : Définir les stratégies d'attaque ==========
    print("\n[Étape 3] Définition des stratégies d'attaque...")
    
    attack_strategies = [
        (random_attack, "random_attack"),
        (degree_attack, "degree_attack"),
        (betweenness_attack, "betweenness_attack")
    ]
    
    print(f"✓ {len(attack_strategies)} stratégies d'attaque définies")
    
    # ========== Étape 4 : Simulation de dégradation ==========
    print("\n[Étape 4] Simulation de dégradation progressive...")
    
    np.random.seed(42)  # Reproductibilité
    
    all_results = []
    for attack_func, attack_name in attack_strategies:
        df_degradation = simulate_degradation(
            G,
            attack_func,
            steps=[1, 5, 10, 20, 30, 40, 50],
            attack_name=attack_name
        )
        all_results.append(df_degradation)
    
    df_results = pd.concat(all_results, ignore_index=True)
    print(f"✓ Dégradation simulée : {len(df_results)} entrées")
    
    # ========== Étape 5 : Sauvegarde des résultats ==========
    print("\n[Étape 5] Sauvegarde des résultats...")
    
    df_results.to_csv('degradation_results.csv', index=False)
    print("✓ Fichier 'degradation_results.csv' créé")
    
    # ========== Étape 6 : Génération des courbes ==========
    print("\n[Étape 6] Génération des courbes de dégradation...")
    
    plot_degradation_curves(df_results, "degradation_curves.html")
    print("✓ Courbes générées")
    
    # ========== Étape 7 : Détection des points de bascule ==========
    print("\n[Étape 7] Détection des points de bascule...")
    
    tipping_points = detect_tipping_points(df_results, threshold_pct=0.20)
    for attack_type, tipping in tipping_points.items():
        if tipping > 0:
            print(f"  → {attack_type}: {tipping}%")
        else:
            print(f"  → {attack_type}: pas de point de bascule détecté")
    
    # ========== Étape 8 : Génération du rapport ==========
    print("\n[Étape 8] Génération du rapport de résilience...")
    
    generate_resilience_report(G, df_results, tipping_points, "resilience_report.txt")
    print("✓ Fichier 'resilience_report.txt' créé")
    
    # ========== Résumé final ==========
    print("\n" + "=" * 80)
    print("✓ PIPELINE COMPLÉTÉ AVEC SUCCÈS")
    print("=" * 80)
    print("\nFichiers générés :")
    print("  1. degradation_results.csv - Données détaillées")
    print("  2. degradation_curves.html - Visualisation interactive")
    print("  3. degradation_curves.png - Visualisation statique")
    print("  4. resilience_report.txt - Rapport synthétique")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
