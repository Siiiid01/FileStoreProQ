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

    # All info in one message with improved formatting
    info_text = (
        f"<blockquote><b>🔥 ᴜꜱᴇʀ ɪɴꜰᴏ</b></blockquote>\n\n"
        f"<blockquote expandable><b>"
        f"🆔 ᴜꜱᴇʀ ɪᴅ: <code>{user_id}</code>\n"
        f"📛 ꜰɪʀꜱᴛ ɴᴀᴍᴇ: <code>{first_name}</code>\n"
        f"📝 ʟᴀꜱᴛ ɴᴀᴍᴇ: <code>{last_name}</code>\n"
        f"🔗 ᴜꜱᴇʀɴᴀᴍᴇ: <code>{username}</code>\n"
        f"🌍 ʟᴀɴɢᴜᴀɢᴇ: <code>{language}</code>\n"
        f"📝 ʙɪᴏ: <code>{about}</code>\n"
        f"🤖 ʙᴏᴛ ʟᴀɴɢᴜᴀɢᴇ: <code>{bot_lang_code}</code></b></blockquote>\n\n"
        f"<blockquote><i>👑 ʙᴏᴛ ᴏᴡɴᴇʀ @Anime106_Request_Bot</i></blockquote>"
    )
    
    # Create button with improved style
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("• ᴄʟᴏꜱᴇ •", callback_data="close")
    ]])

    # Send message with all info
    try:
        bot_msg = await message.reply_photo(
            photo=random.choice(PICS),
            caption=info_text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )
        await bot_msg.react("🔥")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

@Bot.on_callback_query(filters.regex("^close$"))
async def close_callback(client, callback_query: CallbackQuery):
    try:
        await callback_query.message.delete()
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)
