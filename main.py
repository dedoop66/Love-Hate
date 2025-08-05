import requests
import feedparser
import urllib.parse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def get_news_headlines(query):
    """
    Fetches news article headlines from Google News RSS for a given query.

    Args:
        query (str): Search term to look up in Google News.

    Returns:
        list: List of feedparser entry objects, filtered to those with valid published dates, sorted chronologically.
    """
    safe_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={safe_query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    resp = requests.get(url, headers=headers)
    feed = feedparser.parse(resp.text)
    entries = [e for e in feed.entries if hasattr(e, 'published_parsed') and e.published_parsed]
    entries = sorted(entries, key=lambda x: x.published_parsed, reverse=True)
    return entries

def analyze_sentiment(entries):
    """
    Applies VADER sentiment analysis to a list of feedparser entries.

    Args:
        entries (list): List of feedparser entries (from get_news_headlines).

    Returns:
        pd.DataFrame: DataFrame with columns Published, Title, SentimentScore, sorted by Published date.
    """
    analyzer = SentimentIntensityAnalyzer()
    data = []
    for entry in entries:
        title = entry.title
        score = analyzer.polarity_scores(title)['compound']
        published = getattr(entry, 'published', None)
        data.append([published, title, score])

    df = pd.DataFrame(data, columns=['Published', 'Title', 'SentimentScore'])
    df['Published'] = pd.to_datetime(df['Published'], errors='coerce')
    df = df.dropna(subset=['Published'])
    df = df.sort_values('Published')
    return df

def plot_sentiment_aggregated_daily(df):
    """
    Plots daily net sentiment (sum of scores per day) as a colored line (green above zero, red below).

    Args:
        df (pd.DataFrame): DataFrame from analyze_sentiment, with 'Published' and 'SentimentScore' columns.

    Returns:
        None
    """
    df = df.set_index('Published').sort_index()
    sentiment_agg = df['SentimentScore'].resample('D').sum()

    if len(sentiment_agg) < 2:
        return

    plt.figure(figsize=(12, 6))
    x = sentiment_agg.index
    y = sentiment_agg.values

    for i in range(1, len(y)):
        x0, x1 = x[i-1], x[i]
        y0, y1 = y[i-1], y[i]
        if (y0 >= 0 and y1 >= 0):
            plt.plot([x0, x1], [y0, y1], color='green', linewidth=2)
        elif (y0 < 0 and y1 < 0):
            plt.plot([x0, x1], [y0, y1], color='red', linewidth=2)
        else:
            if y1 - y0 != 0:
                x_cross = x0 + (x1 - x0) * (0 - y0) / (y1 - y0)
                plt.plot([x0, x_cross], [y0, 0], color='red' if y0 < 0 else 'green', linewidth=2)
                plt.plot([x_cross, x1], [0, y1], color='green' if y1 > 0 else 'red', linewidth=2)
            else:
                plt.plot([x0, x1], [y0, y1], color='gray', linewidth=2)

    plt.axhline(0, color='black', linewidth=1, linestyle='dashed')
    plt.xlabel("Date")
    plt.ylabel("Net Sentiment (sum per day)")
    plt.title("Daily Aggregated News Sentiment")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def main_cli():
    """
    Command-line interface for single celebrity (for testing/legacy use).
    """
    topic = "Lionel Messi"
    entries = get_news_headlines(topic)
    df = analyze_sentiment(entries)
    plot_sentiment_aggregated_daily(df)

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SentimentApp(tk.Tk):
    """
    Tkinter GUI for comparing net news sentiment for two celebrities or search terms.
    """
    def __init__(self):
        super().__init__()
        self.title("Celebrity News Sentiment Comparison")
        self.geometry("1200x800")

        self.celeb1_var = tk.StringVar()
        self.celeb2_var = tk.StringVar()
        tk.Label(self, text="Celebrity 1:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self, textvariable=self.celeb1_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self, text="Celebrity 2:").grid(row=0, column=2, padx=10, pady=5, sticky="e")
        tk.Entry(self, textvariable=self.celeb2_var, width=30).grid(row=0, column=3, padx=5, pady=5)
        self.go_btn = tk.Button(self, text="Go", command=self.on_go)
        self.go_btn.grid(row=0, column=4, padx=10, pady=5)

        self.figure = plt.Figure(figsize=(11, 3.5))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=5, pady=10)

        self.tree1 = self._create_table(row=2, col=0, title="Celebrity 1 Articles")
        self.tree2 = self._create_table(row=2, col=2, title="Celebrity 2 Articles")

    def _create_table(self, row, col, title):
        """
        Helper to make a table (Treeview) for displaying article titles/scores.

        Args:
            row (int): Row to grid table at.
            col (int): Column to grid table at.
            title (str): Table heading label.

        Returns:
            ttk.Treeview: Table widget.
        """
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
        """
        Launch threaded data fetch and plotting for both celebrities.
        """
        threading.Thread(target=self._fetch_and_plot, daemon=True).start()

    def _fetch_and_plot(self):
        """
        Fetches articles, scores sentiment, updates tables and chart for both celebrities.
        """
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
        """
        Populates a table with (title, score) from DataFrame.

        Args:
            tree (ttk.Treeview): Table widget.
            df (pd.DataFrame): Articles with sentiment.
        """
        for row in tree.get_children():
            tree.delete(row)
        for _, row in df.iterrows():
            title = row['Title'][:50] + "..." if len(row['Title']) > 50 else row['Title']
            tree.insert('', 'end', values=(title, f"{row['SentimentScore']:.2f}"))

    def _plot_comparison(self, df1, df2, celeb1, celeb2):
        """
        Plots both celebrities' net sentiment time series (daily), one in blue, one orange.

        Args:
            df1 (pd.DataFrame): First celeb.
            df2 (pd.DataFrame): Second celeb.
            celeb1, celeb2 (str): Names.
        """
        self.ax.clear()
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
    app = SentimentApp()
    app.mainloop()