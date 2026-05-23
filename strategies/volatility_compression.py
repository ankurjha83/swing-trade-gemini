def check(ticker, df):
    if df is None or df.empty or len(df) < 60:
        return None

    required = ["Close", "BBU", "BBL", "ATR", "Volume", "RSI"]
    if any(col not in df.columns for col in required):
        return None

    df = df.copy().dropna()
    if len(df) < 40:
        return None

    curr = df.iloc[-1]
    close = curr["Close"]

    df["BB_WIDTH"] = (df["BBU"] - df["BBL"]) / df["Close"]
    current_width = df["BB_WIDTH"].iloc[-1]
    avg_width = df["BB_WIDTH"].iloc[-30:-1].mean()

    atr_now = df["ATR"].tail(5).mean()
    atr_before = df["ATR"].iloc[-30:-20].mean()

    compression_ok = current_width <= avg_width * 0.75
    atr_compressing = atr_now <= atr_before * 0.85

    recent_high = df["Close"].iloc[-20:-1].max()
    breakout_ok = close > recent_high

    recent_vol_avg = df["Volume"].tail(10).mean()
    volume_ok = curr["Volume"] >= recent_vol_avg * 1.25

    rsi_ok = 50 <= curr["RSI"] <= 72

    if compression_ok and atr_compressing and breakout_ok and volume_ok and rsi_ok:
        return {
            "ticker": ticker,
            "strategy": "Volatility Compression Breakout",
            "price": close,
            "reason": "Volatility compressed, then price broke out with volume.",
            "target_1": close * 1.05,
            "stop_loss": close * 0.975,
            "risk": "Medium-High",
        }

    return None
