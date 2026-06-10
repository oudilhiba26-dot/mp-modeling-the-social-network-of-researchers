# Network Resilience & Stress Simulation

**Module**: Phase 2 of the Researcher Network Analysis Pipeline  
**Purpose**: Assess network resilience through degradation simulation and stress testing

---

## Overview

This module simulates network behavior under adverse conditions by progressively removing researchers and measuring the impact on network connectivity and structure. It provides insights into network vulnerability, critical nodes, and resilience properties essential for understanding network stability.

---

## Module Structure

```
simulateur_stress/
├── resilience_simulation.py      # Main simulation script
├── resilience_report.txt         # OUTPUT: Detailed analysis report
├── degradation_results.csv       # OUTPUT: Numerical degradation metrics
├── degradation_curves.html       # OUTPUT: Interactive visualization
└── README.md                     # This file
```

---

## Prerequisites

### Input Data Requirements

This module depends on outputs from **Phase 1** only:

**Required Input Files**:
1. `cleaned_researcher_network_edgelist.csv` - Network structure from data_prep_vis
2. `metrics_with_clusters.csv` - Researcher metrics and communities

**Optional Input Files**:
- `link_predictions.csv` - Predicted links (for future network scenario analysis, generated in Phase 3)

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

1. **Ensure input files are available**:
   Copy the required CSV files from previous phases into this directory or adjust paths in the script.

2. **Run the simulation**:
   ```bash
   python resilience_simulation.py
   ```

---

## Methodology

### Degradation Scenarios

The module tests network resilience against three degradation strategies:

#### 1. **Random Removal**
- Removes researchers randomly
- Simulates uniform threat/loss
- Baseline resilience measure

#### 2. **Targeted Attack (Degree-Based)**
- Removes highest-degree (most connected) researchers first
- Tests vulnerability to targeted attacks
- Identifies critical hub nodes

#### 3. **Targeted Attack (Betweenness-Based)**
- Removes researchers with highest betweenness centrality
- Tests impact of broker/intermediary nodes
- Measures network fragmentation risk

### Metrics Calculated

For each degradation scenario:

#### Network Connectivity Metrics
- **Giant Component Size**: Percentage of network in largest connected component
- **Number of Components**: Count of disconnected subgraphs
- **Average Path Length**: Mean shortest path between connected nodes
- **Network Density**: Proportion of possible edges present

#### Network Integrity Metrics
- **Relative Network Strength**: Weighted edge retention percentage
- **Clustering Coefficient**: Local clustering at each removal step
- **Connectivity Collapse Point**: Where network fragments
- **Robustness Index**: Integral of network size under attack

#### Centrality Preservation
- **Degree Variance**: Changes in node degree distribution
- **Betweenness Changes**: Shift in node importance
- **Community Cohesion**: Cluster fragmentation rates

---

## Output Files

### 1. `degradation_results.csv`

**Description**: Quantitative metrics for each removal step in the simulation

**Format**:
```csv
removal_step,removal_strategy,nodes_removed,network_size,giant_component,connectivity,avg_path_length,density
0,random,0,150,1.0,1.0,2.5,0.042
1,random,1,149,0.98,0.97,2.6,0.041
2,random,2,148,0.95,0.93,2.8,0.039
```

**Columns**:
- `removal_step`: Sequential number of removals
- `removal_strategy`: Type of removal (random/degree/betweenness)
- `nodes_removed`: Cumulative researchers removed
- `network_size`: Remaining nodes in network
- `giant_component`: Fraction of nodes in largest connected component
- `connectivity`: Network connectivity measure (0-1)
- `avg_path_length`: Average distance between connected nodes
- `density`: Edge density of remaining network

---

### 2. `degradation_curves.html`

**Description**: Interactive visualization of network degradation over removal steps

**Features**:
- Multiple line charts showing different metrics
- Selectable removal strategies
- Zoom and pan functionality
- Hover tooltips with exact values
- Comparison between strategies
- Critical point identification

**Visualizations Include**:
1. **Network Size vs. Removal**: Shows how quickly network shrinks
2. **Giant Component Decay**: Tracks largest connected component breakdown
3. **Connectivity Index**: Overall network connectedness
4. **Average Path Length**: Network diameter changes
5. **Density Erosion**: Edge loss over time

**Technologies**: Plotly.js, D3.js

---

### 3. `resilience_report.txt`

**Description**: Comprehensive text report with findings and interpretation

**Contents**:
```
NETWORK RESILIENCE ANALYSIS REPORT
===================================

1. EXECUTIVE SUMMARY
   - Network size and initial connectivity
   - Vulnerability assessment
   - Critical findings

2. DEGRADATION ANALYSIS
   - Random removal results
   - Degree-based attack vulnerability
   - Betweenness-based attack vulnerability

3. CRITICAL NODES IDENTIFIED
   - Most critical researchers (by removal impact)
   - Hub nodes essential for connectivity
   - Bridge nodes connecting communities

4. RESILIENCE METRICS
   - Robustness index
   - Fragmentation threshold
   - Recovery capacity (if applicable)

5. NETWORK PROPERTY CHANGES
   - Clustering coefficient trends
   - Degree distribution changes
   - Community structure preservation

6. RECOMMENDATIONS
   - Network strengthening strategies
   - Key researchers to protect
   - Redundancy requirements
```

---

## Key Metrics Explained

### Giant Component
- **Definition**: Largest connected subgraph after removals
- **Interpretation**: How many researchers remain in one connected group
- **Critical Value**: Typically drops sharply at 20-40% removal

### Network Density
- **Range**: 0 to 1
- **Definition**: Ratio of actual edges to possible edges
- **Interpretation**: 
  - High (0.7-1.0): Tightly connected network
  - Medium (0.3-0.7): Moderate connectivity
  - Low (0.0-0.3): Sparse network

### Average Path Length
- **Definition**: Mean shortest path between all node pairs
- **Interpretation**: 
  - Low values: Efficient information flow
  - High values: Network fragmentation occurring
  - Increasing trend: Network connectivity degrading

### Robustness Index
- **Formula**: Area under network size curve
- **Range**: 0 to 1
- **Interpretation**:
  - High (0.8-1.0): Very resilient network
  - Medium (0.5-0.8): Moderate resilience
  - Low (0.0-0.5): Fragile network

---

## Interpretation Guide

### Scenario Analysis

**Network is Resilient if**:
- Giant component remains >70% at 30% node removal
- Average path length increases slowly
- Network fragments only at extreme removal rates
- Density degradation follows gradual curve

**Network is Vulnerable if**:
- Giant component drops below 50% at 10% removal
- Network fragments into many components early
- Few highly connected nodes dominate
- Degree distribution is scale-free

### Critical Nodes

**Hub Nodes** (High Degree):
- Essential for network connectivity
- Removal causes immediate fragmentation
- Usually identified in degree-based attacks

**Broker Nodes** (High Betweenness):
- Connect distant network regions
- Critical for information flow
- Removal isolates communities
- Identified in betweenness attacks

---

## Use Cases

### 1. Network Vulnerability Assessment
Identify which researchers are critical to network integrity and collaboration stability.

### 2. Risk Management
Develop contingency plans for key researcher departures or unavailability.

### 3. Network Design
Understand network redundancy and suggest partnership building strategies.

### 4. Community Identification
Analyze how communities fragment under stress to understand internal cohesion.

### 5. Resource Allocation
Prioritize support/retention for critical researchers identified in simulation.

---

## Advanced Customization

### Modifying Removal Strategies

Edit `resilience_simulation.py` to implement custom removal orders:
```python
# Example: Remove by research productivity
removal_order = sorted(nodes, key=lambda x: productivity[x], reverse=True)
```

### Custom Metrics

Add new metrics by implementing calculation functions:
```python
def calculate_custom_metric(graph):
    # Your custom calculation
    return metric_value
```

### Parallel Simulations

For large networks, implement Monte Carlo iterations:
```python
# Run multiple random removal simulations for statistical significance
for iteration in range(100):
    # Simulate and collect results
```

---

## Performance Considerations

- **Network Size Impact**: O(n²) for pairwise metrics
- **Computational Complexity**: Reduced with sparse graph representations
- **Memory Usage**: Proportional to edge count
- **Execution Time**: 
  - Small networks (< 500 nodes): < 1 minute
  - Medium networks (500-5000 nodes): 1-10 minutes
  - Large networks (> 5000 nodes): 10+ minutes

### Optimization Tips
1. Use sparse graph representations
2. Calculate only essential metrics
3. Reduce number of removal steps (sample instead of step-by-step)
4. Implement parallel processing for multiple strategies

---

## Troubleshooting

### Common Issues

**Issue**: Missing input files
- **Solution**: Ensure Phase 1 and 2 have been completed; check file paths

**Issue**: Slow execution on large networks
- **Solution**: 
  - Reduce network size by sampling edges
  - Decrease removal step granularity
  - Use sparse representations

**Issue**: Unexpected metric values
- **Solution**: 
  - Verify input data quality
  - Check for isolated nodes in input
  - Review calculation method in source code

---

## Dependencies

### Core Libraries
```
pandas>=1.0.0
numpy>=1.18.0
networkx>=2.4
```

### Visualization Libraries
```
plotly>=4.0.0          # Interactive charts
matplotlib>=3.0.0      # Static visualizations
```

### Optional
```
scipy>=1.4.0           # Advanced statistical calculations
```

---

## Research Applications

This module supports research into:

1. **Network Theory**: Understanding resilience in complex networks
2. **Organizational Studies**: Human networks and collaboration networks
3. **Critical Infrastructure**: Identifying essential network nodes
4. **Disease Spread**: Modeling propagation through networks
5. **Information Diffusion**: Understanding information bottlenecks

---

## Version Information

- **Module Version**: 1.0
- **Last Updated**: June 2026
- **Python**: 3.8+
- **Status**: Active Development

---

## Integration Notes

**Upstream Dependencies** (from Phases 1 & 2):
- Network structure from Phase 1
- Predicted links from Phase 2 (for future network scenarios)

**Scientific Foundation**:
- Built on network robustness and resilience theory
- References: Holme et al. (2002), Buldyrev et al. (2010)

---

## Support & References

### Recommended Reading
- Albert, R., & Barabási, A. L. (2002). "Statistical mechanics of complex networks"
- Newman, M. E. (2010). "Networks: An Introduction"
- Holme, P., et al. (2002). "Attack vulnerability of complex networks"

### For Questions
1. Review inline code comments
2. Check console output for diagnostic messages
3. Examine degradation_results.csv for data validation
4. Refer to main backend README for module coordination

---

*This module is part of the Researcher Network Analysis Pipeline*
