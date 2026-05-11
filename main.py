import os
import pandas as pd
import yfinance as yf
import pandas_ta as ta  # This works with pandas-ta-classic too
import requests
from rules import check_buy_signals

# GitHub Secrets
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def get_sp500_tickers():
    """Pulls current S&P 500 tickers from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    # Wikipedia requires a User-Agent header to allow the request
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    
    tables = pd.read_html(response.text)
    df = tables[0]
    
    # Standardize symbols (yfinance likes '-' instead of '.')
    tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
    return tickers

def run_scanner():
    print("🔄 Starting S&P 500 Scan...")
    try:
        tickers = get_sp500_tickers()
    except Exception as e:
        send_telegram_msg(f"❌ Error fetching S&P 500 list: {e}")
        return

    candidates = []

    # Start with a smaller batch for the first success!
    # Once you see it working, change [0:50] to [:] to scan all 500.
    for symbol in tickers[0:50]: 
        try:
            df = yf.download(symbol, period="60d", interval="1d", progress=False)
            
            if df.empty or len(df) < 50:
                continue

            # Calculate Indicators
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['SMA20'] = ta.sma(df['Close'], length=20)
            df['SMA50'] = ta.sma(df['Close'], length=50)
            df['VolAvg'] = ta.sma(df['Volume'], length=10)

            if check_buy_signals(df):
                price = df.iloc[-1]['Close']
                candidates.append(f"🚀 *{symbol}* @ ${price:.2f}")

        except Exception as e:
            print(f"Skipping {symbol}: {e}")

    # Send Notification
    if candidates:
        msg = "🎯 *Momentum Candidates Found:*\n\n" + "\n".join(candidates)
        send_telegram_msg(msg)
    else:
        send_telegram_msg("📭 Scan complete: No stocks matched your 5% setup today.")

if __name__ == "__main__":
    run_scanner()
