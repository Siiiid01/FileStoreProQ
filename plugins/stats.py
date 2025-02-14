import asyncio  # For async handling like sleep and task scheduling
import random  # For selecting random items (if needed)
from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime  # For calculating the bot's uptime
from config import *  # For getting BOT_STATS_TEXT and AUTO_DELETE_TIME
from helper_func import *  # For functions like get_readable_time
from database.database import *  # Keep this if you're querying the database for user info
import humanize  # If you're using it to format the uptime
from plugins.start import show_loading_animation, auto_delete_message # For showing a loading animation
from bot import Bot  # To access the bot client


AUTO_DELETE_TIME=600



@Bot.on_message(filters.command('stats') & filters.private & filters.user(ADMINS))
async def stats(client: Bot, message: Message):
    try:
        # 1. Delete the /stats command message as soon as it is received.
        await message.delete()

        # 2. Show loading animation (showing a loading indicator while fetching stats)
        loading_msg = await show_loading_animation(message)

        # 3. Get the total number of users in the bot's userbase.
        users = await full_userbase()
        total_users = len(users)

        # 4. Calculate bot's uptime since it was started.
        current_time = datetime.now()
        uptime = current_time - client.start_time
        uptime_str = get_readable_time(uptime.total_seconds())  # Convert seconds to readable time format.

        # 5. Format the stats text using the updated template (no images included).
        stats_text = BOT_STATS_TEXT.format(
            uptime=uptime_str
        )

        # 6. Update the loading message with the stats information (no image included).
        await loading_msg.edit_text(
            caption=stats_text  # Updated stats text (uptime)
        )

        # 7. Schedule the auto-deletion of the loading message after a predefined time (10 minutes).
        asyncio.create_task(auto_delete_message(loading_msg, AUTO_DELETE_TIME))

        # 8. Wait for 10 minutes before deleting the stats message.
        await asyncio.sleep(600)  # 600 seconds = 10 minutes
        await loading_msg.delete()  # Delete the stats message after 10 minutes of inactivity.

    except Exception as e:
        # 9. If any error occurs, log it and send an error message to the user.
        print(f"Error in stats command: {e}")
        await message.reply("⚠︎ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ꜰᴇᴛᴄʜɪɴɢ ꜱᴛᴀᴛꜱ.")
