# Love-Hate: Celebrity News Sentiment Comparator

This project lets you compare the daily news sentiment of any two celebritiess or topics side-by-side. It fetches recent headlines from Google News, analyzes their sentiment using VaderSentiment, and displays both a time series chart and tables of headline scores.

---

## Quick Start

### 1. Prerequisites

- Python 3.8 or newer  
- Internet connection

### 2. Installation

Open a terminal or command prompt in your project directory, then run:

### 3. Running the App

From the project directory, run:

If you get an error about Tkinter, install it with your system’s package manager (for example, on Ubuntu: `sudo apt-get install python3-tk`).

---

## How to Use

1. When you run the app, a window will open.
2. Enter the names of any two celebrities or topics into the provided text fields (for example: "LeBron James" and "Donald Trump").
3. Click the "Go" button.
4. The chart will show the net daily sentiment for both names, based on the most recent news headlines available (usually up to 100 per search).
5. The tables below the chart show the article headlines and their sentiment scores.
6. You can run new comparisons by entering different names and clicking "Go" again.

---

## Troubleshooting

- If you see no data or the chart/tables are empty, try using more well-known names, or wait a few seconds and try again.
- If you see a Python error about 'Tkinter', you may need to install it (see Installation above).

---

## Limitations and Known Issues

- The app only displays up to the 100 most recent headlines per search (a Google News RSS limitation).
- Sentiment is analyzed from the headlines only, not the full news articles.
- You cannot select a custom date range. The chart only shows the days for which news is available.
- The chart uses blue and orange lines for the two names being compared.
- Articles without a valid published date are not shown in the chart or tables.

For developer and technical documentation, see [doc/dev_guide.md](doc/dev_guide.md).

---

## About

Developed by Devin Dupree for HCI 5840  
Contact: [ddupree@iastate.edu]  
Licensed as open source. Pull requests and suggestions are welcome.
