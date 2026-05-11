import os
import asyncio
from telegram import Bot

# Configuration from Environment
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_scan_report(matches, total_scanned):
    """
    Decoupled notification function. 
    Edit this to change formatting or switch platforms (Telegram, ClickUp, etc.)
    """
    if not matches:
        # Optional: Send a 'No signals' update or just log it
        summary = f"📭 *Daily Scan Complete*\nNo matches found across {total_scanned} stocks."
        print(summary) 
        # await _deliver_telegram(summary) # Uncomment if you want 'No Signal' alerts
        return

    # --- FORMATTING LOGIC ---
    header = f"🚀 *MOMENTUM ALERT* ({len(matches)} signals found)\n"
    divider = "───────────────────\n"
    body = "\n\n".join(matches)
    footer = f"\n\n📊 Total Scanned: {total_scanned}"
    
    final_message = f"{header}{divider}{body}{footer}"

    # --- DELIVERY LOGIC ---
    await _deliver_telegram(final_message)

async def _deliver_telegram(text):
    """Private method to handle Telegram-specific delivery."""
    if TOKEN and CHAT_ID:
        try:
            bot = Bot(TOKEN)
            await bot.send_message(CHAT_ID, text, parse_mode="Markdown")
        except Exception as e:
            print(f"❌ Notification Delivery Error: {e}")
