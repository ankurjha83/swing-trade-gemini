def check(ticker, df):
    if df is None or df.empty or len(df) < 60:
        return None

    required = ["Close", "RSI", "ATR", "ADX", "MACD", "Volume"]
    if any(col not in df.columns for col in required):
        return None

    df = df.copy().dropna()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df = df.dropna()

    if len(df) < 15:
        return None

    curr = df.iloc[-1]
    prev = df.iloc[-2]

    close = curr["Close"]
    atr_pct = curr["ATR"] / close

    trend_ok = close > curr["EMA20"] and close > curr["SMA50"] and curr["EMA20"] > curr["SMA50"]
    rsi_ok = 50 <= curr["RSI"] <= 70
    atr_ok = 0.015 <= atr_pct <= 0.08
    adx_ok = curr["ADX"] >= 15

    recent_vol_avg = df["Volume"].tail(10).mean()
    volume_ok = curr["Volume"] >= recent_vol_avg * 1.15

    previous_10_high = df["Close"].iloc[-11:-1].max()
    breakout_trigger = close > previous_10_high
    ema_reclaim_trigger = prev["Close"] <= prev["EMA20"] and close > curr["EMA20"]
    macd_trigger = curr["MACD"] > 0 and curr["MACD"] > prev["MACD"]

    if trend_ok and rsi_ok and atr_ok and adx_ok and volume_ok and (breakout_trigger or ema_reclaim_trigger or macd_trigger):
        return {
            "ticker": ticker,
            "strategy": "Early Trend Continuation",
            "price": close,
            "reason": "Trend aligned, RSI healthy, volume confirmed, and momentum trigger active."
        }

    return None
