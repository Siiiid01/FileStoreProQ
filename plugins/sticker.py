from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import random
from config import PICS  # Assuming PICS is imported from your config file

@Client.on_message(filters.command("stickerid") & filters.private)
async def stickerid(bot, message: Message):
    try:
        # Delete the command message
        await message.delete()

        # Send an initial "Please wait..." message
        welcome_msg = await message.reply_photo(
            photo=random.choice(PICS),
            caption="⏳ Please wait...",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Close", callback_data="close_sticker")]
            ])
        )

        # Prompt the user to send a sticker
        s_msg = await bot.ask(chat_id=message.from_user.id, text="Now send me your sticker.")

        # Check if the message contains a sticker
        if s_msg.sticker:
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

            # Create buttons for checking another sticker or closing
            buttons = [
                [InlineKeyboardButton("🔄 Check Another", callback_data="check_another")],
                [InlineKeyboardButton("❌ Close", callback_data="close_sticker")]
            ]

            # Edit the welcome message with the sticker info
            await welcome_msg.edit_caption(
                info_text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        else:
            await welcome_msg.edit_caption(
                "Oops! This isn't a sticker. Please send a sticker file.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ Close", callback_data="close_sticker")
                ]])
            )

    except Exception as e:
        print(f"Error in stickerid: {e}")
        await message.reply_text("An error occurred. Please try again later.")


# Callback handler for buttons
@Client.on_callback_query(filters.regex('^(close_sticker|check_another)$'))
async def sticker_callback(bot, callback_query):
    data = callback_query.data

    if data == "close_sticker":
        await callback_query.message.delete()

    elif data == "check_another":
        await callback_query.message.delete()
        # Trigger the sticker command again
        await bot.send_message(
            callback_query.message.chat.id,
            "/stickerid",
            disable_notification=True
        )