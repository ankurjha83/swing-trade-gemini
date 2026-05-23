import importlib
import pkgutil
from strategies import __path__ as strategies_path


def load_strategies():
    loaded_strategies = []

    for module_info in pkgutil.iter_modules(strategies_path):
        module_name = module_info.name

        if module_name.startswith("_") or module_name == "strategy_runner":
            continue

        module = importlib.import_module(f"strategies.{module_name}")

        if hasattr(module, "check"):
            loaded_strategies.append(module)
        else:
            print(f"⚠️ Skipping strategies.{module_name}: no check() function found")

    return loaded_strategies


def run_all_strategies(ticker, df):
    signals = []
    strategies = load_strategies()

    for strategy in strategies:
        try:
            result = strategy.check(ticker, df)

            if result:
                signals.append(result)

        except Exception as e:
            print(f"❌ Strategy error for {ticker} in {strategy.__name__}: {e}")

    return signals
