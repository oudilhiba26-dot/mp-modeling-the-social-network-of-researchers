# Link Prediction & Machine Learning Analysis

**Module**: Phase 2 of the Researcher Network Analysis Pipeline  
**Purpose**: Predict future research collaborations using machine learning techniques

---

## Overview

This module implements machine learning-based link prediction to forecast future collaborations between researchers based on their historical network structure. It analyzes network topology features and trains predictive models to identify potential new partnerships.

---

## Module Structure

```
link_predictionML/
├── predictive_analysis.py        # Main script for link prediction
├── requirements.txt              # Python dependencies
├── lib/                          # External libraries for visualization
│   ├── vis-9.1.2/              # Vis.js network visualization library
│   ├── tom-select/              # Tom-select UI component library
│   └── bindings/                # JavaScript utility bindings
├── link_predictions.csv          # OUTPUT: Predicted future links
├── vulnerability_scores.csv      # OUTPUT: Link confidence scores
├── feature_importance.csv        # OUTPUT: Predictive feature analysis
├── reseau_futur.html             # OUTPUT: Interactive visualization
└── predictive_report.txt         # OUTPUT: Analysis report
```

---

## Prerequisites

### Input Data Requirements

This module depends on outputs from **Phase 1** (Data Preparation):

**Required Input Files**:
1. `cleaned_researcher_network_edgelist.csv` - Clean network edge list from data_prep_vis
2. `metrics_with_clusters.csv` - Centrality metrics and community information

**File Format Example** (Edge List):
```csv
source,target,weight
researcher1,researcher2,5
researcher1,researcher3,2
researcher2,researcher3,3
```

---

## Execution

### Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure Phase 1 outputs are available**:
   Copy or verify the following files from `data_prep_vis/`:
   - `cleaned_researcher_network_edgelist.csv`
   - `metrics_with_clusters.csv`

### Run the Analysis

```bash
python predictive_analysis.py
```

---

## Methodology

### Feature Engineering

The module extracts network topology features for each potential researcher pair:

- **Common Neighbors**: Number of shared collaborators
- **Jaccard Similarity**: Overlap of collaborator networks
- **Adamic-Adar Index**: Weighted common neighbors based on degree
- **Preferential Attachment**: Product of node degrees
- **Resource Allocation Index**: Resource flow through common neighbors
- **Clustering Coefficient**: Local clustering in neighborhoods
- **Shortest Path Distance**: Network distance between researchers

### Machine Learning Models

Implemented algorithms:
- **Logistic Regression**: Baseline probabilistic classifier
- **Random Forest**: Ensemble-based link prediction
- **Gradient Boosting**: XGBoost or similar for enhanced accuracy
- **Neural Networks**: Deep learning approach (if applicable)

### Model Validation

- **Train-Test Split**: Temporal or random splitting of edges
- **Cross-Validation**: K-fold validation for robustness
- **Evaluation Metrics**:
  - Precision & Recall
  - ROC-AUC Score
  - F1-Score
  - Mean Average Precision

---

## Output Files

### 1. `link_predictions.csv`

**Description**: Predicted future collaborations between researchers

**Format**:
```csv
researcher_a,researcher_b,prediction_score,probability
alice,bob,0.87,0.87
charlie,diana,0.65,0.65
```

**Columns**:
- `researcher_a`: First researcher identifier
- `researcher_b`: Second researcher identifier
- `prediction_score`: Model confidence score (0-1)
- `probability`: Likelihood of future collaboration

---

### 2. `vulnerability_scores.csv`

**Description**: Confidence and vulnerability metrics for each predicted link

**Format**:
```csv
researcher_a,researcher_b,confidence,uncertainty,model_agreement
alice,bob,0.92,0.08,0.95
```

**Columns**:
- `researcher_a`: First researcher
- `researcher_b`: Second researcher
- `confidence`: Model confidence in the prediction
- `uncertainty`: Prediction uncertainty margin
- `model_agreement`: Consensus across multiple models

---

### 3. `feature_importance.csv`

**Description**: Importance ranking of features used in prediction

**Format**:
```csv
feature,importance_score,model_contribution
common_neighbors,0.23,0.18
jaccard_similarity,0.19,0.21
adamic_adar,0.15,0.16
```

---

### 4. `reseau_futur.html`

**Description**: Interactive visualization of the predicted collaboration network

**Features**:
- Color-coded nodes by researcher community
- Edge thickness represents prediction confidence
- Node size reflects researcher centrality
- Interactive exploration and filtering
- Comparison between current and predicted networks

**Technologies**: Vis.js, D3.js

---

### 5. `predictive_report.txt`

**Description**: Comprehensive text report with analysis findings

**Contents**:
- Model performance metrics
- Feature importance rankings
- Top predicted collaborations
- Recommendations for new partnerships
- Statistical summary
- Confidence intervals

---

## Key Metrics Explained

### Prediction Score
- **Range**: 0 to 1
- **Interpretation**: 
  - 0.0-0.3: Low probability of collaboration
  - 0.3-0.6: Moderate probability
  - 0.6-1.0: High probability

### Feature Importance
- **Common Neighbors**: Weight of shared collaborators
- **Jaccard Similarity**: Network structure similarity
- **Preferential Attachment**: Tendency to connect to highly connected researchers

---

## Interpretation & Use Cases

### Use Case 1: Identifying Collaboration Opportunities
Researchers with high prediction scores are likely candidates for future collaboration partnerships.

### Use Case 2: Network Evolution Forecasting
Track predicted changes in network structure over time periods.

### Use Case 3: Missing Collaboration Detection
Identify overlooked collaborations that should exist based on network structure.

### Use Case 4: Vulnerability Assessment
High-scoring predictions may represent critical links for network stability.

---

## Advanced Options

### Tuning Model Parameters

Edit `predictive_analysis.py` to modify:
- Feature extraction methods
- Model hyperparameters
- Train-test split ratios
- Validation strategy

### Adding Custom Features

Extend `predictive_analysis.py` with domain-specific features:
- Co-authorship recency
- Citation patterns
- Research topic similarity
- Geographic proximity

---

## Dependencies

### Core Libraries
```
pandas>=1.0.0
numpy>=1.18.0
networkx>=2.4
scikit-learn>=0.24.0
```

### Optional Libraries
```
xgboost>=1.0.0          # For gradient boosting models
lightgbm>=3.0.0         # Alternative gradient boosting
tensorflow>=2.0.0       # For neural network models
pyvis>=0.1.9            # Network visualization
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## Troubleshooting

### Common Issues

**Issue**: Missing input files from Phase 1
- **Solution**: Run `data_prep_vis` module first and ensure outputs are generated

**Issue**: Memory error on large networks
- **Solution**: Reduce feature set or sample network edges during training

**Issue**: Low prediction accuracy
- **Solution**: 
  - Increase training data from Phase 1
  - Engineer additional features
  - Adjust model hyperparameters
  - Try ensemble methods

---

## Performance Considerations

- **Network Size Impact**: Scales O(n²) with number of researchers
- **Feature Extraction**: Most computationally expensive step
- **Model Training**: Depends on number of potential edges
- **Optimization**: Use sparse representations for large networks

---

## Citation & References

If using this module in research, cite the following methodologies:

1. **Link Prediction**: Lü, L., & Zhou, T. (2011). Link prediction in complex networks
2. **Community Detection**: Blondel et al. (2008). Fast unfolding of communities
3. **Network Analysis**: Newman, M. E. (2010). Networks: An Introduction

---

## Version Information

- **Module Version**: 1.0
- **Last Updated**: June 2026
- **Python**: 3.8+
- **Status**: Active Development

---

## Integration Notes

**Upstream Dependencies** (from Phase 1):
- Data from `data_prep_vis/cleaned_researcher_network_edgelist.csv`
- Metrics from `data_prep_vis/metrics_with_clusters.csv`

**Downstream Usage** (for Phase 3):
- Predicted links can be used for stress simulation
- Network topology insights inform resilience testing

---

## Support & Contributions

For questions or improvements:
1. Review the predictive_analysis.py code comments
2. Check console output for diagnostic information
3. Examine output CSV files for data validation
4. Refer to main backend README for module coordination

---

*This module is part of the Researcher Network Analysis Pipeline*
