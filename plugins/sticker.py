from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import random
from config import PICS  # Import PICS from config

# Welcome stickers - you can add more
WELCOME_STICKERS = [
    "CAACAgEAAxkBAAENwWNnqY0y0m9-EfNyiAPMqYilkaoGCQACVwQAApvNAAFGhwkqyn3jKmg2BA",
    # Add more sticker IDs here
]

@Client.on_message(filters.command(["stickerid", "sticker"]) & filters.private)  # No admin check, anyone can use
async def stickerid(bot, message: Message):
    try:
        # Delete the command message
        await message.delete()
        
        # Send welcome message with photo
        welcome_msg = await message.reply_photo(
            photo=random.choice(PICS),
            caption="<b>👋 Welcome to Sticker ID Finder!</b>\n\n"
                   "<b>Send me any sticker to get its ID and details.</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_sticker")]
            ])
        )
        
        # Send random welcome sticker
        await bot.send_sticker(
            chat_id=message.chat.id, 
            sticker=random.choice(WELCOME_STICKERS)
        )
        
        # Wait for user's sticker
        try:
            s_msg = await bot.wait_for_message(
                chat_id=message.chat.id,
                filters=filters.sticker,
                timeout=60  # 60 seconds timeout
            )
            
            if s_msg.sticker:
                # Get sticker details
                sticker = s_msg.sticker
                info_text = (
                    f"<b>🎯 Sticker Information</b>\n\n"
                    f"<b>🔖 File ID:</b>\n<code>{sticker.file_id}</code>\n\n"
                    f"<b>🎟️ Unique ID:</b>\n<code>{sticker.file_unique_id}</code>\n\n"
                    f"<b>📏 Dimensions:</b> {sticker.width}x{sticker.height}\n"
                    f"<b>📦 File Size:</b> {sticker.file_size} bytes\n"
                    f"<b>🎨 Animated:</b> {'Yes' if sticker.is_animated else 'No'}\n"
                    f"<b>🎭 Video:</b> {'Yes' if sticker.is_video else 'No'}"
                )
                
                # Create buttons
                buttons = [
                    [InlineKeyboardButton("🔄 Check Another", callback_data="check_another")],
                    [InlineKeyboardButton("❌ Close", callback_data="close_sticker")]
                ]
                
                # Edit welcome message with sticker info
                await welcome_msg.edit_photo(
                    photo=random.choice(PICS),
                    caption=info_text,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                
        except asyncio.TimeoutError:
            await welcome_msg.edit_photo(
                photo=random.choice(PICS),
                caption="⏳ Timeout! Please send /sticker to start again.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Try Again", callback_data="check_another")
                ]])
            )
            
    except FloodWait as e:
        await asyncio.sleep(e.x)
    except Exception as e:
        print(f"Error in stickerid: {e}")
        await message.reply_text("An error occurred. Please try again later.")

# Callback handler for buttons
@Client.on_callback_query(filters.regex('^(cancel_sticker|check_another|close_sticker)$'))
async def sticker_callback(bot, callback_query):
    data = callback_query.data
    
    if data == "cancel_sticker" or data == "close_sticker":
        await callback_query.message.delete()
    elif data == "check_another":
        await callback_query.message.delete()
        # Trigger sticker command again
        await bot.send_message(
            callback_query.message.chat.id,
            "/sticker",
            disable_notification=True
        )
