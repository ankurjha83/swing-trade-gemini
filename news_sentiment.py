import json
import os
import yfinance as yf


METADATA_FILE = "ticker_metadata.json"


POSITIVE_WORDS = [
    "beat", "beats", "growth", "upgrade", "upgraded", "surge", "rally",
    "strong", "profit", "profits", "raises", "raised", "bullish",
    "soars", "soaring", "record", "outperform", "partnership"
]

NEGATIVE_WORDS = [
    "miss", "misses", "downgrade", "downgraded", "drop", "drops",
    "falls", "fall", "loss", "losses", "weak", "cuts", "cut",
    "lawsuit", "bearish", "concern", "concerns", "warning",
    "investigation", "slumps", "plunges"
]


def load_ticker_metadata():
    if not os.path.exists(METADATA_FILE):
        return {}

    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Could not load {METADATA_FILE}: {e}")
        return {}


TICKER_METADATA = load_ticker_metadata()


def get_aliases(ticker):
    ticker = ticker.upper()
    metadata = TICKER_METADATA.get(ticker, {})

    aliases = metadata.get("aliases", [])

    if ticker not in aliases:
        aliases.append(ticker)

    return aliases


def is_relevant_headline(ticker, headline):
    aliases = get_aliases(ticker)
    headline_lower = headline.lower()

    return any(alias.lower() in headline_lower for alias in aliases)


def score_sentiment(headlines):
    combined = " ".join(headlines).lower()

    positive_score = sum(1 for word in POSITIVE_WORDS if word in combined)
    negative_score = sum(1 for word in NEGATIVE_WORDS if word in combined)

    if positive_score > negative_score:
        return "Positive"

    if negative_score > positive_score:
        return "Negative"

    return "Neutral"


def extract_news_title_and_publisher(item):
    content = item.get("content", item)

    title = content.get("title") or item.get("title")

    publisher = (
        content.get("provider", {}).get("displayName")
        or item.get("publisher")
        or "Unknown"
    )

    return title, publisher


def get_stock_news_sentiment(ticker, max_items=2):
    try:
        stock = yf.Ticker(ticker)
        news_items = stock.news or []

        relevant_headlines = []

        for item in news_items:
            title, publisher = extract_news_title_and_publisher(item)

            if not title:
                continue

            headline = f"{title} — {publisher}"

            if is_relevant_headline(ticker, headline):
                relevant_headlines.append(headline)

            if len(relevant_headlines) >= max_items:
                break

        if not relevant_headlines:
            return {
                "sentiment": "No relevant news found",
                "headlines": []
            }

        return {
            "sentiment": score_sentiment(relevant_headlines),
            "headlines": relevant_headlines
        }

    except Exception as e:
        print(f"News fetch failed for {ticker}: {e}")
        return {
            "sentiment": "News unavailable",
            "headlines": []
        }
