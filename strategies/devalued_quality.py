def check(ticker, df):
    if df is None or df.empty or len(df) < 60:
        return None

    required = ["Close", "RSI", "MACD", "Volume"]
    if any(col not in df.columns for col in required):
        return None

    df = df.copy().dropna()
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df = df.dropna()

    if len(df) < 20:
        return None

    curr = df.iloc[-1]
    prev = df.iloc[-2]

    close = curr["Close"]
    recent_20_high = df["Close"].tail(20).max()
    recent_50_high = df["Close"].tail(50).max()

    drawdown_20 = (recent_20_high - close) / recent_20_high
    drawdown_50 = (recent_50_high - close) / recent_50_high

    devalued_ok = drawdown_20 >= 0.08 or drawdown_50 >= 0.12
    not_broken = close >= curr["SMA50"] * 0.95
    rsi_ok = 35 <= curr["RSI"] <= 52
    stabilizing = close > prev["Close"] and curr["MACD"] > prev["MACD"]

    recent_vol_avg = df["Volume"].tail(10).mean()
    not_panic_selling = curr["Volume"] <= recent_vol_avg * 2.5

    if devalued_ok and not_broken and rsi_ok and stabilizing and not_panic_selling:
        return {
            "ticker": ticker,
            "strategy": "Temporarily Devalued Quality",
            "price": close,
            "reason": "Stock has corrected meaningfully but is showing early stabilization."
        }

    return None
