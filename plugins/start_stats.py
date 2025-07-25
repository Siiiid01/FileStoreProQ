from pyrogram import filters
from config import ADMINS
from bot import Bot
from plugins.user_start_log import get_start_stats  # ✅ Import function
import asyncio

@Bot.on_message(filters.command("startstats"))
async def startstats_handler(client, message):
    if message.from_user.id not in ADMINS:
        await client.send_message(message.chat.id, "🚫 You're not allowed.")
        return

    stats = get_start_stats()
    msg = "📊 `/start` Usage (IST):\n"
    for day, count in stats.items():
        msg += f"- {day}: {count} times\n"

    stats_msg = await client.send_message(message.chat.id, msg, parse_mode="Markdown")
    await asyncio.sleep(600)
    try:
        await stats_msg.delete()
    except:
            pass
