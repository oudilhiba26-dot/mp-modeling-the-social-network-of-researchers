"""
Module d'automatisation de la dégradation du réseau.
Recalcule la connectivité après chaque pourcentage de suppression.
"""

import networkx as nx
from typing import Dict, List, Tuple
import numpy as np
from network_attacks import NetworkAttackSimulator
from network_metrics import NetworkMetrics


class DegradationSimulator:
    """Classe pour simuler la dégradation progressive du réseau."""
    
    def __init__(self, edgelist_path: str):
        """
        Initialise le simulateur avec un fichier edgelist.
        
        Args:
            edgelist_path: Chemin vers le fichier edgelist CSV
        """
        self.graph = self._load_graph(edgelist_path)
        self.original_size = self.graph.number_of_nodes()
        self.results = {
            'random': [],
            'targeted_hubs': [],
            'targeted_bridges': []
        }
    
    def _load_graph(self, edgelist_path: str) -> nx.Graph:
        """
        Charge le graphe depuis un fichier edgelist.
        
        Args:
            edgelist_path: Chemin vers le fichier CSV
            
        Returns:
            Graphe NetworkX
        """
        G = nx.Graph()
        try:
            with open(edgelist_path, 'r', encoding='utf-8') as f:
                # Sauter l'en-tête
                next(f)
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        source, target, weight = parts[0], parts[1], int(parts[2])
                        G.add_edge(source, target, weight=weight)
        except Exception as e:
            print(f"Erreur lors du chargement du graphe: {e}")
        
        return G
    
    def simulate_degradation(self, removal_percentages: List[float] = None) -> Dict:
        """
        Simule la dégradation du réseau selon trois protocoles.
        
        Args:
            removal_percentages: Liste des pourcentages de suppression (défaut: [1, 5, 10])
            
        Returns:
            Dictionnaire contenant les résultats pour chaque protocole
        """
        if removal_percentages is None:
            removal_percentages = [1, 5, 10]
        
        protocols = {
            'random': 'random_attack',
            'targeted_hubs': 'targeted_attack_hubs',
            'targeted_bridges': 'targeted_attack_bridges'
        }
        
        for protocol_name, protocol_method in protocols.items():
            print(f"\n{'='*60}")
            print(f"Simulation: {protocol_name.upper()}")
            print(f"{'='*60}")
            
            # Réinitialiser pour chaque protocole
            simulator = NetworkAttackSimulator(self.graph)
            self.results[protocol_name] = []
            
            for percentage in removal_percentages:
                # Exécuter l'attaque
                method = getattr(simulator, protocol_method)
                removed_nodes = method(percentage)
                
                # Calculer les métriques
                current_graph = simulator.get_graph()
                metrics = NetworkMetrics.calculate_metrics(current_graph)
                
                result = {
                    'removal_percentage': percentage,
                    'nodes_removed_count': len(removed_nodes),
                    'remaining_nodes': metrics['num_nodes'],
                    'remaining_edges': metrics['num_edges'],
                    'connectivity_ratio': metrics['connectivity_ratio'],
                    'num_components': metrics['num_components'],
                    'largest_component_size': metrics['largest_component_size'],
                    'density': metrics['density'],
                    'avg_degree': metrics['avg_degree'],
                    'avg_clustering': metrics['avg_clustering'],
                    'connectivity_status': NetworkMetrics.get_connectivity_status(
                        metrics['connectivity_ratio']
                    ),
                    'is_fragmented': NetworkMetrics.is_network_fragmented(current_graph)
                }
                
                self.results[protocol_name].append(result)
                
                # Afficher les résultats
                self._print_result(percentage, result, protocol_name)
                
                # Réinitialiser le simulateur pour la prochaine itération
                simulator.reset_graph()
        
        return self.results
    
    def _print_result(self, percentage: float, result: Dict, protocol: str):
        """Affiche les résultats d'une itération."""
        print(f"\n  Pourcentage de suppression: {percentage}%")
        print(f"  Nœuds supprimés: {result['nodes_removed_count']}")
        print(f"  Nœuds restants: {result['remaining_nodes']}")
        print(f"  Arêtes restantes: {result['remaining_edges']}")
        print(f"  Ratio de connectivité: {result['connectivity_ratio']:.2%}")
        print(f"  Nombre de composantes: {result['num_components']}")
        print(f"  Plus grande composante: {result['largest_component_size']}")
        print(f"  Statut: {result['connectivity_status']}")
        print(f"  Fragmenté: {'OUI' if result['is_fragmented'] else 'NON'}")
    
    def get_tipping_point(self, protocol: str, fragmentation_threshold: float = 0.5) -> float:
        """
        Identifie le point de bascule (tipping point) du réseau.
        C'est le premier pourcentage où le ratio de connectivité passe sous le seuil.
        
        Args:
            protocol: Protocole d'attaque ('random', 'targeted_hubs', 'targeted_bridges')
            fragmentation_threshold: Seuil de fragmentation
            
        Returns:
            Pourcentage du point de bascule, ou None si non trouvé
        """
        if protocol not in self.results:
            return None
        
        for result in self.results[protocol]:
            if result['connectivity_ratio'] < fragmentation_threshold:
                return result['removal_percentage']
        
        return None
    
    def print_summary(self):
        """Affiche un résumé des points de bascule pour tous les protocoles."""
        print(f"\n{'='*60}")
        print("RÉSUMÉ DES POINTS DE BASCULE")
        print(f"{'='*60}\n")
        
        for protocol in ['random', 'targeted_hubs', 'targeted_bridges']:
            tipping_point = self.get_tipping_point(protocol)
            if tipping_point is not None:
                print(f"{protocol.upper()}: Point de bascule à {tipping_point}%")
            else:
                print(f"{protocol.upper()}: Pas de fragmentation complète détectée")
