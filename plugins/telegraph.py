import os
import requests
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import MessageNotModified

def upload_image_requests(image_path):
    upload_url = "https://envs.sh"
    
    try:
        with open(image_path, 'rb') as file:
            files = {'file': file} 
            response = requests.post(upload_url, files=files)
            
            if response.status_code == 200:
                return response.text.strip() 
            else:
                return print(f"Upload failed with status code {response.status_code}")
    
    except Exception as e:
        print(f"Error during upload: {e}")
        return None

@Client.on_message(filters.command(["telegraph", "tg"]) & filters.private)
async def telegraph_upload(client, message: Message):
    try:
        # Send initial message
        msg = await message.reply_text("Now Send Me Your Photo Or Video Under 5MB To Get Media Link.")
        
        # Wait for user's media message
        try:
            t_msg = await client.wait_for_message(chat_id=message.chat.id, timeout=60)
        except TimeoutError:
            return await msg.edit_text("**Timeout: No media received within 60 seconds.**")

        if not t_msg.media:
            return await msg.edit_text("**Only Media Supported.**")

        # Download and upload process
        uploading_message = await msg.edit_text("<b>ᴜᴘʟᴏᴀᴅɪɴɢ...</b>")
        
        try:
            path = await t_msg.download()
            image_url = upload_image_requests(path)
            
            # Clean up downloaded file
            if os.path.exists(path):
                os.remove(path)
                
            if not image_url:
                return await uploading_message.edit_text("**Failed to upload file.**")
                
            await uploading_message.edit_text(
                text=f"<b>Link :-</b>\n\n<code>{image_url}</code>",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(text="Open Link", url=image_url),
                    InlineKeyboardButton(text="Share Link", url=f"https://telegram.me/share/url?url={image_url}")
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

# Add callback handler for the close button
@Client.on_callback_query(filters.regex("^close"))
async def close_button(client, callback_query: CallbackQuery):
    try:
        await callback_query.message.delete()
    except MessageNotModified:
        pass
    
