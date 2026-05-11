import os
import yfinance as yf
import pandas_ta as ta
import requests
from rules import check_buy_signals

# GitHub Secrets will be loaded here
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Pull S&P 500 Tickers automatically
def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    return tables[0]['Symbol'].tolist()

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown"
    requests.get(url)

def run_scanner():
    import pandas as pd

def get_sp500_tickers():
    # Pulls the official list of S&P 500 companies
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    df = tables[0]
    # Standardize tickers (yfinance prefers '-' over '.' for symbols like BRK.B)
    tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
    return tickers

def run_scanner():
    tickers = get_sp500_tickers()
    candidates = []
    print(f"Starting scan of {len(tickers)} stocks...")
    
    # ... rest of your loop logic ...

    for symbol in tickers:
        try:
            df = yf.download(symbol, period="60d", interval="1d", progress=False)
            
            # Pre-calculate indicators for the rules file
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['SMA20'] = ta.sma(df['Close'], length=20)
            df['SMA50'] = ta.sma(df['Close'], length=50)
            df['VolAvg'] = ta.sma(df['Volume'], length=10)

            if check_buy_signals(df):
                price = df.iloc[-1]['Close']
                candidates.append(f"🚀 *{symbol}* @ ${price:.2f}")

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    if candidates:
        msg = "🎯 *Buy Rules Triggered:*\n\n" + "\n".join(candidates)
        send_telegram_msg(msg)
    else:
        # This confirms the script is working perfectly even if the market is quiet
        send_telegram_msg("📭 Scanner ran successfully, but no S&P 500 stocks met your 5% setup today.")

if __name__ == "__main__":
    run_scanner()
