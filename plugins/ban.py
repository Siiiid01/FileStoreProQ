from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from config import ADMINS, USER_REPLY_TEXT, PICS
from database.database import add_banned_user, remove_banned_user, get_ban_status
from helper_func import send_ban_log, check_user_ban
import random
import asyncio

# Handler for unauthorized access
@Bot.on_message(filters.command(["ban", "unban"]) & ~filters.user(ADMINS))
async def unauthorized_command(client: Bot, message: Message):
    """Handle unauthorized access to admin commands"""
    try:
        # Send reaction if possible
        # try:
        #     await message.react("🚫", big=True)
        # except:
        #     pass
            
        # Reply with custom message and random image
        await message.reply_text(
            text=USER_REPLY_TEXT,
            quote=True
        )
        
        # Delete the command message if possible
        try:
            await asyncio.sleep(1)
            await message.delete()
        except:
            pass
            
    except Exception as e:
        print(f"Error in unauthorized handler: {e}")

@Bot.on_message(filters.command("ban") & filters.user(ADMINS))
@check_user_ban
async def ban_user(client: Bot, message: Message):
    try:
        # Get command parts
        parts = message.text.split()
        
        # Check command format
        if len(parts) < 2:
            await message.reply_text(
                "<b>❖ Usᴀɢᴇ:</b> /ʙᴀɴ ᴜsᴇʀ_ɪᴅ ʀᴇᴀsᴏɴ\n"
                "<b>• Exᴀᴍᴘʟᴇ:</b> /ʙᴀɴ 1234567890 Sᴘᴀᴍᴍɪɴɢ"
            )
            return
        
        # Get user_id and reason
        try:
            user_id = int(parts[1])
            reason = " ".join(parts[2:]) if len(parts) > 2 else "<i>Nᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ</i>"
        except ValueError:
            await message.reply_text("<b>ッ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴜsᴇʀ ID!</b>")
            return
        
        # Check if user is already banned
        ban_status = await get_ban_status(user_id)
        if ban_status:
            await message.reply_text(
                f"<blockquote expandable><b><i>☙ Usᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ</i>\n\n"
                f"Usᴇʀ ID:<code> {user_id}</code>\n"
                f"Rᴇᴀsᴏɴ: {ban_status['ban_reason']}\n"
                f"Bᴀɴɴᴇᴅ Oɴ: {ban_status['banned_on'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Bᴀɴɴᴇᴅ Bʏ: {ban_status['banned_by']}</b></blockquote>"
            )
            return
        
        # Ban user
        await add_banned_user(user_id, message.from_user.id, reason)
        
        # Try to get user info
        try:
            user = await client.get_users(user_id)
            user_mention = user.mention
        except:
            user_mention = f"Usᴇʀ {user_id}"
        
        # Send confirmation
        await message.reply_text(
            f"<blockquote expandable><b><i>☙ Sᴜᴄᴄᴇssғᴜʟʟʏ Bᴀɴɴᴇᴅ Usᴇʀ</i>\n\n"
            f"Usᴇʀ:<code> {user_mention}</code>\n"
            f"Usᴇʀ ID: <code>{user_id}</code>\n"
            f"Rᴇᴀsᴏɴ: {reason}</b></blockquote>"
        )
        
        # Notify user
        try:
            await client.send_message(
                user_id,
                f"❝Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ\n\nRᴇᴀsᴏɴ:\n<blockquote>{reason}</blockquote>\n\nCᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴs ᴏʀ /ғᴇᴇᴅʙᴀᴄᴋ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ❞"
            )
        except:
            pass

        # Send ban log
        await send_ban_log(client, user_id, message.from_user.id, reason, "banned")

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

@Bot.on_message(filters.command("unban") & filters.user(ADMINS))
@check_user_ban
async def unban_user(client: Bot, message: Message):
    try:
        # Get command parts
        parts = message.text.split()
        
        # Check command format
        if len(parts) != 2:
            await message.reply_text(
                "<b>❖ Usᴀɢᴇ:</b> /Uɴʙᴀɴ ᴜsᴇʀ_ɪᴅ ʀᴇᴀsᴏɴ\n"
                "<b>• Exᴀᴍᴘʟᴇ:</b> /Uɴʙᴀɴ 1234567890 Sᴘᴀᴍᴍɪɴɢ"
            )
            return
        
        # Get user_id
        try:
            user_id = int(parts[1])
        except ValueError:
            await message.reply_text("<b>ッ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴜsᴇʀ ID!</b>")
            return
        
        # Check if user is banned
        ban_status = await get_ban_status(user_id)
        if not ban_status:
            await message.reply_text(f"☙ Usᴇʀ<code> {user_id}</code> ɪs ɴᴏᴛ ʙᴀɴɴᴇᴅ!")
            return
        
        # Unban user
        await remove_banned_user(user_id, message.from_user.id)
        
        # Try to get user info
        try:
            user = await client.get_users(user_id)
            user_mention = user.mention
        except:
            user_mention = f"Usᴇʀ {user_id}"
        
        # Send confirmation
        await message.reply_text(
            f"<blockquote expandable><b><i>Sᴜᴄᴄᴇssғᴜʟʟʏ Uɴʙᴀɴɴᴇᴅ Usᴇʀ</i?\n\n"
            f"Usᴇʀ: {user_mention}\n"
            f"Usᴇʀ ID: <code>{user_id}</code></b></blockquote>"
        )
        
        # Notify user
        try:
            await client.send_message(
                user_id,
                "❝Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ. Yᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ.❞"
            )
        except:
            pass

        # Send ban log
        await send_ban_log(client, user_id, message.from_user.id, action="unbanned")

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

# Add this check at the start of your command handlers
async def check_ban_status(message: Message):
    """Check if user is banned"""
    if message.from_user.id in ADMINS:
        return False
        
    ban_status = await get_ban_status(message.from_user.id)
    if ban_status:
        await message.reply_text(
            f"<b><i>☣ Yᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ</i></b>\n\n"
            f"<blockquote>Rᴇᴀsᴏɴ: {ban_status['ban_reason']}\n"
            f"Bᴀɴɴᴇᴅ Oɴ: {ban_status['banned_on'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"ᴄᴏɴᴛᴀᴄᴛ Aᴅᴍɪɴ @Anime106_Request_bot ᴏʀ /feedback </blockquote>"

        )
        return True
    return False 