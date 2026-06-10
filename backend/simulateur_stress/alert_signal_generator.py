"""
Module de génération des courbes d'alerte et des signaux de fragmentation.
Crée des visualisations montrant le point de bascule du réseau.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import Dict, List
import os


class AlertSignalGenerator:
    """Classe pour générer les courbes et signaux d'alerte de fragmentation."""
    
    def __init__(self, results: Dict, output_dir: str = '.'):
        """
        Initialise le générateur de signaux d'alerte.
        
        Args:
            results: Dictionnaire des résultats de simulation
            output_dir: Répertoire de sortie pour les graphiques
        """
        self.results = results
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Crée le répertoire de sortie s'il n'existe pas."""
        if self.output_dir != '.' and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def plot_connectivity_curves(self, fragmentation_threshold: float = 0.5):
        """
        Trace les courbes de connectivité pour les trois protocoles.
        
        Args:
            fragmentation_threshold: Seuil de fragmentation (ligne rouge)
        """
        fig, ax = plt.subplots(figsize=(12, 7))
        
        colors = {
            'random': '#3498db',              # Bleu
            'targeted_hubs': '#e74c3c',       # Rouge
            'targeted_bridges': '#2ecc71'     # Vert
        }
        
        markers = {
            'random': 'o',
            'targeted_hubs': 's',
            'targeted_bridges': '^'
        }
        
        # Tracer les courbes pour chaque protocole
        for protocol, color in colors.items():
            if protocol in self.results and self.results[protocol]:
                percentages = [r['removal_percentage'] for r in self.results[protocol]]
                connectivity_ratios = [r['connectivity_ratio'] for r in self.results[protocol]]
                
                ax.plot(percentages, connectivity_ratios, 
                       color=color, marker=markers[protocol], linewidth=2.5, 
                       markersize=8, label=protocol.replace('_', ' ').title())
                
                # Identifier et marquer le point de bascule
                tipping_point = None
                for i, ratio in enumerate(connectivity_ratios):
                    if ratio < fragmentation_threshold and tipping_point is None:
                        tipping_point = percentages[i]
                        ax.plot(tipping_point, ratio, marker='*', markersize=20, 
                               color=color, markeredgecolor='black', markeredgewidth=1)
                        ax.annotate(f'Bascule\n{tipping_point}%',
                                   xy=(tipping_point, ratio),
                                   xytext=(10, 10), textcoords='offset points',
                                   fontsize=9, color=color, fontweight='bold',
                                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8),
                                   arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
        
        # Ajouter la ligne de seuil de fragmentation
        ax.axhline(y=fragmentation_threshold, color='red', linestyle='--', 
                  linewidth=2, label=f'Seuil de fragmentation ({fragmentation_threshold:.0%})')
        
        # Remplir la zone de fragmentation
        ax.fill_between(ax.get_xlim(), 0, fragmentation_threshold, 
                        alpha=0.1, color='red', label='Zone de fragmentation')
        
        ax.set_xlabel('Pourcentage de nœuds supprimés (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Ratio de connectivité', fontsize=12, fontweight='bold')
        ax.set_title('Impact des Attaques sur la Connectivité du Réseau\n(Identification du Point de Bascule)',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', fontsize=10, framealpha=0.95)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(-0.05, 1.05)
        ax.set_xlim(-0.5, 11)
        
        # Formater les axes
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, '01_connectivity_curves.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Graphique sauvegardé: {output_path}")
        plt.close()
    
    def plot_fragmentation_stages(self):
        """
        Trace l'évolution du nombre de composantes connexes.
        Plus il y a de composantes, plus le réseau est fragmenté.
        """
        fig, ax = plt.subplots(figsize=(12, 7))
        
        colors = {
            'random': '#3498db',
            'targeted_hubs': '#e74c3c',
            'targeted_bridges': '#2ecc71'
        }
        
        markers = {
            'random': 'o',
            'targeted_hubs': 's',
            'targeted_bridges': '^'
        }
        
        for protocol, color in colors.items():
            if protocol in self.results and self.results[protocol]:
                percentages = [r['removal_percentage'] for r in self.results[protocol]]
                num_components = [r['num_components'] for r in self.results[protocol]]
                
                ax.plot(percentages, num_components,
                       color=color, marker=markers[protocol], linewidth=2.5,
                       markersize=8, label=protocol.replace('_', ' ').title())
        
        ax.set_xlabel('Pourcentage de nœuds supprimés (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Nombre de composantes connexes', fontsize=12, fontweight='bold')
        ax.set_title('Fragmentation Progressive du Réseau\n(Nombre de Composantes)',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=10, framealpha=0.95)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, '02_fragmentation_stages.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Graphique sauvegardé: {output_path}")
        plt.close()
    
    def plot_largest_component_evolution(self):
        """
        Trace l'évolution de la taille de la plus grande composante.
        """
        fig, ax = plt.subplots(figsize=(12, 7))
        
        colors = {
            'random': '#3498db',
            'targeted_hubs': '#e74c3c',
            'targeted_bridges': '#2ecc71'
        }
        
        markers = {
            'random': 'o',
            'targeted_hubs': 's',
            'targeted_bridges': '^'
        }
        
        for protocol, color in colors.items():
            if protocol in self.results and self.results[protocol]:
                percentages = [r['removal_percentage'] for r in self.results[protocol]]
                largest_comp = [r['largest_component_size'] for r in self.results[protocol]]
                
                ax.plot(percentages, largest_comp,
                       color=color, marker=markers[protocol], linewidth=2.5,
                       markersize=8, label=protocol.replace('_', ' ').title())
        
        ax.set_xlabel('Pourcentage de nœuds supprimés (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Taille de la plus grande composante', fontsize=12, fontweight='bold')
        ax.set_title('Dégradation de la Plus Grande Composante\n(Décroissance de Cohésion)',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', fontsize=10, framealpha=0.95)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, '03_largest_component_evolution.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Graphique sauvegardé: {output_path}")
        plt.close()
    
    def plot_resilience_comparison(self):
        """
        Compare la résilience de trois protocoles côte à côte.
        """
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        colors = {
            'random': '#3498db',
            'targeted_hubs': '#e74c3c',
            'targeted_bridges': '#2ecc71'
        }
        
        protocol_titles = {
            'random': 'Attaque Aléatoire\n(Bruit de fond)',
            'targeted_hubs': 'Attaque Ciblée\n(Suppression des Hubs)',
            'targeted_bridges': 'Attaque Ciblée\n(Suppression des Ponts)'
        }
        
        for idx, protocol in enumerate(['random', 'targeted_hubs', 'targeted_bridges']):
            ax = axes[idx]
            color = colors[protocol]
            
            if protocol in self.results and self.results[protocol]:
                percentages = [r['removal_percentage'] for r in self.results[protocol]]
                connectivity_ratios = [r['connectivity_ratio'] for r in self.results[protocol]]
                
                bars = ax.bar(percentages, connectivity_ratios, width=2, color=color, alpha=0.7, edgecolor='black')
                
                # Colorer les barres sous le seuil en rouge
                for i, (bar, ratio) in enumerate(zip(bars, connectivity_ratios)):
                    if ratio < 0.5:
                        bar.set_color('#e74c3c')
                        bar.set_alpha(0.9)
                
                ax.axhline(y=0.5, color='red', linestyle='--', linewidth=2, label='Seuil')
                ax.set_ylabel('Connectivité', fontsize=11, fontweight='bold')
                ax.set_xlabel('% suppression', fontsize=11, fontweight='bold')
                ax.set_title(protocol_titles[protocol], fontsize=12, fontweight='bold')
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
                ax.grid(True, alpha=0.3, axis='y', linestyle='--')
                ax.set_ylim(-0.05, 1.05)
        
        plt.suptitle('Comparaison de la Résilience des Trois Protocoles d\'Attaque',
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, '04_resilience_comparison.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Graphique sauvegardé: {output_path}")
        plt.close()
    
    def plot_critical_transition_phase(self, fragmentation_threshold: float = 0.5):
        """
        Crée une visualisation spécialisée montrant la phase de transition critique.
        """
        fig, ax = plt.subplots(figsize=(12, 7))
        
        colors = {
            'random': '#3498db',
            'targeted_hubs': '#e74c3c',
            'targeted_bridges': '#2ecc71'
        }
        
        # Zones de stabilité
        ax.axhspan(fragmentation_threshold, 1, alpha=0.15, color='green', label='Zone stable')
        ax.axhspan(0, fragmentation_threshold, alpha=0.15, color='red', label='Zone critique')
        
        for protocol, color in colors.items():
            if protocol in self.results and self.results[protocol]:
                percentages = [r['removal_percentage'] for r in self.results[protocol]]
                connectivity_ratios = [r['connectivity_ratio'] for r in self.results[protocol]]
                
                ax.plot(percentages, connectivity_ratios,
                       color=color, marker='o', linewidth=3, markersize=10,
                       label=protocol.replace('_', ' ').title())
        
        ax.axhline(y=fragmentation_threshold, color='darkred', linestyle='--',
                  linewidth=2.5, label='Point critique')
        
        ax.set_xlabel('Pourcentage de nœuds supprimés (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Ratio de connectivité', fontsize=12, fontweight='bold')
        ax.set_title('Phase de Transition Critique: Identification du Point de Bascule\n' +
                    '(Moment où le réseau fragmenté devient irréversible)',
                    fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=10, framealpha=0.95)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(-0.05, 1.05)
        ax.set_xlim(-0.5, 11)
        
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, '05_critical_transition_phase.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Graphique sauvegardé: {output_path}")
        plt.close()
    
    def generate_all_visualizations(self, fragmentation_threshold: float = 0.5):
        """
        Génère toutes les visualisations.
        
        Args:
            fragmentation_threshold: Seuil de fragmentation
        """
        print(f"\n{'='*60}")
        print("GÉNÉRATION DES COURBES D'ALERTE")
        print(f"{'='*60}\n")
        
        self.plot_connectivity_curves(fragmentation_threshold)
        self.plot_fragmentation_stages()
        self.plot_largest_component_evolution()
        self.plot_resilience_comparison()
        self.plot_critical_transition_phase(fragmentation_threshold)
        
        print(f"\n{'='*60}")
        print("✓ Toutes les visualisations ont été générées avec succès!")
        print(f"{'='*60}")
