import asyncio  # For async handling like sleep and task scheduling
import random  # For selecting random items (if needed)
from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime  # For calculating the bot's uptime
from config import *  # For getting BOT_STATS_TEXT and AUTO_DELETE_TIME
from helper_func import *  # For functions like get_readable_time
from database.database import *  # Keep this if you're querying the database for user info
import humanize  # If you're using it to format the uptime
from bot import Bot  # To access the bot client
from helper_func import check_user_ban  # Import check_user_ban function

# Animation constants
WAIT_ANIMATION_TEXT = "○ ○ ○"
ANIMATION_FRAMES = ["● ○ ○", "● ● ○", "● ● ●"]
ANIMATION_INTERVAL = 0.15

AUTO_DELETE_TIME = 600

async def show_loading_animation(message: Message):
    """Shows a loading animation and returns the message object"""
    loading_message = await message.reply_text(WAIT_ANIMATION_TEXT)
    
    for _ in range(2):  # Run animation 2 cycles
        for frame in ANIMATION_FRAMES:
            await asyncio.sleep(ANIMATION_INTERVAL)
            await loading_message.edit_text(frame)
    
    return loading_message

async def auto_delete_message(message: Message, seconds: int):
    """Delete a message after specified seconds"""
    await asyncio.sleep(seconds)
    try:
        await message.delete()
    except:
        pass

@Bot.on_message(filters.command('stats') & filters.private & filters.user(ADMINS))
@check_user_ban
async def stats(client: Bot, message: Message):
    try:
        # Get total users
        users = await full_userbase()
        total_users = len(users)
        
        # Calculate uptime
        current_time = datetime.now()
        uptime = current_time - client.start_time
        uptime_str = get_readable_time(uptime.total_seconds())
        
        # Send stats message
        stats_msg = await message.reply_text(
            f"<b>ღ Bᴏᴛ Sᴛᴀᴛɪsᴛɪᴄs</b>\n\n"
            f"<b>• Tᴏᴛᴀʟ Usᴇʀs:</b> <code>{total_users}</code>\n"
            f"<b>• Uᴘᴛɪᴍᴇ:</b> <code>{uptime_str}</code>"
        )
        
        # Auto-delete after 10 minutes
        await asyncio.sleep(600)
        try:
            await stats_msg.delete()
        except:
            pass
            
    except Exception as e:
        print(f"Stats command error: {e}")
