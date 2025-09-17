import asyncio
import os
import random
import sys
import time
import string
import humanize
from pyrogram import Client, filters, __version__ 
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import (
    FloodWait, UserIsBlocked, InputUserDeactivated, 
    UserNotParticipant, MessageNotModified, MessageIdInvalid
)
from bot import Bot
from config import *
from helper_func import *
from database.database import *
from collections import defaultdict
from datetime import datetime, timedelta
from plugins.user_start_log import log_start_usage, get_start_stats  # for logging
from plugins.maintenance import maintenance_mode_check

# File auto-delete time in seconds (Set your desired time in seconds here)
FILE_AUTO_DELETE = TIME  # Example: 3600 seconds (1 hour)
TUT_VID = f"{TUT_VID}"

# Add these constants at the top with other constants
AUTO_DELETE_TIME = 600  # 10 minutes in seconds
EXEMPT_FROM_DELETE = ['Get File Again!', 'broadcast']  # Messages that shouldn't be deleted
LOADING_ANIMATION = ["\\", "|", "/", "─"]
ANIMATION_INTERVAL = 0.07  # Adjust for smoother animation

# Add these tracking dictionaries
user_requests = defaultdict(list)  # Track user requests
FLOOD_LIMIT = 3  # Max requests within time window
FLOOD_TIME = 600  # 10 minutes in seconds
FLOOD_WAIT = 600  # 10 minutes wait after flood

# Update the constants at the top
START_FLOOD_LIMIT = 2  # Max start commands within time window
START_FLOOD_TIME = 300  # 5 minutes in seconds
START_FLOOD_WAIT = 300  # 5 minutes wait after flood
start_requests = defaultdict(list)  # Track start command requests

# Add this function to check start command flood
async def check_start_flood(user_id: int) -> bool:
    """Check if user has exceeded start command limit"""
    now = datetime.now()
    start_requests[user_id] = [t for t in start_requests[user_id] if now - t < timedelta(seconds=START_FLOOD_TIME)]
    
    if len(start_requests[user_id]) >= START_FLOOD_LIMIT:
        return True
        
    start_requests[user_id].append(now)
    return False

async def show_loading(client: Client, message: Message):
    """Shows a smooth loading animation"""
    try:
        if not message or not message.from_user:
            return

        # Add delay before starting
        await asyncio.sleep(0.2)
        
        try:
            loading_message = await message.reply_text("Iɴɪᴛɪᴀʟɪᴢɪɴɢ \\")
        except UserIsBlocked:
            return
        except Exception as e:
            print(f"Error sending initial loading message: {e}")
            return

        try:
            for _ in range(2):  # Run animation 2 cycles
                for frame in LOADING_ANIMATION:
                    try:
                        await asyncio.sleep(ANIMATION_INTERVAL)
                        await loading_message.edit_text(f"Iɴɪᴛɪᴀʟɪᴢɪɴɢ {frame}")
                    except MessageNotModified:
                        continue
                    except (UserIsBlocked, MessageIdInvalid):
                        return
                    except Exception as e:
                        print(f"Animation frame error: {e}")
                        return
                        
            # Clean up animation message
            try:
                await loading_message.delete()
            except:
                pass
                
        except Exception as e:
            print(f"Loading animation error: {e}")
            try:
                await loading_message.delete()
            except:
                pass
            
    except Exception as e:
        print(f"Show loading overall error: {e}")

@Bot.on_message(filters.command('start') & filters.private & subscribed1 & subscribed2 & subscribed3 & subscribed4)
@check_user_ban
@maintenance_mode_check  # Add this decorator
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    # Log user start usage
    log_start_usage(user_id)
    
    # Check for flood
    if await check_start_flood(user_id):
        wait_time = get_exp_time(START_FLOOD_WAIT)
        await message.reply(
            f"<b>ツ Pʟᴇᴀsᴇ ᴡᴀɪᴛ {wait_time} ʙᴇғᴏʀᴇ ᴜsɪɴɢ sᴛᴀʀᴛ ᴄᴏᴍᴍᴀɴᴅ ᴀɢᴀɪɴ.</b>\n\n"
            "<blockquote expandable><i> Dᴇᴠ Wᴀs ᴜɴᴀʙʟᴇ ᴛᴏ ғɪɴᴅ ᴛʜᴇ sɴᴇᴀᴋʏ ʙᴜɢ ᴄᴀᴜsɪɴɢ ᴡʜɪᴄʜ ᴡᴀs ᴄᴀᴜsɪɴɢ sɪʟᴇɴᴛ ᴇʀʀᴏʀs, sᴏ ʜᴇ ᴀᴅᴅᴇᴅ ᴀ ᴛᴏ ʜᴀɴᴅʟᴇ ɪᴛ😎.</i></blockquote>"
        )
        return

    # Add reaction to start command
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass

    # Show loading animation
    await show_loading(client, message)

    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
            # Send new user notification
            await send_new_user_notification(client, message.from_user)
        except:
            pass

    # Check if user is an admin and treat them as verified
    if id in ADMINS:
        verify_status = {
            'is_verified': True,
            'verify_token': None,  # Admins don't need a token
            'verified_time': time.time(),
            'link': ""
        }
    else:
        verify_status = await get_verify_status(id)

        # If TOKEN is enabled, handle verification logic
        if TOKEN:
            if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
                await update_verify_status(id, is_verified=False)

            if "verify_" in message.text:
                _, token = message.text.split("_", 1)
                if verify_status['verify_token'] != token:
                    return await message.reply("• Yᴏᴜʀ ᴛᴏᴋᴇɴ ɪs ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ. Tʀʏ ᴀɢᴀɪɴ ʙʏ ᴄʟɪᴄᴋɪɴɢ /sᴛᴀʀᴛ.")
                await update_verify_status(id, is_verified=True, verified_time=time.time())
                if verify_status["link"] == "":
                    reply_markup = None
                return await message.reply(
                    f"• Yᴏᴜʀ ᴛᴏᴋᴇɴ ʜᴀs ʙᴇᴇɪɴ sᴜᴄᴄᴇssғᴜʟʟʏ ᴠᴇʀɪғɪᴇᴅ ᴀɴᴅ ɪs ᴠᴀʟɪɖ ғᴏʀ <blockqute>{get_exp_time(VERIFY_EXPIRE)}</blockqute>",
                    reply_markup=reply_markup,
                    protect_content=False,
                    quote=True
                )

            if not verify_status['is_verified']:
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                await update_verify_status(id, verify_token=token, link="")
                link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://telegram.dog/{client.username}?start=verify_{token}')
                btn = [
                    [InlineKeyboardButton("• ᴏᴘᴇɴ ʟɪɴᴋ •", url=link)],
                    [InlineKeyboardButton('• ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ •', url=TUT_VID)]
                ]
                return await message.reply(
                    f"<b>• Yᴏᴜʀ ᴛᴏᴋᴇɴ ʜᴀs ᴇxᴘɪʀᴇᴅ. Pʟᴇᴀsᴇ ʀᴇғʀᴇsʜ ʏᴏᴜʀ ᴛᴏᴋᴇɴ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.\n\n<blockquote>Tᴏᴋᴇɴ Tɪᴍᴇᴏᴜᴛ: {get_exp_time(VERIFY_EXPIRE)}</blockquote>\n\nWʜᴀᴛ ɪs ᴛʜᴇ ᴛᴏᴋᴇɴ?\n\nTʜɪs ɪs ᴀɴ ᴀᴅs ᴛᴏᴋᴇɴ. Pᴀssɪɴɢ ᴏɴᴇ ᴀᴅ ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ ғᴏʀ` {get_exp_time(VERIFY_EXPIRE)}</b>",
                    reply_markup=InlineKeyboardMarkup(btn),
                    protect_content=False,
                    quote=True
                )

    # Handle normal message flow
    text = message.text
    if len(text) > 7:
        user_id = message.from_user.id
        
        # Check for flood
        if await check_flood(user_id):
            wait_time = get_exp_time(FLOOD_WAIT)
            await message.reply(
                f"<b>ツ Pʟᴇᴀsᴇ ᴡᴀɪᴛ {wait_time} ʙᴇғᴏʀᴇ ʀᴇᴏ̨ᴜᴇsᴛɪɴɢ ᴛʜɪs ғɪʟᴇ ᴀɢᴀɪɴ.</b>\n\n"
                "<blockquote><i>Tʜɪs ɪs ᴛᴏ ᴘʀᴇᴠᴇɴᴛ ᴇxᴄᴇssɪᴠᴇ ʀᴇᴏ̨ᴜᴇsᴛs.</i></blockquote>"
            )
            return
            
        try:
            base64_string = text.split(" ", 1)[1]
        except IndexError:
            return

        string = await decode(base64_string)
        argument = string.split("-")

        ids = []
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
            except Exception as e:
                print(f"Error decoding IDs: {e}")
                return

        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except Exception as e:
                print(f"Error decoding ID: {e}")
                return

        # Handle file sending
        sent_msg = []
        
        # Get messages first
        temp_msg = await message.reply("• Pʟᴇᴀsᴇ ᴡᴀɪᴛ...")
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await message.reply_text("• Sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!")
            print(f"Error getting messages: {e}")
            return
        finally:
            await temp_msg.delete()

        # Delete the last text message from bot if it exists
        # try:
        #     async for msg in client.get_chat_history(message.chat.id, limit=1):
        #         if msg.from_user.is_bot and not msg.photo:
        #             await msg.delete()
        #             break
        # except:
        #     pass

        # Handle file sending
        sent_msg = []
        for msg in messages:
            try:
                # Skip empty messages
                if not msg:
                    continue
                    
                # Add delay between messages
                await asyncio.sleep(0.5)
                
                # Copy message with original caption
                reply_markup = msg.reply_markup if not DISABLE_CHANNEL_BUTTON else None
                sent = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=msg.caption.html if msg.caption else None,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                sent_msg.append(sent)
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
                # Retry after flood wait
                sent = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=msg.caption.html if msg.caption else None,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                sent_msg.append(sent)
            except Exception as e:
                print(f"Error sending message: {e}")
                continue

        # Handle auto-delete if enabled
        if FILE_AUTO_DELETE > 0 and sent_msg:
            try:
                user_id = message.from_user.id
                
                # Send notification first
                notification_msg = await message.reply(
                    f"<blockquote><b>This file will be deleted in <i>{get_exp_time(FILE_AUTO_DELETE)}</i>.\n"
                    "Please save or forward it to your saved messages before it gets deleted.</b></blockquote>"
                )

                # Create deletion task
                async def delete_files():
                    try:
                        await asyncio.sleep(FILE_AUTO_DELETE)
                        
                        # Delete sent messages one by one
                        for snt_msg in sent_msg:    
                            try:    
                                if snt_msg and not snt_msg.empty:
                                    await snt_msg.delete()
                                    await asyncio.sleep(0.5)  # Small delay between deletions
                            except Exception as e:
                                print(f"Error deleting message: {e}")
                                continue

                        # Delete notification message
                        try:
                            await notification_msg.delete()
                        except Exception as e:
                            print(f"Error deleting notification: {e}")

                        # Send "Get File Again" message
                        try:
                            reload_url = f"https://t.me/{client.username}?start={message.command[1]}" if len(message.command) > 1 else None
                            keyboard = InlineKeyboardMarkup([
                                [
                                    InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=reload_url),
                                    InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data="close_fileagain")
                                ]
                            ]) if reload_url else None

                            await message.reply(
                                "<b>ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!\n\nᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇</b>",
                                reply_markup=keyboard
                            )
                        except Exception as e:
                            print(f"Error sending get file again message: {e}")

                    except Exception as e:
                        print(f"Error in delete_files task: {e}")

                # Create deletion task
                asyncio.create_task(delete_files())

            except Exception as e:
                print(f"Error setting up auto-delete: {e}")
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("• Mᴏʀᴇ •", callback_data="more")],
            [
                InlineKeyboardButton("• Aʙᴏᴜᴛ", callback_data="about"),
                InlineKeyboardButton('Wʜᴏʟᴇsᴏᴍᴇ ও', url='https://t.me/Wholesomepics_Anime106exe')
            ]
        ])
        start_msg = await message.reply_photo(
            photo=random.choice(PICS),
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=keyboard
        )
        
        # Schedule message deletion
        if AUTO_DELETE_TIME > 0:
            await asyncio.sleep(AUTO_DELETE_TIME)
            try:
                await message.delete(1)
                await start_msg.delete()
            except:
                pass
        return


@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    # Add reaction to command
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass

    # Initialize buttons list
    buttons = []

    # Check if the first and second channels are both set
    if FORCE_SUB_CHANNEL1 and FORCE_SUB_CHANNEL2:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink1),
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink2),
        ])
    # Check if only the first channel is set
    elif FORCE_SUB_CHANNEL1:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink1)
        ])
    # Check if only the second channel is set
    elif FORCE_SUB_CHANNEL2:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink2)
        ])

    # Check if the third and fourth channels are set
    if FORCE_SUB_CHANNEL3 and FORCE_SUB_CHANNEL4:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink3),
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink4),
        ])
    # Check if only the third channel is set
    elif FORCE_SUB_CHANNEL3:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink3)
        ])
    # Check if only the fourth channel is set
    elif FORCE_SUB_CHANNEL4:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink4)
        ])

    # Always add the Try Again button, with proper error handling
    try:
        verify_url = f"https://t.me/{client.username}?start=verify_{message.command[1]}"
    except IndexError:
        verify_url = f"https://t.me/{client.username}?start=verify_start"
    
    buttons.append([
        InlineKeyboardButton(text="• ᴛʀʏ ᴀɢᴀɪɴ/Rᴇʟᴏᴀᴅ •", url=verify_url)
    ])

    force_msg = await message.reply_photo(
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

    # Schedule message deletion
    if AUTO_DELETE_TIME > 0:
        await asyncio.sleep(AUTO_DELETE_TIME)
        try:
            await message.delete(1)
            await force_msg.delete()
        except:
            pass


WAIT_MSG = "<b>Wᴏʀᴋɪɴɢ....</b>"

REPLY_ERROR = "<code>Usᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴇssᴀɢᴇ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ sᴘᴀᴄᴇs.</code>"



@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
@check_user_ban
async def get_users(client: Bot, message: Message):
    try:
        # Send initial processing message
        msg = await message.reply_text("<b>•・Pʀᴏᴄᴇssɪɴɢ ᴜsᴇʀ ᴅᴀᴛᴀ...</b>")
        
        # Get all users
        users = await full_userbase()
        if not users:
            await msg.edit("ツ Nᴏ ᴜsᴇʀs ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ!")
            return
            
        # Prepare user data
        user_data = []
        total_users = len(users)
        
        for user_id in users:
            try:
                user = await client.get_users(user_id)
                user_info = (
                    f"⤹ <b>Nᴀᴍᴇ:</b> {user.first_name}"
                    f"{' ' + user.last_name if user.last_name else ''}\n"
                    f"⤹ <b>Iᴅ:</b> <code>{user.id}</code>\n"
                    f"⤹ <b>Usᴇʀɴᴀᴍᴇ:</b> @{user.username if user.username else 'None'}\n"
                    f"⤹ <b>Cᴏɴᴛᴀᴄᴛ:</b> {user.mention}\n"
                    "───────────────────"
                )
                user_data.append(user_info)
            except Exception as e:
                print(f"Error getting user {user_id}: {e}")
                user_data.append(f"⊱ Usᴇʀ ID: {user_id} (Error fetching details)\n───────────────────")

        # If user list is too long, create a text file
        if total_users > 50:
            # Create text file
            file_path = "users_data.txt"
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(f"Total Users: {total_users}\n\n")
                f.write("\n".join(user_data))
            
            # Send file with caption
            await message.reply_document(
                document=file_path,
                caption=f"<b>❝ Tᴏᴛᴀʟ Usᴇʀs:</b> {total_users}\n<b>• Dᴀᴛᴀ:</b> Fᴜʟʟ ᴜsᴇʀ ʟɪsᴛ ᴀᴛᴛᴀᴄʜᴇᴅ",
                quote=True
            )
            
            # Clean up
            try:
                os.remove(file_path)
            except:
                pass
            
        else:
            # Send as message for smaller lists
            response = (
                f"<b>⤹ Tᴏᴛᴀʟ Usᴇʀs:</b> {total_users}\n\n"
                f"{chr(10).join(user_data)}"
            )
            await msg.edit(response)
            
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")


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

async def check_flood(user_id: int) -> bool:
    """Check if user has exceeded request limit"""
    now = datetime.now()
    user_requests[user_id] = [t for t in user_requests[user_id] if now - t < timedelta(seconds=FLOOD_TIME)]
    
    if len(user_requests[user_id]) >= FLOOD_LIMIT:
        return True
        
    user_requests[user_id].append(now)
    return False
