import yfinance as yf


POSITIVE_WORDS = [
    "beat", "beats", "growth", "upgrade", "bullish", "surge", "rally",
    "record", "strong", "profit", "profits", "partnership", "launch",
    "expansion", "outperform", "raises", "raised"
]

NEGATIVE_WORDS = [
    "miss", "misses", "downgrade", "bearish", "fall", "falls", "drop",
    "drops", "lawsuit", "loss", "losses", "weak", "warning", "cuts",
    "cut", "investigation", "concern", "concerns"
]


def score_sentiment(text):
    text = text.lower()

    positive_score = sum(1 for word in POSITIVE_WORDS if word in text)
    negative_score = sum(1 for word in NEGATIVE_WORDS if word in text)

    if positive_score > negative_score:
        return "Positive"
    if negative_score > positive_score:
        return "Negative"

    return "Neutral"


def get_stock_news_sentiment(ticker, max_items=2):
    try:
        stock = yf.Ticker(ticker)
        news_items = stock.news or []

        if not news_items:
            return {
                "sentiment": "No recent news",
                "headlines": []
            }

        headlines = []

        for item in news_items[:max_items]:
            title = item.get("title", "").strip()
            publisher = item.get("publisher", "Unknown")

            if title:
                headlines.append(f"{title} — {publisher}")

        combined_text = " ".join(headlines)
        sentiment = score_sentiment(combined_text)

        return {
            "sentiment": sentiment,
            "headlines": headlines
        }

    except Exception as e:
        print(f"News fetch failed for {ticker}: {e}")
        return {
            "sentiment": "News unavailable",
            "headlines": []
        }
