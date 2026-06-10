import pandas as pd 

researcher_network_file = 'researcher_network_edgelist.csv'
researcher_network_df = pd.read_csv(researcher_network_file)
# removing duplicate rows
researcher_network_df = researcher_network_df.drop_duplicates()
#i want to remove rows where Researcher_A and Researcher_B are the same (self-loops)
researcher_network_df = researcher_network_df[researcher_network_df['Researcher_A'] !=

researcher_network_df['Researcher_B']]
# save the cleaned dataset to a new CSV file
cleaned_output_file = 'cleaned_researcher_network_edgelist.csv'
researcher_network_df.to_csv(cleaned_output_file, index=False)  
print(f"Cleaned dataset saved to {cleaned_output_file}")
