import yfinance as yf


def get_stock_news_sentiment(ticker, max_items=3):
    try:
        stock = yf.Ticker(ticker)
        news_items = stock.news or []

        headlines = []

        for item in news_items[:max_items]:
            content = item.get("content", item)

            title = content.get("title") or item.get("title")
            publisher = content.get("provider", {}).get("displayName") or item.get("publisher", "Unknown")

            if title:
                headlines.append(f"{title} — {publisher}")

        if not headlines:
            return {
                "sentiment": "No recent news found",
                "headlines": []
            }

        combined = " ".join(headlines).lower()

        positive_words = ["beat", "growth", "upgrade", "surge", "rally", "strong", "profit", "raises", "bullish"]
        negative_words = ["miss", "downgrade", "drop", "falls", "loss", "weak", "cuts", "lawsuit", "bearish"]

        pos = sum(word in combined for word in positive_words)
        neg = sum(word in combined for word in negative_words)

        sentiment = "Neutral"
        if pos > neg:
            sentiment = "Positive"
        elif neg > pos:
            sentiment = "Negative"

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
