import pandas as pd

def check_buy_signals(df: pd.DataFrame) -> bool:
    """
    Intraday Multi-Factor Breakout System
    Optimized for 15m/30m timeframes.
    """
    required_columns = [
        "Close", "RSI", "BBU", "BBL", 
        "ATR", "ADX", "MACD", "Volume", "VolAvg"
    ]

    if df is None or df.empty or len(df) < 5:
        return False

    for col in required_columns:
        if col not in df.columns:
            return False

    df = df.copy().dropna()
    if len(df) < 5:
        return False

    # Get current and previous candles
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 1. THE TRIGGER: Price crossing the Upper Bollinger Band
    # We use 'prev_close <= prev_BBU' to ensure we catch the MOMENT it breaks out
    squeeze_breakout = prev["Close"] <= prev["BBU"] and curr["Close"] > curr["BBU"]

    # 2. TREND STRENGTH: ADX > 25 confirms the move isn't just noise
    trend_confirmation = curr["ADX"] > 25

    # 3. VOLATILITY CHECK: Ensure the stock actually 'moves'
    # ATR * 2 should represent at least a decent chunk of our 5% target
    atr_guard = (curr["ATR"] * 4) >= (curr["Close"] * 0.05)

    # 4. MOMENTUM: RSI in the 'Launch Zone' (60-85)
    momentum_confirmation = 60 <= curr["RSI"] <= 85

    # 5. MACD: Positive and trending up
    macd_confirmation = curr["MACD"] > 0 and curr["MACD"] > prev["MACD"]

    # 6. INTRADAY VOLUME VELOCITY (The Big Change)
    # On intraday charts, we look for the current bar's volume to be 
    # significantly higher than the average of the RECENT bars.
    recent_vol_avg = df["Volume"].tail(10).mean()
    volume_velocity = curr["Volume"] >= (recent_vol_avg * 1.5)

    return bool(
        squeeze_breakout 
        and trend_confirmation 
        and atr_guard 
        and momentum_confirmation 
        and macd_confirmation 
        and volume_velocity
    )
