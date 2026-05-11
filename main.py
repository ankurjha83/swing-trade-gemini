import os
import asyncio
from telegram import Bot
from data_fetcher import get_enriched_data
from rules import check_buy_signals

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_msg(text):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        await Bot(TELEGRAM_TOKEN).send_message(TELEGRAM_CHAT_ID, text, parse_mode="Markdown")

def load_tickers():
    with open("tickers.txt", "r") as f:
        return [l.strip().upper() for l in f if l.strip() and not l.startswith("#")]

async def main():
    tickers = load_tickers()
    print(f"🚀 Scanning {len(tickers)} symbols...")
    matches = []

    for symbol in tickers:
        df = get_enriched_data(symbol)
        if df is not None and check_buy_signals(df):
            price = df['Close'].iloc[-1]
            matches.append(f"🎯 *{symbol}* Breakout @ ${price:.2f}")
            print(f"✅ MATCH: {symbol}")
        else:
            print(f"➖ {symbol}: No signal")

    if matches:
        await send_msg("🔥 *NEW SIGNALS:*\n\n" + "\n".join(matches))

if __name__ == "__main__":
    asyncio.run(main())
