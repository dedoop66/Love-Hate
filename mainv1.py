import feedparser
import urllib.parse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def get_news_headlines(query):
    safe_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={safe_query}"
    feed = feedparser.parse(url)
    return [entry.title for entry in feed.entries]

def analyze_sentiment(headlines):
    analyzer = SentimentIntensityAnalyzer()
    results = []
    for title in headlines:
        score = analyzer.polarity_scores(title)
        results.append((title, score['compound']))
    return results

if __name__ == "__main__":
    topic = "Lionel Messi"
    print(f"Fetching news about: {topic}")
    headlines = get_news_headlines(topic)
    analyzed = analyze_sentiment(headlines)
    
    for title, score in analyzed:
        sentiment = "Positive :-)" if score > 0.05 else "Negative :-(" if score < -0.05 else "Neutral :-|"
        print(f"- {title} ({sentiment}, {score})")

        #
