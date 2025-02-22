import requests
import json
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from newspaper import Article
from time import sleep

# ---------------- Configuration ---------------- #
API_KEY = "AIzaSyDFzbABQ8bIk5d2Zm-EUES598IsWyGvL7M"
SEARCH_ENGINE_ID = "629612033c73b4741"
MIN_ARTICLES = 50
MIN_WORD_COUNT = 300
MAX_WORD_COUNT = 800

# List of search queries to diversify candidate articles.
SEARCH_QUERIES = [
    "London news",
    "London headlines",
    "London current affairs",
    "London latest updates",
]


# ---------------- Helper Functions ---------------- #
def fetch_news_articles(query, total_results=50):
    """
    Fetch candidate news articles from Google Custom Search API.
    Restricts results to trusted sources.
    """
    all_articles = []
    results_per_page = 10
    start = 1  # Start index must be <= 91

    # Force search to trusted sources.
    search_query = f"{query} site:bbc.com OR site:theguardian.com OR site:espn.com OR site:reuters.com"

    while len(all_articles) < total_results and start <= 91:
        url = (
            f"https://www.googleapis.com/customsearch/v1?q={search_query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}"
            f"&num={results_per_page}&start={start}&lr=lang_en&gl=GB"
        )
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            if not items:
                break

            for item in items:
                article_link = item.get("link")
                if is_valid_source(article_link) and is_url_accessible(article_link):
                    all_articles.append(
                        {
                            "title": item.get("title"),
                            "link": article_link,
                            "snippet": item.get("snippet"),
                        }
                    )
                if len(all_articles) >= total_results:
                    break

            start += results_per_page
            sleep(1)  # Respect API rate limits
        except requests.exceptions.RequestException as e:
            print(f"Error fetching articles: {e}")
            break

    return all_articles


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
    trusted_sources = ["bbc.com", "theguardian.com", "espn.com", "reuters.com"]
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
        "DOWNLOAD_TIMEOUT": 2,
        "CONCURRENT_REQUESTS": 5,
        "RETRY_TIMES": 3,
        "LOG_LEVEL": "INFO",
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
    # Step 1: Aggregate candidate article URLs using multiple queries.
    candidate_articles = aggregate_candidate_articles(SEARCH_QUERIES, per_query=50)
    save_to_json(candidate_articles, "news_articles.json")

    # Step 2: Run the Scrapy spider to extract full article content.
    process = CrawlerProcess()
    process.crawl(NewsSpider)
    process.start(stop_after_crawl=False)

    # Step 3: Check if we have enough valid articles; if not, use a fallback query.
    fallback_query = "London in-depth analysis"
    while count_extracted_articles() < MIN_ARTICLES:
        print(
            f"Extracted articles ({count_extracted_articles()}) are less than required ({MIN_ARTICLES})."
        )
        print(f"Fetching additional candidates using fallback query: {fallback_query}")
        extra_candidates = fetch_news_articles(fallback_query, total_results=50)
        # Combine with the existing candidate articles and deduplicate.
        existing_candidates = load_json("news_articles.json")
        combined_candidates = {
            article["link"]: article
            for article in (existing_candidates + extra_candidates)
        }.values()
        combined_candidates = list(combined_candidates)
        save_to_json(combined_candidates, "news_articles.json")

        # Run the spider again on the updated candidate list.
        process = CrawlerProcess()
        process.crawl(NewsSpider)
        process.start(stop_after_crawl=False)

    print(f"Final extracted articles count: {count_extracted_articles()}")