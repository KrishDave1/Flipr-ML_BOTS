import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# Sample news articles with varied topics

# Sample news articles with 2 similar subtopics & 2 distinct ones
# articles = [
#     """LeBron James led the Lakers to a 115-108 victory over the Boston Celtics. 
#     Scoring 32 points with 10 assists, he showcased his dominance. 
#     The Celtics, despite a strong start, struggled with turnovers in the second half, 
#     allowing the Lakers to secure a crucial comeback win.""",  # Sports - NBA

#     """The Kansas City Chiefs secured a dramatic overtime win in the Super Bowl against the San Francisco 49ers. 
#     Patrick Mahomes orchestrated a game-winning drive in the final moments, sealing his legacy as one of the greatest quarterbacks. 
#     The thrilling finish left fans in awe.""",  # Sports - NFL (same subtopic: Sports)

#     """The U.S. Senate has approved a $1.2 trillion infrastructure bill aimed at modernizing roads, bridges, and broadband. 
#     The bipartisan legislation is expected to create jobs, but critics warn of excessive government spending. 
#     President Biden hailed it as a transformative step for America's future.""",  # Politics

#     """The highly anticipated sequel to 'Dune' premiered last night to widespread acclaim. 
#     Critics praised Denis Villeneuve's breathtaking visuals and Timothée Chalamet's performance. 
#     The film is already being considered a strong contender for multiple Oscar nominations.""",  # Entertainment
# ]
articles = [
    """India was one of the top nations in badminton only a few years ago, with players like PV Sindhu and Saina Nehwal securing golds year after year at multiple events, including the Olympics...""",
    
    """Indian badminton star PV Sindhu has officially withdrawn from the 2025 Badminton Asia Mixed Team Championships (BAMTC)...""",
    
    """The 2025 Badminton Asia Mixed Team Championships saw multiple top players withdraw due to injuries...""",
    
    """The stock market experienced a major downturn, with tech companies losing significant value...""",
    
    """Fugitive gangster Shariq Sata is on police radar for his suspected role in the violence that erupted...""",
    
    """Sambhal: The Uttar Pradesh Police's Special Investigation Team (SIT) on Thursday submitted chargesheets..."""
]

# Step 1: Convert Articles into Embeddings
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')  # More accurate model for long texts
embeddings = model.encode(articles, normalize_embeddings=True)

# Step 2: Clustering with Agglomerative Clustering
clustering_model = AgglomerativeClustering(n_clusters=None, distance_threshold=1.2, linkage='ward')
labels = clustering_model.fit_predict(embeddings)

# Step 3: Group Articles by Cluster
subtopic_clusters = {}
for i, label in enumerate(labels):
    subtopic_clusters.setdefault(label, []).append(articles[i])

# Step 4: Generate Subtopic Names
subtopic_names = {}
for cluster, grouped_articles in subtopic_clusters.items():
    subtopic_names[cluster] = grouped_articles[0][:50] + "..."  # Take first few words for naming

# Step 5: Summarize Each Cluster
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

subtopic_summaries = {}
for cluster, grouped_articles in subtopic_clusters.items():
    combined_text = " ".join(grouped_articles)  # Merge articles under one subtopic
    summary = summarizer(combined_text, max_length=10, min_length=7, do_sample=False)  # Longer summaries
    subtopic_summaries[subtopic_names[cluster]] = summary[0]['summary_text']

# Print the results
print("\n### Topic: Various News Categories ###\n")
for subtopic, summary in subtopic_summaries.items():
    print(f"**Subtopic:** {subtopic}")
    print(f"**Summary:** {summary}\n")
