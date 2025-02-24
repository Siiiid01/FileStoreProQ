import os
import requests
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from bot import Bot
from helper_func import send_telegraph_log, check_user_ban

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

@Bot.on_message(filters.command("telegraph") & filters.private)
@check_user_ban  # Add ban check decorator
async def telegraph_upload(bot: Bot, message: Message):
    try:
        # Send instruction message
        t_msg = await message.reply_text("• ɴᴏᴡ ꜱᴇɴᴅ ᴍᴇ ʏᴏᴜʀ ᴘʜᴏᴛᴏ ᴏʀ ᴠɪᴅᴇᴏ ᴜɴᴅᴇʀ 5ᴍʙ ᴛᴏ ɢᴇᴛ ᴍᴇᴅɪᴀ ʟɪɴᴋ.")
        
        # Wait for media response
        async def media_filter(_, __, m):
            return bool(m.media) and m.from_user.id == message.from_user.id
            
        try:
            media_msg = await bot.listen(
                message.chat.id,
                filters=filters.create(media_filter),
                timeout=60
            )
        except TimeoutError:
            await t_msg.edit("⚠️ Timeout: No media received within 60 seconds.")
            return

        if not media_msg.media:
            return await t_msg.edit("⚠︎ ᴏɴʟʏ ᴍᴇᴅɪᴀ ꜱᴜᴘᴘᴏʀᴛᴇᴅ.")

        uploading_message = await message.reply_text("<b>ᴜᴘʟᴏᴀᴅɪɴɢ...</b>")
        
        try:
            # Download and upload file
            path = await media_msg.download()
            image_url = upload_image_requests(path)
            
            # Clean up downloaded file
            try:
                os.remove(path)
            except:
                pass
                
            if not image_url:
                return await uploading_message.edit_text("⚠︎ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴜᴘʟᴏᴀᴅ ꜰɪʟᴇ.")

            # Log the upload
            await send_telegraph_log(
                bot,
                message.from_user.id,
                os.path.basename(path),
                media_msg.media.value,
                image_url
            )

            # Send success message
            await uploading_message.edit_text(
                text=f"<b>Link :-</b>\n\n<code>{image_url}</code>",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("• ᴏᴘᴇɴ ʟɪɴᴋ •", url=image_url),
                        InlineKeyboardButton("• ꜱʜᴀʀᴇ ʟɪɴᴋ •", url=f"https://telegram.me/share/url?url={image_url}")
                    ],
                    [InlineKeyboardButton("• ᴄʟᴏꜱᴇ •", callback_data="close")]
                ])
            )

        except Exception as e:
            await uploading_message.edit_text(f"**Upload failed: {str(e)}**")
            
    except Exception as e:
        print(f"Telegraph command error: {e}")

@Bot.on_callback_query(filters.regex("^close$"))
async def close_callback(client, callback_query: CallbackQuery):
    try:
        await callback_query.message.delete()
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)