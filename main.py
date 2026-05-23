import asyncio
from data_fetcher import get_enriched_data
from strategies.strategy_runner import run_all_strategies
from notifier import send_scan_report


def load_tickers():
    with open("tickers.txt", "r") as f:
        return [l.strip().upper() for l in f if l.strip() and not l.startswith("#")]


async def main():
    tickers = load_tickers()
    print(f"Initializing scan for {len(tickers)} stocks...")

    matches = []

    for symbol in tickers:
        df = get_enriched_data(symbol)  # fetched once per ticker

        if df is None:
            print(f"⚠️ {symbol}: No data")
            continue

        signals = run_all_strategies(symbol, df)

        if signals:
            for signal in signals:
                matches.append(
                    f"✅ *{signal['ticker']}*\n"
                    f"Price: ${signal['price']:.2f}\n"
                    f"Strategy: {signal['strategy']}\n"
                    f"Reason: {signal['reason']}"
                )
                print(f" MATCH FOUND: {symbol} - {signal['strategy']}")
        else:
            print(f"➖ {symbol}: Scanned")

    await send_scan_report(matches, len(tickers))


if __name__ == "__main__":
    asyncio.run(main())
