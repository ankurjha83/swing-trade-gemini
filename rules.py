import pandas as pd


def check_buy_signals(df: pd.DataFrame) -> bool:
    """
    Multi-Factor Breakout System

    Returns True when the latest candle confirms:
    1. Bollinger Band upside breakout
    2. Strong trend via ADX
    3. ATR-supported 5% target potential
    4. RSI momentum without blow-off extension
    5. Relative volume confirmation
    """

    required_columns = [
        "Close",
        "RSI",
        "BBU",
        "BBL",
        "ATR",
        "ADX",
        "MACD",
        "Volume",
        "VolAvg",
    ]

    if df is None or df.empty:
        return False

    if len(df) < 2:
        return False

    for col in required_columns:
        if col not in df.columns:
            return False

    df = df.copy()
    df = df[required_columns].dropna()

    if len(df) < 2:
        return False

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    close = curr["Close"]
    prev_close = prev["Close"]

    if close <= 0:
        return False

    squeeze_breakout = (
        prev_close <= prev["BBU"]
        and close > curr["BBU"]
    )

    trend_confirmation = curr["ADX"] > 25

    atr_guard = (curr["ATR"] * 2) >= (close * 0.05)

    momentum_confirmation = 60 <= curr["RSI"] <= 82

    macd_confirmation = curr["MACD"] > 0

    relative_volume_confirmation = (
        curr["VolAvg"] > 0
        and curr["Volume"] >= curr["VolAvg"] * 1.3
    )

    return bool(
        squeeze_breakout
        and trend_confirmation
        and atr_guard
        and momentum_confirmation
        and macd_confirmation
        and relative_volume_confirmation
    )
