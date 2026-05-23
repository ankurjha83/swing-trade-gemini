def check(ticker, df):
    if df is None or df.empty or len(df) < 50:
        return None

    required = ["Close", "Low", "Volume", "RSI", "MACD"]
    if any(col not in df.columns for col in required):
        return None

    df = df.copy().dropna()
    if len(df) < 30:
        return None

    curr = df.iloc[-1]
    prev = df.iloc[-2]
    close = curr["Close"]

    support = df["Close"].iloc[-25:-2].min()

    broke_support = prev["Close"] < support
    reclaimed_support = close > support

    strong_close = close > prev["Close"]
    macd_improving = curr["MACD"] > prev["MACD"]
    rsi_ok = 35 <= curr["RSI"] <= 60

    recent_vol_avg = df["Volume"].tail(10).mean()
    volume_ok = curr["Volume"] >= recent_vol_avg * 1.2

    if broke_support and reclaimed_support and strong_close and macd_improving and rsi_ok and volume_ok:
        return {
            "ticker": ticker,
            "strategy": "Failed Breakdown Reversal",
            "price": close,
            "reason": "Stock broke support, reclaimed it quickly, and momentum improved.",
            "target_1": close * 1.05,
            "stop_loss": close * 0.97,
            "risk": "High",
        }

    return None
