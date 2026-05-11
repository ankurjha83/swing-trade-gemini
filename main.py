import os
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import requests
from rules import check_buy_signals

# GitHub Secrets - Ensure these are set in your Repo Settings
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Your Momentum Watchlist
TICKERS = [
    "ACHR", "AMD", "AMZN", "COHR", "CRWD", "IONQ", "META", "MSFT", "MSTR", 
    "MU", "NET", "NFLX", "NVDA", "NIO", "PLTR", "PSTG", "QBTS", "QCOM", "QUBT", 
    "RGTI", "SHOP", "SMCI", "TSLA", "TSM", "RKLB", "AAPL", "JOBY", "AVGO", 
    "MRVL", "ARM", "ANET", "PANW", "ASTS", "KTOS", "SNOW", "DDOG", "CCJ", 
    "GEV", "UBER", "APP"
]

def send_telegram_msg(message):
    """Sends a notification via Telegram using a robust POST request."""
    if not TOKEN or not CHAT_ID:
        print("Error: TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set in Secrets.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Telegram message sent successfully.")
        else:
            print(f"Telegram failed. Code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Telegram connection error: {e}")

def run_scanner():
    print(f"🚀 Starting scan for {len(TICKERS)} momentum stocks...")
    candidates = []

    for symbol in TICKERS:
        try:
            # Download 90 days to ensure plenty of overhead for SMAs
            df = yf.download(symbol, period="90d", interval="1d", progress=False)
            
            if df.empty or len(df) < 50:
                print(f"Skipping {symbol}: Insufficient data.")
                continue

            # --- THE FIX FOR "Identically-labeled Series" ERROR ---
            # Flatten the MultiIndex columns returned by new yfinance versions
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            # ------------------------------------------------------

            # Technical Indicator Calculations
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['SMA20'] = ta.sma(df['Close'], length=20)
            df['SMA50'] = ta.sma(df['Close'], length=50)
            df['VolAvg'] = ta.sma(df['Volume'], length=10)

            # Check logic in rules.py
            if check_buy_signals(df):
                # .iloc[-1] gets the most recent closing price
                price = df['Close'].iloc[-1]
                candidates.append(f"🔥 *{symbol}* @ ${float(price):.2f}")
                print(f"✅ Match Found: {symbol}")

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    # Final Output Logic
    if candidates:
        msg = "🎯 *Momentum Candidates Found:*\n\n" + "\n".join(candidates)
        send_telegram_msg(msg)
    else:
        send_telegram_msg("📭 Scan complete: No stocks in your custom list matched today.")
    
    print("Scanner execution finished.")

if __name__ == "__main__":
    run_scanner()
