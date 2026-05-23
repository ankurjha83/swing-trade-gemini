def check(ticker, df):
    if df is None or df.empty or len(df) < 50:
        return None

    required = ["Close", "RSI", "MACD", "Volume"]
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

    recently_oversold = df["RSI"].tail(20).min() <= 30
    reclaim_ema20 = prev["Close"] <= prev["EMA20"] and close > curr["EMA20"]
    macd_improving = curr["MACD"] > prev["MACD"]
    rsi_recovering = 35 <= curr["RSI"] <= 55

    recent_vol_avg = df["Volume"].tail(10).mean()
    volume_ok = curr["Volume"] >= recent_vol_avg * 1.1

    if recently_oversold and reclaim_ema20 and macd_improving and rsi_recovering and volume_ok:
        return {
            "ticker": ticker,
            "strategy": "Oversold Bounce",
            "price": close,
            "reason": "Recently oversold stock is reclaiming EMA20 with improving momentum.",
            "target_1": close * 1.04,
            "stop_loss": close * 0.97,
            "risk": "High",
        }

    return None
