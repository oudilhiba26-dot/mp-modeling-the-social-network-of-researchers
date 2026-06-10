"""
Frontend Streamlit pour l'analyse du réseau social des chercheurs
Connecté au backend de modélisation en 3 phases :
  1. Préparation des données et visualisation (backend/data_prep_vis/)
  2. Simulation de stress et résilience (backend/simulateur_stress/)
  3. Prédiction de liens (backend/link_predictionML/)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
import logging

# =========================
# Configuration et constantes
# =========================

# Chemins relatifs vers le backend
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

# Mapping correct des phases
PHASE1_DIR = BACKEND_DIR / "data_prep_vis"
PHASE2_DIR = BACKEND_DIR / "simulateur_stress"  # Phase 2 = Stress Simulation
PHASE3_DIR = BACKEND_DIR / "link_predictionML"  # Phase 3 = Link Prediction

# Scripts de Phase 1 (dans l'ordre d'exécution)
PHASE1_SCRIPTS = [
    PHASE1_DIR / "collecting_data.py",
    PHASE1_DIR / "data_transforming.py",
    PHASE1_DIR / "new_data_cleaning.py",
    PHASE1_DIR / "metrics.py",
    PHASE1_DIR / "clusters.py",
    PHASE1_DIR / "graphe_presentation.py",
]

# Scripts de Phase 2 et 3
# TODO: remplacer avec le nom exact du script principal si différent
PHASE2_SCRIPT = PHASE2_DIR / "resilience_simulation.py"
PHASE3_SCRIPT = PHASE3_DIR / "predictive_analysis.py"

# Chemins des fichiers de sortie - Phase 1
PHASE1_OUTPUTS = {
    "network_clean": PHASE1_DIR / "cleaned_researcher_network_edgelist.csv",
    "metrics": PHASE1_DIR / "metrics_results.csv",
    "clusters": PHASE1_DIR / "metrics_with_clusters.csv",
    "graph": PHASE1_DIR / "reseau_dynamique.html",
}

# Chemins des fichiers de sortie - Phase 2 (Stress Simulation)
PHASE2_OUTPUTS = {
    "degradation": PHASE2_DIR / "degradation_results.csv",
    "curves": PHASE2_DIR / "degradation_curves.html",
    "report": PHASE2_DIR / "resilience_report.txt",
}

# Chemins des fichiers de sortie - Phase 3 (Link Prediction)
PHASE3_OUTPUTS = {
    "predictions": PHASE3_DIR / "link_predictions.csv",
    "vulnerability": PHASE3_DIR / "vulnerability_scores.csv",
    "features": PHASE3_DIR / "feature_importance.csv",
    "graph": PHASE3_DIR / "reseau_futur.html",
    "report": PHASE3_DIR / "predictive_report.txt",
}

# Configuration Streamlit
st.set_page_config(
    page_title="Réseau Social des Chercheurs",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# Fonctions utilitaires
# =========================

def file_exists(path: Path) -> bool:
    """Vérifie si un fichier existe."""
    return path.exists() and path.is_file()

@st.cache_data
def load_csv_safe(path: Path) -> Optional[pd.DataFrame]:
    """
    Charge un fichier CSV en toute sécurité avec gestion d'erreur.
    Utilise le cache pour améliorer les performances.
    """
    try:
        if not file_exists(path):
            return None
        return pd.read_csv(path)
    except Exception as e:
        logger.error(f"Erreur lors du chargement de {path}: {e}")
        return None

@st.cache_data
def load_text_safe(path: Path) -> Optional[str]:
    """
    Charge un fichier texte en toute sécurité.
    Utilise le cache pour améliorer les performances.
    """
    try:
        if not file_exists(path):
            return None
        return path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Erreur lors du chargement de {path}: {e}")
        return None

def load_html_file(path: Path) -> Optional[str]:
    """Charge un fichier HTML pour affichage dans Streamlit."""
    return load_text_safe(path)

def display_html_graph(path: Path, height: int = 700) -> bool:
    """
    Affiche un graphe HTML dans Streamlit.
    Retourne True si succès, False sinon.
    """
    html_content = load_html_file(path)
    if html_content:
        st.components.v1.html(html_content, height=height, scrolling=True)
        return True
    return False

def file_size_mb(path: Path) -> float:
    """Retourne la taille du fichier en MB."""
    if not file_exists(path):
        return 0.0
    return path.stat().st_size / (1024 * 1024)

def file_modified_time(path: Path) -> Optional[str]:
    """Retourne le timestamp de dernière modification."""
    if not file_exists(path):
        return None
    mtime = path.stat().st_mtime
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")

def clear_cache():
    """Vide le cache Streamlit pour forcer le rechargement des données."""
    st.cache_data.clear()

# =========================
# Fonctions d'exécution backend
# =========================

def run_python_script(script_path: Path, cwd: Optional[Path] = None) -> Tuple[bool, str, str]:
    """
    Exécute un script Python et retourne (succès, stdout, stderr).
    """
    try:
        if not file_exists(script_path):
            return False, "", f"Script non trouvé: {script_path}"
        
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(cwd or script_path.parent),
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes max
        )
        
        success = result.returncode == 0
        return success, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        return False, "", "⏱️ Timeout: le script a pris plus de 10 minutes"
    except Exception as e:
        return False, "", str(e)

def run_phase_1() -> bool:
    """Exécute la phase 1 (préparation des données)."""
    st.info("🔄 Lancement de la Phase 1...")
    
    scripts = [
        ("Collecte de données", PHASE1_DIR / "collecting_data.py"),
        ("Transformation des données", PHASE1_DIR / "data_transforming.py"),
        ("Nettoyage des données", PHASE1_DIR / "new_data_cleaning.py"),
        ("Calcul des métriques", PHASE1_DIR / "metrics.py"),
        ("Détection des clusters", PHASE1_DIR / "clusters.py"),
        ("Génération du graphe", PHASE1_DIR / "graphe_presentation.py"),
    ]
    
    progress_bar = st.progress(0)
    status_container = st.empty()
    
    for idx, (step_name, script_path) in enumerate(scripts):
        status_container.info(f"▶️ {step_name}...")
        
        success, stdout, stderr = run_python_script(script_path, PHASE1_DIR)
        
        if not success:
            st.error(f"❌ Erreur dans {step_name}")
            if stderr:
                with st.expander("📋 Détails de l'erreur"):
                    st.code(stderr)
            return False
        
        # Affiche les logs
        if stdout:
            with st.expander(f"📝 Logs: {step_name}", expanded=False):
                st.code(stdout)
        
        progress = (idx + 1) / len(scripts)
        progress_bar.progress(progress)
    
    status_container.success("✅ Phase 1 complétée avec succès!")
    clear_cache()
    return True

def run_phase_2() -> bool:
    """Exécute la phase 2 (simulation de stress et résilience)."""
    st.info("🔄 Lancement de la Phase 2 (Simulation de Stress)...")
    
    # Vérification des prérequis
    if not file_exists(PHASE1_OUTPUTS["network_clean"]):
        st.error("❌ Les fichiers de Phase 1 sont manquants. Lancez d'abord la Phase 1.")
        return False
    
    progress_bar = st.progress(0)
    
    success, stdout, stderr = run_python_script(
        PHASE2_SCRIPT,
        PHASE2_DIR
    )
    
    if not success:
        st.error("❌ Erreur lors de la simulation de stress")
        if stderr:
            with st.expander("📋 Détails de l'erreur"):
                st.code(stderr)
        return False
    
    if stdout:
        with st.expander("📝 Logs d'exécution", expanded=False):
            st.code(stdout)
    
    progress_bar.progress(1.0)
    st.success("✅ Phase 2 complétée avec succès!")
    st.cache_data.clear()
    return True

def run_phase_3() -> bool:
    """Exécute la phase 3 (prédiction de liens)."""
    st.info("🔄 Lancement de la Phase 3 (Prédiction de Liens)...")
    
    # Vérification des prérequis
    if not file_exists(PHASE1_OUTPUTS["network_clean"]):
        st.error("❌ Les fichiers de Phase 1 sont manquants. Lancez d'abord la Phase 1.")
        return False
    
    progress_bar = st.progress(0)
    
    success, stdout, stderr = run_python_script(
        PHASE3_SCRIPT,
        PHASE3_DIR
    )
    
    if not success:
        st.error("❌ Erreur lors de la prédiction de liens")
        if stderr:
            with st.expander("📋 Détails de l'erreur"):
                st.code(stderr)
        return False
    
    if stdout:
        with st.expander("📝 Logs d'exécution", expanded=False):
            st.code(stdout)
    
    progress_bar.progress(1.0)
    st.success("✅ Phase 3 complétée avec succès!")
    st.cache_data.clear()
    return True

def run_full_pipeline() -> bool:
    """Exécute le pipeline complet (Phases 1, 2, 3)."""
    st.warning("⚙️ Exécution du pipeline complet (peut prendre plusieurs minutes)...")
    
    phases = [
        ("Phase 1: Préparation", run_phase_1),
        ("Phase 2: Simulation de Stress", run_phase_2),
        ("Phase 3: Prédiction de Liens", run_phase_3),
    ]
    
    for phase_name, phase_func in phases:
        st.divider()
        st.subheader(f"▶️ {phase_name}")
        if not phase_func():
            st.error(f"❌ Le pipeline s'est arrêté à {phase_name}")
            return False
    
    st.balloons()
    st.success("🎉 Pipeline complet exécuté avec succès!")
    return True

# =========================
# Fonctions de visualisation Phase 1
# =========================

def display_phase1_kpis():
    """Affiche les KPI de la Phase 1."""
    df_clean = load_csv_safe(PHASE1_OUTPUTS["network_clean"])
    df_metrics = load_csv_safe(PHASE1_OUTPUTS["metrics"])
    
    if df_clean is None or df_metrics is None:
        st.warning("⚠️ Les fichiers de Phase 1 ne sont pas disponibles. Lancez la Phase 1 d'abord.")
        return
    
    # Calcul des KPI
    num_researchers = len(set(df_clean["Researcher_A"].tolist() + df_clean["Researcher_B"].tolist()))
    num_collaborations = len(df_clean)
    
    # Densité approximative
    if num_researchers > 1:
        density = (2 * num_collaborations) / (num_researchers * (num_researchers - 1))
    else:
        density = 0
    
    # Nombre de clusters si disponible
    df_clusters = load_csv_safe(PHASE1_OUTPUTS["clusters"])
    num_clusters = df_clusters["classe"].nunique() if df_clusters is not None else "N/A"
    
    # Affichage des KPI
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Chercheurs", num_researchers)
    
    with col2:
        st.metric("🔗 Collaborations", num_collaborations)
    
    with col3:
        st.metric("📊 Densité", f"{density:.4f}")
    
    with col4:
        st.metric("🎯 Clusters", num_clusters)

def display_phase1_metrics_table():
    """Affiche le tableau des métriques de Phase 1."""
    df_metrics = load_csv_safe(PHASE1_OUTPUTS["metrics"])
    
    if df_metrics is None:
        st.info("📊 Les métriques ne sont pas disponibles.")
        return
    
    st.subheader("📋 Métriques de Centralité")
    
    # Formater les colonnes numériques
    df_display = df_metrics.copy()
    for col in ['degree', 'betweenness', 'closeness', 'pagerank']:
        if col in df_display.columns:
            df_display[col] = df_display[col].round(6)
    
    st.dataframe(df_display.head(50), use_container_width=True, height=400)
    st.caption(f"Affichage des 50 premiers chercheurs sur {len(df_display)}")

def display_phase1_metrics_charts():
    """Affiche les graphiques des métriques."""
    df_metrics = load_csv_safe(PHASE1_OUTPUTS["metrics"])
    
    if df_metrics is None:
        st.info("📊 Les données ne sont pas disponibles.")
        return
    
    st.subheader("📊 Graphiques des Métriques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique 1: Distribution des degrés
        fig1 = px.histogram(
            df_metrics,
            x="degree",
            nbins=30,
            title="Distribution des Degrés",
            labels={"degree": "Degré du chercheur"}
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Graphique 2: Betweenness vs PageRank
        fig2 = px.scatter(
            df_metrics,
            x="betweenness",
            y="pagerank",
            hover_data={"researcher": True, "betweenness": ":.3f", "pagerank": ":.3f"},
            title="Betweenness vs PageRank",
            size="degree",
            color="closeness",
            size_max=30
        )
        st.plotly_chart(fig2, use_container_width=True)

def display_phase1_network_viz():
    """Affiche le graphe du réseau."""
    html_path = PHASE1_OUTPUTS["graph"]
    
    if not file_exists(html_path):
        st.info("📡 Le graphe de réseau n'est pas disponible. Exécutez la Phase 1 complètement.")
        return
    
    st.subheader("🌐 Visualisation du Réseau")
    
    if not display_html_graph(html_path):
        st.info("📡 Impossible de charger la visualisation HTML.")

# =========================
# Fonctions de visualisation Phase 2 (Simulation de Stress)
# =========================

def display_phase2_degradation_charts():
    """Affiche les courbes de dégradation du réseau."""
    df_degrad = load_csv_safe(PHASE2_OUTPUTS["degradation"])
    
    if df_degrad is None:
        st.info("📊 Les résultats de dégradation ne sont pas disponibles. Exécutez la Phase 2.")
        return
    
    st.subheader("📉 Courbes de Dégradation du Réseau")
    
    col1, col2 = st.columns(2)
    
    # Graphique 1: Taille de la composante géante
    with col1:
        fig = px.line(
            df_degrad,
            x="pct_removed",
            y="gcc_size",
            color="attack_type",
            title="Taille de la Composante Géante",
            markers=True,
            labels={"pct_removed": "% de nœuds supprimés", "gcc_size": "Taille GCC"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Graphique 2: Nombre de composantes
    with col2:
        fig = px.line(
            df_degrad,
            x="pct_removed",
            y="n_components",
            color="attack_type",
            title="Nombre de Composantes",
            markers=True,
            labels={"pct_removed": "% de nœuds supprimés", "n_components": "Nombre de composantes"}
        )
        st.plotly_chart(fig, use_container_width=True)

def display_phase2_detailed_table():
    """Affiche le tableau détaillé des résultats de dégradation."""
    df_degrad = load_csv_safe(PHASE2_OUTPUTS["degradation"])
    
    if df_degrad is None:
        st.info("📊 Les résultats ne sont pas disponibles.")
        return
    
    st.subheader("📋 Résultats Détaillés de Résilience")
    st.dataframe(df_degrad, use_container_width=True, height=400)

def display_phase2_curves_viz():
    """Affiche le graphe interactif des courbes de dégradation."""
    html_path = PHASE2_OUTPUTS["curves"]
    
    if not file_exists(html_path):
        st.info("📡 La visualisation des courbes n'est pas disponible.")
        return
    
    st.subheader("📊 Courbes de Dégradation Interactives")
    
    if not display_html_graph(html_path):
        st.info("ℹ️ Impossible de charger la visualisation HTML.")

def display_phase2_report():
    """Affiche le rapport de résilience."""
    report = load_text_safe(PHASE2_OUTPUTS["report"])
    
    if report is None:
        st.info("📄 Le rapport n'est pas disponible.")
        return
    
    with st.expander("📄 Rapport Complet de Résilience"):
        st.text(report)

# =========================
# Fonctions de visualisation Phase 3 (Prédiction de Liens)
# =========================

def display_phase3_predictions():
    """Affiche les prédictions de liens."""
    df_pred = load_csv_safe(PHASE3_OUTPUTS["predictions"])
    
    if df_pred is None:
        st.info("📊 Les prédictions ne sont pas disponibles. Exécutez la Phase 3.")
        return
    
    st.subheader("🔮 Prédictions de Collaborations Futures")
    
    # Filtrer par algorithme
    if "algorithm" in df_pred.columns:
        algorithms = df_pred["algorithm"].unique()
        selected_algo = st.selectbox("Sélectionner l'algorithme", algorithms)
        df_filtered = df_pred[df_pred["algorithm"] == selected_algo]
    else:
        df_filtered = df_pred
    
    st.dataframe(df_filtered.head(50), use_container_width=True, height=400)
    st.caption(f"Affichage des 50 premières prédictions sur {len(df_filtered)}")
    
    # Bouton de téléchargement
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger les prédictions (CSV)",
        data=csv_data,
        file_name="link_predictions.csv",
        mime="text/csv"
    )
    
    # Graphique: Top prédictions par score
    if "score" in df_filtered.columns:
        top_preds = df_filtered.nlargest(20, "score")
        fig = px.bar(
            top_preds,
            x="score",
            y=[f"{row['node_u']} → {row['node_v']}" for _, row in top_preds.iterrows()],
            title="Top 20 des Prédictions (Score les plus élevés)",
            labels={"score": "Score de prédiction"}
        )
        fig.update_layout(yaxis_title="Liens prédits")
        st.plotly_chart(fig, use_container_width=True)

def display_phase3_vulnerability():
    """Affiche les scores de vulnérabilité."""
    df_vuln = load_csv_safe(PHASE3_OUTPUTS["vulnerability"])
    
    if df_vuln is None:
        st.info("📊 Les scores de vulnérabilité ne sont pas disponibles.")
        return
    
    st.subheader("⚠️ Scores de Vulnérabilité des Nœuds")
    
    col1, col2 = st.columns([2, 1])
    
    # Tableau
    with col1:
        st.dataframe(df_vuln.head(50), use_container_width=True, height=400)
        st.caption(f"Affichage des 50 premiers nœuds sur {len(df_vuln)}")
    
    # Statistiques
    with col2:
        st.metric("Nœuds totaux", len(df_vuln))
        if "vulnerability_level" in df_vuln.columns:
            high_vuln = len(df_vuln[df_vuln["vulnerability_level"] == "HIGH"])
            st.metric("Nœuds hautement vulnérables", high_vuln)
    
    # Graphique: Distribution des probabilités de vulnérabilité
    fig = px.histogram(
        df_vuln,
        x="vulnerability_proba",
        nbins=30,
        title="Distribution des Probabilités de Vulnérabilité",
        labels={"vulnerability_proba": "Probabilité de vulnérabilité"}
    )
    st.plotly_chart(fig, use_container_width=True)

def display_phase3_feature_importance():
    """Affiche l'importance des features."""
    df_feat = load_csv_safe(PHASE3_OUTPUTS["features"])
    
    if df_feat is None:
        st.info("📊 L'importance des features n'est pas disponible.")
        return
    
    st.subheader("🎯 Importance des Caractéristiques pour la Prédiction")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.dataframe(df_feat, use_container_width=True)
    
    with col2:
        # Graphique: importance des features
        if "feature" in df_feat.columns and "importance" in df_feat.columns:
            df_sorted = df_feat.sort_values("importance", ascending=True)
            fig = px.bar(
                df_sorted,
                x="importance",
                y="feature",
                orientation="h",
                title="Score d'Importance des Features",
                labels={"importance": "Importance", "feature": "Caractéristique"}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def display_phase3_network_viz():
    """Affiche le graphe futur prédit."""
    html_path = PHASE3_OUTPUTS["graph"]
    
    if not file_exists(html_path):
        st.info("📡 La visualisation du réseau futur n'est pas disponible.")
        return
    
    st.subheader("🔮 Visualisation du Réseau Futur Prédit")
    
    if not display_html_graph(html_path):
        st.info("ℹ️ Impossible de charger la visualisation HTML.")

def display_phase3_report():
    """Affiche le rapport de prédiction."""
    report = load_text_safe(PHASE3_OUTPUTS["report"])
    
    if report is None:
        st.info("📄 Le rapport n'est pas disponible.")
        return
    
    with st.expander("📄 Rapport Complet de Prédiction"):
        st.text(report)
    
    # Bouton de téléchargement du rapport
    report_bytes = report.encode('utf-8')
    st.download_button(
        label="📥 Télécharger le rapport (TXT)",
        data=report_bytes,
        file_name="predictive_report.txt",
        mime="text/plain"
    )

# =========================
# Interface principale
# =========================

def main():
    """Fonction principale de l'application."""
    
    # En-tête
    st.markdown("# 🔬 Modélisation du Réseau Social des Chercheurs")
    st.markdown("**Analyse complète de la collaboration académique avec prédiction et simulation de résilience**")
    
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Contrôle du Pipeline")
        
        st.subheader("Exécution des phases")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ Phase 1", use_container_width=True, key="btn_phase1"):
                st.session_state.run_phase1 = True
        
        with col2:
            if st.button("▶️ Phase 2", use_container_width=True, key="btn_phase2"):
                st.session_state.run_phase2 = True
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ Phase 3", use_container_width=True, key="btn_phase3"):
                st.session_state.run_phase3 = True
        
        with col2:
            if st.button("⏯️ Tout", use_container_width=True, key="btn_all"):
                st.session_state.run_all = True
        
        st.divider()
        
        if st.button("🔄 Rafraîchir les données", use_container_width=True):
            clear_cache()
            st.rerun()
        
        st.divider()
        
        st.subheader("ℹ️ Informations")
        st.info("""
        **Ordre d'exécution:**
        1. Phase 1: Préparation & Visualisation
        2. Phase 2: Simulation de Stress & Résilience
        3. Phase 3: Prédiction de Liens & ML
        
        Chaque phase dépend de la précédente.
        """)
    
    # Gestion des exécutions
    if "run_phase1" in st.session_state and st.session_state.run_phase1:
        with st.spinner("⏳ Phase 1 en cours..."):
            run_phase_1()
        st.session_state.run_phase1 = False
    
    if "run_phase2" in st.session_state and st.session_state.run_phase2:
        with st.spinner("⏳ Phase 2 en cours..."):
            run_phase_2()
        st.session_state.run_phase2 = False
    
    if "run_phase3" in st.session_state and st.session_state.run_phase3:
        with st.spinner("⏳ Phase 3 en cours..."):
            run_phase_3()
        st.session_state.run_phase3 = False
    
    if "run_all" in st.session_state and st.session_state.run_all:
        with st.spinner("⏳ Pipeline en cours..."):
            run_full_pipeline()
        st.session_state.run_all = False
    
    # Onglets principales
    tab1, tab2, tab3 = st.tabs(
        ["📊 Préparation & Visualisation (P1)", "📉 Simulation de Stress (P2)", "🔮 Prédiction de Liens (P3)"]
    )
    
    # ===== ONGLET 1: PHASE 1 =====
    with tab1:
        st.header("Phase 1: Préparation des Données & Visualisation")
        
        st.markdown("""
        Cette phase prépare les données brutes du réseau de chercheurs à partir de l'API arXiv,
        nettoie le réseau et génère les métriques fondamentales.
        """)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("KPI Principaux")
        with col2:
            if st.button("Rafraîchir", key="refresh_phase1"):
                clear_cache()
                st.rerun()
        
        display_phase1_kpis()
        
        st.divider()
        
        # Onglets secondaires pour Phase 1
        sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(
            ["Métriques", "Graphiques", "Réseau", "Clusters"]
        )
        
        with sub_tab1:
            display_phase1_metrics_table()
        
        with sub_tab2:
            display_phase1_metrics_charts()
        
        with sub_tab3:
            display_phase1_network_viz()
        
        with sub_tab4:
            df_clusters = load_csv_safe(PHASE1_OUTPUTS["clusters"])
            if df_clusters is not None:
                st.subheader("👥 Classification des Chercheurs en Clusters")
                
                # Afficher le nombre de clusters
                num_classes = df_clusters["classe"].nunique()
                st.info(f"Total: {num_classes} cluster(s) identifiés")
                
                # Tableau
                st.dataframe(df_clusters.head(50), use_container_width=True, height=400)
                st.caption(f"Affichage des 50 premiers chercheurs sur {len(df_clusters)}")
                
                # Graphique de distribution des clusters
                fig = px.bar(
                    df_clusters.groupby('classe').size().reset_index(name='count'),
                    x='classe',
                    y='count',
                    title="Distribution des Chercheurs par Cluster",
                    labels={'classe': 'Cluster', 'count': 'Nombre de chercheurs'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 Les données de clusters ne sont pas disponibles.")
    
    # ===== ONGLET 2: PHASE 2 (SIMULATION DE STRESS) =====
    with tab2:
        st.header("Phase 2: Simulation de Stress & Analyse de Résilience")
        
        st.markdown("""
        Cette phase simule les impacts de la suppression de chercheurs sur la structure
        et la connectivité du réseau pour évaluer sa résilience face aux perturbations.
        """)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Résultats de Résilience")
        with col2:
            if st.button("Rafraîchir", key="refresh_phase2"):
                clear_cache()
                st.rerun()
        
        # Onglets secondaires pour Phase 2 (Stress Simulation)
        sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(
            ["Courbes de Dégradation", "Données Détaillées", "Visualisation Interactive", "Rapport"]
        )
        
        with sub_tab1:
            display_phase2_degradation_charts()
        
        with sub_tab2:
            display_phase2_detailed_table()
        
        with sub_tab3:
            display_phase2_curves_viz()
        
        with sub_tab4:
            display_phase2_report()
    
    # ===== ONGLET 3: PHASE 3 (PRÉDICTION DE LIENS) =====
    with tab3:
        st.header("Phase 3: Prédiction de Liens & Machine Learning")
        
        st.markdown("""
        Cette phase prédit les futures collaborations entre chercheurs en utilisant
        des modèles d'apprentissage automatique basés sur la topologie du réseau.
        """)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Résultats de Prédiction")
        with col2:
            if st.button("Rafraîchir", key="refresh_phase3"):
                clear_cache()
                st.rerun()
        
        # Onglets secondaires pour Phase 3 (Link Prediction)
        sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5 = st.tabs(
            ["Prédictions", "Vulnérabilité", "Importance des Features", "Réseau Futur", "Rapport"]
        )
        
        with sub_tab1:
            display_phase3_predictions()
        
        with sub_tab2:
            display_phase3_vulnerability()
        
        with sub_tab3:
            display_phase3_feature_importance()
        
        with sub_tab4:
            display_phase3_network_viz()
        
        with sub_tab5:
            display_phase3_report()

if __name__ == "__main__":
    main()
