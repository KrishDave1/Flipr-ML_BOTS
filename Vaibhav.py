import requests
from bs4 import BeautifulSoup

def fetch_google_news(query="technology"):
    url = f"https://news.google.com/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    headers = {"User-Agent": "Mozilla/5.0"}  # Prevent blocking

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Error:", response.status_code)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article")[0:1]  # Get top 5 news articles

    news_list = []
    for article in articles:
        title_tag = article.find("a")
        if title_tag:
            title = title_tag.text.strip()
            link = "https://news.google.com" + title_tag["href"][1:]
            news_list.append({"title": title, "url": link})

    return news_list

news_data = fetch_google_news("politics")

for news in news_data:
    print(news)
