import sys
import os
import yfinance as yf
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_fetcher import add_indicators
from strategies.strategy_runner import run_all_strategies


# ============================================
# CONFIG
# ============================================

import os

SCAN_DATE = os.getenv("SCAN_DATE", "2026-05-15")
SCAN_TIME = os.getenv("SCAN_TIME", "15:30")

TARGET_TIMESTAMP = f"{SCAN_DATE} {SCAN_TIME}"


# ============================================
# LOAD TICKERS
# ============================================

with open("tickers.txt", "r") as f:
    TICKERS = [
        line.strip()
        for line in f.readlines()
        if line.strip() and not line.startswith("#")
    ]


# ============================================
# RUN HISTORICAL SCAN
# ============================================

def run_historical_scan(ticker):

    try:
        print(f"Scanning {ticker}")

        df = yf.download(
            ticker,
            period="59d",
            interval="15m",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return []

        df = add_indicators(df)

        df.index = pd.to_datetime(df.index)

        historical_df = df[
            df.index <= TARGET_TIMESTAMP
        ]

        if len(historical_df) < 80:
            return []

        signals = run_all_strategies(
            ticker,
            historical_df
        )

        return signals

    except Exception as e:
        print(f"Error scanning {ticker}: {e}")
        return []


# ============================================
# MAIN
# ============================================

all_signals = []

print(f"\n========== HISTORICAL SCAN ==========")
print(f"Timestamp: {TARGET_TIMESTAMP}\n")


for ticker in TICKERS:

    signals = run_historical_scan(ticker)

    if signals:

        for signal in signals:

            all_signals.append(signal)

            print(
                f"{ticker} | "
                f"{signal['strategy']} | "
                f"${signal['price']:.2f}"
            )


print("\n========== SUMMARY ==========")

print(f"Total Signals Found: {len(all_signals)}")
