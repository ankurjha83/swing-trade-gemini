# rules.py

def check_buy_signals(df):
    """
    Returns True if the stock meets the criteria.
    Edit these parameters to tune your strategy.
    """
    if len(df) < 50:
        return False

    # Get latest data points
    last = df.iloc[-1]
    price = last['Close']
    
    # 1. MOMENTUM PARAMETERS
    rsi_value = last['RSI']
    rsi_min = 50
    rsi_max = 70
    
    # 2. TREND PARAMETERS
    above_sma20 = price > last['SMA20']
    above_sma50 = price > last['SMA50']
    
    # 3. VOLUME PARAMETERS
    min_volume = 1_000_000
    rel_vol_threshold = 1.2
    relative_volume = last['Volume'] / last['VolAvg']
    
    # --- LOGIC TRIGGER ---
    momentum_ok = rsi_min < rsi_value < rsi_max
    trend_ok = above_sma20 and above_sma50
    volume_ok = (last['Volume'] > min_volume) and (relative_volume > rel_vol_threshold)

    return momentum_ok and trend_ok and volume_ok
