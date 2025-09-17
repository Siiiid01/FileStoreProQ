from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS, OWNER, PICS, NEW_USER_LOG_CHANNEL
from database.database import set_maintenance_mode, get_maintenance_mode
import random
from datetime import datetime

MAINTENANCE_TEXT = """
<b>🛠 Bot Maintenance Mode</b>

<blockquote>Sorry, the bot is currently under maintenance. Please try again later.

• Status: <code>Maintenance Active</code>
• Expected Duration: <code>Unspecified</code>
• Updates: <a href='https://t.me/WilsonVerse'>Channel</a>
• Use This bot instead: @SaitamaMovieBot

We'll be back soon! Thanks for your patience.</blockquote>

<i>Contact: @{}</i>
"""

@Bot.on_message(filters.command("maintenance") & filters.user(ADMINS))
async def maintenance_command(client: Bot, message: Message):
    """Toggle maintenance mode (Admin only)"""
    try:
        # Get command argument
        args = message.text.split()
        if len(args) != 2 or args[1].lower() not in ['on', 'off']:
            await message.reply(
                "<b>Usage:</b> <code>/maintenance [on|off]</code>\n"
                "<i>Example: /maintenance on</i>"
            )
            return

        # Set maintenance status
        status = args[1].lower() == 'on'
        await set_maintenance_mode(status)
        
        # Send confirmation with stats button
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Bot Status", callback_data="maintenance_status")]
        ])
        
        await message.reply(
            f"<b>✅ Maintenance mode {'activated' if status else 'deactivated'}</b>\n\n"
            f"<blockquote>• Status: <code>{'🛠 Under Maintenance' if status else '🟢 Operational'}</code>\n"
            f"• Changed By: {message.from_user.mention}</blockquote>",
            reply_markup=keyboard
        )

    except Exception as e:
        await message.reply(f"Error: {str(e)}")

@Bot.on_callback_query(filters.regex("^maintenance_status$"))
async def maintenance_status_callback(client: Bot, callback_query):
    """Show maintenance status details"""
    try:
        is_maintenance = await get_maintenance_mode()
        total_users = len(await full_userbase())  # Assuming you have this function
        
        await callback_query.edit_message_text(
            "<b>🤖 Bot Status Information</b>\n\n"
            f"<blockquote>• Mode: <code>{'🛠 Maintenance' if is_maintenance else '🟢 Normal'}</code>\n"
            f"• Total Users: <code>{total_users}</code>\n"
            f"• Access: <code>{'Admins Only' if is_maintenance else 'All Users'}</code></blockquote>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="maintenance_status")]
            ])
        )
    except Exception as e:
        print(f"Error in maintenance status: {e}")

# Maintenance check decorator
def maintenance_mode_check(func):
    async def wrapper(client, message):
        # Always allow admins
        if message.from_user.id in ADMINS:
            return await func(client, message)
            
        # Check maintenance status
        if await get_maintenance_mode():
            # Log access attempt
            try:
                await client.send_message(
                    NEW_USER_LOG_CHANNEL,
                    f"<b>⚠️ Maintenance Mode Access Attempt</b>\n\n"
                    f"<blockquote>• User: {message.from_user.mention}\n"
                    f"• ID: <code>{message.from_user.id}</code>\n"
                    f"• Username: @{message.from_user.username if message.from_user.username else 'None'}\n"
                    f"• Command: <code>{message.text}</code>\n"
                    f"• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</blockquote>"
                )
            except Exception as e:
                print(f"Error logging maintenance access: {e}")

            # Send maintenance message with photo
            try:
                await message.reply_photo(
                    photo=random.choice(PICS),
                    caption=MAINTENANCE_TEXT.format(OWNER),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📢 Updates", url=f"https://t.me/Moviess_Ok")]
                    ])
                )
            except Exception as e:
                print(f"Error sending maintenance message: {e}")
            return
        
        # If not in maintenance, process normally
        return await func(client, message)
    return wrapper
