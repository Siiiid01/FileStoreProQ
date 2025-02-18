import asyncio
import os
from itertools import cycle
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid
from bot import Bot
from database.database import *
from config import *

loading_frames = cycle(["\\", "|", "/", "—"])  # Rotating loading animation

def progress_bar(current, total, length=10):
    """Generates a visual progress bar dynamically."""
    filled_length = int((current / total) * length)
    bar = "█" * filled_length + "░" * (length - filled_length)
    return f"[{bar}] {int((current / total) * 100)}%"

@Bot.on_message(filters.private & filters.command('broadcast'))
async def send_text(client: Bot, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("🚫 You are not authorized to use this command.")

    if not message.reply_to_message:
        msg = await message.reply("❌ Reply to a message to broadcast.")
        await asyncio.sleep(8)
        return await msg.delete()

    query = await full_userbase()
    broadcast_msg = message.reply_to_message
    total = len(query)
    successful = blocked = deleted = unsuccessful = 0
    errors = []

    pls_wait = await message.reply("📢 **Broadcast Starting...**")

    for i, chat_id in enumerate(query, 1):
        try:
            if not isinstance(chat_id, (int, str)):
                chat_id = str(chat_id)

            await broadcast_msg.copy(chat_id)
            successful += 1
        
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except Exception as err:
                unsuccessful += 1
                errors.append(f"Failed to send to {chat_id}: {err}")
        
        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1
            errors.append(f"User blocked the bot: {chat_id}")
        
        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1
            errors.append(f"Deleted account: {chat_id}")
        
        except PeerIdInvalid:
            await del_user(chat_id)
            unsuccessful += 1
            errors.append(f"Invalid user ID (peer ID issue): {chat_id}")
        
        except Exception as err:
            unsuccessful += 1
            errors.append(f"Failed to send to {chat_id}: {err}")

        # Dynamic Progress Update
        if i % 5 == 0 or i == total:  # Update every 5 messages
            status = f"""
📢 **Broadcast In Progress...** {next(loading_frames)}
{progress_bar(i, total)}

👥 **Total Users:** `{total}`
✅ **Successful:** `{successful}`
🚫 **Blocked:** `{blocked}`
❌ **Deleted Accounts:** `{deleted}`
⚠️ **Unsuccessful:** `{unsuccessful}`
            """
            await pls_wait.edit(status)
        
        await asyncio.sleep(0.3)  # Reduced delay for better speed

    # Final Status Update
    final_status = f"""
<b>📢 **Broadcast Completed!** ✅</b>
{progress_bar(total, total)}

👥 **Total Users:** `{total}`
✅ **Successful:** `{successful}`
🚫 **Blocked:** `{blocked}`
❌ **Deleted Accounts:** `{deleted}`
⚠️ **Unsuccessful:** `{unsuccessful}`
    """
    await pls_wait.edit(final_status)

    # Save errors if any
    if errors:
        error_file = "broadcast_errors.txt"
        with open(error_file, "w") as f:
            f.write("\n".join(errors))
        await message.reply_document(error_file, caption="🚨 **Broadcast Errors**")
        os.remove(error_file)

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
