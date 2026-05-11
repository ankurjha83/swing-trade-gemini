import os
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import requests
from rules import check_buy_signals

# GitHub Secrets
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TICKERS = [
    "ACHR", "AMD", "AMZN", "COHR", "CRWD", "IONQ", "META", "MSFT", "MSTR", 
    "MU", "NET", "NFLX", "NVDA", "NIO", "PLTR", "PSTG", "QBTS", "QCOM", "QUBT", 
    "RGTI", "SHOP", "SMCI", "TSLA", "TSM", "RKLB", "AAPL", "JOBY", "AVGO", 
    "MRVL", "ARM", "ANET", "PANW", "ASTS", "KTOS", "SNOW", "DDOG", "CCJ", 
    "GEV", "UBER", "APP"
]

def send_telegram_msg(message):
    if not TOKEN or not CHAT_ID:
        print("Missing Telegram Secrets.")
        return
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # Ensure CHAT_ID is handled as a string/integer correctly
    payload = {
        "chat_id": str(CHAT_ID).strip(),
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("🚀 Message sent successfully!")
        else:
            print(f"❌ Telegram Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def run_scanner():
    print(f"🚀 Starting scan for {len(TICKERS)} momentum stocks...")
    candidates = []

    for symbol in TICKERS:
        try:
            df = yf.download(symbol, period="90d", interval="1d", progress=False)
            if df.empty or len(df) < 50: continue

            # Flatten MultiIndex for new yfinance versions
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Technicals
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
        send_telegram_msg("📭 Scan complete: No momentum matches today.")

if __name__ == "__main__":
    run_scanner()
