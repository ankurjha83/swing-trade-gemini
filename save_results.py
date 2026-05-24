import csv
import os
from datetime import datetime, timezone


RESULTS_FILE = "results/signals.csv"

FIELDNAMES = [
    "run_timestamp",
    "source",
    "scan_timestamp",
    "ticker",
    "strategy",
    "entry",
    "target",
    "stop",
    "risk",
    "sentiment",
    "outcome",
    "exit_price",
    "pnl_pct",
    "notes",
]


def ensure_results_file_exists():
    os.makedirs("results", exist_ok=True)

    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            f.write("\n")


def save_signals(signals, source, scan_timestamp, sentiment_lookup=None):
    """
    Appends signal rows to results/signals.csv.

    source:
        LIVE or HISTORICAL

    scan_timestamp:
        Market timestamp being evaluated.

    sentiment_lookup:
        Optional dict:
        {
            "IONQ": "Neutral",
            "QBTS": "Positive"
        }
    """

    if not signals:
        return

    ensure_results_file_exists()

    run_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    rows = []

    for signal in signals:
        ticker = signal.get("ticker", "")
        price = signal.get("price", "")

        target = signal.get("target_1", price * 1.05 if price else "")
        stop = signal.get("stop_loss", price * 0.975 if price else "")

        sentiment = ""
        if sentiment_lookup:
            sentiment = sentiment_lookup.get(ticker, "")

        rows.append({
            "run_timestamp": run_timestamp,
            "source": source,
            "scan_timestamp": scan_timestamp,
            "ticker": ticker,
            "strategy": signal.get("strategy", ""),
            "entry": round(price, 2) if price else "",
            "target": round(target, 2) if target else "",
            "stop": round(stop, 2) if stop else "",
            "risk": signal.get("risk", ""),
            "sentiment": sentiment,
            "outcome": signal.get("outcome", ""),
            "exit_price": signal.get("exit_price", ""),
            "pnl_pct": signal.get("pnl_pct", ""),
            "notes": signal.get("reason", ""),
        })

    with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerows(rows)

    print(f"Saved {len(rows)} signals to {RESULTS_FILE}")
