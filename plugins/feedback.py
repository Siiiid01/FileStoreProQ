from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
import asyncio

@Bot.on_message(filters.command('feedback') & filters.private)
async def feedback_handler(bot: Bot, message: Message):
    try:
        # Add small delay to prevent spam
        await asyncio.sleep(0.5)
        await message.reply_text(
            "<b>卐 For any feedback or support, please contact:</b>\n"
            "<b><i> Aᴅᴍɪɴ:</b> @Anime106_Request_bot</i></b>",
            quote=True
        )
    except Exception as e:
        print(f"Feedback command error: {e}")
        try:
            await message.reply_text("• Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
        except:
            pass 