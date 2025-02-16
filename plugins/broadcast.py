import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from config import ADMINS
from database.database import full_userbase, del_user
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

# Settings
AUTO_DELETE_TIME = 600  # Auto-delete status message in 10 mins

@Bot.on_message(filters.command('broadcast') & filters.private & filters.user(ADMINS))
async def broadcast_handler(client: Bot, message: Message):
    if not message.reply_to_message:
        return await message.reply("ᴘʟᴇᴀꜱᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ!")
    
    users = await full_userbase()
    if not users:
        return await message.reply("ɴᴏ ᴜꜱᴇʀꜱ ꜰᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ!")
    
    total = len(users)
    successful = 0
    blocked = 0
    deleted = 0
    failed = 0
    
    status_msg = await message.reply("ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜱᴛᴀʀᴛᴇᴅ... ᴘʀᴏᴄᴇꜱꜱɪɴɢ ᴜꜱᴇʀꜱ...")
    
    for user_id in users:
        try:
            await message.reply_to_message.copy(user_id)
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_to_message.copy(user_id)
                successful += 1
            except:
                failed += 1
        except UserIsBlocked:
            await del_user(user_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(user_id)
            deleted += 1
        except:
            failed += 1
    
    final_status = (f"◘ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!\n\n"
                    f"• ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: {total}\n"
                    f"• ​🇸​​🇺​​🇨​​🇨​​🇪​​🇸​​🇸​​🇫​​🇺​​🇱​: {successful}\n"
                    f"• ʙʟᴏᴄᴋᴇᴅ: {blocked}\n"
                    f"• ᴅᴇʟᴇᴛᴇᴅ: {deleted}\n"
                    f"• ꜰᴀɪʟᴇᴅ: {failed}")
    
    await status_msg.edit(final_status)
    await asyncio.sleep(AUTO_DELETE_TIME)
    await status_msg.delete()
