"""
Script de test pour valider que app.py fonctionne avec les données existantes
"""
import sys
from pathlib import Path
import pandas as pd

# Chemin vers le backend
BACKEND_DIR = Path(__file__).parent / "backend"

print("=" * 70)
print("🧪 VÉRIFICATION DE LA COMPATIBILITÉ DES DONNÉES")
print("=" * 70)

errors = []
warnings = []

# Test Phase 1 - Data Prep
print("\n📊 PHASE 1: Préparation des Données")
print("-" * 70)

try:
    df_clean = pd.read_csv(BACKEND_DIR / "data_prep_vis" / "cleaned_researcher_network_edgelist.csv")
    cols_needed = ["Researcher_A", "Researcher_B", "Co_Publications"]
    cols_missing = [col for col in cols_needed if col not in df_clean.columns]
    
    if cols_missing:
        errors.append(f"❌ cleaned_researcher_network_edgelist.csv - Colonnes manquantes: {cols_missing}")
        print(f"❌ cleaned_researcher_network_edgelist.csv")
        print(f"   Colonnes trouvées: {list(df_clean.columns)}")
    else:
        print(f"✅ cleaned_researcher_network_edgelist.csv")
        print(f"   Shape: {df_clean.shape}")
        print(f"   Colonnes: {cols_needed}")
except Exception as e:
    errors.append(f"❌ cleaned_researcher_network_edgelist.csv: {e}")
    print(f"❌ cleaned_researcher_network_edgelist.csv: {e}")

try:
    df_metrics = pd.read_csv(BACKEND_DIR / "data_prep_vis" / "metrics_results.csv")
    cols_needed = ["researcher", "degree", "betweenness", "closeness", "pagerank"]
    cols_missing = [col for col in cols_needed if col not in df_metrics.columns]
    
    if cols_missing:
        errors.append(f"❌ metrics_results.csv - Colonnes manquantes: {cols_missing}")
        print(f"❌ metrics_results.csv")
        print(f"   Colonnes trouvées: {list(df_metrics.columns)}")
    else:
        print(f"✅ metrics_results.csv")
        print(f"   Shape: {df_metrics.shape}")
        print(f"   Colonnes: {cols_needed}")
except Exception as e:
    errors.append(f"❌ metrics_results.csv: {e}")
    print(f"❌ metrics_results.csv: {e}")

try:
    df_clusters = pd.read_csv(BACKEND_DIR / "data_prep_vis" / "metrics_with_clusters.csv")
    if "classe" not in df_clusters.columns:
        errors.append(f"❌ metrics_with_clusters.csv - Colonne 'classe' manquante")
        print(f"❌ metrics_with_clusters.csv - Colonne 'classe' manquante")
        print(f"   Colonnes trouvées: {list(df_clusters.columns)}")
    else:
        print(f"✅ metrics_with_clusters.csv")
        print(f"   Shape: {df_clusters.shape}")
        print(f"   Clusters: {df_clusters['classe'].nunique()}")
except Exception as e:
    errors.append(f"❌ metrics_with_clusters.csv: {e}")
    print(f"❌ metrics_with_clusters.csv: {e}")

# Test Phase 2 - Stress Simulation
print("\n📉 PHASE 2: Simulation de Stress")
print("-" * 70)

try:
    df_degrad = pd.read_csv(BACKEND_DIR / "simulateur_stress" / "degradation_results.csv")
    cols_needed = ["step", "pct_removed", "gcc_size", "n_components", "diameter", "density", "attack_type"]
    cols_missing = [col for col in cols_needed if col not in df_degrad.columns]
    
    if cols_missing:
        errors.append(f"❌ degradation_results.csv - Colonnes manquantes: {cols_missing}")
        print(f"❌ degradation_results.csv")
        print(f"   Colonnes trouvées: {list(df_degrad.columns)}")
    else:
        print(f"✅ degradation_results.csv")
        print(f"   Shape: {df_degrad.shape}")
        print(f"   Attack types: {df_degrad['attack_type'].unique().tolist()}")
except Exception as e:
    errors.append(f"❌ degradation_results.csv: {e}")
    print(f"❌ degradation_results.csv: {e}")

# Test Phase 3 - Link Prediction
print("\n🔮 PHASE 3: Prédiction de Liens")
print("-" * 70)

try:
    df_pred = pd.read_csv(BACKEND_DIR / "link_predictionML" / "link_predictions.csv")
    cols_needed = ["removed_node", "algorithm", "node_u", "node_v", "score", "rank"]
    cols_missing = [col for col in cols_needed if col not in df_pred.columns]
    
    if cols_missing:
        errors.append(f"❌ link_predictions.csv - Colonnes manquantes: {cols_missing}")
        print(f"❌ link_predictions.csv")
        print(f"   Colonnes trouvées: {list(df_pred.columns)}")
    else:
        print(f"✅ link_predictions.csv")
        print(f"   Shape: {df_pred.shape}")
        print(f"   Algorithmes: {df_pred['algorithm'].unique().tolist()}")
except Exception as e:
    errors.append(f"❌ link_predictions.csv: {e}")
    print(f"❌ link_predictions.csv: {e}")

try:
    df_vuln = pd.read_csv(BACKEND_DIR / "link_predictionML" / "vulnerability_scores.csv")
    cols_needed = ["node", "vulnerability_proba", "vulnerability_level"]
    cols_missing = [col for col in cols_needed if col not in df_vuln.columns]
    
    if cols_missing:
        errors.append(f"❌ vulnerability_scores.csv - Colonnes manquantes: {cols_missing}")
        print(f"❌ vulnerability_scores.csv")
        print(f"   Colonnes trouvées: {list(df_vuln.columns)}")
    else:
        print(f"✅ vulnerability_scores.csv")
        print(f"   Shape: {df_vuln.shape}")
        print(f"   Niveaux de vulnérabilité: {df_vuln['vulnerability_level'].unique().tolist()}")
except Exception as e:
    errors.append(f"❌ vulnerability_scores.csv: {e}")
    print(f"❌ vulnerability_scores.csv: {e}")

try:
    df_feat = pd.read_csv(BACKEND_DIR / "link_predictionML" / "feature_importance.csv")
    cols_needed = ["feature", "importance"]
    cols_missing = [col for col in cols_needed if col not in df_feat.columns]
    
    if cols_missing:
        errors.append(f"❌ feature_importance.csv - Colonnes manquantes: {cols_missing}")
        print(f"❌ feature_importance.csv")
        print(f"   Colonnes trouvées: {list(df_feat.columns)}")
    else:
        print(f"✅ feature_importance.csv")
        print(f"   Shape: {df_feat.shape}")
        print(f"   Features: {df_feat['feature'].tolist()}")
except Exception as e:
    errors.append(f"❌ feature_importance.csv: {e}")
    print(f"❌ feature_importance.csv: {e}")

# Test fichiers HTML et TXT
print("\n📄 FICHIERS HTML & RAPPORTS")
print("-" * 70)

files_to_check = [
    ("data_prep_vis", "reseau_dynamique.html"),
    ("simulateur_stress", "degradation_curves.html"),
    ("simulateur_stress", "resilience_report.txt"),
    ("link_predictionML", "reseau_futur.html"),
    ("link_predictionML", "predictive_report.txt"),
]

for phase, filename in files_to_check:
    filepath = BACKEND_DIR / phase / filename
    if filepath.exists():
        size_kb = filepath.stat().st_size / 1024
        print(f"✅ {phase}/{filename} ({size_kb:.1f} KB)")
    else:
        warnings.append(f"⚠️ {phase}/{filename} - Fichier non trouvé")
        print(f"⚠️ {phase}/{filename} - Fichier non trouvé")

# Résumé
print("\n" + "=" * 70)
print("📊 RÉSUMÉ")
print("=" * 70)

if not errors and not warnings:
    print("✅ TOUS LES TESTS PASSÉS!")
    print("L'application app.py est prête à fonctionner avec vos données.")
    sys.exit(0)
else:
    if errors:
        print(f"\n❌ ERREURS ({len(errors)}):")
        for err in errors:
            print(f"  {err}")
    if warnings:
        print(f"\n⚠️ AVERTISSEMENTS ({len(warnings)}):")
        for warn in warnings:
            print(f"  {warn}")
    sys.exit(1)
