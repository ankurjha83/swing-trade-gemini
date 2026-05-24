import yfinance as yf
import pandas_ta as ta
import pandas as pd


# ============================================
# INDICATOR ENGINE
# ============================================

def add_indicators(df: pd.DataFrame):

    if df is None or df.empty or len(df) < 50:
        return None

    try:

        # Clean MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # ====================================
        # BOLLINGER BANDS
        # ====================================

        bbands = ta.bbands(
            df['Close'],
            length=20,
            std=2
        )

        df['BBL'] = bbands.iloc[:, 0]
        df['BBU'] = bbands.iloc[:, 2]

        # ====================================
        # RSI
        # ====================================

        df['RSI'] = ta.rsi(
            df['Close'],
            length=14
        )

        # ====================================
        # ATR
        # ====================================

        df['ATR'] = ta.atr(
            df['High'],
            df['Low'],
            df['Close'],
            length=14
        )

        # ====================================
        # ADX
        # ====================================

        adx_df = ta.adx(
            df['High'],
            df['Low'],
            df['Close'],
            length=14
        )

        df['ADX'] = adx_df.iloc[:, 0]

        # ====================================
        # MACD
        # ====================================

        macd_df = ta.macd(df['Close'])

        df['MACD'] = macd_df.iloc[:, 0]

        # ====================================
        # VOLUME AVERAGE
        # ====================================

        df['VolAvg'] = ta.sma(
            df['Volume'],
            length=20
        )

        return df

    except Exception as e:
        print(f"❌ Indicator error: {e}")
        return None


# ============================================
# LIVE FETCHER
# ============================================

def get_enriched_data(symbol: str):

    try:

        df = yf.download(
            symbol,
            period="5d",
            interval="15m",
            progress=False
        )

        if df.empty or len(df) < 50:
            return None

        df = add_indicators(df)

        return df

    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return None