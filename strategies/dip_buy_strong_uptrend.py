def check(ticker, df):
    if df is None or df.empty or len(df) < 80:
        return None

    required = ["Close", "RSI", "MACD", "Volume"]
    if any(col not in df.columns for col in required):
        return None

    df = df.copy().dropna()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df = df.dropna()

    if len(df) < 30:
        return None

    curr = df.iloc[-1]
    prev = df.iloc[-2]
    close = curr["Close"]

    trend_ok = curr["EMA20"] > curr["SMA50"] and close > curr["SMA50"]

    recent_high = df["Close"].tail(30).max()
    pullback = (recent_high - close) / recent_high if recent_high > 0 else 0

    pullback_ok = 0.03 <= pullback <= 0.10
    rsi_ok = 40 <= curr["RSI"] <= 58
    bounce_ok = close > prev["Close"] and curr["MACD"] >= prev["MACD"]

    if trend_ok and pullback_ok and rsi_ok and bounce_ok:
        return {
            "ticker": ticker,
            "strategy": "Dip Buy in Strong Uptrend",
            "price": close,
            "reason": "Strong trend stock has pulled back and is showing a bounce.",
            "target_1": close * 1.05,
            "stop_loss": close * 0.975,
            "risk": "Medium",
        }

    return None
