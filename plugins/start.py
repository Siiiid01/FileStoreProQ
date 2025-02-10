import asyncio
import random
import time
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import *
from helper_func import *
from database.database import *

FILE_AUTO_DELETE = TIME

@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    id = message.from_user.id

    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass

    # Reply to the user's command
    start_reply = await message.reply("🔥", quote=True)

    # Send a reaction emoji with big=True
    await client.send_reaction(
        chat_id=message.chat.id,
        message_id=message.id,
        emoji=random.choice(REACTIONS),
        big=True
    )

    # Choose a random start image
    start_photo = random.choice(START_PICS)

    # Define buttons with "More" on top
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 More", callback_data="refresh_start")],  # New button on top
        [
            InlineKeyboardButton("⚡️ About", callback_data="about"),
            InlineKeyboardButton("🍁 SeriesFlix", url="https://t.me/Team_Netflix/40")
        ]
    ])

    # Send the start photo message
    start_msg = await message.reply_photo(
        photo=start_photo,
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=reply_markup
    )

    # Auto-delete command and replies after 10 minutes
    await asyncio.sleep(600)
    await message.delete()
    await start_reply.delete()
    await start_msg.delete()


# Handle "More" button to refresh with a new random image
@Bot.on_callback_query(filters.regex("refresh_start"))
async def refresh_start(client: Client, callback_query):
    new_photo = random.choice(PICS)

    await callback_query.message.edit_media(
        media=new_photo,
        reply_markup=callback_query.message.reply_markup
    )


# Optimized Broadcast System
@Bot.on_message(filters.private & filters.command("broadcast") & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if not message.reply_to_message:
        error_msg = await message.reply("<code>Reply to a message to broadcast.</code>")
        await asyncio.sleep(8)
        return await error_msg.delete()

    users = await full_userbase()
    broadcast_msg = message.reply_to_message

    total, successful, blocked, deleted, failed = 0, 0, 0, 0, 0

    processing_msg = await message.reply("<i>Broadcasting...</i>")
    
    for chat_id in users:
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
            failed += 1
        total += 1

    status = f"""<b>📢 Broadcast Summary:

👥 Total Users: {total}
✅ Delivered: {successful}
🚫 Blocked: {blocked}
🗑️ Deleted Accounts: {deleted}
⚠️ Failed: {failed}</b>"""

    await processing_msg.edit(status)