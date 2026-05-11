import yfinance as yf
import pandas_ta as ta
import pandas as pd

def get_enriched_data(symbol: str):
    """Downloads and calculates indicators for a symbol."""
    try:
        df = yf.download(symbol, period="150d", interval="1d", progress=False)
        if df.empty or len(df) < 50:
            return None

        # Clean up column names for consistency
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Volatility & Momentum
        bbands = df.ta.bbands(length=20, std=2)
        df['BBU'] = bbands['BBU_20_2.0']
        df['BBL'] = bbands['BBL_20_2.0']
        df['RSI'] = df.ta.rsi(length=14)
        df['ATR'] = df.ta.atr(length=14)
        
        # Trend & Volume
        adx_data = df.ta.adx(length=14)
        df['ADX'] = adx_data['ADX_14']
        macd_data = df.ta.macd()
        df['MACD'] = macd_data['MACD_12_26_9']
        df['VolAvg'] = df.ta.sma(df['Volume'], length=20)
        
        return df
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return None
