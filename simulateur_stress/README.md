# 📊 Simulateur de Stress du Réseau de Chercheurs

Un outil complet de simulation permettant d'analyser la **résilience** et les **points de bascule critiques** d'un réseau social de chercheurs soumis à différentes formes d'attaque.

---

## 📋 Description

Ce projet implémente trois **étapes principales**:

### ✅ **Étape 1: Programmation des Scénarios d'Attaque**
Programme des fonctions permettant de retirer des nœuds de manière itérative selon **deux protocoles**:

- **Aléatoire**: Suppression aléatoire de nœuds (simule le bruit de fond)
- **Ciblée - Hubs**: Suppression stratégique des nœuds avec le plus haut degré (connecteurs clés)
- **Ciblée - Ponts**: Suppression des nœuds avec la plus haute betweenness centrality (connecteurs entre groupes)

### ✅ **Étape 2: Automatisation de la Dégradation**
Boucle automatisée qui:
- Supprime un pourcentage de nœuds (1%, 5%, 10%)
- Recalcule la connectivité globale après chaque suppression
- Suit l'évolution de la fragmentation du réseau
- Identifie le point de bascule critique

### ✅ **Étape 3: Génération des Signaux d'Alerte**
Crée des courbes visualisant:
- **Courbes de connectivité** avec identification du point de bascule
- **Évolution de la fragmentation** (nombre de composantes connexes)
- **Dégradation de la cohésion** (taille de la plus grande composante)
- **Comparaison des résiliences** entre les trois protocoles
- **Phase de transition critique** détaillée

---

## 🏗️ Structure du Projet

```
simulateur_stress/
├── network_attacks.py           # Implémentation des protocoles d'attaque
├── network_metrics.py           # Calcul des métriques de connectivité
├── degradation_simulator.py     # Automatisation de la simulation
├── alert_signal_generator.py    # Génération des visualisations
├── main.py                      # Script principal d'orchestration
├── requirements.txt             # Dépendances Python
├── README.md                    # Ce fichier
└── results/                     # Résultats et graphiques (créé automatiquement)
    ├── 01_connectivity_curves.png
    ├── 02_fragmentation_stages.png
    ├── 03_largest_component_evolution.png
    ├── 04_resilience_comparison.png
    └── 05_critical_transition_phase.png
```

---

## 🚀 Installation et Utilisation

### 1. Installer les dépendances

```bash
cd simulateur_stress
pip install -r requirements.txt
```

### 2. Exécuter la simulation

```bash
python main.py
```

### 3. Consulter les résultats

Les graphiques sont automatiquement sauvegardés dans le dossier `results/`

---

## 📊 Modules Détaillés

### `network_attacks.py`
Classe `NetworkAttackSimulator`:
- `random_attack(percentage)` - Suppression aléatoire
- `targeted_attack_hubs(percentage)` - Suppression des hubs
- `targeted_attack_bridges(percentage)` - Suppression des ponts

### `network_metrics.py`
Classe `NetworkMetrics`:
- `calculate_metrics(graph)` - Calcule connectivité, densité, clustering, etc.
- `is_network_fragmented(graph)` - Détecte la fragmentation
- `get_connectivity_status(ratio)` - Évalue l'état du réseau

### `degradation_simulator.py`
Classe `DegradationSimulator`:
- `simulate_degradation(removal_percentages)` - Lance la simulation complète
- `get_tipping_point(protocol)` - Identifie le point de bascule critique

### `alert_signal_generator.py`
Classe `AlertSignalGenerator`:
- `plot_connectivity_curves()` - Courbes principales
- `plot_fragmentation_stages()` - Évolution des composantes
- `plot_largest_component_evolution()` - Dégradation de cohésion
- `plot_resilience_comparison()` - Comparaison des protocoles
- `plot_critical_transition_phase()` - Phase critique
- `generate_all_visualizations()` - Génère tous les graphiques

---

## 📈 Interprétation des Résultats

### Connectivité (Ratio)
- **> 90%**: Très connecté ✓
- **70-90%**: Bien connecté ✓
- **50-70%**: Modérément connecté ⚠️
- **20-50%**: Peu connecté 🚨
- **< 20%**: Fortement fragmenté 🔴

### Point de Bascule
Le moment où le **ratio de connectivité passe sous 50%** - moment où le réseau devient irréversiblement fragmenté.

### Protocoles Comparés
- **Aléatoire**: Moins efficace (réseau résilient)
- **Hubs**: Très efficace (impact maximum)
- **Ponts**: Très efficace (segmentation rapide)

---

## 🔬 Métriques Calculées

Pour chaque simulation:
- **Connectivité**: Ratio de la plus grande composante / total
- **Fragmentation**: Nombre de composantes connexes
- **Densité**: Nombre d'arêtes / arêtes maximales possibles
- **Degré moyen**: Moyenne des connexions par nœud
- **Clustering**: Coefficient de clustering moyen
- **Chemin moyen**: Distance moyenne entre nœuds

---

## 💡 Cas d'Usage

1. **Prévention de crises**: Identifier les nœuds critiques à protéger
2. **Planification de résilience**: Tester différentes topologies
3. **Analyse de vulnérabilité**: Déterminer le point de bascule
4. **Stratégies de protection**: Renforcer les connexions critiques

---

## 📝 Exemple de Sortie

```
Pourcentage de suppression: 5%
Nœuds supprimés: 2
Nœuds restants: 37
Arêtes restantes: 82
Ratio de connectivité: 97.30%
Nombre de composantes: 1
Plus grande composante: 37
Statut: Très connecté
Fragmenté: NON

⚡ POINT DE BASCULE: Attaque aléatoire à 10%
⚡ POINT DE BASCULE: Attaque ciblée (hubs) à 5%
⚡ POINT DE BASCULE: Attaque ciblée (ponts) à 5%
```

---

## 🔧 Configuration

Vous pouvez modifier les paramètres dans `main.py`:

```python
removal_percentages = [1, 5, 10]  # Pourcentages testés
fragmentation_threshold = 0.5      # Seuil de fragmentation (50%)
```

---

## 📦 Dépendances

- `networkx` - Analyse de graphes
- `numpy` - Calculs numériques
- `matplotlib` - Visualisations
- `pandas` - (optionnel) pour manipulation de données

---

## 👥 Auteur

Système de simulation du stress réseau pour analyse de résilience des réseaux sociaux.

---

## 📄 Licence

MIT

---

## ❓ Questions Fréquentes

**Q: Pourquoi 3 protocoles d'attaque?**
R: Pour représenter différents scénarios réalistes: attaque aléatoire (perte accidentelle), ciblée sur hubs (démontage stratégique), ou sur ponts (segmentation).

**Q: Qu'est-ce qu'un point de bascule?**
R: Le moment où le réseau passe d'un état connecté à un état fragmenté - crucial pour comprendre la fragilité du système.

**Q: Comment améliorer la résilience?**
R: Renforcer les connexions des nœuds critiques (hubs), diversifier les chemins de communication, ou créer des connexions redondantes.

---
