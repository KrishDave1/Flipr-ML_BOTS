import scrapy
from newspaper import Article
import json
import os


class MaharashtraNewsSpider(scrapy.Spider):
    name = "maharashtra_news"

    def start_requests(self):
        """Reads URLs from a JSON file and starts crawling."""
        with open("news_articles.json", "r", encoding="utf-8") as f:
            news_data = json.load(f)

        for item in news_data:
            url = item.get("link")
            if url:
                yield scrapy.Request(url, callback=self.parse_article)

    def parse_article(self, response):
        """Extracts article details using Newspaper3k and stores in a JSON file."""
        article = Article(response.url)
        article.download()
        article.parse()

        article_data = {
            "title": article.title,
            "author": ", ".join(article.authors) if article.authors else "Unknown",
            "published_date": (
                article.publish_date.strftime("%Y-%m-%d")
                if article.publish_date
                else "Unknown"
            ),
            "content": article.text,
            "url": response.url,
            "source": response.url.split("/")[2],
        }

        self.store_in_json(article_data)

        yield article_data

    def store_in_json(self, article_data):
        """Stores extracted article data into a JSON file."""
        file_name = "extracted_articles.json"

        # Check if the file already exists and load existing data
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as f:
                try:
                    articles = json.load(f)
                except json.JSONDecodeError:
                    articles = []  # If file is empty or invalid, start fresh
        else:
            articles = []

        # Append new article
        articles.append(article_data)

        # Write back to the file
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=4, ensure_ascii=False)

        print(f"Saved article: {article_data['title']}")
