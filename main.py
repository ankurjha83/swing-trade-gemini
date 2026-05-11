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
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown"
    requests.get(url)

def get_sp500_tickers():
    """Pulls current S&P 500 tickers from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    # Wikipedia blocks simple bots, so we add a 'User-Agent' header
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    # Now we use 'pd' (it will work because it's imported at the top!)
    tables = pd.read_html(response.text)
    df = tables[0]
    
    # Standardize symbols (yfinance likes '-' instead of '.')
    tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
    return tickers

def run_scanner():
    print("🔄 Starting S&P 500 Scan...")
    tickers = get_sp500_tickers()
    candidates = []

    # Let's just scan the first 50 to keep it fast for this test
    # Once it works, remove the [:50] to scan all 500
    for symbol in tickers[:50]: 
        try:
            df = yf.download(symbol, period="60d", interval="1d", progress=False)
            
            if df.empty or len(df) < 20: continue

            # Technical Indicators
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['SMA20'] = ta.sma(df['Close'], length=20)
            df['SMA50'] = ta.sma(df['Close'], length=50)
            df['VolAvg'] = ta.sma(df['Volume'], length=10)

            if check_buy_signals(df):
                price = df.iloc[-1]['Close']
                candidates.append(f"🚀 *{symbol}* @ ${price:.2f}")

        except Exception as e:
            print(f"Skipping {symbol}: {e}")

    # Final Notification
    if candidates:
        msg = "🎯 *Momentum Candidates Found:*\n\n" + "\n".join(candidates)
        send_telegram_msg(msg)
    else:
        send_telegram_msg("📭 Scan complete: No S&P 500 stocks met the criteria today.")

if __name__ == "__main__":
    run_scanner()
