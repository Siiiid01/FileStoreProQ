import asyncio
import os
from pyrogram import Client, filters  
from pyrogram.types import Message  
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated  
from bot import Bot  
from database.database import *  
from config import *  

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))  
async def send_text(client: Bot, message: Message):  
    if message.reply_to_message:  
        query = await full_userbase()  
        broadcast_msg = message.reply_to_message  
        total = len(query)  
        successful = 0  
        blocked = 0  
        deleted = 0  
        unsuccessful = 0  

        pls_wait = await message.reply("<i>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴏᴄᴇꜱꜱɪɴɢ....</i>")  

        for chat_id in query:  
            try:  
                await broadcast_msg.copy(chat_id)  
                successful += 1  
            except FloodWait as e:  
                delay = e.value  
                print(f"FloodWait of {delay}s, sleeping...")  
                await asyncio.sleep(delay + 1)  
                try:  
                    await broadcast_msg.copy(chat_id)  
                    successful += 1  
                except Exception as e:  
                    print(f"Failed after FloodWait for {chat_id}: {e}")  
                    unsuccessful += 1  
            except UserIsBlocked:  
                await del_user(chat_id)  
                blocked += 1  
            except InputUserDeactivated:  
                await del_user(chat_id)  
                deleted += 1  
            except Exception as e:  
                print(f"Failed to send to {chat_id}: {e}")  # Logs the exact error  
                unsuccessful += 1  

            await asyncio.sleep(0.5)  # Small delay to avoid Telegram rate limits  

        status = f"""<b><u>ʙʀᴏᴀᴅᴄᴀꜱᴛ...</u>  
  
◈ Tᴏᴛᴀʟ Usᴇʀs: <code>{total}</code>  
◈ Sᴜᴄᴄᴇssғᴜʟ: <code>{successful}</code>  
◈ Bʟᴏᴄᴋᴇᴅ Usᴇʀs: <code>{blocked}</code>  
◈ Dᴇʟᴇᴛᴇᴅ Aᴄᴄᴏᴜɴᴛs: <code>{deleted}</code>  
◈ Uɴsᴜᴄᴄᴇssғᴜʟ: <code>{unsuccessful}</code></b>"""  

        return await pls_wait.edit(status)  

    else:  
        msg = await message.reply(REPLY_ERROR)  
        await asyncio.sleep(8)  
        await msg.delete()

# import asyncio
# import time
# from pyrogram import Client, filters
# from pyrogram.types import Message
# from bot import Bot
# from config import ADMINS
# from database.database import full_userbase, del_user
# from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

# # Settings
# AUTO_DELETE_TIME = 600  # Auto-delete status message in 10 mins

# @Bot.on_message(filters.command('broadcast') & filters.private & filters.user(ADMINS))
# async def broadcast_handler(client: Bot, message: Message):
#     if not message.reply_to_message:
#         return await message.reply("ᴘʟᴇᴀꜱᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ!")
    
#     users = await full_userbase()
#     if not users:
#         return await message.reply("ɴᴏ ᴜꜱᴇʀꜱ ꜰᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ!")
    
#     total = len(users)
#     successful = 0
#     blocked = 0
#     deleted = 0
#     failed = 0
    
#     status_msg = await message.reply("• ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜱᴛᴀʀᴛᴇᴅ...\n• ᴘʀᴏᴄᴇꜱꜱɪɴɢ ᴜꜱᴇʀꜱ...")
    
#     for user_id in users:
#         try:
#             await message.reply_to_message.copy(user_id)
#             successful += 1
#         except FloodWait as e:
#             await asyncio.sleep(e.value)
#             try:
#                 await message.reply_to_message.copy(user_id)
#                 successful += 1
#             except:
#                 failed += 1
#         except UserIsBlocked:
#             await del_user(user_id)
#             blocked += 1
#         except InputUserDeactivated:
#             await del_user(user_id)
#             deleted += 1
#         except:
#             failed += 1
    
#     final_status = (f"◘ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!\n\n"
#                     f"• ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: {total}\n"
#                     f"• sᴜᴄᴇssꜰᴜʟʟ: {successful}\n"
#                     f"• ʙʟᴏᴄᴋᴇᴅ: {blocked}\n"
#                     f"• ᴅᴇʟᴇᴛᴇᴅ: {deleted}\n"
#                     f"• ꜰᴀɪʟᴇᴅ: {failed}")
    
#     await status_msg.edit(final_status)
#     await asyncio.sleep(AUTO_DELETE_TIME)
#     await status_msg.delete()
