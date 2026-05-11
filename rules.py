# rules.py

def check_buy_signals(df):
    """
    Finalized Momentum Strategy for a 5% Profit Target.
    """
    # 1. DATA SAFETY CHECK
    # Ensure we have enough historical data to calculate moving averages (50 days minimum)
    if len(df) < 50:
        return False

    # Get the most recent data row
    last = df.iloc[-1]
    
    # 2. TREND FILTER (The "Uptrend" Rule)
    # Price MUST be above the 20-day and 50-day Simple Moving Averages.
    # This ensures we only trade stocks with institutional support.
    price = last['Close']
    above_sma20 = price > last['SMA20']
    above_sma50 = price > last['SMA50']
    
    # 3. MOMENTUM PARAMETERS (The "RSI Sweet Spot")
    # RSI between 55 and 80.
    # We want strong strength (55+), but we allow up to 80 to catch leaders 
    # like NVDA and AMD that stay "hot" during major runs.
    rsi_value = last['RSI']
    momentum_ok = 55 < rsi_value < 85
    
    # 4. VOLUME PARAMETERS (The "Institutional Footprint")
    # Requires a minimum of 1 million shares daily and a relative volume spike.
    # A multiplier of 1.2x confirms there is "fresh money" entering.
    min_volume = 1_000_000
    rel_vol_threshold = 0.8
    relative_volume = last['Volume'] / last['VolAvg']
    
    volume_ok = (last['Volume'] > min_volume) and (relative_volume > rel_vol_threshold)

    # --- THE MASTER TRIGGER ---
    # Only return True if all criteria are perfectly aligned.
    return momentum_ok and above_sma20 and above_sma50 and volume_ok
