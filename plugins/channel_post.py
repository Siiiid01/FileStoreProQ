import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode, check_user_ban

@Bot.on_message(
    filters.private 
    & filters.user(ADMINS) 
    & ~filters.command([
        "start", "id", "users", "broadcast", "batch", "genlink", "stats", "telegraph", "alive", "ping", "stickerid", "errors", "ban", "unban", "feedback", "restart", "startstats"
    ])
)
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...!", quote = True)
    try:
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ..!\n\n<blockquote>ᴛʀʏ ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ @Anime106_Request_bot ✨</blockquote>")
        return
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("• ꜱʜᴀʀᴇ ᴜʀʟ •", url=f'https://telegram.me/share/url?url={link}')]])

    await reply_text.edit(f"<b><i>​• ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ​</i></b>\n\n{link}",reply_markup=reply_markup, disable_web_page_preview = True)

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)
