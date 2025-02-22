import requests
import json
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from newspaper import Article
from time import sleep

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


# ---------------- Main Script Execution ---------------- #
if __name__ == "__main__":
    # Aggregate candidate article URLs using both main and fallback queries.
    all_queries = SEARCH_QUERIES + [FALLBACK_QUERY]
    candidate_articles = aggregate_candidate_articles(all_queries, per_query=50)
    save_to_json(candidate_articles, "news_articles.json")

    # Run the Scrapy spider to extract full article content (all crawls in one reactor run)
    process = CrawlerProcess()
    process.crawl(NewsSpider)
    process.start()

    print(f"Final extracted articles count: {count_extracted_articles()}")
