import asyncio
import os
from itertools import cycle
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid
from bot import Bot
from database.database import *
from config import *
from helper_func import check_user_ban

# Loading animation frames
LOADING_CHARS = ['\\', '|', '/', '—']
loading_animation = cycle(LOADING_CHARS)

def get_progress_bar(current, total, length=10):
    """Create a dynamic progress bar that updates with actual progress"""
    progress = (current / total) * length
    filled = int(progress)
    remaining = length - filled
    percent = (current / total) * 100
    return f"[{'█' * filled}{'░' * remaining}] {percent:.1f}% {next(loading_animation)}"

async def update_progress_message(message, current, total, successful, blocked, deleted, unsuccessful):
    """Update progress message with current statistics"""
    try:
        progress_text = get_progress_bar(current, total)
        
        status_text = f"""
<b>❂ ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀᴛᴜs</b>

<code>{progress_text}</code>

<b>◈ ᴘʀᴏɢʀᴇss:</b> <code>{current}/{total}</code>
<b>◈ sᴜᴄᴄᴇssғᴜʟ:</b> <code>{successful}</code>
<b>◈ ʙʟᴏᴄᴋᴇᴅ:</b> <code>{blocked}</code>
<b>◈ ᴅᴇʟᴇᴛᴇᴅ:</b> <code>{deleted}</code>
<b>◈ ғᴀɪʟᴇᴅ:</b> <code>{unsuccessful}</code>

<i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>
"""
        await message.edit(status_text)
    except Exception as e:
        print(f"Error updating progress: {e}")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
@check_user_ban
async def broadcast_handler(client: Bot, message: Message):
    if not message.reply_to_message:
        temp_msg = await message.reply("• ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ!")
        await asyncio.sleep(8)
        await temp_msg.delete()
        return

    # Initialize broadcast
    users = await full_userbase()
    if not users:
        return await message.reply("• ɴᴏ ᴜsᴇʀs ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ!")

    total_users = len(users)
    stats = {
        "successful": 0,
        "blocked": 0,
        "deleted": 0,
        "unsuccessful": 0
    }
    
    # Start broadcast with initial status
    status_msg = await message.reply("❂ ɪɴɪᴛɪᴀʟɪᴢɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ...")
    last_update_time = 0
    update_interval = 1  # Update every second for more real-time feel

    errors = []
    broadcast_msg = message.reply_to_message

    for i, user_id in enumerate(users, 1):
        try:
            await broadcast_msg.copy(chat_id=user_id)
            stats["successful"] += 1
            
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await broadcast_msg.copy(chat_id=user_id)
                stats["successful"] += 1
            except Exception as e:
                stats["unsuccessful"] += 1
                errors.append(f"Failed for {user_id}: {str(e)}")
                
        except UserIsBlocked:
            stats["blocked"] += 1
            await del_user(user_id)
            
        except InputUserDeactivated:
            stats["deleted"] += 1
            await del_user(user_id)
            
        except PeerIdInvalid:
            stats["unsuccessful"] += 1
            await del_user(user_id)
            
        except Exception as e:
            stats["unsuccessful"] += 1
            errors.append(f"Failed for {user_id}: {str(e)}")

        # Update status with controlled frequency
        current_time = asyncio.get_event_loop().time()
        if current_time - last_update_time >= update_interval:
            await update_progress_message(
                status_msg, i, total_users,
                stats["successful"], stats["blocked"],
                stats["deleted"], stats["unsuccessful"]
            )
            last_update_time = current_time

        await asyncio.sleep(0.1)  # Prevent flooding

    # Final status update
    final_status = f"""
<b>‡ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>

[██████████] 100% ✓

<b>◈ ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{total_users}</code>
<b>◈ sᴜᴄᴄᴇssғᴜʟ:</b> <code>{stats['successful']}</code>
<b>◈ ʙʟᴏᴄᴋᴇᴅ:</b> <code>{stats['blocked']}</code>
<b>◈ ᴅᴇʟᴇᴛᴇᴅ:</b> <code>{stats['deleted']}</code>
<b>◈ ғᴀɪʟᴇᴅ:</b> <code>{stats['unsuccessful']}</code>
"""
    await status_msg.edit(final_status)

    # Log errors if any
    if errors:
        with open("broadcast_errors.txt", "w") as f:
            f.write("\n".join(errors))

        await message.reply_document(
            "broadcast_errors.txt",
            caption="• ʙʀᴏᴀᴅᴄᴀsᴛ ᴇʀʀᴏʀs"
        )
        os.remove("broadcast_errors.txt")

        
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
