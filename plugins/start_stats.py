from pyrogram import filters
from config import ADMINS
from bot import Bot
from plugins.user_start_log import get_start_stats  # ✅ Import function
import asyncio

@Bot.on_message(filters.command("startstats"))
async def stats_handler(client, message):
    if message.from_user.id not in ADMINS:
        await client.send_message(message.chat.id, "🚫 You're not allowed.")
        return

    stats = get_start_stats()
    msg_lines = ["📊 /start Usage (IST):"]
    for day, count in stats.items():
        msg_lines.append(f"- {day}: {count} times")
    msg = "\n".join(msg_lines)

    await client.send_message(message.chat.id, msg)

    
    await asyncio.sleep(600)
    try:
        await stats.delete()
    except:
            pass
