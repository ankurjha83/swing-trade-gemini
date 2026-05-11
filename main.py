import os
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import requests
from rules import check_buy_signals

# GitHub Secrets
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_msg(message):
    """Reliable POST request for Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=data)
        print(f"Telegram response: {response.status_code}")
    except Exception as e:
        print(f"Telegram error: {e}")

def get_sp500_tickers():
    """Pulls current S&P 500 tickers from Wikipedia with User-Agent"""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    print("Fetching tickers from Wikipedia...")
    response = requests.get(url, headers=headers)
    tables = pd.read_html(response.text)
    df = tables[0]
    
    tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
    return tickers

def run_scanner():
    print("🔄 Starting S&P 500 Scan...")
    
    try:
        all_tickers = get_sp500_tickers()
        # Scan the first 100 stocks to stay within GitHub's time limits
        tickers = all_tickers[:100] 
        print(f"Successfully loaded {len(tickers)} tickers.")
    except Exception as e:
        print(f"Critical error fetching tickers: {e}")
        return

    candidates = []

    for symbol in tickers:
        try:
            # Download data
            df = yf.download(symbol, period="60d", interval="1d", progress=False)
            if df.empty or len(df) < 50:
                continue

            # Calculate Indicators
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['SMA20'] = ta.sma(df['Close'], length=20)
            df['SMA50'] = ta.sma(df['Close'], length=50)
            df['VolAvg'] = ta.sma(df['Volume'], length=10)

            # Check your rules.py logic
            if check_buy_signals(df):
                price = df['Close'].iloc[-1]
                candidates.append(f"🚀 *{symbol}* @ ${price:.2f}")
                print(f"MATCH FOUND: {symbol}")

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    # Send Notification
    if candidates:
        msg = "🎯 *Momentum Candidates Found:*\n\n" + "\n".join(candidates)
        send_telegram_msg(msg)
    else:
        send_telegram_msg("📭 Scan complete: No stocks matched your rules today.")
    
    print("Done.")

if __name__ == "__main__":
    run_scanner()
