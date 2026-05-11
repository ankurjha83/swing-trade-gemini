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
    tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "AMD", "GOOGL", "META"] # Add or use a list puller
    candidates = []

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
        print("No matches found today.")

if __name__ == "__main__":
    run_scanner()