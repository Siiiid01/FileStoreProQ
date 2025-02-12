import asyncio
import os
import random
import sys
import time
import string
import humanize
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import *
from helper_func import *
from database.database import *

# Cache frequently used values
CACHE_TIME = 3600  # 1 hour cache time
message_cache = {}

# File auto-delete time in seconds
FILE_AUTO_DELETE = TIME  # Example: 3600 seconds (1 hour)

LOADING_ANIMATION = ["○ ○ ○", "• ○ ○", "• • ○", "• • •"]

async def show_loading(client, message):
    """Show a quick loading animation, delete it, and then send the start message."""
    
    loading_msg = await message.reply("○ ○ ○")  # Initial loading message
    prev_frame = ""  # Track the last frame to avoid unnecessary edits

    for _ in range(2):  # Run animation for about 2 seconds
        for frame in LOADING_ANIMATION:
            if frame != prev_frame:  # Only update if the frame is different
                await loading_msg.edit(frame)
                prev_frame = frame
                await asyncio.sleep(0.4)  # Short delay for smooth animation

    await loading_msg.delete()  # Remove loading animation after completion

    # Now send the actual start message
    await send_start_message(client, message)  

async def send_start_message(client, message):
    """Send the /start message after the loading animation."""
    start_text = "🔥 Welcome to the Bot! How can I help you today?"
    await message.reply(start_text)


async def show_loading(client, message):
    """ Show a dynamic loading animation before sending a message. """
    loading_msg = await message.reply("○ ○ ○")
    for _ in range(4):
        for frame in LOADING_ANIMATION:
            await loading_msg.edit(frame)
            await asyncio.sleep(0.5)
    await loading_msg.delete()


@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    await show_loading(client, message)  # Show loading animation
    
    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⚡️ ᴀʙᴏᴜᴛ", callback_data="about")],
            [InlineKeyboardButton('🍁 sᴇʀɪᴇsғʟɪx', url='https://t.me/Team_Netflix/40')]
        ]
    )

    sent_message = await message.reply_photo(
        photo=random.choice(PICS),
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=reply_markup
    )

    # Make bot react to /start
    try:
        await client.send_reaction(message.chat.id, message.id, emoji="🔥", big=True)
    except:
        pass

    # Schedule deletion of the message after 10 minutes
    await asyncio.sleep(600)
    await message.delete()
    await sent_message.delete()


@Bot.on_message(filters.command("broadcast") & filters.private & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    """ Broadcast optimized for large user bases while keeping formatting intact. """
    if not message.reply_to_message:
        msg = await message.reply("<code>Reply to a message to broadcast.</code>")
        await asyncio.sleep(8)
        return await msg.delete()

    broadcast_msg = message.reply_to_message
    query = await full_userbase()
    total, successful, blocked, deleted, unsuccessful = 0, 0, 0, 0, 0

    pls_wait = await message.reply("<i>Broadcasting...</i>")
    for chat_id in query:
        try:
            await broadcast_msg.copy(chat_id)
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await broadcast_msg.copy(chat_id)
            successful += 1
        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1
        except:
            unsuccessful += 1
        total += 1

    status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

    return await pls_wait.edit(status)