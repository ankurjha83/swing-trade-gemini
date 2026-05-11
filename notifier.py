import os
import asyncio
from telegram import Bot

# Configuration from Environment
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_scan_report(matches, total_scanned):
    """
    Decoupled notification function. 
    Sends a report to Telegram regardless of whether matches were found.
    """
    
    # --- 1. CASE: NO SIGNALS DETECTED ---
    if not matches:
        summary = (
            f"📡 *System Status: Active*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔍 Scanned `{total_scanned}` stocks.\n"
            f"⚖️ Result: No breakout signals detected.\n"
            f"✅ Strategy: 15m Squeeze Hunter"
        )
        print(f"Log: Scan complete. {total_scanned} stocks checked. No matches.")
        
        # We now explicitly call the delivery method here
        await _deliver_telegram(summary)
        return

    # --- 2. CASE: MOMENTUM SIGNALS FOUND ---
    header = f"🔥 *MOMENTUM ALERT* ({len(matches)} found)\n"
    divider = "━━━━━━━━━━━━━━━━━━\n"
    body = "\n\n".join(matches)
    footer = f"\n\n📊 Total Scanned: {total_scanned}"
    
    final_message = f"{header}{divider}{body}{footer}"

    # --- DELIVERY LOGIC ---
    await _deliver_telegram(final_message)

async def _deliver_telegram(text):
    """Private method to handle Telegram-specific delivery."""
    if not TOKEN or not CHAT_ID:
        print("⚠️ Telegram Credentials missing. Check your Secrets.")
        return

    try:
        bot = Bot(TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")
    except Exception as e:
        print(f"❌ Notification Delivery Error: {e}")
