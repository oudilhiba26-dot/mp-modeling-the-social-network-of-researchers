# 🚀 Guide de Déploiement de l'Application

## ✅ Status: PRÊT À ÊTRE LANCÉ

Tous les tests de compatibilité sont passés. L'application est entièrement adaptée à la structure de vos données.

---

## 📊 Résumé des Adaptations Effectuées

### ✨ Modifications Frontend (app.py)

#### Phase 1: Préparation & Visualisation
```
✅ cleaned_researcher_network_edgelist.csv
   Colonnes: Researcher_A, Researcher_B, Co_Publications
   
✅ metrics_results.csv  
   Colonnes: researcher, degree, betweenness, closeness, pagerank
   
✅ metrics_with_clusters.csv
   Colonnes: classe (au lieu de cluster)
   - 135 chercheurs
   - 17 clusters identifiés
```

**Fonctions adaptées:**
- `display_phase1_kpis()`: Calcule le nombre de chercheurs, collaborations, densité, clusters
- `display_phase1_metrics_table()`: Affiche les 50 premiers chercheurs avec métriques
- `display_phase1_metrics_charts()`: Histogrammes et scatter plots interactifs
- `display_phase1_network_viz()`: Charge le graphe HTML (reseau_dynamique.html)

#### Phase 2: Simulation de Stress & Résilience
```
✅ degradation_results.csv
   Colonnes: step, pct_removed, gcc_size, n_components, diameter, density, attack_type
   - 24 résultats de simulation
   - 3 types d'attaque: random_attack, degree_attack, betweenness_attack
   
✅ degradation_curves.html (4.7 MB)
   Visualisation interactive Plotly
   
✅ resilience_report.txt (4.2 KB)
   Rapport synthétique en texte
```

**Fonctions adaptées:**
- `display_phase2_degradation_charts()`: Graphiques gcc_size et n_components colorés par attack_type
- `display_phase2_detailed_table()`: Tableau complet des résultats
- `display_phase2_curves_viz()`: Visualisation HTML interactive
- `display_phase2_report()`: Affichage du rapport

#### Phase 3: Prédiction de Liens & ML
```
✅ link_predictions.csv
   Colonnes: removed_node, algorithm, node_u, node_v, score, rank
   - 45 prédictions
   - 3 algorithmes: adamic_adar, jaccard, preferential_attachment
   
✅ vulnerability_scores.csv
   Colonnes: node, degree, betweenness, closeness, pagerank, clustering_coeff,
            avg_neighbor_degree, n_triangles, is_bridge, is_isolated_in_crisis,
            vulnerability_proba, vulnerability_level
   - 135 nœuds évalués
   - Niveaux: HIGH, MEDIUM, LOW
   
✅ feature_importance.csv
   Colonnes: feature, importance
   - 8 features: pagerank, n_triangles, avg_neighbor_degree, betweenness,
                 degree, clustering_coeff, closeness, is_bridge
   
✅ reseau_futur.html (145 KB)
   Visualisation du réseau prédit
   
✅ predictive_report.txt (1.4 KB)
   Rapport de prédictions
```

**Fonctions adaptées:**
- `display_phase3_predictions()`: Filtre par algorithme, graphique top 20
- `display_phase3_vulnerability()`: Histogramme de vulnerability_proba, stats
- `display_phase3_feature_importance()`: Graphique horizontal des scores
- `display_phase3_network_viz()`: Visualisation HTML du réseau futur
- `display_phase3_report()`: Affichage du rapport avec download

---

## 🚀 Comment Lancer l'Application

### 1. Vérifier les dépendances
```bash
pip install streamlit pandas plotly networkx
```

### 2. Lancer l'application
```bash
streamlit run frontend/app.py
```

### 3. Accéder à l'interface
- L'application s'ouvrira automatiquement dans votre navigateur
- URL: `http://localhost:8501`
- Port: 8501 (peut être changé avec `--server.port XXXX`)

---

## 🎮 Interface Utilisateur

### Barre Latérale (Sidebar)
- **Contrôle du Pipeline**: Boutons pour exécuter chaque phase individuellement ou complètement
- **Rafraîchir**: Vide le cache et recharge les données
- **Informations**: Ordre d'exécution des phases et dépendances

### Onglets Principaux

#### 1️⃣ Onglet "Préparation & Visualisation (P1)"
- KPI principaux: Chercheurs, Collaborations, Densité, Clusters
- Sous-onglets:
  - **Métriques**: Tableau avec les 50 meilleurs chercheurs
  - **Graphiques**: Distribution des degrés + scatter Betweenness/PageRank
  - **Réseau**: Visualisation HTML du réseau initial
  - **Clusters**: Distribution des clusters avec graphique

#### 2️⃣ Onglet "Simulation de Stress (P2)"
- Résultats de résilience
- Sous-onglets:
  - **Courbes de Dégradation**: Graphiques gcc_size et n_components
  - **Données Détaillées**: Tableau complet des résultats
  - **Visualisation Interactive**: Graphes HTML Plotly
  - **Rapport**: Rapport de résilience complet

#### 3️⃣ Onglet "Prédiction de Liens (P3)"
- Résultats de ML
- Sous-onglets:
  - **Prédictions**: Tableau + graphique top 20 par score + download CSV
  - **Vulnérabilité**: Tableau + histogramme de probabilité + stats
  - **Importance des Features**: Tableau + graphique horizontal
  - **Réseau Futur**: Visualisation HTML du réseau prédit
  - **Rapport**: Rapport de prédiction + download TXT

---

## 🧪 Tests de Validation

Trois scripts de test ont été créés:

### 1. `test_data_compatibility.py`
Vérifie que toutes les colonnes CSV existent et sont correctes.
```bash
python test_data_compatibility.py
```
✅ Résultat: **TOUS LES TESTS PASSÉS!**

### 2. `validate_app.py`
Valide la syntaxe Python et les imports de l'app.
```bash
python validate_app.py
```
✅ Résultat: **VALIDATION COMPLÈTE!**

### 3. `inspect_data.py`
Affiche la structure détaillée de tous les fichiers CSV.
```bash
python inspect_data.py
```

---

## 📁 Structure du Projet

```
mp-modeling-the-social-network-of-researchers/
├── frontend/
│   └── app.py                    ✅ Application Streamlit adaptée
├── backend/
│   ├── data_prep_vis/
│   │   ├── cleaned_researcher_network_edgelist.csv
│   │   ├── metrics_results.csv
│   │   ├── metrics_with_clusters.csv
│   │   └── reseau_dynamique.html
│   ├── simulateur_stress/
│   │   ├── degradation_results.csv
│   │   ├── degradation_curves.html
│   │   └── resilience_report.txt
│   └── link_predictionML/
│       ├── link_predictions.csv
│       ├── vulnerability_scores.csv
│       ├── feature_importance.csv
│       ├── reseau_futur.html
│       └── predictive_report.txt
├── test_data_compatibility.py    ✅ Test des colonnes CSV
├── validate_app.py               ✅ Test de validation
├── inspect_data.py               ✅ Inspection des données
├── ADAPTATION_NOTES.md           ✅ Détails des adaptations
└── DOCUMENTATION_SUMMARY.md      ✅ Documentation complète
```

---

## 🔧 Configuration Avancée

### Changer le port Streamlit
```bash
streamlit run frontend/app.py --server.port 3000
```

### Mode dark/light
Streamlit détecte automatiquement vos préférences système ou vous permet de les changer dans les Settings.

### Désactiver le cache
```bash
streamlit run frontend/app.py --client.caching=false
```

---

## 🐛 Dépannage

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
```

### "The app stopped because the main script raised an exception"
- Vérifiez que tous les fichiers CSV et HTML existent
- Exécutez `python test_data_compatibility.py`

### Les graphiques ne s'affichent pas
- Vérifiez que Plotly est installé: `pip install plotly`
- Vérifiez que les fichiers CSV ne sont pas vides

### Performances lentes
- Utilisez `st.cache_data` (déjà implémenté)
- Augmentez la mémoire RAM disponible
- Réduisez la fréquence de rafraîchissement

---

## 📞 Support

Pour toute question ou problème:
1. Vérifiez d'abord les résultats des tests
2. Consultez les logs Streamlit (terminal)
3. Vérifiez la structure des fichiers avec `inspect_data.py`

---

**Status**: ✅ **PRÊT À ÊTRE LANCÉ**
**Date**: 2026-06-11
**Version**: 1.0