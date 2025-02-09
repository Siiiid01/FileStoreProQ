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

    # Basic info message
    basic_info = (
        f"<blockquote>🔥 User Info:\n"
        f"🆔 User ID: `{user_id}`\n"
        f"📛 First Name: `{first_name}`\n"
        f"📝 Last Name: `{last_name}`\n"
        f"🔗 Username: `{username}`</blockquote>"
    )
    
    # Create buttons
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📑 For More", callback_data="more_info")],
        [InlineKeyboardButton("• Close •", callback_data="close")]
    ])

    # Send initial message with basic info
    bot_msg = await message.reply_photo(
        photo=random.choice(PICS),
        caption=basic_info,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.MARKDOWN
    )

    await bot_msg.react("🔥")

@Bot.on_callback_query(filters.regex("^more_info"))
async def more_info_callback(client, callback_query: CallbackQuery):
    user = callback_query.from_user
    user_id = user.id
    
    # Fetch additional user info
    language = user.language_code if user.language_code else "N/A"
    about = (await client.get_chat(user_id)).bio or "N/A"
    join_date = user.date if user.date else "Unknown"
    if join_date != "Unknown":
        join_date = join_date.strftime("%Y-%m-%d %H:%M:%S")
    bot_lang_code = client.me.language_code if client.me.language_code else "N/A"

    # Basic info (same as before)
    basic_info = (
        f"<blockquote>🔥 User Info:\n"
        f"🆔 User ID: `{user_id}`\n"
        f"📛 First Name: `{user.first_name}`\n"
        f"📝 Last Name: `{user.last_name or 'N/A'}`\n"
        f"🔗 Username: `{'@' + user.username if user.username else 'N/A'}`</blockquote>"
    )

    # Additional info
    additional_info = (
        f"\n<blockquote>🔹 More Info:\n"
        f"🌍 Language: `{language}`\n"
        f"📷 Profile Picture: Default (no fetching)\n"
        f"📝 Bio: `{about}`\n"
        f"📅 Joined Telegram: `{join_date}`\n"
        f"🤖 Bot Language Code: `{bot_lang_code}`\n\n"
        f"👑 Bot Owner: @Anime106_Request_Bot </blockquote>"
    )

    # Combined message
    full_message = basic_info + additional_info

    # Update message with close button only
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("• Close •", callback_data="close")
    ]])

    try:
        await callback_query.message.edit_caption(
            caption=full_message,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)

@Bot.on_callback_query(filters.regex("^close"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()
