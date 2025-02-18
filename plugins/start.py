
import asyncio
import random
import time
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import *
from helper_func import *
from database.database import *

# File auto-delete time in seconds
FILE_AUTO_DELETE = TIME
TUT_VID = f"{TUT_VID}"

# Loading Animation Constants
WAIT_ANIMATION_TEXT = "○ ○ ○"
ANIMATION_FRAMES = ["● ○ ○", "● ● ○", "● ● ●"]
ANIMATION_INTERVAL = 0.15

# Auto-delete constants
AUTO_DELETE_TIME = 10  # 10 seconds
EXEMPT_FROM_DELETE = ['Get File Again!', 'broadcast']


async def show_loading_animation(message: Message):
    """Display a dynamic loading animation and delete it before sending the actual response."""
    try:
        anim_msg = await message.reply(WAIT_ANIMATION_TEXT)
        for frame in ANIMATION_FRAMES:
            await anim_msg.edit(frame)
            await asyncio.sleep(ANIMATION_INTERVAL)
        return anim_msg
    except:
        return None


@Bot.on_message(filters.command('start') & filters.private & subscribed1 & subscribed2 & subscribed3 & subscribed4)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass

    # React to /start command
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass

    # Show loading animation
    loading_msg = await show_loading_animation(message)

    # Handle bot start via URL button
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")

            ids = []
            if len(argument) == 3:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))

            elif len(argument) == 2:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]

            if loading_msg:
                await loading_msg.delete()

            messages = await get_messages(client, ids)
            sent_msgs = []
            for msg in messages:
                caption = (CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, 
                                                 filename=msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document)
                           else ("" if not msg.caption else msg.caption.html))
                reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

                try:
                    sent_msg = await msg.copy(
                        chat_id=message.from_user.id, caption=caption,
                        parse_mode=ParseMode.HTML, reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT
                    )
                    sent_msgs.append(sent_msg)
                except Exception as e:
                    print(f"Failed to send message: {e}")
                    pass

            if FILE_AUTO_DELETE > 0:
                notification_msg = await message.reply(
                    f"<b>This file will be deleted in {get_exp_time(FILE_AUTO_DELETE)}. Save it before deletion.</b>"
                )

                await asyncio.sleep(FILE_AUTO_DELETE)

                for snt_msg in sent_msgs:
                    try:
                        await snt_msg.delete()
                    except:
                        pass

                reload_url = f"https://t.me/{client.username}?start={message.command[1]}" if message.command and len(message.command) > 1 else None
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=reload_url)],
                     [InlineKeyboardButton("✖ Close", callback_data="close_file_again")]]
                ) if reload_url else None

                await notification_msg.edit(
                    "<b>Your file has been deleted! Click below to retrieve it again.</b>",
                    reply_markup=keyboard
                )
            return

    # If not starting via URL button, show normal start message
    if loading_msg:
        await loading_msg.delete()

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("𝗠𝗼𝗿𝗲", callback_data="more")],
        [InlineKeyboardButton("𝗔𝗯𝗼𝘂𝘁", callback_data="about"),
         InlineKeyboardButton('𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀', url='https://t.me/nova_flix')]
    ])

    sent_start_msg = await message.reply_photo(
        photo=random.choice(PICS),
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=reply_markup
    )

    # Auto-delete after 10 seconds
    await asyncio.sleep(AUTO_DELETE_TIME)
    try:
        await message.delete()
        await sent_start_msg.delete()
    except:
        pass


@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = []
    if FORCE_SUB_CHANNEL1 and FORCE_SUB_CHANNEL2:
        buttons.append([
            InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink1),
            InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink2),
        ])
    elif FORCE_SUB_CHANNEL1:
        buttons.append([InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink1)])
    elif FORCE_SUB_CHANNEL2:
        buttons.append([InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink2)])

    if FORCE_SUB_CHANNEL3 and FORCE_SUB_CHANNEL4:
        buttons.append([
            InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink3),
            InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink4),
        ])
    elif FORCE_SUB_CHANNEL3:
        buttons.append([InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink3)])
    elif FORCE_SUB_CHANNEL4:
        buttons.append([InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink4)])

    await message.reply_photo(
        photo=random.choice(PICS),
        caption=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )





# @Bot.on_message(filters.command('stats') & filters.private & filters.user(ADMINS))
# async def stats(client: Bot, message: Message):
#     try:
#         # Add reaction to command
#         try:
#             await message.react(emoji=random.choice(REACTIONS), big=True)
#         except:
#             pass

#         # Show loading animation
#         loading_msg = await show_loading_animation(message)

#         # Get user count
#         users = await full_userbase()
#         total_users = len(users)

#         # Calculate uptime
#         current_time = datetime.now()
#         uptime = current_time - client.start_time
#         uptime_str = get_readable_time(uptime.total_seconds())

#         # Format stats text
#         stats_text = BOT_STATS_TEXT.format(
#             total_users=total_users,
#             uptime=uptime_str
#         )

#         # Update loading message with stats
#         await edit_message_with_photo(
#             loading_msg,
#             photo=random.choice(PICS),
#             caption=stats_text,
#             has_spoiler=True
#         )

#         # Schedule message for auto-deletion
#         asyncio.create_task(auto_delete_message(loading_msg, AUTO_DELETE_TIME))

#     except Exception as e:
#         print(f"Error in stats command: {e}")
#         await message.reply("❌ An error occurred while fetching stats.")