from bot import Bot
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pyrogram import filters
from config import ADMINS, BOT_STATS_TEXT, USER_REPLY_TEXT, PICS, REACTIONS
from datetime import datetime
from helper_func import get_readable_time
import random
import asyncio
from collections import defaultdict
from time import time
from typing import Dict, Set, Optional, Union
import weakref

# Constants
ANIMATION_INTERVAL = 0.3
REFRESH_COOLDOWN = 5  # seconds between refreshes
DEFAULT_DELETE_DELAY = 600  # 10 minutes

# Add to imports
from collections import defaultdict
from time import time

# Add before callback handler
refresh_timestamps = defaultdict(float)

# Add after constants
active_messages: Dict[int, Set[int]] = defaultdict(set)  # user_id -> set of message_ids

async def edit_message_with_photo(
    message: Message,
    photo: Union[str, bytes],
    caption: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None
) -> Optional[Message]:
    """
    Edit a message with a new photo while preserving the message ID.
    
    Args:
        message: The message to edit
        photo: The new photo (file_id or URL)
        caption: The new caption
        reply_markup: Optional inline keyboard markup
        
    Returns:
        The edited message or None if failed
    """
    for attempt in range(3):  # Try up to 3 times
        try:
            if getattr(message, 'photo', None):
                return await message.edit_media(
                    media=InputMediaPhoto(photo, caption=caption, has_spoiler=True),
                    reply_markup=reply_markup
                )
            await message.delete()
            return await message.reply_photo(
                photo=random.choice(PICS),
                caption=caption,
                reply_markup=reply_markup,
                has_spoiler=True
            )
        except Exception as e:
            if attempt == 2:  # Last attempt
                print(f"Final error in edit_message_with_photo: {e}")
                # Try one last time with a fresh message
                try:
                    await message.delete()
                    return await message.reply_photo(
                        photo=random.choice(PICS),
                        caption=caption,
                        reply_markup=reply_markup,
                        has_spoiler=True
                    )
                except Exception as final_e:
                    print(f"Fatal error in photo send: {final_e}")
                    return None
            await asyncio.sleep(0.5)  # Wait before retry

@Bot.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(bot: Bot, message: Message):
    try:
        # Add reaction to command
        try:
            await message.react(emoji=random.choice(REACTIONS), big=True)
        except:
            pass

        # Send initial status message with photo
        status_msg = await message.reply_photo(
            photo=random.choice(PICS),
            caption="<i>Processing stats...</i>",
            has_spoiler=True
        )

        # Calculate uptime
        now = datetime.now()
        delta = now - bot.uptime
        time = get_readable_time(delta.seconds)

        # Create stats message with buttons
        buttons = [
            [InlineKeyboardButton("♻️ Refresh", callback_data="refresh_stats")],
            [InlineKeyboardButton("❌ Close", callback_data="close_stats")]
        ]

        # Update status message with stats
        await edit_message_with_photo(
            status_msg,
            photo=random.choice(PICS),
            caption=BOT_STATS_TEXT.format(uptime=time),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        print(f"Error in stats command: {e}")
        await message.reply_text("❌ An error occurred while fetching stats.")

@Bot.on_callback_query(filters.regex('^(refresh_stats|close_stats|close)$'))
async def callback_handler(bot: Bot, callback_query):
    try:
        if callback_query.data == "close" or callback_query.data == "close_stats":
            await callback_query.message.delete()
            
        elif callback_query.data == "refresh_stats":
            # Check cooldown
            user_id = callback_query.from_user.id
            last_refresh = refresh_timestamps[user_id]
            if time() - last_refresh < REFRESH_COOLDOWN:
                await callback_query.answer(
                    f"Please wait {int(REFRESH_COOLDOWN - (time() - last_refresh))}s before refreshing again!",
                    show_alert=True
                )
                return
                
            refresh_timestamps[user_id] = time()
            
            # Calculate new uptime
            now = datetime.now()
            delta = now - bot.uptime
            time = get_readable_time(delta.seconds)
            
            # Update message with new stats
            await edit_message_with_photo(
                callback_query.message,
                photo=random.choice(PICS),
                caption=BOT_STATS_TEXT.format(uptime=time),
                reply_markup=callback_query.message.reply_markup
            )
            await callback_query.answer("Stats refreshed!")
            
    except Exception as e:
        print(f"Error in callback handler: {e}")
        await callback_query.answer("Error processing request!", show_alert=True)

@Bot.on_message(filters.private & filters.incoming)
async def useless(_,message: Message):
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
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ Close", callback_data="close")
                ]]),
                has_spoiler=True
            )
        except Exception as e:
            print(f"Error in useless handler: {e}")

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
