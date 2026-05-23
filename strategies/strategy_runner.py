from strategies import early_trend, devalued_quality

ENABLED_STRATEGIES = [
    early_trend,
    devalued_quality,
]


def run_all_strategies(ticker, df):
    signals = []

    for strategy in ENABLED_STRATEGIES:
        try:
            result = strategy.check(ticker, df)

            if result:
                signals.append(result)

        except Exception as e:
            print(f"❌ Strategy error for {ticker} in {strategy.__name__}: {e}")

    return signals
