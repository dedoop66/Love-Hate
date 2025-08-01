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

#CLI BELOW--------------------- (note to self)
def main_cli():
    topic = "Lionel Messi"
    print(f"Fetching news about: {topic}")

    entries = get_news_headlines(topic)
    df = analyze_sentiment(entries)
    plot_sentiment_aggregated_daily(df) #the chart also looked weird because it was showing sentiments for each article so basically we just lump and get the daily net aggregate of sentiment for a celebrity within a given day

#GUI BELOW--------------------- (note to self)

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SentimentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Celebrity News Sentiment Comparison")
        self.geometry("1200x800")

        # super simple input fields for two celebrities
        self.celeb1_var = tk.StringVar()
        self.celeb2_var = tk.StringVar()
        tk.Label(self, text="Celebrity 1:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self, textvariable=self.celeb1_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self, text="Celebrity 2:").grid(row=0, column=2, padx=10, pady=5, sticky="e")
        tk.Entry(self, textvariable=self.celeb2_var, width=30).grid(row=0, column=3, padx=5, pady=5)

        self.go_btn = tk.Button(self, text="Go", command=self.on_go)
        self.go_btn.grid(row=0, column=4, padx=10, pady=5)

        #matplotlib figure same as above, different colors because red green wont work for two variables
        self.figure = plt.Figure(figsize=(11, 3.5))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=5, pady=10)

        #article tables for below (need to align these better)
        self.tree1 = self._create_table(row=2, col=0, title="Celebrity 1 Articles")
        self.tree2 = self._create_table(row=2, col=2, title="Celebrity 2 Articles")

    def _create_table(self, row, col, title):
        frame = tk.Frame(self)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="n")
        tk.Label(frame, text=title).pack()
        tree = ttk.Treeview(frame, columns=("Title", "Score"), show="headings", height=15)
        tree.heading("Title", text="Title")
        tree.heading("Score", text="Score")
        tree.column("Title", width=360)
        tree.column("Score", width=60)
        tree.pack()
        return tree

    def on_go(self):
        threading.Thread(target=self._fetch_and_plot, daemon=True).start()

    def _fetch_and_plot(self):
        celeb1 = self.celeb1_var.get().strip()
        celeb2 = self.celeb2_var.get().strip()

        if not celeb1 or not celeb2:
            messagebox.showerror("Input Error", "Please enter both celebrity names.")
            return

        df1 = analyze_sentiment(get_news_headlines(celeb1))
        df2 = analyze_sentiment(get_news_headlines(celeb2))

        self._update_table(self.tree1, df1)
        self._update_table(self.tree2, df2)
        self._plot_comparison(df1, df2, celeb1, celeb2)

    def _update_table(self, tree, df):
        for row in tree.get_children():
            tree.delete(row)
        for _, row in df.iterrows():
            title = row['Title'][:50] + "..." if len(row['Title']) > 50 else row['Title']
            tree.insert('', 'end', values=(title, f"{row['SentimentScore']:.2f}"))

    def _plot_comparison(self, df1, df2, celeb1, celeb2):
        self.ax.clear()
        #aggregate by day like always
        if not df1.empty:
            agg1 = df1.set_index('Published').resample('D')['SentimentScore'].sum()
            self.ax.plot(agg1.index, agg1.values, label=celeb1, color='blue')
        if not df2.empty:
            agg2 = df2.set_index('Published').resample('D')['SentimentScore'].sum()
            self.ax.plot(agg2.index, agg2.values, label=celeb2, color='orange')
        self.ax.axhline(0, color='black', linestyle='dashed')
        self.ax.set_title("News Sentiment Over Time")
        self.ax.set_ylabel("Net Sentiment")
        self.ax.legend()
        self.figure.autofmt_xdate()
        self.canvas.draw()

if __name__ == "__main__":


    #Gui...
    app = SentimentApp()
    app.mainloop()