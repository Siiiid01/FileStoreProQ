from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import asyncio 
from bot import Bot

ANIMATION_FRAMES = ["● ○ ○", "● ● ○", "● ● ●"]
ANIMATION_INTERVAL = 0.15  # 100ms
AUTO_DELETE_TIME = 600  # 10 minutes

async def show_loading_animation(message: Message):
    """Shows an animated loading message and deletes it after completion."""
    try:
        loading_msg = await message.reply("○ ○ ○")
        await message.delete()  # Delete the /stickerid command message
        
        for _ in range(2):  # Run animation twice
            for frame in ANIMATION_FRAMES:
                await asyncio.sleep(ANIMATION_INTERVAL)
                await loading_msg.edit(frame)
        
        await asyncio.sleep(ANIMATION_INTERVAL)
        await loading_msg.delete()  # Delete animation message
    except Exception as e:
        print(f"Error in animation: {e}")
    
@Bot.on_message(filters.command("stickerid") & filters.private)
async def stickerid(bot, message):
    """Handle /stickerid command with animation and sticker request."""
    await show_loading_animation(message)
    
    ask_msg = await bot.send_message(
        chat_id=message.from_user.id,
        text="• ɴᴏᴡ ꜱᴇɴᴅ ᴍᴇ ʏᴏᴜʀ ꜱᴛɪᴄᴋᴇʀ!"
    )
    
    try:
        s_msg = await bot.listen(message.chat.id, timeout=30)  # Wait for sticker
        if s_msg.sticker:
            info_text = (
                f"<blockquote expandable><b><i>🎯 Sticker Information</b></i>\n\n"
                f"<b><i>🔖 File ID:</b></i>\n`{s_msg.sticker.file_id}`\n\n"
                f"<b><i>🎟️ Unique ID:</b></i>\n`{s_msg.sticker.file_unique_id}`\n\n"
                f"<b><i>📏 Dimensions:</b></i> {s_msg.sticker.width}x{s_msg.sticker.height}\n"
                f"<b><i>📦 File Size:</b></i> {s_msg.sticker.file_size} bytes\n"
                f"<b><i>🎨 Animated:</b></i> {'Yes' if s_msg.sticker.is_animated else 'No'}\n"
                f"<b><i>🎭 Video:</b></i> {'Yes' if s_msg.sticker.is_video else 'No'}<blockquote>"
            )
            
            buttons = [[InlineKeyboardButton("• ᴄʟᴏꜱᴇ •", callback_data="close")]]
            await s_msg.reply_text(info_text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await s_msg.reply_text("<b><i>ᴏᴏᴘꜱ! ᴛʜᴀᴛ'ꜱ ɴᴏᴛ ᴀ ꜱᴛɪᴄᴋᴇʀ ꜰɪʟᴇ.</i></b>")
    except asyncio.TimeoutError:
        await ask_msg.edit("⏳<b><i>ᴛɪᴍᴇᴏᴜᴛ! ʏᴏᴜ ᴅɪᴅɴ'ᴛ ꜱᴇɴᴅ ᴀ ꜱᴛɪᴄᴋᴇʀ ɪɴ ᴛɪᴍᴇ.</i></b>")

@Bot.on_callback_query(filters.regex("^close_sticker$"))
async def close_callback(client, callback_query: CallbackQuery):
    try:
        await callback_query.message.delete()
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)

