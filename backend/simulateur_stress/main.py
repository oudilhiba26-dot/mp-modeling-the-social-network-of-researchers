"""
Script principal pour exécuter la simulation complète du stress du réseau.
Orchestre les trois étapes: attaque, dégradation et génération des signaux d'alerte.
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire courant au chemin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from degradation_simulator import DegradationSimulator
from alert_signal_generator import AlertSignalGenerator


def main():
    """Fonction principale d'orchestration."""
    
    print("="*80)
    print(" "*15 + "SIMULATEUR DE STRESS DU RÉSEAU DE CHERCHEURS")
    print("="*80)
    
    # Chemin vers le fichier edgelist
    edgelist_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'data_prep_vis',
        'cleaned_researcher_network_edgelist.csv'
    )
    
    # Vérifier que le fichier existe
    if not os.path.exists(edgelist_path):
        print(f"\n❌ Erreur: Le fichier {edgelist_path} n'existe pas!")
        sys.exit(1)
    
    print(f"\n📂 Fichier edgelist: {edgelist_path}")
    
    # Créer le répertoire de sortie
    output_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📊 Répertoire de sortie: {output_dir}\n")
    
    # ============================================================================
    # ÉTAPE 1 & 2: PROGRAMMATION DES ATTAQUES + AUTOMATISATION DE LA DÉGRADATION
    # ============================================================================
    
    print("\n" + "="*80)
    print("ÉTAPE 1 & 2: PROGRAMMATION ET AUTOMATISATION DE LA DÉGRADATION")
    print("="*80)
    
    # Initialiser le simulateur
    simulator = DegradationSimulator(edgelist_path)
    
    print(f"\n📈 Réseau original:")
    print(f"   - Nombre de nœuds: {simulator.original_size}")
    print(f"   - Nombre d'arêtes: {simulator.graph.number_of_edges()}")
    
    # Lancer la simulation avec les pourcentages définis
    removal_percentages = [1, 5, 10]
    print(f"\n🎯 Pourcentages de suppression testés: {removal_percentages}%")
    print(f"\n🔬 Protocoles d'attaque:")
    print(f"   1. ALÉATOIRE (Bruit de fond)")
    print(f"   2. CIBLÉE - Suppression des HUBS (degré)")
    print(f"   3. CIBLÉE - Suppression des PONTS (betweenness centrality)")
    
    results = simulator.simulate_degradation(removal_percentages)
    
    # Afficher le résumé
    simulator.print_summary()
    
    # ============================================================================
    # ÉTAPE 3: GÉNÉRATION DES SIGNAUX D'ALERTE
    # ============================================================================
    
    print("\n\n" + "="*80)
    print("ÉTAPE 3: GÉNÉRATION DES SIGNAUX D'ALERTE (COURBES CRITIQUES)")
    print("="*80)
    
    # Créer le générateur de signaux
    alert_generator = AlertSignalGenerator(results, output_dir)
    
    # Générer toutes les visualisations
    alert_generator.generate_all_visualizations(fragmentation_threshold=0.5)
    
    # ============================================================================
    # RAPPORT FINAL
    # ============================================================================
    
    print("\n\n" + "="*80)
    print("RAPPORT FINAL - ANALYSE DES POINTS DE BASCULE")
    print("="*80)
    
    print("\n🔍 Analyse des résultats:\n")
    
    for protocol in ['random', 'targeted_hubs', 'targeted_bridges']:
        print(f"\n{'─'*60}")
        print(f"PROTOCOLE: {protocol.upper()}")
        print(f"{'─'*60}")
        
        if protocol in results and results[protocol]:
            for result in results[protocol]:
                pct = result['removal_percentage']
                conn = result['connectivity_ratio']
                comps = result['num_components']
                status = result['connectivity_status']
                fragmented = "🚨 FRAGMENTÉ" if result['is_fragmented'] else "✓ CONNECTÉ"
                
                print(f"\n  Suppression {pct}%:")
                print(f"    • Connectivité: {conn:.1%} {fragmented}")
                print(f"    • Composantes: {comps}")
                print(f"    • Statut: {status}")
            
            tipping_point = simulator.get_tipping_point(protocol)
            if tipping_point:
                print(f"\n  ⚡ POINT DE BASCULE: {tipping_point}%")
            else:
                print(f"\n  ⚡ Point de bascule: Non détecté dans cette plage")
    
    print("\n" + "="*80)
    print("SIGNIFICATION DES COURBES D'ALERTE:")
    print("="*80)
    print("""
    1. ZONE STABLE (Vert): Connectivité > 50%
       → Le réseau continue de fonctionner normalement
       → Communication possible entre la plupart des nœuds
    
    2. ZONE CRITIQUE (Rouge): Connectivité < 50%
       → Le réseau commence à se fragmenter sérieusement
       → Isolement de groupes importants
    
    3. POINT DE BASCULE: Le moment où le réseau devient irrécupérable
       → Identification précise du seuil critique
       → Important pour mettre en place les mesures de protection
    
    4. COMPARAISON DES PROTOCOLES:
       → Attaque aléatoire: Moins efficace (réseau plus résilient)
       → Attaque sur hubs: Très efficace (perte rapide de connectivité)
       → Attaque sur ponts: Très efficace (segmentation rapide)
    """)
    
    print("\n" + "="*80)
    print("✅ SIMULATION TERMINÉE AVEC SUCCÈS")
    print("="*80)
    print(f"\n📁 Les résultats et graphiques sont disponibles dans: {output_dir}")
    print("\nFichiers générés:")
    print("  1️⃣  01_connectivity_curves.png - Courbes de connectivité (PRINCIPAL)")
    print("  2️⃣  02_fragmentation_stages.png - Évolution de la fragmentation")
    print("  3️⃣  03_largest_component_evolution.png - Dégradation de la cohésion")
    print("  4️⃣  04_resilience_comparison.png - Comparaison des protocoles")
    print("  5️⃣  05_critical_transition_phase.png - Phase critique détaillée")


if __name__ == '__main__':
    main()
