import yfinance as yf
import pandas_ta as ta
import pandas as pd

def get_enriched_data(symbol: str):
    """Downloads and calculates indicators with guaranteed column names."""
    try:
        df = yf.download(symbol, period="150d", interval="1d", progress=False)
        if df.empty or len(df) < 50:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # --- BOLLINGER BANDS FIX ---
        # Calculate bbands
        bbands = df.ta.bbands(length=20, std=2)
        
        # Instead of guessing the name, we take the columns by position:
        # Bollinger bands usually return: [Lower, Mid, Upper, Bandwidth, %B]
        # We grab the first and third columns to be safe.
        df['BBL'] = bbands.iloc[:, 0]  # Lower Band
        df['BBU'] = bbands.iloc[:, 2]  # Upper Band
        
        # --- OTHER INDICATORS ---
        df['RSI'] = df.ta.rsi(length=14)
        df['ATR'] = df.ta.atr(length=14)
        
        # ADX Fix (sometimes returns a DataFrame, we just need the ADX column)
        adx_df = df.ta.adx(length=14)
        df['ADX'] = adx_df.iloc[:, 0] 
        
        # MACD Fix
        macd_df = df.ta.macd()
        df['MACD'] = macd_df.iloc[:, 0] # The main MACD line
        
        # Volume
        df['VolAvg'] = df.ta.sma(df['Volume'], length=20)
        
        return df
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return None
