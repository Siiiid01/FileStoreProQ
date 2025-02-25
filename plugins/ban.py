from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from config import ADMINS, USER_REPLY_TEXT, PICS
from database.database import add_banned_user, remove_banned_user, get_ban_status
from helper_func import send_ban_log
import random

# Handler for unauthorized access
@Bot.on_message(filters.command(["ban", "unban"]) & ~filters.user(ADMINS))
async def unauthorized_command(client: Bot, message: Message):
    """Handle unauthorized access to admin commands"""
    try:
        # Send reaction if possible
        try:
            await message.react("🚫", big=True)
        except:
            pass
            
        # Reply with custom message and random image
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=USER_REPLY_TEXT,
            quote=True
        )
        
        # Delete the command message if possible
        try:
            await message.delete()
        except:
            pass
            
    except Exception as e:
        print(f"Error in unauthorized handler: {e}")

@Bot.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_user(client: Bot, message: Message):
    try:
        # Get command parts
        parts = message.text.split()
        
        # Check command format
        if len(parts) < 2:
            await message.reply_text(
                "**Usage:** `/ban user_id reason`\n"
                "**Example:** `/ban 1234567890 Spamming`"
            )
            return
        
        # Get user_id and reason
        try:
            user_id = int(parts[1])
            reason = " ".join(parts[2:]) if len(parts) > 2 else "No reason provided"
        except ValueError:
            await message.reply_text("Please provide a valid user ID!")
            return
        
        # Check if user is already banned
        ban_status = await get_ban_status(user_id)
        if ban_status:
            await message.reply_text(
                f"**User is already banned**\n\n"
                f"**User ID:** `{user_id}`\n"
                f"**Reason:** {ban_status['ban_reason']}\n"
                f"**Banned On:** {ban_status['banned_on'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"**Banned By:** `{ban_status['banned_by']}`"
            )
            return
        
        # Ban user
        await add_banned_user(user_id, message.from_user.id, reason)
        
        # Try to get user info
        try:
            user = await client.get_users(user_id)
            user_mention = user.mention
        except:
            user_mention = f"User {user_id}"
        
        # Send confirmation
        await message.reply_text(
            f"**Successfully Banned User**\n\n"
            f"**User:** {user_mention}\n"
            f"**User ID:** `{user_id}`\n"
            f"**Reason:** {reason}"
        )
        
        # Notify user
        try:
            await client.send_message(
                user_id,
                f"**You have been banned**\n**Reason:** {reason}"
            )
        except:
            pass

        # Send ban log
        await send_ban_log(client, user_id, message.from_user.id, reason, "banned")

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

@Bot.on_message(filters.command("unban") & filters.user(ADMINS))
async def unban_user(client: Bot, message: Message):
    try:
        # Get command parts
        parts = message.text.split()
        
        # Check command format
        if len(parts) != 2:
            await message.reply_text(
                "**Usage:** `/unban user_id`\n"
                "**Example:** `/unban 1234567890`"
            )
            return
        
        # Get user_id
        try:
            user_id = int(parts[1])
        except ValueError:
            await message.reply_text("Please provide a valid user ID!")
            return
        
        # Check if user is banned
        ban_status = await get_ban_status(user_id)
        if not ban_status:
            await message.reply_text(f"User `{user_id}` is not banned!")
            return
        
        # Unban user
        await remove_banned_user(user_id, message.from_user.id)
        
        # Try to get user info
        try:
            user = await client.get_users(user_id)
            user_mention = user.mention
        except:
            user_mention = f"User {user_id}"
        
        # Send confirmation
        await message.reply_text(
            f"**Successfully Unbanned User**\n\n"
            f"**User:** {user_mention}\n"
            f"**User ID:** `{user_id}`"
        )
        
        # Notify user
        try:
            await client.send_message(
                user_id,
                "You have been unbanned. You can now use the bot."
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
            f"**You are banned from using this bot**\n\n"
            f"**Reason:** {ban_status['ban_reason']}\n"
            f"**Banned On:** {ban_status['banned_on'].strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return True
    return False 