import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Configuration de la page
# =========================

st.set_page_config(
    page_title="Research Network Stress Simulator",
    page_icon="🔬",
    layout="wide"
)

# =========================
# Titre
# =========================

st.title("🔬 Research Network Stress Simulator")

st.write("""
Cette application permet de simuler des attaques sur un réseau de chercheurs
et d'analyser sa résilience.
""")

# =========================
# Sidebar
# =========================

st.sidebar.header("⚙️ Paramètres")

theme = st.sidebar.text_input(
    "🔍 Sujet de recherche",
    "Artificial Intelligence"
)

attack_type = st.sidebar.selectbox(
    "Type d'attaque",
    [
        "Random",
        "Degree",
        "Betweenness"
    ]
)

stress_level = st.sidebar.slider(
    "Pourcentage supprimé",
    min_value=0,
    max_value=50,
    value=10,
    step=5
)

launch = st.sidebar.button(
    "🚀 Lancer la simulation"
)

if launch:
    st.success(
        f"Recherche : {theme} | Attaque : {attack_type} | Stress : {stress_level}%"
    )

# =========================
# KPI
# =========================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Chercheurs",
        150
    )

with col2:
    st.metric(
        "Collaborations",
        420
    )

with col3:
    st.metric(
        "Densité",
        0.045
    )

# =========================
# Onglets
# =========================

tab1, tab2 = st.tabs(
    [
        "Simulation",
        "Prédiction"
    ]
)

# =========================
# Onglet Simulation
# =========================

with tab1:

    st.subheader(
        "Résultats de la simulation"
    )

    df = pd.DataFrame({
        "pct_deleted":[0,5,10,15,20,25,30],
        "giant_component":[150,140,120,95,70,50,30]
    })

    fig = px.line(
        df,
        x="pct_deleted",
        y="giant_component",
        title="Dégradation du réseau",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Cartographie du réseau"
    )

    st.info(
        "Le graphe Pyvis sera affiché ici lorsque le backend sera connecté."
    )

# =========================
# Onglet Prédiction
# =========================

with tab2:

    st.subheader(
        "Analyse prédictive"
    )

    df_vulnerable = pd.DataFrame({
        "Chercheur":[
            "Researcher A",
            "Researcher B",
            "Researcher C"
        ],
        "Score":[
            0.92,
            0.81,
            0.77
        ]
    })

    st.dataframe(
        df_vulnerable,
        use_container_width=True
    )
