"""
Module de calcul des métriques de connectivité et de résilience du réseau.
"""

import networkx as nx
from typing import Dict, List, Tuple
import numpy as np


class NetworkMetrics:
    """Classe pour calculer les métriques de connectivité et de résilience."""
    
    @staticmethod
    def calculate_metrics(graph: nx.Graph) -> Dict:
        """
        Calcule les principales métriques de connectivité du graphe.
        
        Args:
            graph: Un graphe NetworkX
            
        Returns:
            Dictionnaire contenant les métriques
        """
        metrics = {}
        
        # Nombre de nœuds et d'arêtes
        metrics['num_nodes'] = graph.number_of_nodes()
        metrics['num_edges'] = graph.number_of_edges()
        
        if metrics['num_nodes'] == 0:
            # Graphe vide
            metrics['largest_component_size'] = 0
            metrics['num_components'] = 0
            metrics['connectivity_ratio'] = 0
            metrics['density'] = 0
            metrics['avg_degree'] = 0
            metrics['avg_shortest_path'] = float('inf')
            return metrics
        
        # Composantes connexes
        components = list(nx.connected_components(graph))
        metrics['num_components'] = len(components)
        metrics['largest_component_size'] = len(max(components, key=len)) if components else 0
        
        # Ratio de connectivité (taille de la plus grande composante / total)
        metrics['connectivity_ratio'] = metrics['largest_component_size'] / metrics['num_nodes']
        
        # Densité
        metrics['density'] = nx.density(graph)
        
        # Degré moyen
        if metrics['num_nodes'] > 0:
            degrees = [degree for node, degree in graph.degree()]
            metrics['avg_degree'] = np.mean(degrees)
            metrics['max_degree'] = np.max(degrees)
            metrics['min_degree'] = np.min(degrees)
        else:
            metrics['avg_degree'] = 0
            metrics['max_degree'] = 0
            metrics['min_degree'] = 0
        
        # Chemin le plus court moyen (pour la plus grande composante)
        if metrics['largest_component_size'] > 1:
            largest_component = max(components, key=len)
            subgraph = graph.subgraph(largest_component)
            try:
                avg_shortest_path = nx.average_shortest_path_length(subgraph)
                metrics['avg_shortest_path'] = avg_shortest_path
            except:
                metrics['avg_shortest_path'] = float('inf')
        else:
            metrics['avg_shortest_path'] = float('inf')
        
        # Coefficient de clustering moyen
        metrics['avg_clustering'] = nx.average_clustering(graph)
        
        return metrics
    
    @staticmethod
    def is_network_fragmented(graph: nx.Graph, fragmentation_threshold: float = 0.5) -> bool:
        """
        Détermine si le réseau est considéré comme fragmenté.
        
        Args:
            graph: Un graphe NetworkX
            fragmentation_threshold: Seuil du ratio de connectivité (défaut: 50%)
            
        Returns:
            True si le réseau est fragmenté, False sinon
        """
        if graph.number_of_nodes() == 0:
            return True
        
        metrics = NetworkMetrics.calculate_metrics(graph)
        return metrics['connectivity_ratio'] < fragmentation_threshold
    
    @staticmethod
    def get_connectivity_status(connectivity_ratio: float) -> str:
        """
        Retourne le statut de connectivité basé sur le ratio.
        
        Args:
            connectivity_ratio: Ratio de la plus grande composante
            
        Returns:
            Statut descriptif
        """
        if connectivity_ratio >= 0.9:
            return "Très connecté"
        elif connectivity_ratio >= 0.7:
            return "Bien connecté"
        elif connectivity_ratio >= 0.5:
            return "Modérément connecté"
        elif connectivity_ratio >= 0.2:
            return "Peu connecté"
        else:
            return "Fortement fragmenté"
