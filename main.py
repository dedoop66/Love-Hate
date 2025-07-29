import requests
import feedparser
import urllib.parse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import matplotlib.pyplot as plt #added in matplot for the chart, I have had to use this before in python to create charts/viz in my work
import numpy as np

def get_news_headlines(query):
    safe_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={safe_query}"
    print("RSS feed URL:", url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    } #this took me an insane amount of time to figure out, I can attach some pictures as well to show, I needed to use AI to solve, my dataframe kept on returning empty because the RSS was 
    #basically blocking my from accessing since I was attempting to pull from a programatic environment without permissions? I discuss this more in notes
    resp = requests.get(url, headers=headers)
    print("HTTP status:", resp.status_code)
    feed = feedparser.parse(resp.text)
    print(f"Number of articles in feed: {len(feed.entries)}")

    #filter entries with a valid published_parsed date
    entries = [e for e in feed.entries if hasattr(e, 'published_parsed') and e.published_parsed]
    print("Number of entries with published_parsed:", len(entries))
    entries = sorted(entries, key=lambda x: x.published_parsed, reverse=True) #Like you mentioned in the feedback I needed to return the date results chronologically for a line chart so...
    for entry in entries:
        print(entry.published, entry.title)
    return entries

def analyze_sentiment(entries):
    analyzer = SentimentIntensityAnalyzer()
    data = []

    for entry in entries:
        title = entry.title
        score = analyzer.polarity_scores(title)['compound']
        published = getattr(entry, 'published', None)
        data.append([published, title, score]) #trashed the sentiment and score since they were redundant like you mentioned score = sentiment 

    df = pd.DataFrame(data, columns=['Published', 'Title', 'SentimentScore'])
    df['Published'] = pd.to_datetime(df['Published'], errors='coerce')
    df = df.dropna(subset=['Published'])
    df = df.sort_values('Published')
    print(df)
    print("Number of rows in DataFrame:", len(df))
    return df

def plot_sentiment_aggregated_daily(df):
    #set Published as index, resample daily (sum sentiment)
    df = df.set_index('Published').sort_index()
    sentiment_agg = df['SentimentScore'].resample('D').sum()

    if len(sentiment_agg) < 2:
        print("Not enough data for line plot.")
        return

    plt.figure(figsize=(12, 6))
    x = sentiment_agg.index
    y = sentiment_agg.values

    for i in range(1, len(y)):
        x0, x1 = x[i-1], x[i]
        y0, y1 = y[i-1], y[i]
            #adding color to the charts

        if (y0 >= 0 and y1 >= 0):
            plt.plot([x0, x1], [y0, y1], color='green', linewidth=2)
        elif (y0 < 0 and y1 < 0):
            plt.plot([x0, x1], [y0, y1], color='red', linewidth=2)
        else:
            #crosses zero 
            if y1 - y0 != 0:
                x_cross = x0 + (x1 - x0) * (0 - y0) / (y1 - y0)
                plt.plot([x0, x_cross], [y0, 0], color='red' if y0 < 0 else 'green', linewidth=2)
                plt.plot([x_cross, x1], [0, y1], color='green' if y1 > 0 else 'red', linewidth=2)
            else:
                #shouldnt happen, but just in case
                plt.plot([x0, x1], [y0, y1], color='gray', linewidth=2)

    plt.axhline(0, color='black', linewidth=1, linestyle='dashed')
    plt.xlabel("Date")
    plt.ylabel("Net Sentiment (sum per day)")
    plt.title("Daily Aggregated News Sentiment")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    topic = "Lionel Messi"
    print(f"Fetching news about: {topic}")

    entries = get_news_headlines(topic)
    df = analyze_sentiment(entries)
    plot_sentiment_aggregated_daily(df) #the chart also looked weird because it was showing sentiments for each article so basically we just lump and get the daily net aggregate of sentiment for a celebrity within a given day