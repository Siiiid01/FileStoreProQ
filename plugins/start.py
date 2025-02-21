import asyncio
import os
import random
import sys
import time
import string
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

# File auto-delete time in seconds (Set your desired time in seconds here)
FILE_AUTO_DELETE = TIME  # Example: 3600 seconds (1 hour)
TUT_VID = f"{TUT_VID}"

# Add these constants at the top with other constants
AUTO_DELETE_TIME = 600  # 10 minutes in seconds
EXEMPT_FROM_DELETE = ['Get File Again!', 'broadcast']  # Messages that shouldn't be deleted
LOADING_ANIMATION = ["\\", "|", "/", "─"]
ANIMATION_INTERVAL = 0.2  # Adjust for smoother animation


async def show_loading(client: Client, message: Message):
    """Shows a smooth loading animation"""
    if not message or not message.from_user:
        return

    try:
        loading_message = await message.reply_text("Iɴɪᴛɪᴀʟɪᴢɪɴɢ \\")
    except UserIsBlocked:
        return
    except Exception as e:
        from plugins.logs import log_error
        log_error(f"Error sending initial loading message: {str(e)}")
        return

    animation_completed = False
    try:
        for _ in range(2):  # Run animation 2 cycles
            for frame in LOADING_ANIMATION:
                await asyncio.sleep(ANIMATION_INTERVAL)
                try:
                    await loading_message.edit_text(f"Iɴɪᴛɪᴀʟɪᴢɪɴɢ {frame}")
                except UserIsBlocked:
                    return
                except MessageNotModified:
                    continue  # Just skip this frame
                except Exception as e:
                    from plugins.logs import log_error
                    log_error(f"Animation frame error: {str(e)}")
                    continue
        animation_completed = True
    finally:
        if animation_completed:
            try:
                await loading_message.delete()
            except (MessageIdInvalid, UserIsBlocked):
                pass  # Message already deleted or user blocked
            except Exception as e:
                from plugins.logs import log_error
                log_error(f"Error deleting loading message: {str(e)}")

@Bot.on_message(filters.command('start') & filters.private & subscribed1 & subscribed2 & subscribed3 & subscribed4)
async def start_command(client: Client, message: Message):
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
                    return await message.reply("Your token is invalid or expired. Try again by clicking /start.")
                await update_verify_status(id, is_verified=True, verified_time=time.time())
                if verify_status["link"] == "":
                    reply_markup = None
                return await message.reply(
                    f"Your token has been successfully verified and is valid for {get_exp_time(VERIFY_EXPIRE)}",
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

        # Replace the temp_msg block with direct message handling
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            error_msg = await message.reply_text("Sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!")
            await asyncio.sleep(10)  # Wait 3 seconds
            try:
                await error_msg.delete()
            except:
                pass
            print(f"Error getting messages: {e}")
            return

        # Delete the last text message from bot if it exists
        # try:
        #     async for msg in client.get_chat_history(message.chat.id, limit=1):
        #         if msg.from_user.is_bot and not msg.photo:
        #             await msg.delete()
        #             break
        # except:
        #     pass

        sent_msg = []
        for msg in messages:
            # Skip empty messages
            if not msg or (not msg.document and not msg.video and not msg.photo and not msg.text and not msg.audio):
                continue

            caption = (CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, 
                                             filename=msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document)
                       else ("" if not msg.caption else msg.caption.html))

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                sent_msg.append(copied_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                sent_msg.append(copied_msg)
            except Exception as e:
                print(f"Failed to send message: {e}")
                pass

        if FILE_AUTO_DELETE > 0:
            notification_msg = await message.reply(
                f"<blockquote><b>Tʜɪs ғɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ {get_exp_time(FILE_AUTO_DELETE)}.</blockquote>\nPʟᴇᴀsᴇ sᴀᴠᴇ ᴏʀ ғᴏʀᴡᴀʀᴅ ɪᴛ ᴛᴏ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ʙᴇғᴏʀᴇ ɪᴛ ɢᴇᴛs ᴅᴇʟᴇᴛᴇᴅ.</b>"
            )

            await asyncio.sleep(FILE_AUTO_DELETE)

            for snt_msg in sent_msg:    
                if snt_msg:
                    try:    
                        await snt_msg.delete()  
                    except Exception as e:
                        print(f"Error deleting message {snt_msg.id}: {e}")

            try:
                reload_url = (
                    f"https://t.me/{client.username}?start={message.command[1]}"
                    if message.command and len(message.command) > 1
                    else None
                )
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=reload_url)],
                    [InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data="close_fileagain")]
                    ]
                ) if reload_url else None

                await notification_msg.edit(
                    "<b>ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!\n\nᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇</b>",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Error updating notification with 'Get File Again' button: {e}")
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
                await message.delete()
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
            await message.delete()
            await force_msg.delete()
        except:
            pass


WAIT_MSG = "<b>Wᴏʀᴋɪɴɢ....</b>"

REPLY_ERROR = "<code>Usᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴇssᴀɢᴇ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ sᴘᴀᴄᴇs.</code>"



@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} ᴜsᴇʀs ᴀʀᴇ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ 卐")


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