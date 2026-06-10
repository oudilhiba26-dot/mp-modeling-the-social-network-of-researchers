# Data Preparation & Network Visualization

**Module**: Phase 1 of the Researcher Network Analysis Pipeline  
**Purpose**: Collect, prepare, and visualize the researcher collaboration network

---

## Overview

This module implements a comprehensive pipeline for building and analyzing researcher collaboration networks from academic publication data. The workflow includes data collection, transformation, cleaning, network metrics calculation, community detection, and interactive visualization.

The module transforms raw publication metadata into a structured network representation, enabling subsequent analysis of researcher collaborations, influence, and community structures.

---

## Module Structure

The `data_prep_vis` directory contains all scripts and data files for Phase 1 execution:

```
data_prep_vis/
├── collecting_data.py                    # Step 1: API data collection
├── data_transforming.py                  # Step 2: Raw data transformation
├── new_data_cleaning.py                  # Step 3: Data validation & cleaning
├── metrics.py                            # Step 4: Network metrics calculation
├── clusters.py                           # Step 5: Community detection
├── graphe_presentation.py                # Step 6: Visualization generation
├── requirements.txt                      # Python dependencies
├── lib/                                  # External visualization libraries
│   ├── vis-9.1.2/                       # Vis.js network library
│   ├── tom-select/                       # UI component library
│   └── bindings/                         # JavaScript utilities
├── README.md                             # This file
├── arxiv_data.csv                        # OUTPUT: Raw publication data
├── researcher_network_edgelist.csv       # OUTPUT: Initial network
├── cleaned_researcher_network_edgelist.csv # OUTPUT: Cleaned network
├── metrics_results.csv                   # OUTPUT: Centrality metrics
├── metrics_with_clusters.csv             # OUTPUT: Enriched metrics
└── reseau_dynamique.html                 # OUTPUT: Interactive visualization
```

---

## Execution Pipeline

The module follows a sequential processing pipeline where each step depends on the output of the previous step:

```
Step 1: collecting_data.py
    ↓ Output: arxiv_data.csv
Step 2: data_transforming.py
    ↓ Output: researcher_network_edgelist.csv
Step 3: new_data_cleaning.py
    ↓ Output: cleaned_researcher_network_edgelist.csv
Step 4: metrics.py
    ↓ Output: metrics_results.csv
Step 5: clusters.py
    ↓ Output: metrics_with_clusters.csv
Step 6: graphe_presentation.py
    ↓ Output: reseau_dynamique.html
```

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- arXiv API access (publicly available, no authentication required)

### Installation Steps

1. **Navigate to the module directory**:
   ```bash
   cd data_prep_vis
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python -c "import arxiv, networkx, pandas; print('All dependencies installed successfully')"
   ```

---

## Quick Start

Execute the complete pipeline with:

```bash
python collecting_data.py       # Step 1: Collect data
python data_transforming.py     # Step 2: Transform to network
python new_data_cleaning.py     # Step 3: Clean network
python metrics.py               # Step 4: Calculate metrics
python clusters.py              # Step 5: Detect communities
python graphe_presentation.py   # Step 6: Generate visualization
```

After execution, open `reseau_dynamique.html` in a web browser to explore the interactive visualization.

---

## Detailed Workflow

### Step 1: Data Collection (`collecting_data.py`)

**Purpose**: Retrieve publication metadata from the arXiv preprint repository

**Methodology**:
- Queries arXiv API for articles in specified category (e.g., `cs.AI` for Artificial Intelligence)
- Extracts metadata: authors, title, publication date, abstract
- Aggregates multi-author publication information

**Configuration**:
```python
# In collecting_data.py, modify:
SEARCH_QUERY = "cat:cs.AI"  # Change to different category
MAX_RESULTS = 10000         # Adjust number of papers to collect
```

**Output**: `arxiv_data.csv`
```csv
title,authors,date,abstract
"Deep Learning Survey","Author1, Author2","2023-01-15","Abstract text..."
```

**Metrics**:
- Typical execution time: 5-30 minutes (depends on MAX_RESULTS)
- Output file size: 50-500 MB
- API rate limit: Handled automatically with delays

### Step 2: Data Transformation (`data_transforming.py`)

**Purpose**: Convert publication metadata into a network edge list

**Methodology**:
- Identifies co-author relationships from publication metadata
- Creates edges between all author pairs in each publication
- Weights edges by number of co-publications
- Normalizes author names

**Algorithm**:
```
For each publication with authors [a1, a2, ..., an]:
  For each pair (ai, aj) where i < j:
    Add/increment edge weight between ai and aj
```

**Output**: `researcher_network_edgelist.csv`
```csv
source,target,weight
Alice,Bob,3
Alice,Charlie,1
Bob,Charlie,2
```

**Metrics**:
- Output file size: 10-100 MB
- Execution time: 1-5 minutes
- Nodes created: Typically 10-50% of total author mentions

---

### Step 3: Data Cleaning (`new_data_cleaning.py`)

**Purpose**: Ensure data quality and network integrity

**Cleaning Operations**:
1. Remove duplicate edges
2. Eliminate self-loops (researcher paired with themselves)
3. Standardize author name formatting
4. Filter low-weight edges (optional)
5. Verify edge consistency

**Validation Checks**:
- No researcher appears with weight 0
- All edges have positive weights
- Names are consistently formatted
- No cycles in directed representation (if applicable)

**Output**: `cleaned_researcher_network_edgelist.csv`
```csv
source,target,weight
Alice,Bob,3
Alice,Charlie,1
Bob,Charlie,2
```

**Impact Metrics**:
- Duplicate edges removed: Typically 5-15%
- Self-loops removed: Usually < 1%
- Data quality score: Validation report printed to console

---

### Step 4: Network Metrics (`metrics.py`)

**Purpose**: Calculate centrality and structural measures for each researcher

**Centrality Measures Computed**:

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| **Degree** | Number of collaborators | Direct collaboration count |
| **Betweenness** | Proportion of shortest paths through node | Bridging importance in network |
| **Closeness** | Inverse average distance to all nodes | Proximity/accessibility in network |
| **PageRank** | Eigenvalue-based importance | Overall influence/authority |
| **Clustering Coefficient** | Proportion of closed triangles | Local clustering tendency |
| **Eigenvector Centrality** | Weighted connection importance | Connected to important researchers |

**Output**: `metrics_results.csv`
```csv
researcher,degree,betweenness,closeness,pagerank,clustering_coeff
Alice,15,0.042,0.456,0.025,0.38
Bob,12,0.031,0.423,0.021,0.42
Charlie,8,0.015,0.389,0.015,0.51
```

**Metrics**:
- Execution time: 2-10 minutes (depends on network size)
- Output contains 6+ numerical metrics per researcher
- Statistical summary printed to console

---

### Step 5: Community Detection (`clusters.py`)

**Purpose**: Identify groups of closely connected researchers (communities)

**Algorithm**: Louvain Modularity Optimization
- Detects natural community structure
- Maximizes within-community edges
- Minimizes between-community edges
- Assigns each researcher to single community

**Process**:
1. Load cleaned network and metrics
2. Apply Louvain algorithm
3. Merge community assignments with metrics
4. Generate statistics for each community

**Output**: `metrics_with_clusters.csv`
```csv
researcher,degree,betweenness,closeness,pagerank,clustering_coeff,community
Alice,15,0.042,0.456,0.025,0.38,0
Bob,12,0.031,0.423,0.021,0.42,0
Charlie,8,0.015,0.389,0.015,0.51,1
Diana,10,0.028,0.401,0.018,0.45,1
```

**Metrics**:
- Execution time: 1-5 minutes
- Communities detected: Typically 5-50 depending on network
- Modularity score: Reported in console output
- Inter-community edges percentage: Indicates cluster strength

**Interpretation**:
- High modularity (> 0.4): Strong, distinct communities
- Low modularity (< 0.2): Weak community structure
- Average community size: Network density indicator

---

### Step 6: Visualization (`graphe_presentation.py`)

**Purpose**: Generate interactive HTML visualization of the researcher network

**Visualization Features**:
- **Node Coloring**: By detected community (each color = one community)
- **Node Sizing**: Proportional to PageRank (importance)
- **Edge Appearance**: Width proportional to collaboration frequency
- **Interactivity**: 
  - Drag nodes to explore layout
  - Hover for detailed researcher information
  - Zoom and pan functionality
  - Filter by community or metrics
- **Layout Algorithm**: Force-directed (simulates physical forces)

**Output**: `reseau_dynamique.html`
- Standalone HTML file (fully contained)
- Runs in any modern web browser
- No server required
- File size: 5-50 MB

**Technologies Used**:
- Vis.js: Network visualization library
- D3.js: Data-driven visualization
- Tom-select: Interactive filters

**Browser Compatibility**:
- Chrome/Chromium: Full support
- Firefox: Full support
- Safari: Full support
- Internet Explorer: Limited support

---

## Output Files Reference

### Input Files

| File | Source | Purpose |
|------|--------|---------|
| arXiv API | External | Raw publication metadata |

### Generated Files

| File | Step | Format | Size | Contents |
|------|------|--------|------|----------|
| `arxiv_data.csv` | 1 | CSV | 50-500 MB | Raw publications with authors |
| `researcher_network_edgelist.csv` | 2 | CSV | 10-100 MB | Initial co-author edges |
| `cleaned_researcher_network_edgelist.csv` | 3 | CSV | 10-100 MB | Validated edge list |
| `metrics_results.csv` | 4 | CSV | 1-10 MB | Centrality metrics |
| `metrics_with_clusters.csv` | 5 | CSV | 1-10 MB | Metrics + community IDs |
| `reseau_dynamique.html` | 6 | HTML | 5-50 MB | Interactive visualization |

---

## Key Concepts & Terminology

### Network Concepts

**Node**: Represents a researcher (author) in the network
**Edge**: Represents a collaboration (co-authorship) between two researchers
**Weight**: Number of co-publications between two researchers
**Component**: Connected subgroup of researchers
**Isolate**: Node with no connections

### Centrality Measures

**Degree Centrality**: Number of direct collaborators
- Researchers with high degree are prolific collaborators
- Simple measure, easy to interpret

**Betweenness Centrality**: Importance as a bridge between groups
- High values indicate "gatekeeper" researchers
- Critical for network communication flow

**PageRank**: Authority/importance score
- Iterative calculation based on incoming connections
- Accounts for quality of connections, not just quantity
- Values typically 0.0-1.0

**Clustering Coefficient**: Local density of connections
- Measures tendency of neighbors to connect
- Range: 0 (no local clustering) to 1 (complete local clique)

---

## Dependencies

### Core Libraries

```txt
pandas>=1.0.0          # Data manipulation
numpy>=1.18.0          # Numerical computing
networkx>=2.4          # Graph/network analysis
python-louvain>=0.15   # Community detection
arxiv>=1.4.0           # arXiv API interface
pyvis>=0.1.9           # Network visualization
plotly>=4.0.0          # Interactive plotting
```

Install with:
```bash
pip install -r requirements.txt
```

---

## Configuration & Customization

### Modifying Data Collection

Edit `collecting_data.py`:
```python
SEARCH_QUERY = "cat:cs.LG"  # Change to Machine Learning papers
MAX_RESULTS = 5000          # Collect 5000 papers instead of default
START_DATE = "2020-01-01"   # Filter by date range
```

### Filtering Network

Edit `new_data_cleaning.py`:
```python
MIN_EDGE_WEIGHT = 2         # Only keep researchers with 2+ co-publications
MAX_NODES = 1000            # Limit to top 1000 researchers by degree
```

### Customizing Visualization

Edit `graphe_presentation.py`:
```python
NODE_SIZE_MULTIPLIER = 30   # Adjust node size scale
EDGE_WIDTH_MULTIPLIER = 1.5 # Adjust edge thickness
COLOR_SCHEME = "rainbow"    # Change color palette
```

---

## Troubleshooting

### Common Issues & Solutions

**Issue**: arXiv API timeout
- **Solution**: Reduce MAX_RESULTS or increase timeout delay
- **Code**: In `collecting_data.py`, increase `time.sleep(3)` value

**Issue**: Memory error on large datasets
- **Solution**: Process in smaller batches or filter by date range
- **Code**: Add date filtering in data collection step

**Issue**: Visualization HTML too large
- **Solution**: Reduce network size by filtering low-degree nodes
- **Code**: In `new_data_cleaning.py`, increase MIN_EDGE_WEIGHT

**Issue**: Communities not detected properly
- **Solution**: Increase network density by including more papers
- **Code**: Increase MAX_RESULTS in collection step

**Issue**: HTML visualization won't open
- **Solution**: 
  1. Verify file was created (check file size)
  2. Use full file path: `file:///C:/path/to/reseau_dynamique.html`
  3. Try different browser
  4. Check browser console for JavaScript errors

---

## Performance Optimization

### Execution Time Estimates

| Network Size | Collection | Transform | Clean | Metrics | Clusters | Visualize | **Total** |
|--------------|-----------|-----------|-------|---------|----------|-----------|---------|
| 100 papers | 2 min | 30 sec | 10 sec | 30 sec | 20 sec | 10 sec | ~4 min |
| 1,000 papers | 10 min | 3 min | 30 sec | 2 min | 1 min | 30 sec | ~17 min |
| 10,000 papers | 60 min | 20 min | 3 min | 15 min | 5 min | 3 min | ~106 min |

### Memory Requirements

- Small networks (< 1000 researchers): < 1 GB
- Medium networks (1000-10000 researchers): 1-5 GB
- Large networks (> 10000 researchers): 5+ GB

### Optimization Tips

1. **Parallel processing**: Use multiprocessing for data transformation
2. **Sparse representations**: Use sparse matrices for large networks
3. **Batch processing**: Collect data in time windows
4. **Sampling**: Use stratified sampling for very large networks

---

## Academic References

### Key Papers

1. Newman, M. E. J. (2003). "The structure and function of complex networks"
2. Blondel, V. D., et al. (2008). "Fast unfolding of communities in large networks"
3. Barabási, A. L., & Albert, R. (1999). "Emergence of scaling in random networks"
4. Freeman, L. C. (1977). "A set of measures of centrality based on betweenness"

### Related Methodologies

- Co-authorship network analysis
- Social network analysis
- Complex network science
- Community detection algorithms
- Network visualization techniques

---

## Validation & Quality Assurance

### Data Validation Checks

After each step, the scripts verify:
- ✓ No missing required fields
- ✓ Edge weights are positive integers
- ✓ No duplicate edges
- ✓ Consistent researcher naming
- ✓ Valid metric values (0-1 range where applicable)

### Output Verification

Validate results with:
```bash
# Check file integrity
wc -l *.csv          # Line count

# Verify data quality
python -c "import pandas as pd; df = pd.read_csv('metrics_results.csv'); print(df.describe())"
```

---

## Version Information

- **Module Version**: 1.0
- **Last Updated**: June 2026
- **Python**: 3.8+
- **Status**: Active Development

---

## Integration with Other Modules

**Outputs Feed Into**:
- Phase 2: Link Prediction (uses cleaned network & metrics)
- Phase 3: Resilience Simulation (uses network structure)

**Coordination Notes**:
- All output files must be generated before proceeding to Phase 2
- File naming must not be changed (Phase 2 scripts expect specific names)
- Metadata in metrics file is critical for accurate community detection

---

## Support & Contact

### Getting Help

1. Check the troubleshooting section above
2. Review console output for error messages
3. Verify input data quality
4. Refer to referenced academic papers for methodological questions
5. Check dependencies are correctly installed

### Reporting Issues

Include:
- Python version and OS
- Error message with full traceback
- Input data characteristics (number of papers, date range)
- Steps completed successfully before error

---

*This module is part of the Researcher Network Analysis Pipeline*
*For the complete project overview, see the parent backend README.md*

