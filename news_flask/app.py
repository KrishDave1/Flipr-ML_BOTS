import requests
import json
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from newspaper import Article
from time import sleep
import spacy
from flask import Flask, request, jsonify
from transformers import pipeline, AutoTokenizer, AutoModel
from neo4j import GraphDatabase
from scipy.spatial.distance import cosine
import numpy as np
import random
# Summarizer starts

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
        keywords.append(ent.label_)
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
def fetch_news_articles(query, total_results=50):
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


def aggregate_candidate_articles(queries, per_query=50):
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

        for item in news_data:
            url = item.get("link")
            if url and is_url_accessible(url):
                yield scrapy.Request(
                    url, callback=self.parse_article, errback=self.handle_failure
                )

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

def scraper(search_query:list):
    # Aggregate candidate article URLs using both main and fallback queries.
    all_queries = search_query
    candidate_articles = aggregate_candidate_articles(all_queries, per_query=50)
    save_to_json(candidate_articles, "news_articles.json")

    # Run the Scrapy spider to extract full article content (all crawls in one reactor run)
    process = CrawlerProcess()
    process.crawl(NewsSpider)
    process.start()

    print(f"Final extracted articles count: {count_extracted_articles()}")

    return candidate_articles

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
    RETURN id(a) as article_id;
    """
    with driver.session() as session:
        result = session.run(cypher_query)
        return result.single["article_id"] if result else None
    
# Graph updation helper function
def create_relationships_by_keywords(article_id, keywords_list):
    """ Creates IS_RELATED_TO relationships between the given article_id and articles with matching keywords """
    query = """
    MATCH (source:Article) WHERE source.id = $article_id
    MATCH (target:Article)
    WHERE ANY(keyword IN target.keywords WHERE keyword IN $keywords_list) AND target.id <> $article_id
    MERGE (source)-[:IS_RELATED_TO]->(target);
    MERGE (target)-[:IS_RELATED_TO]->(source);
    """
    with driver.session() as session:
        session.run(query, article_id=article_id, keywords_list=keywords_list)

def save_article(keywords, content, domain):
    """Saves an Article instance into Neo4j with an auto-generated ID and returns the ID."""
    query = """
    CREATE (a:Article {
        title: $title,
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
    4: "entertainment"
}

@app.route("/cronjob", methods=['GET'])
def cronJob():
    topic_num:int = random.randrange(5)
    hardcoded_query = "London " + topic_dict[topic_num] + " news" 
    articles = scraper([hardcoded_query])
    for article in articles:
        keywords = do_ner_and_extract_keywords(article["content"])
        saved_article_id = save_article(keywords=keywords, content=article["content"], domain=topic_dict[topic_num])
        create_relationships_by_keywords(article_id=saved_article_id, keywords_list=keywords)

@app.route("/generate-summary", methods=['GET'])
def generate_summary():
    random_article_id = get_random_article()
    neighbour_contents = get_related_articles_content(start_id=random_article_id)
    # DO AHEAD

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)