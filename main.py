import asyncio
from data_fetcher import get_enriched_data
from strategies.strategy_runner import run_all_strategies
from notifier import send_scan_report
from datetime import datetime, timezone
from save_results import save_signals

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
                signal["target_1"] = signal.get("target_1", signal["price"] * 1.05)
                signal["stop_loss"] = signal.get("stop_loss", signal["price"] * 0.975)
                signal["risk"] = signal.get("risk", "UNK")
            
                matches.append(signal)
            
                print(f"MATCH FOUND: {symbol} - {signal['strategy']}")
        else:
            print(f"➖ {symbol}: Scanned")

    scan_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    save_signals(
        signals=matches,
        source="LIVE",
        scan_timestamp=scan_timestamp
    )
    await send_scan_report(matches, len(tickers))


if __name__ == "__main__":
    asyncio.run(main())
