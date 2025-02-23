import os
import json
import requests
import json
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
from scrapy.utils.log import configure_logging
from newspaper import Article
from time import sleep
import spacy
from flask import Flask, request, jsonify
from transformers import pipeline, AutoTokenizer, AutoModel
from neo4j import GraphDatabase
from scipy.spatial.distance import cosine
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from transformers import pipeline, AutoTokenizer
from gensim.models import KeyedVectors
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import random
import re
# Summarizer starts

from sentence_transformers import SentenceTransformer
model_sentence_transformer = SentenceTransformer("all-mpnet-base-v2")

from transformers import pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
tokenizer = summarizer.tokenizer
tokenizer.model_max_length = 1024  
MAX_CHUNK_TOKENS = 1200 
MIN_CHUNK_TOKENS = 600
MIN_TOTAL_LAST = 2 * MIN_CHUNK_TOKENS


def load_json(filename):
    """Load JSON data from a file."""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

all_articles = load_json("extracted_articles.json")
all_contents = []

for article in all_articles:
    all_contents.append(article.get("content"))

def super_summary(articles):
    # Step 1: Convert Articles into Embeddings
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    embeddings = model.encode(articles, normalize_embeddings=True)

    # Step 3: Clustering with Agglomerative Clustering
    clustering_model = AgglomerativeClustering(n_clusters=None, distance_threshold=1.2, linkage='ward')
    labels = clustering_model.fit_predict(embeddings)

    # Step 4: Group Articles by Cluster
    subtopic_clusters = {}
    for i, label in enumerate(labels):
        subtopic_clusters.setdefault(label, []).append(articles[i])

    # Step 5: Concatenate Articles in Each Cluster
    cluster_texts = {cluster: " ".join(grouped_articles) for cluster, grouped_articles in subtopic_clusters.items()}

    # Step 6: Load BART large model for classification
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", framework="pt")

    # Step 7: Define Candidate Labels
    candidate_labels = [
        "Government", "Elections", "Foreign Policy", "Legislation", "Political Parties", 
        "Political Debates", "Protests & Movements", "Public Policy", "Corruption", "Political Scandals",
        
      "Stock Market", "Business", "Inflation", "Trade", "Economic Policies", 
        "GDP & Growth Rate", "Unemployment", "Banking & Finance", "Real Estate", "International Trade",
        
        "AI", "Cybersecurity", "Gadgets", "Space Exploration", "Internet & Connectivity", 
        "Robotics", "Blockchain & Cryptocurrency", "Quantum Computing", "Software & Programming", "5G & Telecommunications",
        
        "Sports", "Cricket", "Football", "Tennis", "Badminton", "Olympics", 
        "Basketball", "Athletics", "Hockey", "Golf", "Wrestling",
        
       "Medicine", "Pandemic", "Mental Health", "Nutrition", "Fitness & Exercise", 
        "Healthcare Policies", "Diseases & Vaccines", "Alternative Medicine", "Public Health", "Medical Research",
        
        "Schools", "Universities", "Scholarships", "Research", "Online Learning", 
        "Examinations & Results", "Student Loans", "Educational Policies", "Teaching Methods", "EdTech",
        
        "Law Enforcement", "Court Cases", "Scams & Frauds", "Violence", "Cybercrime", 
        "White-Collar Crime", "Drug Trafficking", "Kidnapping", "Human Trafficking", "Organized Crime",
        
        "Startups", "Corporate News", "Mergers & Acquisitions", "Real Estate Market", "E-commerce", 
        "Small Businesses", "Investment Strategies", "Taxation Policies", "Supply Chain & Logistics", "Financial Scandals",
        
        "Climate Change", "Renewable Energy", "Deforestation", "Wildlife Conservation", "Pollution & Air Quality", 
        "Ocean & Marine Life", "Natural Disasters", "Sustainable Development", "Carbon Emissions", "Water Crisis",
        
        "Space Exploration", "Astronomy", "Physics", "Biology & Genetics", "Chemistry", 
        "Scientific Discoveries", "AI in Science", "Renewable Energy Technologies", "Geology & Earth Science", "Research & Innovations"
          "Movies & Cinema",
        "TV Shows & Series",
        "Music & Concerts",
        "Celebrity News & Gossip",
        "Awards & Red Carpet Events",
        "Streaming Platforms (Netflix, Disney+, etc.)",
        "Theater & Performing Arts",
        "Video Games & eSports",
        "Bollywood & Hollywood",
        "Comics & Animation"
    ]

    # Step 8: Classify Each Cluster and Assign the Closest Label
    final_clusters = {}

    for cluster, concatenated_text in cluster_texts.items():
        result = classifier(concatenated_text, candidate_labels, multi_label=False)  # Single best label
        best_label = result["labels"][0]  # The highest-scoring label
        
        # Store articles under the best matching subtopic
        final_clusters.setdefault(best_label, []).extend(subtopic_clusters[cluster])

    # Step 9: Print Final Clustered Articles
    print("\n### Final Clustered Articles ###\n")
    for subtopic, articles in final_clusters.items():
        print(f"**Subtopic:** {subtopic}")
        print("Articles in this cluster:")
        for article in articles:
            print(f"- {article[:100]}...")  # Print first 100 characters for readability
        print("\n" + "-"*80 + "\n")



# Step 6: Summarize Each Cluster

    # DO AHEAD
    def recursive_summarize(text, min_tokens=MIN_CHUNK_TOKENS, max_tokens=MAX_CHUNK_TOKENS):
        all_tokens = tokenizer.encode(text, add_special_tokens=False)
        total_tokens = len(all_tokens)
        print(f"Total tokens: {total_tokens}")

        if total_tokens <= max_tokens:
            return text
        
        full_chunks = total_tokens // max_tokens
        remainder = total_tokens % max_tokens
        
        if full_chunks >= 1 and remainder < MIN_TOTAL_LAST:
            full_chunks -= 1
            start_last = full_chunks * max_tokens
            last_tokens = all_tokens[start_last:]
        else:
            start_last = full_chunks * max_tokens
            last_tokens = all_tokens[start_last:]

        chunks_tokens = []

        for i in range(full_chunks):
            chunk = all_tokens[i * max_tokens : (i + 1) * max_tokens]
            chunks_tokens.append(chunk)

        last_total = len(last_tokens)
        split_index = last_total // 2

        if split_index < min_tokens or (last_total - split_index) < min_tokens:
            split_index = min_tokens
            if last_total - split_index < min_tokens:
                chunks_tokens.append(last_tokens)
            else:
                chunks_tokens.append(last_tokens[:split_index])
                chunks_tokens.append(last_tokens[split_index:])
        else:
            chunks_tokens.append(last_tokens[:split_index])
            chunks_tokens.append(last_tokens[split_index:])
        
        chunks = [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks_tokens]
        print(f"Number of chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            chunk_len = len(tokenizer.encode(chunk, add_special_tokens=False))
            print(f"Chunk {i+1}: {chunk_len} tokens")

        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            chunk_len = len(tokenizer.encode(chunk, add_special_tokens=False))
            print(f"\nSummarizing chunk {i+1}/{len(chunks)} (token length: {chunk_len})...")
            try:
                summary_chunk = summarizer(
                    chunk,
                    max_length=600,
                    min_length=400,
                    do_sample=False,
                    truncation=True
                )
                chunk_summaries.append(summary_chunk[0]['summary_text'])
            except Exception as e:
                print(f"Error summarizing chunk {i+1}: {e}")
                chunk_summaries.append(chunk)
        
        combined_summary = " ".join(chunk_summaries)
        print("\nCombined Intermediate Summary:")
        print(combined_summary)

        return recursive_summarize(combined_summary, min_tokens, max_tokens)
    

    summarized_clusters = {}

# Iterate over each subtopic and its associated articles
    for subtopic, articles in final_clusters.items():
        print(f"**Processing Subtopic:** {subtopic}")

    # Summarize all articles under this subtopic
        summary = recursive_summarize(" ".join(articles), min_tokens=400, max_tokens=600)

    # Store the summarized result
        summarized_clusters[subtopic] = summary

        print(f"**Summary for {subtopic}:** {summary}\n")
        print("\n" + "-" * 80 + "\n")
    return summarized_clusters

print(super_summary(all_contents))