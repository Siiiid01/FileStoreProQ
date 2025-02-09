import os
import requests
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import MessageNotModified
from asyncio.exceptions import TimeoutError  # Importing correctly

# Ensure the correct Telegraph upload URL
UPLOAD_URL = "https://telegra.ph/upload"

def upload_image_requests(image_path):
    """Uploads image to Telegraph and returns the URL."""
    try:
        with open(image_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(UPLOAD_URL, files=files)

            if response.status_code == 200:
                return f"https://telegra.ph{response.json()[0]['src']}"  # Ensure full URL
            else:
                print(f"Upload failed with status code {response.status_code}")
                return None
    except Exception as e:
        print(f"Error during upload: {e}")
        return None

@Client.on_message(filters.command(["telegraph", "tg"]) & filters.private)
async def telegraph_upload(client, message: Message):
    """Handles the /telegraph command."""
    print("✅ /telegraph command received!")  # Debugging log

    msg = await message.reply_text("Now send me your **photo or video (max 5MB)** to get a Telegraph link.")

    try:
        # Wait for user to send a media file
        t_msg = await client.wait_for_message(chat_id=message.chat.id, timeout=60)
    except TimeoutError:
        return await msg.edit_text("❌ **Timeout:** No media received within **60 seconds**.")

    # Check if media is received
    if not t_msg.media:
        return await msg.edit_text("❌ **Only photos & videos are supported.**")

    # Start upload process
    uploading_message = await msg.edit_text("<b>Uploading...</b>")

    try:
        path = await t_msg.download()
        image_url = upload_image_requests(path)

        # Remove the downloaded file after upload
        if os.path.exists(path):
            os.remove(path)

        if not image_url:
            return await uploading_message.edit_text("❌ **Upload failed. Please try again.**")

        # Send the final message with link
        await uploading_message.edit_text(
            text=f"<b>✅ Link Generated:</b>\n\n<code>{image_url}</code>",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="🔗 Open Link", url=image_url),
                InlineKeyboardButton(text="📤 Share Link", url=f"https://telegram.me/share/url?url={image_url}")
            ],[
                InlineKeyboardButton(text="✗ Close ✗", callback_data="close")
            ]])
        )

    except Exception as error:
        await uploading_message.edit_text(f"❌ **Upload failed:** {str(error)}")
        if os.path.exists(path):
            os.remove(path)

@Client.on_callback_query(filters.regex("^close"))
async def close_button(client, callback_query: CallbackQuery):
    """Handles the close button."""
    try:
        await callback_query.message.delete()
    except MessageNotModified:
        pass