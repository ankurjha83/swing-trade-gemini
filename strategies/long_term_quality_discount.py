"""
Long-Term Quality Discount Strategy

Purpose:
    Identify high-quality Nasdaq / mega-cap / elite growth stocks that are temporarily
    beaten down but not technically broken.

Use case:
    This is NOT a short-term swing-trading breakout strategy.
    It is an accumulation radar for long-term compounders that have corrected meaningfully.

Expected df columns:
    Close, RSI, MACD, Volume
Optional df columns:
    ATR, ADX

Return:
    A signal dict compatible with the existing strategy_runner/main.py format.
"""


def check(ticker, df):
    if df is None or df.empty or len(df) < 220:
        return None

    required = ["Close", "RSI", "MACD", "Volume"]
    if any(col not in df.columns for col in required):
        return None

    df = df.copy().dropna()

    # Core trend / valuation-dislocation proxies
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df["SMA100"] = df["Close"].rolling(window=100).mean()
    df["SMA200"] = df["Close"].rolling(window=200).mean()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()

    df = df.dropna()
    if len(df) < 20:
        return None

    curr = df.iloc[-1]
    prev = df.iloc[-2]

    close = curr["Close"]

    # Recent reference points
    high_52w = df["Close"].tail(252).max()
    high_6m = df["Close"].tail(126).max()
    low_3m = df["Close"].tail(63).min()

    drawdown_52w = (high_52w - close) / high_52w
    drawdown_6m = (high_6m - close) / high_6m
    rebound_from_3m_low = (close - low_3m) / low_3m if low_3m > 0 else 0

    # 1. Discount condition:
    # We want meaningful correction, but not full collapse.
    discounted = (
        drawdown_52w >= 0.18 or
        drawdown_6m >= 0.14
    )

    not_crashed = drawdown_52w <= 0.55

    # 2. Quality proxy:
    # Since this scanner currently appears price/indicator based, use long-term trend survival
    # as a proxy for business quality. Fundamental filters can be added later.
    long_term_quality_proxy = close >= curr["SMA200"] * 0.80

    # 3. Avoid broken names:
    # A great stock can temporarily trade below the 200DMA, but avoid severe structural breaks.
    not_structurally_broken = (
        close >= curr["SMA200"] * 0.80 and
        curr["SMA50"] >= curr["SMA200"] * 0.85
    )

    # 4. Oversold but stabilizing:
    # We want fear, but not blind falling-knife buying.
    rsi_discount_zone = 32 <= curr["RSI"] <= 55

    price_stabilizing = (
        close > prev["Close"] or
        close > curr["EMA20"] or
        rebound_from_3m_low >= 0.06
    )

    macd_stabilizing = curr["MACD"] >= prev["MACD"]

    # 5. Volume sanity:
    # Avoid extreme panic/liquidity events unless manually reviewed.
    recent_vol_avg = df["Volume"].tail(20).mean()
    volume_not_extreme = curr["Volume"] <= recent_vol_avg * 3.0

    # 6. Accumulation strength classification
    score = 0

    if drawdown_52w >= 0.25:
        score += 25
    elif drawdown_52w >= 0.18:
        score += 18

    if close >= curr["SMA200"]:
        score += 20
    elif close >= curr["SMA200"] * 0.90:
        score += 14
    elif close >= curr["SMA200"] * 0.80:
        score += 8

    if 35 <= curr["RSI"] <= 50:
        score += 15
    elif 50 < curr["RSI"] <= 55:
        score += 10

    if macd_stabilizing:
        score += 10

    if price_stabilizing:
        score += 15

    if volume_not_extreme:
        score += 10

    if rebound_from_3m_low >= 0.08:
        score += 5

    if (
        discounted and
        not_crashed and
        long_term_quality_proxy and
        not_structurally_broken and
        rsi_discount_zone and
        price_stabilizing and
        macd_stabilizing and
        volume_not_extreme and
        score >= 65
    ):
        if score >= 85:
            rating = "Aggressive accumulation candidate"
        elif score >= 75:
            rating = "Strong accumulation candidate"
        else:
            rating = "Watch / gradual accumulation candidate"

        return {
            "ticker": ticker,
            "strategy": "Long-Term Quality Discount",
            "price": close,
            "reason": (
                f"{rating}. "
                f"52W drawdown: {drawdown_52w:.1%}, "
                f"6M drawdown: {drawdown_6m:.1%}, "
                f"RSI: {curr['RSI']:.1f}, "
                f"score: {score}/100. "
                "Stock appears meaningfully discounted while showing early stabilization."
            )
        }

    return None
