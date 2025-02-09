from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import random 
from bot import Bot
from config import PICS  # Ensure PICS is correctly imported

# NO_PROFILE_PHOTO = "https://i.ibb.co/Mx2JYfrV/Shawn-Levy.jpg"  # Default photo URL

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
    about = (await client.get_chat(user_id)).bio or "N/A"
    join_date = (await client.get_chat(user_id)).dc_id or "Unknown"
    bot_lang_code = client.me.language_code if client.me.language_code else "N/A"

    response_text = (
        f"<blockquote>🔥 User Info:\n"
        f"🆔 User ID: `{user_id}`\n"
        f"📛 First Name: `{first_name}`\n"
        f"📝 Last Name: `{last_name}`\n"
        f"🔗 Username: `{username}`\n"
        f"🌍 Language: `{language}`</blockquote>\n\n"
        f"<blockquote>🔹 More Info:\n"
        f"📷 Profile Picture: Default (no fetching)\n"
        f"📝 Bio: `{about}`\n"
        f"📅 Joined Telegram: `{join_date}`\n"
        f"🤖 Bot Language Code: `{bot_lang_code}`\n\n"
        f"👑 Bot Owner: @Anime106_Request_Bot </blockquote>"
    )
    
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("• Close •", callback_data="close")
    ]])

    # Since there's no profile photo fetching, we can use a default photo
    bot_msg = await message.reply_photo(
        caption=response_text,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.MARKDOWN
    )
    
    await bot_msg.react("🔥")

@Bot.on_callback_query(filters.regex("^close"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()
