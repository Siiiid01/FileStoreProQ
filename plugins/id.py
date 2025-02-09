from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import random
from bot import Bot
from config import PICS  # Ensure PICS is correctly imported

@Bot.on_message(filters.command("id") & filters.private)
async def showid(client, message: Message):
    try:
        await message.delete()
    except:
        pass  # Ignore errors if the bot cannot delete the message

    user = message.from_user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name or "N/A"
    username = f"@{user.username}" if user.username else "N/A"
    language = user.language_code if user.language_code else "N/A"
    
    # Fetch additional user info
    chat = await client.get_chat(user_id)
    about = chat.bio or "N/A"
    bot_lang_code = client.me.language_code if client.me.language_code else "N/A"

    # All info in one message
    info_text = (
        f"<b><blockquote><i>🔥 User Information</i></blockquote></b>\n\n"
        f"<b><blockquote>🆔 User ID: <code>{user_id}</code>\n"
        f"📛 First Name: <code>{first_name}</code>\n"
        f"📝 Last Name: <code>{last_name}</code>\n"
        f"🔗 Username: <code>{username}</code>\n"
        f"🌍 Language: <code>{language}</code>\n"
        f"📝 Bio: <code>{about}</code>\n"
        f"<b><blockquote>🤖 Bot Language: <code>{bot_lang_code}</code></b></blockquote>\n\n"
        f"</b></blockquote><i>👑 Bot Owner: @Anime106_Request_Bot</i></b></blockquote>"
    )
    
    # Create button
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("• Close •", callback_data="close")
    ]])

    # Send message with all info
    bot_msg = await message.reply_photo(
        photo=random.choice(PICS),
        caption=info_text,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML
    )

    await bot_msg.react("🔥")

@Bot.on_callback_query(filters.regex("^close$"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()
