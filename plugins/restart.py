import os
import sys
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from config import ADMINS
from datetime import datetime
from helper_func import check_user_ban

@Bot.on_message(filters.command("restart") & filters.user(ADMINS))
@check_user_ban
async def restart_bot(client: Bot, message: Message):
    try:
        # Send restart message
        msg = await message.reply_text(
            "<b>🔄 Restarting bot...</b>\n\n"
            "<i>This will take a few seconds.</i>"
        )
        
        # Log restart time
        with open("restart.txt", "w") as f:
            f.write(f"{msg.chat.id}\n{msg.id}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        # Send notification to owner
        try:
            await client.send_message(
                chat_id=ADMINS[0],  # Send to first admin
                text=f"<b>🔄 Bot is restarting...</b>\n"
                     f"<b>Initiated by:</b> {message.from_user.mention}\n"
                     f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        except:
            pass
            
        # Restart the bot
        os.execl(sys.executable, sys.executable, "-m", "bot")
        
    except Exception as e:
        await message.reply_text(f"<b>❌ Error in restart:</b>\n<code>{str(e)}</code>") 