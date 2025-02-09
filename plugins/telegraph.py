import os
import requests
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import MessageNotModified
from asyncio.exceptions import TimeoutError  # Correctly import TimeoutError

# Ensure correct URL (replace if needed)
UPLOAD_URL = "https://telegra.ph/upload"

def upload_image_requests(image_path):
    """Uploads image to Telegraph and returns the URL."""
    try:
        with open(image_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(UPLOAD_URL, files=files)
            
            if response.status_code == 200:
                return response.json()[0]['src']  # Adjust if response format differs
            else:
                print(f"Upload failed with status code {response.status_code}")
                return None
    except Exception as e:
        print(f"Error during upload: {e}")
        return None

@Client.on_message(filters.command(["telegraph", "tg"]))  # Supports both groups and private chats
async def telegraph_upload(client, message: Message):
    try:
        msg = await message.reply_text("Now Send Me Your Photo Or Video Under 5MB To Get Media Link.")

        try:
            t_msg = await client.wait_for_message(chat_id=message.chat.id, timeout=60)
        except asyncio.TimeoutError:
            return await msg.edit_text("**Timeout: No media received within 60 seconds.**")

        if not t_msg.media:
            return await msg.edit_text("**Only Media Supported.**")

        uploading_message = await msg.edit_text("<b>Uploading...</b>")

        try:
            path = await t_msg.download()
            image_url = upload_image_requests(path)

            if os.path.exists(path):
                os.remove(path)

            if not image_url:
                return await uploading_message.edit_text("**Failed to upload file.**")

            final_url = f"https://telegra.ph{image_url}"  # Ensure full URL

            await uploading_message.edit_text(
                text=f"<b>Link :-</b>\n\n<code>{final_url}</code>",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(text="Open Link", url=final_url),
                    InlineKeyboardButton(text="Share Link", url=f"https://telegram.me/share/url?url={final_url}")
                ],[
                    InlineKeyboardButton(text="✗ Close ✗", callback_data="close")
                ]])
            )

        except Exception as error:
            await uploading_message.edit_text(f"**Upload failed: {str(error)}**")
            if os.path.exists(path):
                os.remove(path)

    except Exception as e:
        await message.reply_text(f"**An error occurred: {str(e)}**")

@Client.on_callback_query(filters.regex("^close"))
async def close_button(client, callback_query: CallbackQuery):
    """Handles the close button."""
    try:
        await callback_query.message.delete()
    except MessageNotModified:
        pass