import os
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import requests
from rules import check_buy_signals

# GitHub Secrets
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Your Refined Momentum List
TICKERS = [
    "ACHR", "AMD", "AMZN", "COHR", "CRWD", "IONQ", "META", "MSFT", "MSTR", 
    "MU", "NET", "NFLX", "NVDA", "NIO", "PLTR", "PSTG", "QBTS", "QCOM", "QUBT", 
    "RGTI", "SHOP", "SMCI", "TSLA", "TSM", "RKLB", "AAPL", "JOBY", "AVGO", 
    "MRVL", "ARM", "ANET", "PANW", "ASTS", "KTOS", "SNOW", "DDOG", "CCJ", 
    "GEV", "UBER", "APP"
]

def send_telegram_msg(message):
    """Sends a reliable notification via Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Telegram response: {response.status_code}")
    except Exception as e:
        print(f"Telegram error: {e}")

def run_scanner():
    print(f"🚀 Starting scan for {len(TICKERS)} momentum stocks...")
    candidates = []

    for symbol in TICKERS:
        try:
            # Fetch 60 days to ensure enough data for 50-day SMA
            df = yf.download(symbol, period="60d", interval="1d", progress=False)
            
            if df.empty or len(df) < 50:
                continue

            # Indicators
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['SMA20'] = ta.sma(df['Close'], length=20)
            df['SMA50'] = ta.sma(df['Close'], length=50)
            df['VolAvg'] = ta.sma(df['Volume'], length=10)

            # Check logic in rules.py
            if check_buy_signals(df):
                price = df['Close'].iloc[-1]
                candidates.append(f"🔥 *{symbol}* @ ${float(price):.2f}")
                print(f"✅ Match Found: {symbol}")

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    # Results
    if candidates:
        msg = "🎯 *Momentum Candidates Found:*\n\n" + "\n".join(candidates)
        send_telegram_msg(msg)
    else:
        send_telegram_msg("📭 Scan complete: No stocks in your custom list matched today.")
    
    print("Done.")

if __name__ == "__main__":
    run_scanner()
