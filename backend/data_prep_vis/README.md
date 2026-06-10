# Analyse et Visualisation de Réseaux Sociaux de Chercheurs

## Introduction

Dans cette phase 1 du projet on vise à construire, analyser et visualiser le réseau de collaboration entre chercheurs . Le processus inclut la collecte de données, la transformation, le nettoyage, le calcul de métriques de centralité, la détection de communautés et la visualisation interactive du réseau.

## Structure du Projet

Le dossier `data_prep_vis` contient les scripts Python et les fichiers de données nécessaires à l'exécution du projet :

- `collecting_data.py` : Script pour la collecte initiale de données depuis l'API arXiv.

- `data_transforming.py` : Script pour transformer les données brutes en une liste d'arêtes de réseau.

- `new_data_cleaning.py` : Script pour nettoyer la liste d'arêtes générée.

- `metrics.py` : Script pour calculer diverses métriques de centralité sur le réseau.

- `clusters.py` : Script pour détecter les communautés de chercheurs et fusionner les résultats avec les métriques.

- `graphe_presentation.py` : Script pour générer une visualisation interactive du réseau.

- `requirements.txt` : Liste des dépendances Python du projet.

- `lib/` : Contient les bibliothèques JavaScript et CSS pour la visualisation interactive.

## Flux d'Exécution des Codes

Le projet suit une pipeline séquentielle pour la préparation des données, l'analyse et la visualisation. Chaque script prend en entrée le résultat du script précédent et produit un nouveau fichier de données ou une visualisation.

1. **`collecting_data.py`**
  - **Description** : Ce script se connecte à l'API arXiv pour collecter des informations sur des articles scientifiques (par exemple, dans le domaine de l'Intelligence Artificielle). Il extrait les titres, auteurs, dates de soumission, résumés et URLs.
  - **Entrée** : Requête à l'API arXiv (ex: `cat:cs.AI`).
  - **Sortie** : `arxiv_data.csv` - Un fichier CSV contenant les données brutes des articles collectés.

1. **`data_transforming.py`**
  - **Description** : Ce script transforme les données brutes d'arXiv en une liste d'arêtes représentant les collaborations entre chercheurs. Il identifie les co-auteurs pour chaque article et agrège les co-publications pour former des liens pondérés.
  - **Entrée** : `arxiv_data.csv`.
  - **Sortie** : `researcher_network_edgelist.csv` - Un fichier CSV listant les paires de chercheurs et le nombre de leurs co-publications.

1. **`new_data_cleaning.py`**
  - **Description** : Ce script effectue un nettoyage de base sur la liste d'arêtes. Il supprime les doublons et les auto-boucles (un chercheur collaborant avec lui-même), assurant ainsi l'intégrité du réseau.
  - **Entrée** : `researcher_network_edgelist.csv`.
  - **Sortie** : `cleaned_researcher_network_edgelist.csv` - La liste d'arêtes nettoyée, prête pour l'analyse.

1. **`metrics.py`**
  - **Description** : Ce script calcule diverses métriques de centralité pour chaque chercheur dans le réseau. Les métriques incluent le degré, la centralité d'intermédiarité (betweenness), la centralité de proximité (closeness) et le PageRank, qui sont essentiels pour comprendre l'influence et la position des chercheurs.
  - **Entrée** : `cleaned_researcher_network_edgelist.csv`.
  - **Sortie** : `metrics_results.csv` - Un fichier CSV contenant les métriques calculées pour chaque chercheur.

1. **`clusters.py`**
  - **Description** : Ce script applique des algorithmes de détection de communautés (par exemple, l'algorithme de Louvain) pour identifier des groupes de chercheurs fortement connectés. Les résultats des communautés sont ensuite fusionnés avec les métriques de centralité.
  - **Entrée** : `cleaned_researcher_network_edgelist.csv` et `metrics_results.csv`.
  - **Sortie** : `metrics_with_clusters.csv` - Un fichier CSV enrichi incluant les métriques de centralité et l'appartenance à une communauté pour chaque chercheur.

1. **`graphe_presentation.py`**
  - **Description** : Le script final génère une visualisation interactive du réseau de collaboration. Il utilise les données enrichies (`metrics_with_clusters.csv`) pour représenter les chercheurs (nœuds) et leurs collaborations (arêtes), en colorant les nœuds par communauté et en dimensionnant par PageRank. La visualisation est exportée au format HTML, permettant une exploration dynamique.
  - **Entrée** : `cleaned_researcher_network_edgelist.csv` et `metrics_with_clusters.csv`.
  - **Sortie** : `reseau_dynamique.html` - Un fichier HTML interactif présentant le réseau de chercheurs.

## Objectif du Projet

L'objectif principal de ce projet est de fournir une méthodologie complète pour l'analyse des réseaux sociaux de chercheurs. Cela inclut :

- **Préparation des Données** : Collecter, transformer et nettoyer des données académiques pour les rendre exploitables.

- **Analyse de Réseau** : Calculer des métriques clés et détecter des communautés pour comprendre la structure et la dynamique des collaborations.

- **Visualisation** : Offrir une représentation interactive et intuitive du réseau, facilitant l'exploration des relations et l'identification des acteurs influents.

## Dépendances

Les dépendances Python nécessaires pour exécuter ce projet sont listées dans `requirements.txt` et peuvent être installées via `pip` :

```bash
pip install -r requirements.txt
```

Les principales bibliothèques incluent :

- `pandas` et `numpy` pour la manipulation de données.

- `networkx` pour la création et l'analyse de graphes.

- `python-louvain` pour la détection de communautés.

- `arxiv` pour l'accès à l'API arXiv.

- `pyvis` et `plotly` pour la visualisation interactive.

## Utilisation

Pour exécuter la pipeline complète, naviguez vers le répertoire `data_prep_vis` et exécutez les scripts Python dans l'ordre spécifié :

```bash
python collecting_data.py
python data_transforming.py
python new_data_cleaning.py
python metrics.py
python clusters.py
python graphe_presentation.py
```

Après l'exécution du dernier script, le fichier `reseau_dynamique.html` sera généré dans le répertoire du projet. Ouvrez ce fichier dans un navigateur web pour explorer la visualisation interactive du réseau de chercheurs.

