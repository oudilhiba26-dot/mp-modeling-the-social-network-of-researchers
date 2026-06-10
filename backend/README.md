# Backend - Modeling the Social Network of Researchers

## Overview

This backend repository implements a comprehensive analysis pipeline for modeling and analyzing the social network of researchers. The project encompasses three main analytical modules that work together to provide insights into researcher collaboration networks, predict future research partnerships, and assess network resilience under stress conditions.

---

## Project Structure

The backend is organized into three sequential modules that must be executed in order:

```
backend/
├── 1-data_prep_vis/           # Phase 1: Data Collection, Preparation & Visualization
├── 2-simulateur_stress/       # Phase 2: Network Resilience & Stress Simulation
├── 3-link_predictionML/       # Phase 3: Link Prediction & Machine Learning Analysis
└── README.md                  # This file
```

---

## Modules Description

### 1. Data Preparation and Visualization (`data_prep_vis/`)

**Purpose**: Collects, processes, and visualizes the researcher collaboration network from academic publication data.

**Key Functionality**:
- Collect researcher and publication data from arXiv API
- Extract and normalize collaboration relationships
- Calculate network centrality metrics
- Detect researcher communities/clusters
- Generate interactive network visualizations

**Main Outputs**:
- `arxiv_data.csv` - Raw publication data
- `researcher_network_edgelist.csv` - Researcher collaboration edges
- `cleaned_researcher_network_edgelist.csv` - Cleaned network data
- `metrics_results.csv` - Network centrality metrics
- `metrics_with_clusters.csv` - Metrics enriched with community detection
- `reseau_dynamique.html` - Interactive network visualization

**Technologies**: Python (pandas, networkx, pyvis, arxiv API)

**Execution**: Must be executed first as it generates the base network data required by subsequent phases.

---

### 2. Resilience Simulation & Stress Testing (`simulateur_stress/`)

**Purpose**: Simulates network behavior under stress and evaluates resilience to researcher disruptions. This phase must be executed before link prediction to establish baseline network resilience metrics.

**Key Functionality**:
- Simulate network degradation scenarios
- Model impact of researcher removal on network connectivity
- Calculate resilience metrics
- Identify critical nodes and vulnerabilities
- Generate degradation curves and reports

**Main Outputs**:
- `degradation_results.csv` - Results from degradation scenarios
- `degradation_curves.html` - Visualization of network resilience curves
- `resilience_report.txt` - Comprehensive resilience analysis

**Input Requirements**: Phase 1 outputs (cleaned network data)

**Technologies**: Python (networkx, simulation algorithms)

**Execution**: Must be executed second, after Phase 1, before link prediction analysis.

---

### 3. Link Prediction & Machine Learning (`link_predictionML/`)

**Purpose**: Predicts future research collaborations using machine learning and analyzes predictive features. This phase builds upon resilience baseline established in Phase 2.

**Key Functionality**:
- Train ML models to predict future links between researchers
- Feature engineering based on network topology and resilience data
- Evaluate prediction accuracy and model performance
- Generate vulnerability scores for predicted links
- Visualize predicted collaboration networks

**Main Outputs**:
- `link_predictions.csv` - Predicted future collaborations
- `vulnerability_scores.csv` - Scores for prediction confidence
- `reseau_futur.html` - Visualization of predicted network
- `feature_importance.csv` - Feature importance analysis
- `predictive_report.txt` - Detailed analysis report

**Input Requirements**: Phase 1 outputs and optional Phase 2 results

**Technologies**: Python (scikit-learn, networkx, machine learning algorithms)

**Execution**: Must be executed last, after Phase 2 stress simulation.

---

## Execution Pipeline

**IMPORTANT**: The modules must be executed in the following order to ensure correct analysis:

```
Phase 1: Data Collection & Preparation (data_prep_vis/)
    ↓
    Generates: cleaned network, metrics, clusters
    ↓
Phase 2: Resilience Simulation & Stress Testing (simulateur_stress/)
    ↓
    Analyzes: network resilience, critical nodes, degradation curves
    ↓
Phase 3: Link Prediction & Machine Learning Analysis (link_predictionML/)
    ↓
    Generates: future collaboration predictions, ML models, vulnerability scores
```

### Rationale for Execution Order

1. **Phase 1 First**: Provides the foundation - clean network data with metrics and communities
2. **Phase 2 Second**: Establishes network resilience baseline and identifies critical infrastructure
3. **Phase 3 Third**: Uses Phase 2 insights for more informed link prediction and vulnerability assessment

### Quick Start

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Execute Phase 1** (Data Preparation):
   ```bash
   cd data_prep_vis
   pip install -r requirements.txt
   python collecting_data.py
   python data_transforming.py
   python new_data_cleaning.py
   python metrics.py
   python clusters.py
   python graphe_presentation.py
   ```

3. **Execute Phase 2** (Link Prediction):
   ```bash
   cd ../link_predictionML
   pip install -r requirements.txt
   python predictive_analysis.py
   ```

4. **Execute Phase 3** (Stress Simulation):
   ```bash
   cd ../simulateur_stress
   python resilience_simulation.py
   ```

---

## Key Concepts & Terminology

### Network Analysis Terms
- **Centrality Metrics**: Measures of node importance (degree, betweenness, closeness, PageRank)
- **Community Detection**: Algorithm to identify clusters of densely connected researchers
- **Link Prediction**: Predicting future collaborations based on network structure
- **Network Resilience**: Ability of the network to maintain connectivity under disruption

### Data Files
- **Edge List**: CSV file with pairs of connected researchers and edge weights
- **Metrics**: Quantitative measures of researcher importance and position in the network
- **Clusters/Communities**: Groups of researchers with strong collaborative bonds

---

## Dependencies

### Common Requirements
- Python 3.8+
- pandas, numpy (data manipulation)
- networkx (graph analysis)
- scikit-learn (machine learning)

### Module-Specific Requirements
Refer to each module's `requirements.txt` for specific dependencies.

---

## Research Methodology

This project implements a three-phase methodology for analyzing researcher networks:

1. **Phase 1 - Exploratory Analysis**: Understanding network structure through visualization and metrics
2. **Phase 2 - Predictive Modeling**: Forecasting future collaborations using ML techniques
3. **Phase 3 - Vulnerability Assessment**: Testing network stability and identifying critical nodes

---

## Output Visualizations

- **Interactive Network Graphs**: HTML-based visualizations using vis.js library
- **Degradation Curves**: Charts showing network performance under stress
- **Community Maps**: Color-coded researcher clusters and their relationships
- **Feature Importance Plots**: Visualization of predictive feature significance

---

## Contributing

Each module is self-contained and can be developed independently. However, ensure:
- Phase 1 outputs are generated before running Phase 2
- Phase 2 analysis should incorporate Phase 1 results
- All Python code follows PEP 8 style guidelines
- Update module READMEs when making significant changes

---

## License & Attribution

This project is developed for academic research purposes. All contributions should be properly documented and attributed.

---

## Contact & Support

For questions about specific modules, refer to the individual README files in each module directory:
- `data_prep_vis/README.md` - Data preparation guidance
- `link_predictionML/README.md` - Machine learning details
- `simulateur_stress/README.md` - Resilience testing information

---

## Last Updated

Generated: June 2026
Project Status: Active Development
