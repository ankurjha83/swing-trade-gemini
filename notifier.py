import os
import telegram
from collections import defaultdict

from news_sentiment import get_stock_news_sentiment


BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def format_signal(signal):
    ticker = signal["ticker"]
    news = get_stock_news_sentiment(ticker, max_items=3)

    message = (
        f"✅ *{ticker}*\n"
        f"Entry: `${signal['price']:.2f}`\n"
        f"Target +5%: `${signal['target_1']:.2f}`\n"
        f"Stop: `${signal['stop_loss']:.2f}`\n"
        f"Risk: `{signal['risk']}`\n"
        f"Sentiment: `{news['sentiment']}`\n"
        f"Reason: {signal['reason']}"
    )

    if news["headlines"]:
        message += "\nLatest News:"
        for headline in news["headlines"]:
            message += f"\n- {headline}"

    return message


async def send_scan_report(matches, total_scanned):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing.")
        return

    bot = telegram.Bot(token=BOT_TOKEN)

    if matches:
        grouped = defaultdict(list)

        for signal in matches:
            grouped[signal["strategy"]].append(signal)

        message_parts = [
            f"🔥 *SWING ALERT* ({len(matches)} found)",
            "━━━━━━━━━━━━━━━━━━"
        ]

        for strategy, signals in grouped.items():
            message_parts.append(f"📌 *{strategy}* ({len(signals)})")

            for signal in signals:
                message_parts.append(format_signal(signal))

        message_parts.append(f"📊 Total Scanned: `{total_scanned}`")

        message = "\n\n".join(message_parts)

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
