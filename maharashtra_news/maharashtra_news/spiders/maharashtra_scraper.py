import requests
import json
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from newspaper import Article
from time import sleep

API_KEY = "AIzaSyDFzbABQ8bIk5d2Zm-EUES598IsWyGvL7M"
SEARCH_ENGINE_ID = "629612033c73b4741"
MIN_ARTICLES = 50  # Ensure at least 50 articles
MIN_WORD_COUNT = 300  # Minimum words required in an article
MAX_WORD_COUNT = 800  # Maximum words allowed


def fetch_news_articles(query, total_results=50):
    """Fetch high-quality news articles from Google Custom Search API."""
    all_articles = []
    results_per_page = 10  # Max per request
    page_number = 1

    # 🔹 **Optimize query for better results**
    search_query = (
        f"{query} inurl:news OR site:bbc.com OR site:theguardian.com OR site:espn.com"
        f" OR site:reuters.com OR site:independent.co.uk OR site:skysports.com"
    )

    while len(all_articles) < total_results:
        url = (
            f"https://www.googleapis.com/customsearch/v1?"
            f"q={search_query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}"
            f"&num={results_per_page}&start={page_number}"
            f"&lr=lang_en&gl=GB"  # 🔹 Prioritize English & UK sources
            f"&sort=date"  # 🔹 Sort by newest
        )

        response = requests.get(url)

        if response.status_code != 200:
            print(f"❌ Error fetching articles: {response.status_code}")
            break

        data = response.json()
        items = data.get("items", [])

        if not items:
            print("⚠️ No more articles found.")
            break

        for item in items:
            article_link = item.get("link")

            # 🔹 **Check if link is accessible and not spam**
            if is_url_accessible(article_link) and is_valid_source(article_link):
                all_articles.append(
                    {
                        "title": item.get("title"),
                        "link": article_link,
                        "snippet": item.get("snippet"),
                    }
                )
                if len(all_articles) >= total_results:
                    break  # Stop when we reach required count

        page_number += results_per_page

    return all_articles

def is_valid_source(url):
    """Checks if the URL belongs to a known good news source."""
    trusted_sources = [
        "bbc.com",
        "theguardian.com",
        "espn.com",
        "reuters.com",
        "independent.co.uk",
        "skysports.com",
        "aljazeera.com",
    ]

    for source in trusted_sources:
        if source in url:
            return True
    return False


def is_url_accessible(url):
    """Checks if a URL is accessible (HTTP 200)."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def save_to_json(data, filename):
    """Saves data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    print(f"Saved {len(data)} articles to {filename}")


class LondonNewsSpider(scrapy.Spider):
    name = "london_news"

    custom_settings = {
        "DOWNLOAD_TIMEOUT": 10,
        "CONCURRENT_REQUESTS": 5,
        "RETRY_TIMES": 3,
        "LOG_LEVEL": "INFO",
    }

    def start_requests(self):
        """Reads URLs from the JSON file and starts scraping."""
        json_file = "news_articles.json"
        if not os.path.exists(json_file):
            print(f"Error: {json_file} not found.")
            return

        with open(json_file, "r", encoding="utf-8") as f:
            news_data = json.load(f)

        for item in news_data:
            url = item.get("link")
            if url and is_url_accessible(url):  # Verify link
                yield scrapy.Request(
                    url, callback=self.parse_article, errback=self.handle_failure
                )

    def parse_article(self, response):
        """Extracts article details using Newspaper3k, ensuring proper length."""
        try:
            article = Article(response.url)
            article.download()
            article.parse()

            word_count = len(article.text.split())

            # 🔹 **Filter out too short or too long articles**
            if word_count < MIN_WORD_COUNT or word_count > MAX_WORD_COUNT:
                print(f"Skipping article (word count {word_count}): {response.url}")
                return

            article_data = {
                "title": article.title if article.title else "No Title",
                "author": ", ".join(article.authors) if article.authors else "Unknown",
                "published_date": (
                    article.publish_date.strftime("%Y-%m-%d")
                    if article.publish_date
                    else "Unknown"
                ),
                "content": article.text.strip(),
                "word_count": word_count,
                "url": response.url,
                "source": response.url.split("/")[2],
            }

            self.store_in_json(article_data)
            yield article_data

        except Exception as e:
            print(f"Error processing {response.url}: {e}")

    def handle_failure(self, failure):
        """Handles failed requests and logs errors."""
        url = failure.request.url
        print(f"Failed to scrape: {url}")

    def store_in_json(self, article_data):
        """Appends extracted article data into a JSON file."""
        file_name = "extracted_articles.json"

        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as f:
                try:
                    articles = json.load(f)
                except json.JSONDecodeError:
                    articles = []  # Reset if JSON is corrupt
        else:
            articles = []

        articles.append(article_data)

        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=4, ensure_ascii=False)

        print(
            f"Saved article ({article_data['word_count']} words): {article_data['title']}"
        )


def ensure_minimum_articles(process):
    """Ensures that at least 50 articles are present in extracted_articles.json."""
    file_name = "extracted_articles.json"

    # Load current articles
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            try:
                articles = json.load(f)
            except json.JSONDecodeError:
                articles = []
    else:
        articles = []

    # If less than MIN_ARTICLES, fetch more
    if len(articles) < MIN_ARTICLES:
        print(f"Only {len(articles)} articles found. Fetching more...")
        remaining = MIN_ARTICLES - len(articles)
        extra_articles = fetch_news_articles(
            "London news", total_results=remaining
        )
        save_to_json(extra_articles, "news_articles.json")

        # Run Scrapy again for extra links
        process.crawl(LondonNewsSpider)  # No `.start()`, reuse process


if __name__ == "__main__":
    # Step 1: Fetch at least 50 article URLs
    news_articles = fetch_news_articles("London news", total_results=50)
    save_to_json(news_articles, "news_articles.json")

    # Step 2: Create a single CrawlerProcess instance
    process = CrawlerProcess()
    process.crawl(LondonNewsSpider)

    # Step 3: Run Scrapy and ensure minimum articles
    ensure_minimum_articles(process)  # Ensures at least 50 articles
    process.start(stop_after_crawl=False)  # Ensures reactor runs only once
