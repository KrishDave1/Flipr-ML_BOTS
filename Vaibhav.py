import requests

API_KEY = "bc2a5562f82b45bd80f7fb88c0644020"
NEWS_API_URL = "https://newsapi.org/v2/everything"  # Use 'everything' instead of 'top-headlines'

def fetch_news(query="girls", language="en"):
    params = {
        "q": query,
        "language": language,
        "apiKey": API_KEY,
        "sortBy": "publishedAt",  # Get recent news first
        "pageSize": 45,  # Limit to 5 articles
    }
    response = requests.get(NEWS_API_URL, params=params)
    
    if response.status_code != 200:
        print("Error:", response.json())
        return []
    
    return response.json().get("articles", [])

news_data = fetch_news("girls", "en")
for article in news_data:
    print(article["title"], "-", article["url"])
