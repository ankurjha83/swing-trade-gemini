import os
import asyncio
from telegram import Bot
from data_fetcher import get_enriched_data
from rules import check_buy_signals

# GitHub Secrets
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_notification(text):
    if TOKEN and CHAT_ID:
        bot = Bot(TOKEN)
        await bot.send_message(CHAT_ID, text, parse_mode="Markdown")

async def main():
    with open("tickers.txt", "r") as f:
        tickers = [l.strip().upper() for l in f if l.strip() and not l.startswith("#")]

    print(f"🚀 Scanning {len(tickers)} stocks...")
    matches = []

    for symbol in tickers:
        df = get_enriched_data(symbol)
        
        # This calls your rules.py file automatically
        if df is not None and check_buy_signals(df):
            price = df['Close'].iloc[-1]
            matches.append(f"🎯 *{symbol}* Breakout @ ${price:.2f}")
            print(f"✅ MATCH: {symbol}")
        else:
            print(f"➖ {symbol}: No Signal")

    if matches:
        await send_notification("🔥 *NEW MOMENTUM SIGNALS:*\n\n" + "\n".join(matches))
    else:
        print("📭 Scan complete. No matches found.")

if __name__ == "__main__":
    asyncio.run(main())
