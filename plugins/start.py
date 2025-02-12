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

# File auto-delete time in seconds (Set your desired time in seconds here)
FILE_AUTO_DELETE = TIME  # Example: 3600 seconds (1 hour)
TUT_VID = f"{TUT_VID}"

# Add these constants at the top
BROADCAST_CHUNK_SIZE = 100  # Number of users to broadcast to at once
MAX_RETRIES = 3  # Maximum number of retry attempts for failed broadcasts
WAIT_ANIMATION_TEXT = "○ ○ ○"
ANIMATION_FRAMES = ["● ○ ○", "● ● ○", "● ● ●"]
ANIMATION_INTERVAL = 0.3  # Speed of animation in seconds

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
        
    # Show loading animation first
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
                    f"<b>Your token has expired. Please refresh your token to continue.\n\nToken Timeout: {get_exp_time(VERIFY_EXPIRE)}\n\nWhat is the token?\n\nThis is an ads token. Passing one ad allows you to use the bot for {get_exp_time(VERIFY_EXPIRE)}</b>",
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

        temp_msg = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await message.reply_text("Something went wrong!")
            print(f"Error getting messages: {e}")
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
                print(f"Failed to send message: {e}")
                pass

        if FILE_AUTO_DELETE > 0:
            notification_msg = await message.reply(
                f"<b>This file will be deleted in {get_exp_time(FILE_AUTO_DELETE)}. Please save or forward it to your saved messages before it gets deleted.</b>"
            )

            await asyncio.sleep(FILE_AUTO_DELETE)

            for snt_msg in sent_messages:    
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
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Get File Again!", url=reload_url)]]
                ) if reload_url else None

                # Edit the notification message instead of deleting and sending new
                await edit_message_with_photo(
                    notification_msg,
                    photo=random.choice(PICS),
                    caption="<b>ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!\n\nᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇</b>",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Error updating notification with 'Get File Again' button: {e}")
    else:
        # Delete the loading animation
        await loading_msg.delete()
        
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("More", callback_data="more")
            ],
            [
                InlineKeyboardButton("⚡️ ᴀʙᴏᴜᴛ", callback_data="about"),
                InlineKeyboardButton('🍁 sᴇʀɪᴇsғʟɪx', url='https://t.me/Team_Netflix/40')
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
                text="ʀᴇʟᴏᴀᴅ",
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

WAIT_MSG = "<b>Working....</b>"

REPLY_ERROR = "<code>Use this command as a reply to any telegram message without any spaces.</code>"

#=====================================================================================##


@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

# Add these utility functions
async def get_verify_status(user_id: int):
    """Cache verify status to reduce database hits"""
    return await _get_verify_status(user_id)  # Actual database query function

async def get_messages(client, ids):
    """Cache message fetching to reduce API calls"""
    return await _get_messages(client, ids)

async def send_broadcast_to_chunk(client: Bot, message: Message, users) -> tuple:
    """Send broadcast to a chunk of users and return statistics"""
    successful = blocked = deleted = unsuccessful = 0
    failed_users = []
    
    for chat_id in users:
        try:
            await message.copy(chat_id)
            successful += 1
            await asyncio.sleep(0.1)  # Rate limiting to prevent floods
        except FloodWait as e:
            await asyncio.sleep(e.x)
            try:
                await message.copy(chat_id)
                successful += 1
            except:
                unsuccessful += 1
                failed_users.append(chat_id)
        except UserIsBlocked:
            blocked += 1
            await del_user(chat_id)
        except InputUserDeactivated:
            deleted += 1
            await del_user(chat_id)
        except Exception:
            unsuccessful += 1
            failed_users.append(chat_id)
            
    return successful, blocked, deleted, unsuccessful, failed_users

# Replace the existing broadcast command with this improved version
@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def broadcast_handler(client: Bot, message: Message):
    if not message.reply_to_message:
        await message.reply(REPLY_ERROR)
        return

    status_msg = await message.reply_photo(
        photo=random.choice(PICS),
        caption="<i>Starting broadcast...</i>",
        has_spoiler=True
    )
    broadcast_msg = message.reply_to_message
    
    try:
        all_users = await full_userbase()
        total_users = len(all_users)
        
        if total_users == 0:
            await status_msg.edit_caption("No users found in database!")
            return

        # Split users into chunks
        chunks = [all_users[i:i + BROADCAST_CHUNK_SIZE] for i in range(0, len(all_users), BROADCAST_CHUNK_SIZE)]
        total_chunks = len(chunks)
        
        # Initialize counters
        total_success = total_blocked = total_deleted = total_unsuccessful = 0
        failed_users = []
        
        # Process each chunk
        for index, chunk in enumerate(chunks, 1):
            retry_count = 0
            chunk_success = False
            
            while not chunk_success and retry_count < MAX_RETRIES:
                try:
                    success, blocked, deleted, unsuccessful, failed = await send_broadcast_to_chunk(
                        client, broadcast_msg, chunk
                    )
                    chunk_success = True
                    
                    # Update counters
                    total_success += success
                    total_blocked += blocked
                    total_deleted += deleted
                    total_unsuccessful += unsuccessful
                    failed_users.extend(failed)

                    # Update status message periodically
                    if index % 5 == 0 or index == total_chunks:
                        progress = f"<b>Broadcast Progress: {index}/{total_chunks} chunks</b>\n\n"
                        progress += f"Total Users: {total_users}\n"
                        progress += f"✅ Successful: {total_success}\n"
                        progress += f"🚫 Blocked: {total_blocked}\n"
                        progress += f"❌ Deleted: {total_deleted}\n"
                        progress += f"📝 Failed: {total_unsuccessful}\n"
                        progress += f"\nProcessing chunk {index}..."
                        
                        await status_msg.edit_caption(progress)
                        
                except Exception as e:
                    retry_count += 1
                    if retry_count == MAX_RETRIES:
                        await message.reply(f"⚠️ Failed to process chunk {index}/{total_chunks} after {MAX_RETRIES} attempts.\nError: {str(e)}")
                    await asyncio.sleep(5)

        # Final status message
        final_status = f"<b>📊 Broadcast Completed!</b>\n\n"
        final_status += f"Total Users: {total_users}\n"
        final_status += f"✅ Successful: {total_success}\n"
        final_status += f"🚫 Blocked: {total_blocked}\n"
        final_status += f"❌ Deleted: {total_deleted}\n"
        final_status += f"📝 Failed: {total_unsuccessful}"

        if failed_users:
            with open('failed_broadcasts.txt', 'w') as f:
                f.write('\n'.join(map(str, failed_users)))
            await message.reply_document(
                'failed_broadcasts.txt',
                caption="List of users where broadcast failed"
            )

        await status_msg.edit_caption(final_status)

    except Exception as e:
        await status_msg.edit_caption(f"<b>❌ Broadcast Failed!</b>\n\nError: {str(e)}")
        await message.reply(f"⚠️ Broadcast system encountered a critical error: {str(e)}")

# Add this helper function at the top with other utilities
async def edit_message_with_photo(message: Message, photo, caption, reply_markup=None):
    """Helper function to edit message with photo while preserving message ID"""
    try:
        # Try to edit existing photo message
        if getattr(message, 'photo', None):
            return await message.edit_media(
                media=InputMediaPhoto(photo, caption=caption, has_spoiler=True),
                reply_markup=reply_markup
            )
        # If not a photo message, delete and send new
        await message.delete()
        return await message.reply_photo(
            photo=photo,
            caption=caption,
            reply_markup=reply_markup,
            has_spoiler=True
        )
    except Exception as e:
        print(f"Error in edit_message_with_photo: {e}")
        # Fallback to delete and send new
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

# Modify the loading animation function to use edit
async def show_loading_animation(message: Message):
    """Shows an animated loading message"""
    # First animation cycle
    loading_msg = await message.reply_photo(
        photo=random.choice(PICS),
        caption=WAIT_ANIMATION_TEXT,
        has_spoiler=True
    )
    
    for _ in range(2):  # Run animation 2 times
        for frame in ANIMATION_FRAMES:
            await sleep(ANIMATION_INTERVAL)
            try:
                await loading_msg.edit_caption(frame)
            except Exception as e:
                print(f"Error in animation frame update: {e}")
        # Reset animation
        await sleep(ANIMATION_INTERVAL)
        try:
            await loading_msg.edit_caption(WAIT_ANIMATION_TEXT)
        except Exception as e:
            print(f"Error in animation reset: {e}")
    
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
        print(f"Error in auto-delete: {e}")
        pass