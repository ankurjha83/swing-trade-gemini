import os
import telegram


BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def send_scan_report(matches, total_scanned):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing.")
        return

    bot = telegram.Bot(token=BOT_TOKEN)

    if matches:
        header = f"🔥 *SWING ALERT* ({len(matches)} found)\n"
        separator = "━━━━━━━━━━━━━━━━━━\n"

        message = (
            header
            + separator
            + "\n\n".join(matches)
            + f"\n\n📊 Total Scanned: `{total_scanned}`"
        )

    else:
        message = (
            f"🟢 *System Status: Active*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Scanned `{total_scanned}` stocks.\n"
            f"⚖️ Result: No strategy signals detected.\n"
            f"✅ Engine: Multi-strategy swing scanner"
        )

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="Markdown"
        )
        print("Telegram notification sent.")

    except Exception as e:
        print(f"Telegram send failed: {e}")
