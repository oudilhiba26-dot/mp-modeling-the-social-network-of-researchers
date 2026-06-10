import pandas as pd
from pathlib import Path

backend = Path(r'C:\Users\PC\Desktop\mp_modeling_the_social_network_of_reseqrchers\mp-modeling-the-social-network-of-researchers\backend')

files = {
    'cleaned_researcher_network_edgelist.csv': backend / 'data_prep_vis' / 'cleaned_researcher_network_edgelist.csv',
    'metrics_results.csv': backend / 'data_prep_vis' / 'metrics_results.csv',
    'metrics_with_clusters.csv': backend / 'data_prep_vis' / 'metrics_with_clusters.csv',
    'degradation_results.csv': backend / 'simulateur_stress' / 'degradation_results.csv',
    'link_predictions.csv': backend / 'link_predictionML' / 'link_predictions.csv',
    'vulnerability_scores.csv': backend / 'link_predictionML' / 'vulnerability_scores.csv',
    'feature_importance.csv': backend / 'link_predictionML' / 'feature_importance.csv',
}

for name, path in files.items():
    if path.exists():
        try:
            df = pd.read_csv(path)
            print(f'\n=== {name} ===')
            print(f'Shape: {df.shape}')
            print(f'Columns: {list(df.columns)}')
            print(f'First row:\n{df.iloc[0] if len(df) > 0 else "Empty"}')
        except Exception as e:
            print(f'\n=== {name} === ERROR: {e}')
    else:
        print(f'\n=== {name} === NOT FOUND')
