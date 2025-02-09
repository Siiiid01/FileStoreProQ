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
        f"<b>🔥 User Info:</b>\n\n"
        f"🆔 User ID: <code>{user_id}</code>\n"
        f"📛 First Name: <code>{first_name}</code>\n"
        f"📝 Last Name: <code>{last_name}</code>\n"
        f"🔗 Username: <code>{username}</code>"
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
        parse_mode=enums.ParseMode.HTML
    )

    await bot_msg.react("🔥")

@Bot.on_callback_query(filters.regex("^more_info$"))
async def more_info_callback(client, callback_query: CallbackQuery):
    user = callback_query.from_user
    user_id = user.id
    
    # Fetch additional user info
    language = user.language_code if user.language_code else "N/A"
    chat = await client.get_chat(user_id)
    about = chat.bio or "N/A"
    bot_lang_code = client.me.language_code if client.me.language_code else "N/A"

    # Basic info
    basic_info = (
        f"<b>🔥 User Info:</b>\n\n"
        f"🆔 User ID: <code>{user_id}</code>\n"
        f"📛 First Name: <code>{user.first_name}</code>\n"
        f"📝 Last Name: <code>{user.last_name or 'N/A'}</code>\n"
        f"🔗 Username: <code>{'@' + user.username if user.username else 'N/A'}</code>"
    )

    # Additional info
    additional_info = (
        f"\n\n<b>🔹 More Info:</b>\n\n"
        f"🌍 Language: <code>{language}</code>\n"
        f"📝 Bio: <code>{about}</code>\n"
        f"🤖 Bot Language Code: <code>{bot_lang_code}</code>\n\n"
        f"👑 Bot Owner: @Anime106_Request_Bot"
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
            parse_mode=enums.ParseMode.HTML
        )
        await callback_query.answer("Showing more information!")
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)

@Bot.on_callback_query(filters.regex("^close$"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()
