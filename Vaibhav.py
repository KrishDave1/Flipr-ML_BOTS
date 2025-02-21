from transformers import pipeline


news_articles = [
    {
        "title": "Government Unveils New Economic Policy to Boost Growth",
        "content": """The government has introduced a comprehensive economic reform package aimed at boosting growth and creating jobs. 
        The new policy focuses on increasing foreign investment, reducing corporate taxes, and simplifying regulations for small businesses. 
        Experts believe that this move will help strengthen the economy by attracting international investors. 
        However, some critics argue that the policy does not address the growing income inequality in the country."""
    },
    {
        "title": "AI Technology to Revolutionize Healthcare Sector",
        "content": """The healthcare industry is on the verge of a major transformation with the introduction of artificial intelligence (AI). 
        AI-driven diagnostics are improving the speed and accuracy of disease detection, allowing doctors to provide better treatment options. 
        Hospitals are also using AI-powered robots for administrative tasks, freeing up time for medical professionals. 
        While the advancements are promising, concerns about data privacy and ethical implications remain a major challenge for the industry."""
    },
    {
        "title": "Stock Market Sees Historic Surge Amid Economic Optimism",
        "content": """The stock market experienced a record-breaking surge today, with major indices reaching all-time highs. 
        Investors reacted positively to recent government policies and strong corporate earnings reports. 
        The technology sector, in particular, saw massive gains, with major companies reporting higher-than-expected revenues. 
        Financial analysts predict continued growth if economic conditions remain stable, but warn of potential risks from global inflation concerns."""
    },
    {
        "title": "Scientists Discover New Exoplanet Capable of Supporting Life",
        "content": """Astronomers have identified a new exoplanet located in the habitable zone of a distant star. 
        The planet, named Kepler-1649c, is similar in size to Earth and has conditions that could potentially support life. 
        Scientists are now analyzing its atmospheric composition to determine whether it has water and other essential elements. 
        This discovery raises hopes for the existence of extraterrestrial life and future space exploration possibilities."""
    },
    {
        "title": "Olympics 2024: Historic Wins and Surprising Upsets",
        "content": """The ongoing Olympics have been full of excitement, with athletes from around the world setting new records. 
        This year, the competition has seen unexpected victories, with underdog athletes defeating top-ranked contenders. 
        In the swimming category, a young competitor from Japan stunned the audience with a record-breaking performance. 
        Meanwhile, in gymnastics, the reigning champion faced a shocking defeat. 
        Fans are eagerly waiting to see how the final events unfold in the coming days."""
    }
]


# Load zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Example news article
title = "Government Announces New Policies for Economic Growth"
content = "The government has introduced a new set of economic policies aimed at boosting GDP growth and reducing inflation."
text = f"{title}: {content}"

candidate_labels = [
    "Politics", "Government", "Elections", "Foreign Policy", "Legislation",
    "Economy", "Stock Market", "Business", "Inflation", "Trade", 
    "Technology", "AI", "Cybersecurity", "Gadgets", "Space",
    "Sports", "Football", "Cricket", "Olympics", "Tennis",
    "Health", "Medicine", "Pandemic", "Mental Health", "Nutrition",
    "Education", "Schools", "Universities", "Scholarships", "Research",
    "Crime", "Law Enforcement", "Court Cases", "Scams", "Violence"
]

# Classify the news article
for article in news_articles:
    text = f"{article['title']}: {article['content']}"
    result = classifier(text, candidate_labels, multi_label=True)

    print(f"\n**Title:** {article['title']}")
    print("Predicted Categories:")
    for label, score in zip(result["labels"], result["scores"]):
        print(f"  - {label}: {score:.4f}")