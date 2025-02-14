import asyncio
import os
import random
import sys
import time
import string
import humanize
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import *
from helper_func import *
from database.database import *
from asyncio import sleep
from datetime import datetime

# File auto-delete time in seconds (Set your desired time in seconds here)
FILE_AUTO_DELETE = TIME  # Example: 3600 seconds (1 hour)
TUT_VID = f"{TUT_VID}"

# Add these constants at the top
WAIT_ANIMATION_TEXT = "○ ○ ○"
ANIMATION_FRAMES = ["● ○ ○", "● ● ○", "● ● ●"]
ANIMATION_INTERVAL = 0.13  # Speed of animation in seconds

# Add at the top with other constants
AUTO_DELETE_TIME = 600  # 10 minutes in seconds
EXEMPT_FROM_DELETE = ['Get File Again!', 'broadcast']  # Messages that shouldn't be deleted

@Bot.on_message(filters.command('start') & filters.private & subscribed1 & subscribed2 & subscribed3 & subscribed4)
async def start_command(client: Client, message: Message):
    # Add reaction to start command
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass
        
    # Show loading animation
    loading_msg = await show_loading_animation(message)
    
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
                    return await message.reply("• ʏᴏᴜʀ ᴛᴏᴋᴇɴ ɪꜱ ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ. ᴛʀʏ ᴀɢᴀɪɴ ʙʏ ᴄʟɪᴄᴋɪɴɢ /ꜱᴛᴀʀᴛ.")
                await update_verify_status(id, is_verified=True, verified_time=time.time())
                if verify_status["link"] == "":
                    reply_markup = None
                return await message.reply(
                    f"• 🇾​​🇴​​🇺​​🇷​ ​🇹​​🇴​​🇰​​🇪​​🇳​ ​🇭​​🇦​​🇸​ ​🇧​​🇪​​🇪​​🇳​ ​🇸​​🇺​​🇨​​🇨​​🇪​​🇸​​🇸​​🇫​​🇺​​🇱​​🇱​​🇾​ ​🇻​​🇪​​🇷​​🇮​​🇫​​🇮​​🇪​​🇩​ ​🇦​​🇳​​🇩​ ​🇮​​🇸​ ​🇻​​🇦​​🇱​​🇮​​🇩​ ​🇫​​🇴​​🇷​ {get_exp_time(VERIFY_EXPIRE)}",
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
                    f"<b>ʏᴏᴜʀ ᴛᴏᴋᴇɴ ʜᴀꜱ ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀꜱᴇ ʀᴇꜰʀᴇꜱʜ ʏᴏᴜʀ ᴛᴏᴋᴇɴ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.\n\nᴛᴏᴋᴇɴ ᴛɪᴍᴇᴏᴜᴛ {get_exp_time(VERIFY_EXPIRE)}\n\n​🇼​​🇭​​🇦​​🇹​ ​🇮​​🇸​ ​🇹​​🇭​​🇪​ ​🇹​​🇴​​🇰​​🇪​​🇳​?\n\n🇹​​🇭​​🇮​​🇸​ ​🇮​​🇸​ ​🇦​​🇳​ ​🇦​​🇩​​🇸​ ​🇹​​🇴​​🇰​​🇪​​🇳​. ​🇵​​🇦​​🇸​​🇸​​🇮​​🇳​​🇬​ ​🇴​​🇳​​🇪​ ​🇦​​🇩​ ​🇦​​🇱​​🇱​​🇴​​🇼​​🇸​ ​🇾​​🇴​​🇺​ ​🇹​​🇴​ ​🇺​​🇸​​🇪​ ​🇹​​🇭​​🇪​ ​🇧​​🇴​​🇹​ ​🇫​​🇴​​🇷​ {get_exp_time(VERIFY_EXPIRE)}</b>",
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
                print(f"⚠︎ Error Decoding Id's: {e}")
                return

        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except Exception as e:
                print(f"⚠︎ Error Decoding Id's: {e}")
                return

        temp_msg = await message.reply("ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...")
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await message.reply_text("⚠︎ ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!")
            print(f"⚠︎ Error Getting Messages: {e}")
            return
        finally:
            await temp_msg.delete()

        sent_messages = []
        for msg in messages:
            caption = (CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, 
                                             filename=msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document)
                       else ("" if not msg.caption else msg.caption.html))

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                sent_messages.append(copied_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                sent_messages.append(copied_msg)
            except Exception as e:
                print(f"⚠︎ Failed to send message {e}")
                pass

        if FILE_AUTO_DELETE > 0:
            notification_msg = await message.reply(
                f"<b>ᴛʜɪꜱ ꜰɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ {get_exp_time(FILE_AUTO_DELETE)}. ᴘʟᴇᴀꜱᴇ ꜱᴀᴠᴇ ᴏʀ ꜰᴏʀᴡᴀʀᴅ ɪᴛ ᴛᴏ ʏᴏᴜʀ ꜱᴀᴠᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ ʙᴇꜰᴏʀᴇ ɪᴛ ɢᴇᴛꜱ ᴅᴇʟᴇᴛᴇᴅ.</b>"
            )

            await asyncio.sleep(FILE_AUTO_DELETE)

            for snt_msg in sent_messages:    
                if snt_msg:
                    try:    
                        await snt_msg.delete()  
                    except Exception as e:
                        print(f"⚠︎ Error Deleting Message {snt_msg.id}: {e}")

            try:
                reload_url = (
                    f"https://t.me/{client.username}?start={message.command[1]}"
                    if message.command and len(message.command) > 1
                    else None
                )
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("• ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ! •", url=reload_url)]]
                ) if reload_url else None

                # Edit the notification message instead of deleting and sending new
                await edit_message_with_photo(
                    notification_msg,
                    photo=random.choice(PICS),
                    caption="<b>• ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!\n\n• ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇</b>",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"⚠︎ Error Updating Notification With 'get file again' Button: {e}")
    else:
        # Delete the loading message before showing start menu
        await loading_msg.delete()
        
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴍᴏʀᴇ •", callback_data="more")
            ],
    [
                InlineKeyboardButton("• ᴀʙᴏᴜᴛ •", callback_data="about"),
                InlineKeyboardButton('• sᴇʀɪᴇsғʟɪx •', url='https://t.me/Moviess_Ok')
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
            reply_markup=reply_markup,
            has_spoiler=True
            #message_effect_id=5104841245755180586  # 🔥
        )
        
        # Schedule message for deletion after 10 minutes
        asyncio.create_task(auto_delete_message(start_msg, AUTO_DELETE_TIME))
        return



#=====================================================================================##


@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    # Add reaction to start command
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass
        
    # Show loading animation first
    loading_msg = await show_loading_animation(message)
    
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
                text="• ʀᴇʟᴏᴀᴅ •",
                url=f"https://t.me/{client.username}?start={message.command[1]}"
            )
        ])
    except IndexError:
        pass  # Ignore if no second argument is present

    # Delete loading animation before sending final message
    await loading_msg.delete()
    
    force_msg = await message.reply_photo(
        photo=random.choice(PICS),
        caption=FORCE_MSG.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=None if not message.from_user.username else '@' + message.from_user.username,
        mention=message.from_user.mention,
        id=message.from_user.id
    ),
    reply_markup=InlineKeyboardMarkup(buttons),
    #message_effect_id=5104841245755180586  # 🔥
    has_spoiler=True
)
    
    # Schedule force message for deletion
    asyncio.create_task(auto_delete_message(force_msg, AUTO_DELETE_TIME))


#=====================================================================================##

WAIT_MSG = "<b>• ​🇼​​🇴​​🇷​​🇰​​🇮​​🇳​​🇬​....</b>"

REPLY_ERROR = "<code>• ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴀꜱ ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴇꜱꜱᴀɢᴇ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ ꜱᴘᴀᴄᴇꜱ.</code>"

#=====================================================================================##


@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} ᴜꜱᴇʀꜱ ᴀʀᴇ ᴜꜱɪɴɢ ᴛʜɪꜱ ʙᴏᴛ")

# Modify the loading animation function to use edit
async def show_loading_animation(message: Message):
    """Shows an animated loading message"""
    # First animation cycle
    loading_msg = await message.reply_photo(
        photo=random.choice(PICS),
        caption=WAIT_ANIMATION_TEXT,
        has_spoiler=True
    )
    
    try:
        for _ in range(2):  # Run animation 2 times
            for frame in ANIMATION_FRAMES:
                await asyncio.sleep(ANIMATION_INTERVAL)
                if frame != loading_msg.caption:  # Only edit if content is different
                    await loading_msg.edit_caption(frame)
            # Reset animation
            await asyncio.sleep(ANIMATION_INTERVAL)
            if WAIT_ANIMATION_TEXT != loading_msg.caption:  # Only edit if content is different
                await loading_msg.edit_caption(WAIT_ANIMATION_TEXT)
    except Exception as e:
        print(f"⚠︎ Error In Animation {e}")
        
    return loading_msg

# Add the auto-delete utility function
async def auto_delete_message(message: Message, delay: int):
    """Delete a message after specified delay unless it contains exempt text"""
    await asyncio.sleep(delay)
    
    try:
        # Check if message contains any exempt text
        if message and message.caption:
            if any(exempt_text in message.caption for exempt_text in EXEMPT_FROM_DELETE):
                return
                
        # Check if message has exempt buttons
        if message and message.reply_markup:
            for row in message.reply_markup.inline_keyboard:
                for button in row:
                    if any(exempt_text in button.text for exempt_text in EXEMPT_FROM_DELETE):
                        return
                        
        await message.delete()
    except Exception as e:
        print(f"⚠︎ Error In Auto Delete: {e}")
        pass

# Keep these utility functions as they're used by other features
async def edit_message_with_photo(message: Message, photo, caption, reply_markup=None):
    """Helper function to edit message with photo while preserving message ID"""
    try:
        if getattr(message, 'photo', None):
            # Check if content is actually different
            current_caption = getattr(message, 'caption', None)
            current_markup = getattr(message, 'reply_markup', None)
            
            if (current_caption != caption or 
                str(current_markup) != str(reply_markup)):
                return await message.edit_media(
                    media=InputMediaPhoto(photo, caption=caption, has_spoiler=True),
                    reply_markup=reply_markup
                )
            return message  # Return existing message if no changes needed
            
        await message.delete()
        return await message.reply_photo(
            photo=photo,
            caption=caption,
            reply_markup=reply_markup,
            has_spoiler=True
        )
    except Exception as e:
        print(f"Error in edit_message_with_photo: {e}")
        try:
            await message.delete()
            return await message.reply_photo(
                photo=photo,
                caption=caption,
                reply_markup=reply_markup,
                has_spoiler=True
            )
        except Exception as e:
            print(f"Error in fallback photo send: {e}")
            return None

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