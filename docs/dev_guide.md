# Developer Guide: Love-Hate Sentiment App

## Overview

This app lets users compare the day-by-day news sentiment of two celebrities (or topics) by pulling Google News headlines, scoring them for sentiment, and plotting results. It has a Tkinter GUI for user-friendly interaction, and a CLI mode for quick testing.  
Goal: provide an intuitive snapshot of "who's loved, who's hated" in the news, and how that fluctuates.

---

## What’s Implemented (Specs Recap)

- Google News RSS scraping (max 100 articles per celeb/topic)
- Sentiment analysis with VADER on article headlines
- Aggregation and line chart of daily net sentiment per topic
- Tkinter GUI for inputting two names and visualizing comparison
- Data tables (Tkinter Treeview) listing all articles and their scores for each celeb
- CLI mode (single-celebrity sentiment chart for testing/debug)
- Handles RSS blocks (user-agent spoofing)
- Ensures chronological plotting

**Not Implemented/Deferred:**
- No date range selection (limited by Google News)
- No CSV export yet
- No advanced error handling or UI customizations

---

## Install, Deployment, and Admin Notes

- Clone repo:  
  `git clone https://github.com/dedoop66/Love-Hate.git && cd Love-Hate`
- Install Python requirements:  
  `pip install requests feedparser vaderSentiment pandas matplotlib`
- Run with:  
  `python main.py`
- No special admin steps needed.  
- All data is pulled fresh at runtime (nothing stored locally).
- If you want to run in CLI mode, just uncomment the CLI section at the bottom of `main.py` and comment out the GUI section.

**If you see HTTP errors:**
- Check your internet connection.
- Google News might throttle you for excessive scraping, but currently the spoofed user-agent solves this.

---

## User Interaction & Flow Through the Code

### UX Flow

1. **User launches app:** (Tkinter window pops up)
2. **Inputs two celebrity/topic names:** (text boxes)
3. **Clicks "Go":**
    - Program fetches most recent 100 Google News headlines for both names.
    - Sentiment is analyzed and stored.
    - Chart is plotted (blue for celeb1, orange for celeb2) with 0 line marked.
    - Two tables below show articles and scores.
4. **User reviews chart, can try new names anytime.**

### Code Walkthrough

**All logic is in `main.py`**  
**Key components:**
- `get_news_headlines(query)` — fetches Google News RSS, parses entries
- `analyze_sentiment(entries)` — runs VADER sentiment analysis, returns DataFrame
- `plot_sentiment_aggregated_daily(df)` — CLI only: shows matplotlib line chart
- `SentimentApp (tk.Tk)` — Main Tkinter GUI class
    - Fields for input
    - `on_go()` starts new thread, calls `_fetch_and_plot`
    - `_fetch_and_plot()` pulls headlines, scores, updates tables, redraws chart
    - `_update_table()` populates Treeview widget with results
    - `_plot_comparison()` does matplotlib plotting in GUI

**Class hierarchy:**  
- Only one main custom class: `SentimentApp` (subclass of `tk.Tk`). All GUI code is methods of this class.

**Threading:**  
- Fetch/analysis/plot is run in a thread to keep the UI from freezing.

---

## Known Issues / Bugs / Gotchas

### Minor
- Google News RSS only allows last 100 stories per query (limiting history and analysis depth)
- UI tables can look misaligned on small screens
- If headlines are missing publish dates, those rows are skipped
- Plot colors are not configurable (hardcoded for clarity)
- Sentiment is simple "net daily score"  not a rolling average or advanced metric

### Major
- No persistent storage data is lost on close
- If Google News RSS changes format or blocks your IP, fetching may fail

### Inefficiencies
- All fetching is synchronous (except for the thread to avoid UI freeze). For larger or multiple queries, async could help.
- VADER is fast, but if analyzing more than 1000s of articles (not currently possible), vectorization would help.

---

## Future Work

- Add CSV/Excel export for tables and chart data
- Allow date range filtering, if alternative data source found
- Improve GUI layout (responsive design, colorblind safe, etc.)
- Modularize code into separate files (fetching, analysis, GUI)
- Add automated tests for key functions
- Support more news sources (e.g., Bing News, paid APIs)
- Add language support (non-English headlines)

---

## Ongoing Development

- All new features should be added as new functions or as methods on `SentimentApp`.
- Keep dependencies minimal document any additions in this guide.
- If new news sources added, clearly document new fetching functions.
- Consider refactoring as a pip-installable package if project expands.

---

