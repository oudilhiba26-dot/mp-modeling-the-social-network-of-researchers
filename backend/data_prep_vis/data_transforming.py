import pandas as pd
import ast
from itertools import combinations
from collections import Counter


# 1. Load the original CSV dataset (image_1.png)
input_filename = 'arxiv_data.csv'
output_filename = 'researcher_network_edgelist.csv'

try:
    df = pd.read_csv(input_filename)
except FileNotFoundError:
    print(f"Error: Could not find the file '{input_filename}'. Please ensure it exists.")
    exit()

# 2. Convert the 'Authors' column from string representations of lists 
# (e.g., "['A', 'B']") into actual Python lists.
# This is crucial because pd.read_csv imports them as plain strings.
print("Parsing author lists...")
df['Authors'] = df['Authors'].apply(ast.literal_eval)

# 3. Generate all possible pairs of co-authors across all papers
all_pairs = []
print("Generating author pairs...")

for authors_list in df['Authors']:
    # Standardize names to 'Lastname I.' format (Optional but recommended)
    # This helps match "Jure Leskovec" with "Leskovec J."
    cleaned_authors = []
    for name in authors_list:
        parts = name.strip().split()
        if len(parts) >= 2:
            # Format as: Leskovec J.
            standardized_name = f"{parts[-1]} {parts[0][0]}."
            cleaned_authors.append(standardized_name)
        else:
            cleaned_authors.append(name.strip())

    # Generate all pairs (Author A, Author B) from this paper.
    # We sort them to ensure (A, B) is treated the same as (B, A).
    pairs = list(combinations(sorted(cleaned_authors), 2))
    all_pairs.extend(pairs)

# 4. Count how many times each specific pair appears (co-publications)
print("Counting co-publications...")
pair_counts = Counter(all_pairs)

# 5. Format the data into the structure requested (image_2.png)
print("Formatting new dataset...")
network_data = []
for (auth_a, auth_b), count in pair_counts.items():
    network_data.append({
        "Researcher_A": auth_a,
        "Researcher_B": auth_b,
        "Co_Publications": count
    })

# 6. Save the new DataFrame to a new CSV file
new_df = pd.DataFrame(network_data)

# Sort by Co_Publications descending to show strongest links first
new_df = new_df.sort_values(by="Co_Publications", ascending=False)

new_df.to_csv(output_filename, index=False)
print(f"Success! New network dataset saved as '{output_filename}'.")
print(new_df.head())