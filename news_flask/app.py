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

# Summarizer ends

# NER starts

# Load the pre-trained English NER model
nlp = spacy.load("en_core_web_trf")

# NER ends

app = Flask(__name__)

# Neo4j Database Connection
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "valmik_neo4j"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Summarizer helper function

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

# NER helper function
def do_ner_and_extract_keywords(text:str) -> list:
    doc = nlp(text)
    keywords =  []
    for ent in doc.ents:
        print(f"{ent.text} -> {ent.label_} ({spacy.explain(ent.label_)})")
        keywords.append(ent.text)
    return keywords


# ---------------- Configuration ---------------- #
NEWSAPI_KEY = "5829d16a66d743379a9c80bfc2241c66"  # Replace with your NewsAPI key
MIN_ARTICLES = 50
MIN_WORD_COUNT = 300
MAX_WORD_COUNT = 800

# List of search queries to diversify candidate articles.
SEARCH_QUERIES = [
    "London economy",
    "London politics",
    "London crime news",
    "London technology",
    "London housing crisis",
]
# Fallback query to help gather more candidates
FALLBACK_QUERY = "London in-depth analysis"


# ---------------- Helper Functions ---------------- #
def fetch_news_articles(query, total_results=10):
    """
    Fetch candidate news articles from NewsAPI.
    Restricts results to trusted sources.
    """
    # Trusted sources as defined by NewsAPI (source IDs):
    # - BBC: bbc-news
    # - The Guardian: the-guardian-uk
    # - Reuters: reuters
    url = (
        f"https://newsapi.org/v2/everything?q={query}"
        # f"&sources=bbc-news,the-guardian-uk,reuters"
        f"&apiKey={NEWSAPI_KEY}&pageSize={total_results}&page=1"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
    except Exception as e:
        print(f"Error fetching articles from NewsAPI for query '{query}': {e}")
        articles = []

    print(f"Fetched {len(articles)} articles from NewsAPI for query '{query}'")

    candidate_articles = []
    for article in articles:
        link = article.get("url")
        # if link and is_valid_source(link) and is_url_accessible(link):
        if link:
            candidate_articles.append(
                {
                    "title": article.get("title"),
                    "link": link,
                    "snippet": article.get("description") or "",
                }
            )
    return candidate_articles


def aggregate_candidate_articles(queries, per_query=10):
    """Aggregate candidate articles from multiple search queries and deduplicate by URL."""
    all_candidates = []
    for query in queries:
        print(f"Fetching articles for query: {query}")
        candidates = fetch_news_articles(query, total_results=per_query)
        all_candidates.extend(candidates)
    # Remove duplicates based on URL.
    unique_candidates = {
        article["link"]: article for article in all_candidates
    }.values()
    return list(unique_candidates)


def is_valid_source(url):
    """Check if the URL belongs to one of the trusted news sources."""
    # Check for domain indicators.
    trusted_sources = [
        "bbc.com",
        "theguardian.com",
        "reuters.com",
        "bbc-news",
        "the-guardian-uk",
    ]
    return any(source in url for source in trusted_sources)


def is_url_accessible(url):
    """Check if a URL is accessible."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def save_to_json(data, filename):
    """Save data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    print(f"Saved {len(data)} items to {filename}")


def load_json(filename):
    """Load JSON data from a file."""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def count_extracted_articles():
    """Return the count of successfully extracted articles."""
    articles = load_json("extracted_articles.json")
    return len(articles)


# ---------------- Scrapy Spider ---------------- #
class NewsSpider(scrapy.Spider):
    name = "news_spider"
    custom_settings = {
        "DOWNLOAD_TIMEOUT": 10,
        "CONCURRENT_REQUESTS": 5,
        "RETRY_TIMES": 3,
        "LOG_LEVEL": "INFO",
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    def start_requests(self):
        json_file = "news_articles.json"
        if not os.path.exists(json_file):
            self.logger.error(f"Error: {json_file} not found.")
            return

        news_data = load_json(json_file)

        request_count = 0  # Debugging count
        for item in news_data:
            url = item.get("link")
            if url and is_url_accessible(url):
                yield scrapy.Request(
                    url, callback=self.parse_article, errback=self.handle_failure
                )

        self.logger.info(f"Total requests sent: {request_count}")

    def parse_article(self, response):
        try:
            article = Article(response.url)
            article.download()
            article.parse()

            word_count = len(article.text.split())
            if word_count < MIN_WORD_COUNT or word_count > MAX_WORD_COUNT:
                self.logger.info(
                    f"Skipping {response.url} due to word count: {word_count}"
                )
                return

            article_data = {
                "title": article.title or "No Title",
                "author": ", ".join(article.authors) if article.authors else "Unknown",
                "published_date": (
                    article.publish_date.strftime("%Y-%m-%d")
                    if article.publish_date
                    else "Unknown"
                ),
                "content": article.text.strip(),
                "word_count": word_count,
                "url": response.url,
            }

            self.store_in_json(article_data)
            yield article_data
        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {e}")

    def handle_failure(self, failure):
        self.logger.error(f"Failed to scrape: {failure.request.url}")

    def store_in_json(self, article_data):
        file_name = "extracted_articles.json"
        articles = load_json(file_name)
        articles.append(article_data)
        save_to_json(articles, file_name)

# Scraping helper function

def scraper(search_query: list):
    # Aggregate candidate article URLs using both main and fallback queries.
    all_queries = search_query
    candidate_articles = aggregate_candidate_articles(all_queries, per_query=50)
    save_to_json(candidate_articles, "news_articles.json")

    # Configure logging to prevent duplicate logs
    configure_logging()
    
    # Use CrawlerRunner instead of CrawlerProcess
    runner = CrawlerRunner()

    @defer.inlineCallbacks
    def crawl():
        yield runner.crawl(NewsSpider)
        print(f"Final extracted articles count: {count_extracted_articles()}")
        reactor.stop()
    
    # Ensure we don't restart the reactor
    if reactor.running:
        return runner.join().addCallback(lambda _: candidate_articles)
    else:
        crawl()
        reactor.run()
    
    return load_json("extracted_articles.json")

# Get related articles => helper function
def get_related_articles_content(start_id):
        """
        Retrieves the content of up to 10 articles related to the given article ID.
        
        :param start_id: The ID of the starting article.
        :return: A list of article content.
        """
        query = """
        MATCH (start:Article) WHERE id(start) = $start_id
        CALL apoc.path.expandConfig(start, {
            relationshipFilter: 'IS_RELATED_TO',
            minLevel: 1,
            maxLevel: 3,
            uniqueness: 'NODE_GLOBAL'
        }) 
        YIELD path
        WITH nodes(path) AS articles
        UNWIND articles AS article
        RETURN article.content AS content
        LIMIT 10;
        """
        with driver.session() as session:
            result = session.run(query, start_id=start_id)
            return [record["content"] for record in result]
    
# Get random article => helper function
    
def get_random_article():
    cypher_query = """
    MATCH (a:Article) 
    WITH a, rand() AS random 
    ORDER BY random 
    LIMIT 1 
    RETURN id(a) as article_id, a.domain AS domain;
    """
    with driver.session() as session:
        result = session.run(cypher_query)
        return (result.single["article_id"], result.single["domain"]) if result else None
    
# Graph updation
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def create_relationships_by_keywords(article_id):
    print("In the create relationships by keywords function.")
    
    query = """
    MATCH (source:Article {id: $article_id})
    MATCH (target:Article)
    WHERE target.id <> $article_id AND source.keywords IS NOT NULL AND target.keywords IS NOT NULL

    // Compute cosine similarity manually
    WITH source, target, 
        gds.similarity.cosine(source.keywords, target.keywords) AS similarity
    WHERE similarity > -1  // Use a meaningful threshold

    // Create a relationship with similarity score
    MERGE (source)-[:IS_RELATED_TO {similarity: similarity}]->(target);
    """
    
    with driver.session() as session:
        session.run(query, article_id=article_id)

def save_article(keywords, content, domain):
    """Saves an Article instance into Neo4j with an auto-generated ID and returns the ID."""
    query = """
    CREATE (a:Article {
        keywords: $keywords,
        content: $content,
        domain: $domain
    })
    RETURN elementId(a) AS id;
    """
    with driver.session() as session:
        result = session.run(query, keywords=keywords, content=content, domain=domain)
        record = result.single()
        return record["id"] if record else None

topic_dict = {
    0: "business",
    1: "sports",
    2: "technology",
    3: "politics",
    4: "entertainment",
    5: "economy",
    6: "healthcare",
    7: "crime",
    8: "education",
    9: "environment",
    10: "science"
}

@app.route("/")
def home():
    return "<h1>HELLO</h1>"

@app.route("/cronjob", methods=['GET'])
def cronJob():
    print("Entered cron job.")
    topic_num:int = random.randrange(5)
    hardcoded_query = "London " + topic_dict[topic_num] + " news" 
    articles = scraper([hardcoded_query])
    print("Done with scraping.")
    print(f"ARTICLES {len(articles)}")
    count = 0
    for article in articles:
        count += 1
        print(f"COUNT = {count}")
        # keywords = do_ner_and_extract_keywords(article.get("content"))
        para_embedding = model_sentence_transformer.encode(article.get("content"))
        saved_article_id = save_article(keywords=para_embedding, content=article.get("content"), domain=topic_dict[topic_num])
        create_relationships_by_keywords(article_id=saved_article_id)
    return jsonify({
        "message": "HELLO FROM FLASK."
    })

@app.route("/generate-summary", methods=['GET'])
def generate_summary():
    random_article_id, random_article_domain = get_random_article()
    neighbour_contents = get_related_articles_content(start_id=random_article_id)
    articles=neighbour_contents
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
    return (summarized_clusters, random_article_domain)

      
# Step 6: Generate Summaries

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)