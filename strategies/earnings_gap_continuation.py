def check(ticker, df):
    if df is None or df.empty or len(df) < 50:
        return None

    required = ["Open", "Close", "High", "Low", "Volume", "RSI"]
    if any(col not in df.columns for col in required):
        return None

    df = df.copy().dropna()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df = df.dropna()

    if len(df) < 30:
        return None

    curr = df.iloc[-1]
    prev = df.iloc[-2]

    close = curr["Close"]
    gap = (curr["Open"] - prev["Close"]) / prev["Close"] if prev["Close"] > 0 else 0

    candle_range = curr["High"] - curr["Low"]
    close_position = (close - curr["Low"]) / candle_range if candle_range > 0 else 0

    recent_vol_avg = df["Volume"].tail(20).mean()

    gap_ok = gap >= 0.04
    volume_ok = curr["Volume"] >= recent_vol_avg * 1.8
    close_strong = close_position >= 0.65
    trend_ok = close > curr["EMA20"]
    rsi_ok = 55 <= curr["RSI"] <= 78

    if gap_ok and volume_ok and close_strong and trend_ok and rsi_ok:
        return {
            "ticker": ticker,
            "strategy": "Gap Continuation",
            "price": close,
            "reason": "Large gap up with strong close, high volume, and trend confirmation.",
            "target_1": close * 1.05,
            "stop_loss": close * 0.975,
            "risk": "High",
        }

    return None
