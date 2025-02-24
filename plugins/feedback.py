from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from helper_func import check_user_ban
import asyncio

@Bot.on_message(filters.command('feedback') & filters.private)
@check_user_ban
async def feedback(client: Bot, message: Message):
    try:
        # Add small delay to prevent spam
        await asyncio.sleep(0.5)
        await message.reply_text(
            "<b>📬 For any feedback or support, please contact:</b>\n"
            "<b>👤 Admin:</b> @Anime106_Request_bot",
            quote=True
        )
    except Exception as e:
        print(f"Feedback command error: {e}")
        try:
            await message.reply_text("⚠️ An error occurred. Please try again later.")
        except:
            pass 