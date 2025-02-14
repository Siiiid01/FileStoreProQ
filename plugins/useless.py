from bot import Bot
import bot
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pyrogram import Client, filters
from config import ADMINS, BOT_STATS_TEXT, USER_REPLY_TEXT, PICS, REACTIONS
from datetime import datetime
from helper_func import get_readable_time
import random
import asyncio
from collections import defaultdict
from time import time
from typing import Dict, Set, Optional, Union
import weakref
from plugins.start import EXEMPT_FROM_DELETE
from functools import lru_cache  # Use built-in lru_cache instead

# Constants
REFRESH_COOLDOWN = 5  # seconds between refreshes
DEFAULT_DELETE_DELAY = 600  # 10 minutes

# Add to imports
refresh_timestamps = defaultdict(float)

# Add before callback handler
active_messages = defaultdict(set)  # user_id -> set of message_ids

# Auto-respond to private messages with random image and user reply text
@Bot.on_message(filters.private & filters.incoming)
async def useless(_, message: Message):
    if USER_REPLY_TEXT:
        try:
            # Add reaction to message
            try:
                await message.react(emoji=random.choice(REACTIONS), big=True)
            except:
                pass
                
            await message.reply_photo(
                photo=random.choice(PICS),
                caption=USER_REPLY_TEXT,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close")]]),
                has_spoiler=True
            )
        except Exception as e:
            print(f"Error in useless handler: {e}")

# Close message or replied message
@Bot.on_message(filters.command('close') & filters.private)
async def close_message(bot: Bot, message: Message):
    try:
        # Add reaction to command
        try:
            await message.react(emoji=random.choice(REACTIONS), big=True)
        except:
            pass
            
        # If message is a reply, delete the replied message
        if message.reply_to_message:
            try:
                temp_msg = await message.reply_photo(
                    photo=random.choice(PICS),
                    caption="🗑️ Deleting messages...",
                    has_spoiler=True
                )
                await asyncio.sleep(1)  # Brief delay for visual feedback
                await message.reply_to_message.delete()
                await message.delete()
                await temp_msg.delete()
            except Exception as e:
                print(f"Error deleting replied message: {e}")
        else:
            await message.delete()
                
    except Exception as e:
        print(f"Error in close command: {e}")

# Callback for close button
@Bot.on_callback_query(filters.regex('^(close)$'))
async def callback_handler(bot: Bot, callback_query):
    try:
        if callback_query.data == "close":
            await callback_query.message.delete()
            
    except Exception as e:
        print(f"Error in callback handler: {e}")
        await callback_query.answer("Error processing request!", show_alert=True)

async def cleanup_old_messages(user_id: int, keep_latest: int = 5):
    """Cleanup old messages, keeping only the latest few"""
    if len(active_messages[user_id]) > keep_latest:
        messages_to_delete = sorted(list(active_messages[user_id]))[:-keep_latest]
        for msg_id in messages_to_delete:
            try:
                # You'll need to store Bot instance or pass it as parameter
                await bot.delete_messages(user_id, msg_id)
                active_messages[user_id].remove(msg_id)
            except Exception as e:
                print(f"Error cleaning up message {msg_id}: {e}")

async def schedule_message_deletion(message: Message, delay: int = DEFAULT_DELETE_DELAY):
    """Schedule a message for deletion after delay"""
    if not message or message.text in EXEMPT_FROM_DELETE:
        return
        
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        print(f"Error deleting scheduled message: {e}")
