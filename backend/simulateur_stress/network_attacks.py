"""
Module de programmation des scénarios d'attaque réseau.
Implémente deux protocoles : aléatoire (bruit de fond) et ciblé (hubs/ponts).
"""

import networkx as nx
import random
from typing import List, Tuple, Set
import numpy as np


class NetworkAttackSimulator:
    """Classe pour simuler différents types d'attaques sur un réseau."""
    
    def __init__(self, graph: nx.Graph):
        """
        Initialise le simulateur avec un graphe.
        
        Args:
            graph: Un graphe NetworkX
        """
        self.original_graph = graph.copy()
        self.current_graph = graph.copy()
        self.attacked_nodes = set()
        self.removal_history = []
        
    def reset_graph(self):
        """Réinitialise le graphe à son état original."""
        self.current_graph = self.original_graph.copy()
        self.attacked_nodes = set()
        self.removal_history = []
    
    def random_attack(self, percentage: float) -> Set[int]:
        """
        Protocole d'attaque ALÉATOIRE (bruit de fond).
        Retire aléatoirement un pourcentage de nœuds.
        
        Args:
            percentage: Pourcentage de nœuds à retirer (0-100)
            
        Returns:
            Ensemble des nœuds retirés
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Le pourcentage doit être entre 0 et 100")
        
        # Calculer le nombre de nœuds à retirer
        num_nodes_to_remove = int(len(self.current_graph) * percentage / 100)
        
        # Sélectionner aléatoirement les nœuds
        nodes_to_remove = random.sample(list(self.current_graph.nodes()), num_nodes_to_remove)
        
        # Retirer les nœuds
        self.current_graph.remove_nodes_from(nodes_to_remove)
        self.attacked_nodes.update(nodes_to_remove)
        self.removal_history.append({
            'protocol': 'random',
            'percentage': percentage,
            'nodes_removed': len(nodes_to_remove),
            'removed_nodes': nodes_to_remove
        })
        
        return set(nodes_to_remove)
    
    def targeted_attack_hubs(self, percentage: float) -> Set[int]:
        """
        Protocole d'attaque CIBLÉE - Suppression des HUBS.
        Cible les nœuds avec le plus haut degré (connectivité).
        
        Args:
            percentage: Pourcentage de nœuds à retirer (0-100)
            
        Returns:
            Ensemble des nœuds retirés
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Le pourcentage doit être entre 0 et 100")
        
        # Calculer le nombre de nœuds à retirer
        num_nodes_to_remove = int(len(self.current_graph) * percentage / 100)
        
        # Trier les nœuds par degré (en ordre décroissant)
        nodes_by_degree = sorted(
            self.current_graph.degree(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Sélectionner les nœuds avec le plus haut degré
        nodes_to_remove = [node for node, degree in nodes_by_degree[:num_nodes_to_remove]]
        
        # Retirer les nœuds
        self.current_graph.remove_nodes_from(nodes_to_remove)
        self.attacked_nodes.update(nodes_to_remove)
        self.removal_history.append({
            'protocol': 'targeted_hubs',
            'percentage': percentage,
            'nodes_removed': len(nodes_to_remove),
            'removed_nodes': nodes_to_remove,
            'avg_degree_removed': np.mean([degree for _, degree in nodes_by_degree[:num_nodes_to_remove]])
        })
        
        return set(nodes_to_remove)
    
    def targeted_attack_bridges(self, percentage: float) -> Set[int]:
        """
        Protocole d'attaque CIBLÉE - Suppression des PONTS (betweenness centrality).
        Cible les nœuds qui connectent différentes parties du réseau.
        
        Args:
            percentage: Pourcentage de nœuds à retirer (0-100)
            
        Returns:
            Ensemble des nœuds retirés
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Le pourcentage doit être entre 0 et 100")
        
        # Calculer le nombre de nœuds à retirer
        num_nodes_to_remove = int(len(self.current_graph) * percentage / 100)
        
        # Calculer la betweenness centrality
        betweenness = nx.betweenness_centrality(self.current_graph)
        
        # Trier par betweenness (ordre décroissant)
        nodes_by_betweenness = sorted(
            betweenness.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Sélectionner les nœuds avec le plus haut betweenness
        nodes_to_remove = [node for node, _ in nodes_by_betweenness[:num_nodes_to_remove]]
        
        # Retirer les nœuds
        self.current_graph.remove_nodes_from(nodes_to_remove)
        self.attacked_nodes.update(nodes_to_remove)
        self.removal_history.append({
            'protocol': 'targeted_bridges',
            'percentage': percentage,
            'nodes_removed': len(nodes_to_remove),
            'removed_nodes': nodes_to_remove,
            'avg_betweenness_removed': np.mean([bc for _, bc in nodes_by_betweenness[:num_nodes_to_remove]])
        })
        
        return set(nodes_to_remove)
    
    def get_graph(self) -> nx.Graph:
        """Retourne le graphe actuel après les attaques."""
        return self.current_graph.copy()
