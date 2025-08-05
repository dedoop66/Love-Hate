# Developer Guide: Love-Hate Sentiment App

## Overview

This project is a news sentiment analysis tool that lets users compare the net daily news sentiment for two celebrities or topics using recent Google News headlines. It provides a simple Tkinter GUI for interactive use, and can also be run from the command line. The app leverages `vaderSentiment` for sentiment analysis and matplotlib for visualization.

## Project Structure

- `main.py` – Main application entry point. Contains both CLI and GUI.
- `dev_guide.md` – This developer guide.
- `README.md` – User guide and quick start instructions.


## Features Implemented

- Fetches up to 100 recent Google News headlines per query via RSS.
- Analyzes each headline's sentiment using VADER.
- Aggregates and plots net sentiment by day.
- Tkinter GUI: enter two celeb names, click Go, view daily sentiment comparison line chart, and review article tables below.
- Table view for each celebrity/topic’s articles and sentiment scores.
- CLI mode (run directly in terminal for a single celebrity).
- Handles HTTP access issues and sorts results chronologically for accurate plotting.

## Installation / Setup

Assumes Python 3 is installed.

