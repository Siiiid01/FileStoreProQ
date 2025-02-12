import asyncio
import os
import random
import sys
import time
import string
import string as rohit
import humanize
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, MessageNotModified
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import *
from helper_func import *
from database.database import *

# Constants
FILE_AUTO_DELETE = TIME  # Example: 3600 seconds (1 hour)
CACHE_TIME = 3600  # 1 hour cache time
INACTIVITY_TIMEOUT = 600  # 10 minutes
message_cache = {}

async def show_loading_animation(message):
    """Shows a dynamic loading animation"""
    loading_symbols = ["○ ○ ○", "● ○ ○", "● ● ○", "● ● ●", "○ ● ●", "○ ○ ●"]
    loading_msg = await message.reply_text("ᴘʀᴏᴄᴇssɪɴɢ...")
    
    for _ in range(2):  # 2 cycles of animation
        for symbol in loading_symbols:
            await asyncio.sleep(0.3)  # 0.3 seconds delay between frames
            try:
                await loading_msg.edit_text(f"ᴘʀᴏᴄᴇssɪɴɢ... {symbol}")
            except MessageNotModified:
                pass
    
    return loading_msg

async def auto_delete(message, timeout=INACTIVITY_TIMEOUT):
    """Auto delete messages after timeout"""
    await asyncio.sleep(timeout)
    try:
        await message.delete()
    except:
        pass

async def send_file_message(client, user_id, msg, reply_markup=None):
    """Send file with caching"""
    cache_key = f"{user_id}_{msg.id}"
    
    if cache_key in message_cache:
        return message_cache[cache_key]
    
    try:
        sent_msg = await msg.copy(
            chat_id=user_id,
            reply_markup=reply_markup,
            protect_content=PROTECT_CONTENT
        )
        message_cache[cache_key] = sent_msg
        
        # Clear cache after CACHE_TIME
        await asyncio.sleep(CACHE_TIME)
        message_cache.pop(cache_key, None)
        
        return sent_msg
    except Exception as e:
        print(f"Error sending file: {e}")
        return None

@Bot.on_message(filters.command('start') & filters.private & subscribed1 & subscribed2 & subscribed3 & subscribed4)
async def start_command(client: Client, message: Message):
    try:
        # Delete command message
        await message.delete()
    except:
        pass

    # Show loading animation
    loading_msg = await show_loading_animation(message)
    
    try:
        await message.react("🔥", big=True)
    except:
        pass

    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
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
                token = ''.join(random.choices(rohit.ascii_letters + rohit.digits, k=10))
                await update_verify_status(id, verify_token=token, link="")
                link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://telegram.dog/{client.username}?start=verify_{token}')
                btn = [
                    [InlineKeyboardButton("• ᴏᴘᴇɴ ʟɪɴᴋ •", url=link)],
                    [InlineKeyboardButton('• ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ •', url=TUT_VID)]
                ]
                return await message.reply(
                    f"<b>Your token has expired. Please refresh your token to continue.\n\nToken Timeout: {get_exp_time(VERIFY_EXPIRE)}\n\nWhat is the token?\n\nThis is an ads token. Passing one ad allows you to use the bot for {get_exp_time(VERIFY_EXPIRE)}</b>",
                    reply_markup=InlineKeyboardMarkup(btn),
                    protect_content=False,
                    quote=True
                )

    # Handle normal message flow
    text = message.text
    if len(text) > 7:
        # File sharing logic
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

        temp_msg = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await message.reply_text("Something went wrong!")
            print(f"Error getting messages: {e}")
            return
        finally:
            await temp_msg.delete()

        sent_files = []
        for msg in messages:
            caption = (CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, 
                                             filename=msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document)
                       else ("" if not msg.caption else msg.caption.html))

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                sent_msg = await msg.copy(
                    chat_id=message.from_user.id, 
                    caption=caption, 
                    parse_mode=ParseMode.HTML, 
                    reply_markup=reply_markup, 
                    protect_content=PROTECT_CONTENT
                )
                sent_files.append(sent_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                sent_msg = await msg.copy(
                    chat_id=message.from_user.id, 
                    caption=caption, 
                    parse_mode=ParseMode.HTML, 
                    reply_markup=reply_markup, 
                    protect_content=PROTECT_CONTENT
                )
                sent_files.append(sent_msg)
            except Exception as e:
                print(f"Failed to send message: {e}")
                continue

        if FILE_AUTO_DELETE > 0:
            notification_msg = await message.reply_photo(
                photo=random.choice(PICS),
                caption=f"<b>⚠️ This file will be deleted in {get_exp_time(FILE_AUTO_DELETE)}.\n\nPlease save or forward it to your saved messages.</b>"
            )

            await asyncio.sleep(FILE_AUTO_DELETE)

            for sent_file in sent_files:    
                if sent_file:
                    try:    
                        await sent_file.delete()  
                    except Exception as e:
                        print(f"Error deleting message {sent_file.id}: {e}")

            try:
                reload_url = (
                    f"https://t.me/{client.username}?start={message.command[1]}"
                    if message.command and len(message.command) > 1
                    else None
                )
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Get File Again", url=reload_url)
                ]]) if reload_url else None

                await notification_msg.edit(
                    photo=random.choice(PICS),
                    caption="<b>ʏᴏᴜʀ ꜰɪʟᴇs ʜᴀᴠᴇ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ!\n\nᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ᴛʜᴇᴍ ᴀɢᴀɪɴ 👇</b>",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Error updating notification: {e}")
    else:
        # Normal start message
        buttons = [
            [
                InlineKeyboardButton("⚡️ ᴀʙᴏᴜᴛ", callback_data="about"),
                InlineKeyboardButton("📑 ᴍᴏʀᴇ", callback_data="more")
            ],
            [
                InlineKeyboardButton("🍁 sᴇʀɪᴇsғʟɪx", url='https://t.me/Team_Netflix/40')
            ]
        ]
        
        start_msg = await loading_msg.edit_text(
            START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        
        # Schedule message deletion
        asyncio.create_task(auto_delete(start_msg))

#=====================================================================================##
# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    # Initialize buttons list
    buttons = []

    # Check if the first and second channels are both set
    if FORCE_SUB_CHANNEL1 and FORCE_SUB_CHANNEL2:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink1),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink2),
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
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink3),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink4),
        ])
    # Check if only the first channel is set
    elif FORCE_SUB_CHANNEL3:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink3)
        ])
    # Check if only the second channel is set
    elif FORCE_SUB_CHANNEL4:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink4)
        ])

    # Append "Try Again" button if the command has a second argument
    try:
        buttons.append([
            InlineKeyboardButton(
                text="ʀᴇʟᴏᴀᴅ",
                url=f"https://t.me/{client.username}?start={message.command[1]}"
            )
        ])
    except IndexError:
        pass  # Ignore if no second argument is present

    await message.reply_photo(
        photo=random.choice(PICS),
        caption=FORCE_MSG.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=None if not message.from_user.username else '@' + message.from_user.username,
        mention=message.from_user.mention,
        id=message.from_user.id
    ),
    reply_markup=InlineKeyboardMarkup(buttons)#,
    #message_effect_id=5104841245755180586  # Add the effect ID here
)


#=====================================================================================##

WAIT_MSG = "<b>Working....</b>"

REPLY_ERROR = "<code>Use this command as a reply to any telegram message without any spaces.</code>"

#=====================================================================================##


@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def broadcast_handler(client: Bot, message: Message):
    if not message.reply_to_message:
        await message.reply("Please reply to a message to broadcast!")
        return

    # Show loading animation
    loading_msg = await show_loading_animation(message)
    
    users = await full_userbase()
    broadcast_msg = message.reply_to_message
    
    success = 0
    failed = 0
    blocked = 0
    deleted = 0
    
    progress_msg = await message.reply_text("Broadcasting messages...")
    
    for user_id in users:
        try:
            await broadcast_msg.copy(
                chat_id=user_id,
                parse_mode=ParseMode.HTML
            )
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await broadcast_msg.copy(
                chat_id=user_id,
                parse_mode=ParseMode.HTML
            )
            success += 1
        except UserIsBlocked:
            blocked += 1
            await del_user(user_id)
        except InputUserDeactivated:
            deleted += 1
            await del_user(user_id)
        except Exception:
            failed += 1
            
        # Update progress message periodically
        if (success + failed + blocked + deleted) % 20 == 0:
            try:
                await progress_msg.edit_text(
                    f"Broadcast in progress...\n\n"
                    f"Success: {success}\n"
                    f"Failed: {failed}\n"
                    f"Blocked: {blocked}\n"
                    f"Deleted: {deleted}"
                )
            except:
                pass
    
    # Final broadcast status
    await progress_msg.edit_text(
        f"<b>Broadcast Completed!</b>\n\n"
        f"Total Users: {len(users)}\n"
        f"Successful: {success}\n"
        f"Blocked Users: {blocked}\n"
        f"Deleted Accounts: {deleted}\n"
        f"Failed: {failed}"
    )