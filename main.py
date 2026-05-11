import os
import asyncio
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from telegram import Bot
from rules import check_buy_signals

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TICKERS_FILE = "tickers.txt"

async def send_telegram_msg(message):
    """Sends a formatted message to your Telegram channel."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials missing. Skipping message.")
        return
    bot = Bot(token=TELEGRAM_TOKEN)
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

def load_tickers():
    """Reads the tickers.txt file and returns a clean list of symbols."""
    if not os.path.exists(TICKERS_FILE):
        print(f"❌ Error: {TICKERS_FILE} not found!")
        return []
    with open(TICKERS_FILE, "r") as f:
        return [line.strip().upper() for line in f if line.strip() and not line.startswith("#")]

async def run_scanner():
    tickers = load_tickers()
    print(f"🚀 Starting Advanced Scan for {len(tickers)} stocks...")
    
    candidates = []
    
    for symbol in tickers:
        try:
            # 1. Download Data (150d period gives indicators enough 'runway' to calculate)
            df = yf.download(symbol, period="150d", interval="1d", progress=False)
            
            if df.empty or len(df) < 50:
                print(f"⚠️ {symbol}: Skipping (Insufficient Data)")
                continue

            # Flatten MultiIndex columns if necessary (common in newer yfinance versions)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # 2. CALCULATE ADVANCED INDICATORS
            # Bollinger Bands
            bbands = df.ta.bbands(length=20, std=2)
            df['BBU'] = bbands['BBU_20_2.0']
            df['BBL'] = bbands['BBL_20_2.0']
            
            # Trend & Momentum
            df['RSI'] = df.ta.rsi(length=14)
            df['ATR'] = df.ta.atr(length=14)
            
            # ADX (Average Directional Index)
            adx_data = df.ta.adx(length=14)
            df['ADX'] = adx_data['ADX_14']
            
            # MACD
            macd_data = df.ta.macd()
            df['MACD'] = macd_data['MACD_12_26_9']
            
            # Volume Moving Average (20-day)
            df['VolAvg'] = df.ta.sma(df['Volume'], length=20)

            # 3. RUN RULES ENGINE
            if check_buy_signals(df):
                price = df['Close'].iloc[-1]
                rsi = df['RSI'].iloc[-1]
                candidates.append(f"🎯 *{symbol}* Breakout!\n💰 Price: ${price:.2f}\n📈 RSI: {rsi:.1f}")
                print(f"✅ MATCH FOUND: {symbol}")
            else:
                # Debug line to see what's happening in GitHub logs
                last = df.iloc[-1]
                print(f"📊 {symbol}: ${last['Close']:.2f} | RSI: {last['RSI']:.1f} | ADX: {last['ADX']:.1f}")

        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")

    # 4. FINAL REPORTING
    if candidates:
        summary = "🔥 *MOMENTUM ALERTS FOUND* 🔥\n\n" + "\n\n".join(candidates)
        await send_telegram_msg(summary)
    else:
        print("📭 Scan complete. No stocks met the multi-factor criteria.")

if __name__ == "__main__":
    asyncio.run(run_scanner())
