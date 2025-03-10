from pyrogram import Client, filters
from PIL import Image
import os
import io
import aiohttp
from config import ADMINS
from database.database import Database

# Initialize database
db = Database()

# Default thumbnail URL
THUMB_URL = "https://i.ibb.co/XxbHQ9Gk/9a45465f2734f8605fed7f4af74327d7.jpg"

THUMB_DIR = "bot/assets/thumbnails"
if not os.path.exists(THUMB_DIR):
    os.makedirs(THUMB_DIR)

async def resize_thumb(thumb_path, is_video=True):
    """Resize thumbnail to optimal size"""
    try:
        img = Image.open(thumb_path)
        if is_video:
            # 16:9 ratio for videos
            img.thumbnail((320, 180))
        else:
            # 1:1 ratio for documents
            img.thumbnail((320, 320))
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=95)
        output.seek(0)
        return output
    except Exception as e:
        print(f"Error resizing thumbnail: {e}")
        return None

@Client.on_message(filters.command(["setthumb"]) & filters.private & filters.user(ADMINS))
async def set_thumbnail(client, message):
    """Set custom thumbnail (Admin only)"""
    try:
        if not message.reply_to_message or not message.reply_to_message.photo:
            return await message.reply_text("❌ Reply to an image to set as thumbnail.")
        
        user_id = str(message.from_user.id)
        thumb_path = f"{THUMB_DIR}/{user_id}.jpg"
        
        await message.reply_to_message.download(thumb_path)
        
        video_thumb = await resize_thumb(thumb_path, is_video=True)
        doc_thumb = await resize_thumb(thumb_path, is_video=False)
        
        if video_thumb and doc_thumb:
            with open(f"{THUMB_DIR}/{user_id}_video.jpg", "wb") as f:
                f.write(video_thumb.getvalue())
            with open(f"{THUMB_DIR}/{user_id}_doc.jpg", "wb") as f:
                f.write(doc_thumb.getvalue())
                
            await db.set_thumbnail(user_id, True)
            await message.reply_text("✅ Thumbnail saved successfully!")
        else:
            await message.reply_text("❌ Failed to process thumbnail.")
            
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command(["delthumb"]) & filters.private & filters.user(ADMINS))
async def delete_thumbnail(client, message):
    """Delete custom thumbnail (Admin only)"""
    user_id = str(message.from_user.id)
    try:
        for suffix in ['', '_video', '_doc']:
            path = f"{THUMB_DIR}/{user_id}{suffix}.jpg"
            if os.path.exists(path):
                os.remove(path)
        
        await db.set_thumbnail(user_id, False)
        await message.reply_text("✅ Thumbnail deleted successfully!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command(["show_thumb", "showthumb"]) & filters.private)
async def show_thumbnail(client, message):
    """Command to show current thumbnail"""
    user_id = str(message.from_user.id)
    video_path = f"{THUMB_DIR}/{user_id}_video.jpg"
    
    if os.path.exists(video_path):
        await message.reply_photo(
            photo=video_path,
            caption="🖼️ Your current thumbnail"
        )
    else:
        await message.reply_text("❌ No custom thumbnail found!")

async def get_user_thumbnail(user_id, is_video=True):
    """Get user's thumbnail for file sending"""
    suffix = "_video" if is_video else "_doc"
    thumb_path = f"{THUMB_DIR}/{user_id}{suffix}.jpg"
    
    if os.path.exists(thumb_path):
        return thumb_path
    return None

async def get_thumbnail_from_url():
    """Fetch thumbnail from URL"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(THUMB_URL) as response:
                if response.status == 200:
                    return await response.read()
    except Exception as e:
        print(f"Error fetching thumbnail: {e}")
    return None

async def add_thumbnail(client, chat_id, file_id, file_type="document", reply_to_message_id=None):
    """
    Adds custom thumbnail to files when sending through special links
    
    Args:
        client: Pyrogram client instance
        chat_id: Chat ID to send file to
        file_id: Telegram file_id of the document/video
        file_type: "document" or "video"
        reply_to_message_id: Optional message ID to reply to
    
    Returns:
        Message object on success, None on failure
    """
    try:
        # Get thumbnail data
        thumb_data = await get_thumbnail_from_url()
        
        if thumb_data:
            # Send file with thumbnail based on type
            if file_type.lower() == "video":
                return await client.send_video(
                    chat_id=chat_id,
                    video=file_id,
                    thumb=io.BytesIO(thumb_data),
                    reply_to_message_id=reply_to_message_id
                )
            else:
                return await client.send_document(
                    chat_id=chat_id,
                    document=file_id,
                    thumb=io.BytesIO(thumb_data),
                    reply_to_message_id=reply_to_message_id
                )
        else:
            # If thumbnail fetch fails, send without thumbnail
            raise FileNotFoundError("Could not fetch thumbnail")

    except Exception as e:
        print(f"Thumbnail Error: {e}")
        # Continue sending without thumbnail rather than failing
        if file_type.lower() == "video":
            return await client.send_video(
                chat_id=chat_id,
                video=file_id,
                reply_to_message_id=reply_to_message_id
            )
        else:
            return await client.send_document(
                chat_id=chat_id,
                document=file_id,
                reply_to_message_id=reply_to_message_id
            ) 