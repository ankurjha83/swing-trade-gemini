def check(ticker, df):
    if df is None or df.empty or len(df) < 60:
        return None

    required = ["Close", "Volume", "RSI", "ATR", "MACD"]
    if any(col not in df.columns for col in required):
        return None

    df = df.copy().dropna()
    if len(df) < 60:
        return None

    curr = df.iloc[-1]
    close = curr["Close"]

    recent_low = df["Close"].iloc[-60:-20].min()
    recent_high = df["Close"].iloc[-20:].max()

    if recent_low <= 0:
        return None

    prior_runup = (recent_high - recent_low) / recent_low

    flag_high = df["Close"].iloc[-15:-1].max()
    flag_low = df["Close"].iloc[-15:-1].min()
    flag_range = (flag_high - flag_low) / flag_low if flag_low > 0 else 999

    recent_vol = df["Volume"].tail(10).mean()
    older_vol = df["Volume"].iloc[-40:-20].mean()

    runup_ok = prior_runup >= 0.18
    tight_flag_ok = flag_range <= 0.08
    volume_dryup_ok = recent_vol <= older_vol * 0.9
    breakout_ok = close > flag_high
    rsi_ok = 55 <= curr["RSI"] <= 75

    if runup_ok and tight_flag_ok and volume_dryup_ok and breakout_ok and rsi_ok:
        return {
            "ticker": ticker,
            "strategy": "High Tight Flag",
            "price": close,
            "reason": "Strong prior run, tight consolidation, volume contraction, and breakout.",
            "target_1": close * 1.05,
            "stop_loss": close * 0.975,
            "risk": "Medium-High",
        }

    return None
