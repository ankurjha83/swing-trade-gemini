import asyncio
from data_fetcher import get_enriched_data
from rules import check_buy_signals
from notifier import send_scan_report

def load_tickers():
    with open("tickers.txt", "r") as f:
        return [l.strip().upper() for l in f if l.strip() and not l.startswith("#")]

async def main():
    tickers = load_tickers()
    print(f"🚀 Initializing scan for {len(tickers)} stocks...")
    
    matches = []

    for symbol in tickers:
        df = get_enriched_data(symbol)
        
        if df is not None and check_buy_signals(df):
            price = df['Close'].iloc[-1]
            # Create a string representation of the match
            matches.append(f"✅ *{symbol}*\n💰 Price: ${price:.2f}\n📈 Setup: Squeeze Breakout")
            print(f"🔥 MATCH FOUND: {symbol}")
        else:
            # Silent logging for non-matches
            print(f"➖ {symbol}: Scanned")

    # Hand off the results to the decoupled notifier
    await send_scan_report(matches, len(tickers))

if __name__ == "__main__":
    asyncio.run(main())
