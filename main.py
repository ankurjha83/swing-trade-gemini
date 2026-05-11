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
    tickers = load_tickers()
    print(f"🚀 Starting scan for {len(tickers)} stocks...")
    candidates = []

    for symbol in tickers:
        try:
            # Download data
            df = yf.download(symbol, period="90d", interval="1d", progress=False)
            
            # --- THE HEARTBEAT CHECK ---
            if df.empty:
                print(f"⚠️ {symbol}: Download failed (Empty DataFrame)")
                continue
            
            # Flatten columns for new yfinance versions
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Calculate Indicators
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['SMA20'] = ta.sma(df['Close'], length=20)
            df['SMA50'] = ta.sma(df['Close'], length=50)
            df['VolAvg'] = ta.sma(df['Volume'], length=10)

            # Get the latest values
            current_price = df['Close'].iloc[-1]
            current_rsi = df['RSI'].iloc[-1]
            
            # This line will show up in your GitHub Action logs!
            print(f"📊 {symbol}: Price=${current_price:.2f} | RSI={current_rsi:.1f}")

            # Run your rules.py check
            if check_buy_signals(df):
                candidates.append(f"🔥 *{symbol}* @ ${float(current_price):.2f}")
                print(f"✅ MATCH FOUND: {symbol}")

        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")

    # Final Report
    if candidates:
        msg = "🎯 *Momentum Candidates Found:*\n\n" + "\n".join(candidates)
        send_telegram_msg(msg)
    else:
        send_telegram_msg(f"📭 Scan complete: No matches found in {len(tickers)} stocks.")

if __name__ == "__main__":
    run_scanner()
