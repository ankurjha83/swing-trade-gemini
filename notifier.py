import os
import telegram
from collections import defaultdict

from news_sentiment import get_stock_news_sentiment


BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MAX_TELEGRAM_LENGTH = 3500


def format_signal(signal):
    ticker = signal["ticker"]
    news = get_stock_news_sentiment(ticker, max_items=2)

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
        message += "\nNews:"
        for headline in news["headlines"][:2]:
            message += f"\n- {headline[:180]}"

    return message


def build_messages(matches, total_scanned):
    if not matches:
        return [
            (
                f"🟢 *System Status: Active*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"Scanned `{total_scanned}` stocks.\n"
                f"⚖️ Result: No strategy signals detected.\n"
                f"✅ Engine: Multi-strategy swing scanner"
            )
        ]

    grouped = defaultdict(list)

    for signal in matches:
        grouped[signal["strategy"]].append(signal)

    messages = []
    current_message = (
        f"🔥 *SWING ALERT* ({len(matches)} found)\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    for strategy, signals in grouped.items():
        section_header = f"\n\n📌 *{strategy}* ({len(signals)})"

        if len(current_message) + len(section_header) > MAX_TELEGRAM_LENGTH:
            messages.append(current_message)
            current_message = section_header.strip()
        else:
            current_message += section_header

        for signal in signals:
            block = "\n\n" + format_signal(signal)

            if len(current_message) + len(block) > MAX_TELEGRAM_LENGTH:
                messages.append(current_message)
                current_message = f"📌 *{strategy}* continued\n" + format_signal(signal)
            else:
                current_message += block

    footer = f"\n\n📊 Total Scanned: `{total_scanned}`"

    if len(current_message) + len(footer) > MAX_TELEGRAM_LENGTH:
        messages.append(current_message)
        messages.append(footer.strip())
    else:
        current_message += footer
        messages.append(current_message)

    return messages


async def send_scan_report(matches, total_scanned):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing.")
        return

    bot = telegram.Bot(token=BOT_TOKEN)
    messages = build_messages(matches, total_scanned)

    try:
        for message in messages:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode="Markdown"
            )

        print(f"Telegram notification sent. Messages: {len(messages)}")

    except Exception as e:
        print(f"Telegram send failed: {e}")
