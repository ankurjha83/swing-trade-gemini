from strategies.strategy_runner import run_all_strategies


def check_buy_signals(df):
    signals = run_all_strategies("UNKNOWN", df)
    return len(signals) > 0
