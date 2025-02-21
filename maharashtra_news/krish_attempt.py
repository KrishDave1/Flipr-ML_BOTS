import requests
import json

API_KEY = "AIzaSyDFzbABQ8bIk5d2Zm-EUES598IsWyGvL7M"
SEARCH_ENGINE_ID = "629612033c73b4741"


def fetch_news_articles(query, total_results=50):
    all_articles = []
    results_per_page = 10  # Google API allows max 10 per request

    for start in range(1, total_results, results_per_page):
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}&num={results_per_page}&start={start}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break

        data = response.json()
        items = data.get("items", [])

        if not items:
            break  # No more results

        for item in items:
            all_articles.append(
                {
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                }
            )

    return all_articles


news_articles = fetch_news_articles("Maharashtra Sports news", total_results=50)

# Save to JSON file
file_name = "news_articles.json"
with open(file_name, "w", encoding="utf-8") as json_file:
    json.dump(news_articles, json_file, indent=4, ensure_ascii=False)

print(f"Saved {len(news_articles)} articles to {file_name}")
