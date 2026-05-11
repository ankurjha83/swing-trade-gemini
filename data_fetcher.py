import yfinance as yf
import pandas_ta as ta
import pandas as pd

def get_enriched_data(symbol: str):
    """Downloads and calculates indicators using the most stable function calls."""
    try:
        # 1. Download with a bit more history for stability
        # df = yf.download(symbol, period="150d", interval="1d", progress=False)
        df = yf.download(symbol, period="5d", interval="15m", progress=False)
        if df.empty or len(df) < 50:
            return None

        # Clean MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 2. CALCULATE INDICATORS (Standard Method)
        
        # Bollinger Bands: Returns a DataFrame [BBL, BBM, BBU, BBB, BBP]
        bbands = ta.bbands(df['Close'], length=20, std=2)
        df['BBL'] = bbands.iloc[:, 0]
        df['BBU'] = bbands.iloc[:, 2]
        
        # RSI
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # ATR
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        
        # ADX: Returns a DataFrame [ADX, DMP, DMN]
        adx_df = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        df['ADX'] = adx_df.iloc[:, 0]
        
        # MACD: Returns a DataFrame [MACD, Histogram, Signal]
        macd_df = ta.macd(df['Close'])
        df['MACD'] = macd_df.iloc[:, 0]
        
        # Volume Average - The specific fix for your error
        df['VolAvg'] = ta.sma(df['Volume'], length=20)
        
        return df
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return None
