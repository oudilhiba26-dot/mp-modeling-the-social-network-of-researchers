import arxiv

# 1. Initialize the Client (Handles rate limiting automatically)
client = arxiv.Client()

# 2. Define your search
# Use 'ti' for title, 'au' for author, or 'cat' for category
search = arxiv.Search(
    query = "cat:cs.AI", # This searches for Artificial Intelligence papers
    max_results = 5000,  # Number of articles to collect (increased for big dataset)
    sort_by = arxiv.SortCriterion.SubmittedDate
)

# 3. Collect and store the information
import pandas as pd

print("Collecting AI papers from arXiv...")
data = []
count = 0

for paper in client.results(search):
    count += 1
    data.append({
        "Title": paper.title,
        "Authors": [a.name for a in paper.authors],
        "Date": paper.published,
        "Summary": paper.summary,
        "URL": paper.entry_id,
        "PDF_URL": paper.pdf_url
    })
    
    if count % 100 == 0:
        print(f"Collected {count} papers...")

print(f"\nTotal papers collected: {count}")

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("arxiv_data.csv", index=False)
print(f"Data saved to arxiv_data.csv")