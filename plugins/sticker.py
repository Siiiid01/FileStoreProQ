from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import random
from config import PICS  # Import PICS from config

# Welcome message animation steps
WAIT_ANIMATION = ["W", "Wa", "Wai", "Wait", "Wait🔥", "Wait🔥🔥"]

@Client.on_message(filters.command(["stickerid", "sticker"]) & filters.private)
async def stickerid(bot, message: Message):
    try:
        # Delete the command message
        await message.delete()

        # Send initial "Please wait..." message
        welcome_msg = await message.reply_photo(
            photo=random.choice(PICS),
            caption="⏳ W",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Close", callback_data="close_sticker")]
            ])
        )

        # Animate the "Wait🔥🔥" text
        for text in WAIT_ANIMATION:
            await asyncio.sleep(0.07)  # 70ms delay
            await welcome_msg.edit_caption(f"⏳ {text}")

        # Update the final welcome message
        await asyncio.sleep(1)  # Small delay before showing final text
        await welcome_msg.edit_caption(
            "<b>👋 Welcome to Sticker ID Finder!</b>\n\n"
            "<b>Send me any sticker to get its ID and details.</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Close", callback_data="close_sticker")]
            ])
        )

        # Auto-delete welcome message after 60 seconds
        asyncio.create_task(auto_delete(welcome_msg, 60))

        # Wait for user's sticker
        async with bot.listen(message.chat.id, filters.sticker, timeout=60) as listener:
            s_msg = await listener.get()

            if s_msg and s_msg.sticker:
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
                await welcome_msg.edit_caption(
                    info_text,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

    except asyncio.TimeoutError:
        # Timeout reached, update the message
        await welcome_msg.edit_caption(
            "⏳ Timeout! Please send /sticker to start again.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 Try Again", callback_data="check_another")
            ]])
        )

    except FloodWait as e:
        await asyncio.sleep(e.x)
    except Exception as e:
        print(f"Error in stickerid: {e}")
        await message.reply_text("An error occurred. Please try again later.")


# Auto-delete function for the welcome message after 60s
async def auto_delete(msg: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass


# Callback handler for buttons
@Client.on_callback_query(filters.regex('^(close_sticker|check_another)$'))
async def sticker_callback(bot, callback_query):
    data = callback_query.data

    if data == "close_sticker":
        await callback_query.message.delete()

    elif data == "check_another":
        await callback_query.message.delete()
        # Trigger sticker command again
        await bot.send_message(
            callback_query.message.chat.id,
            "/sticker",
            disable_notification=True
        )