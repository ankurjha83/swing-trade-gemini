import os
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import requests
from rules import check_buy_signals

# GitHub Secrets
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def load_tickers():
    """Reads tickers from tickers.txt, skipping empty lines and comments."""
    if not os.path.exists("tickers.txt"):
        print("❌ tickers.txt not found! Please create it.")
        return []
    
    with open("tickers.txt", "r") as f:
        # Read lines, strip whitespace, and ignore empty lines or lines starting with '#'
        tickers = [line.strip().upper() for line in f if line.strip() and not line.startswith("#")]
    return tickers

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": str(CHAT_ID).strip(), "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

def run_scanner():
    tickers = load_tickers() # <--- Now loading from the file!
    if not tickers:
        print("No tickers to scan.")
        return

    print(f"🚀 Starting scan for {len(tickers)} stocks...")
    candidates = []

    for symbol in tickers:
        try:
            df = yf.download(symbol, period="90d", interval="1d", progress=False)
            if df.empty or len(df) < 50: continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['SMA20'] = ta.sma(df['Close'], length=20)
            df['SMA50'] = ta.sma(df['Close'], length=50)
            df['VolAvg'] = ta.sma(df['Volume'], length=10)

            if check_buy_signals(df):
                price = df['Close'].iloc[-1]
                candidates.append(f"🔥 *{symbol}* @ ${float(price):.2f}")
                print(f"✅ Match: {symbol}")

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    if candidates:
        msg = "🎯 *Momentum Candidates Found:*\n\n" + "\n".join(candidates)
        send_telegram_msg(msg)
    else:
        send_telegram_msg(f"📭 Scan complete: No matches found in {len(tickers)} stocks today.")

if __name__ == "__main__":
    run_scanner()
