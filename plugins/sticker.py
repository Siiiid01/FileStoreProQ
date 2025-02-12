from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import random
from config import PICS
import asyncio

# Constants
WAIT_ANIMATION_TEXT = "○ ○ ○"
ANIMATION_FRAMES = ["● ○ ○", "● ● ○", "● ● ●"]
ANIMATION_INTERVAL = 0.2
AUTO_DELETE_TIME = 600  # 10 minutes

async def show_loading_animation(message: Message):
    """Shows an animated loading message"""
    loading_msg = await message.reply_photo(
        photo=random.choice(PICS),
        caption=WAIT_ANIMATION_TEXT,
        has_spoiler=True
    )
    
    for _ in range(2):  # Run animation 2 times
        for frame in ANIMATION_FRAMES:
            await asyncio.sleep(ANIMATION_INTERVAL)
            try:
                await loading_msg.edit_caption(frame)
            except Exception as e:
                print(f"Error in animation frame update: {e}")
        await asyncio.sleep(ANIMATION_INTERVAL)
        try:
            await loading_msg.edit_caption(WAIT_ANIMATION_TEXT)
        except Exception as e:
            print(f"Error in animation reset: {e}")
    
    return loading_msg

async def edit_message_with_photo(message: Message, photo, caption, reply_markup=None):
    """Helper function to edit message with photo while preserving message ID"""
    try:
        if getattr(message, 'photo', None):
            return await message.edit_media(
                media=InputMediaPhoto(photo, caption=caption, has_spoiler=True),
                reply_markup=reply_markup
            )
        await message.delete()
        return await message.reply_photo(
            photo=photo,
            caption=caption,
            reply_markup=reply_markup,
            has_spoiler=True
        )
    except Exception as e:
        print(f"Error in edit_message_with_photo: {e}")
        try:
            await message.delete()
            return await message.reply_photo(
                photo=photo,
                caption=caption,
                reply_markup=reply_markup,
                has_spoiler=True
            )
        except Exception as e:
            print(f"Error in fallback photo send: {e}")
            return None

@Client.on_message(filters.command('stickerid') & filters.private)
async def stickerid(bot: Client, message: Message):
    try:
        # Add reaction to command
        try:
            await message.react(emoji=random.choice(REACTIONS), big=True)
        except:
            pass

        # Show initial message
        await message.reply_photo(
            photo=random.choice(PICS),
            caption="📤 Please send me any sticker as a reply to this message to get its information...",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Cancel", callback_data="close_sticker")
            ]]),
            has_spoiler=True
        )
    except Exception as e:
        print(f"Error in stickerid: {e}")
        await message.reply("❌ An error occurred. Please try again.")

@Client.on_callback_query(filters.regex('^(close_sticker|check_another)$'))
async def sticker_callback(bot, callback_query):
    try:
        if callback_query.data == "close_sticker":
            await callback_query.message.delete()
        elif callback_query.data == "check_another":
            # Delete current message
            await callback_query.message.delete()
            # Start new sticker ID request
            new_msg = await bot.send_message(
                callback_query.message.chat.id,
                "/stickerid"
            )
            # Delete the command message after a short delay
            await asyncio.sleep(0.5)
            await new_msg.delete()
    except Exception as e:
        print(f"Error in sticker callback: {e}")

@Client.on_message(filters.private & filters.sticker & filters.reply)
async def process_sticker(client: Client, message: Message):
    """Handle sticker in response to stickerid command"""
    try:
        sticker = message.sticker
        info_text = (
            f"<b>🎯 Sticker Information</b>\n\n"
            f"<b>🔖 File ID:</b>\n<code>{sticker.file_id}</code>\n\n"
            f"<b>🎟️ Unique ID:</b>\n<code>{sticker.file_unique_id}</code>\n\n"
            f"<b>📏 Dimensions:</b> {sticker.width}x{sticker.height}\n"
            f"<b>📦 File Size:</b> {sticker.file_size} bytes\n"
            f"<b>🎨 Animated:</b> {'Yes' if sticker.is_animated else 'No'}\n"
            f"<b>🎭 Video:</b> {'Yes' if sticker.is_video else 'No'}"
        )

        buttons = [
            [InlineKeyboardButton("🔄 Check Another", callback_data="check_another")],
            [InlineKeyboardButton("❌ Close", callback_data="close_sticker")]
        ]

        await message.reply_photo(
            photo=random.choice(PICS),
            caption=info_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            has_spoiler=True
        )

    except Exception as e:
        print(f"Error processing sticker: {e}")
        await message.reply("❌ An error occurred. Please try again.")