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
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import *
from helper_func import *
from database.database import *
from datetime import datetime
import logging
from typing import Union, List, Dict
from cachetools import TTLCache

# File auto-delete time in seconds (Set your desired time in seconds here)
FILE_AUTO_DELETE = TIME  # Example: 3600 seconds (1 hour)
TUT_VID = f"{TUT_VID}"

# Cache frequently used values
CACHE_TIME = 3600  # 1 hour cache time
message_cache = {}

# Add constants for broadcast
BROADCAST_CHUNK_SIZE = 100
BROADCAST_FAILURE_THRESHOLD = 0.5  # 50% failure threshold
MAX_RETRIES = 3

# Add cache for users and channels
user_cache = TTLCache(maxsize=1000, ttl=3600)  # Cache user info for 1 hour
channel_cache = TTLCache(maxsize=100, ttl=3600)  # Cache channel info for 1 hour

@Bot.on_message(filters.command('start') & filters.private & subscribed1 & subscribed2 & subscribed3 & subscribed4)
async def start_command(client: Client, message: Message):
    try:
        # Check subscription status
        sub_status = await check_subscription(client, message.from_user.id)
        if not sub_status["subscribed"]:
            return await handle_not_subscribed(client, message, sub_status["channels"])
            
        # Add reaction
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except Exception as e:
        print(f"Failed to add reaction: {e}")
        pass
    
    # Delete command after 10 minutes
    asyncio.create_task(delete_message_after_delay(message, 600))
    
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

        # Try to show dynamic "Please wait..." message
        try:
            temp_msg = await send_dynamic_text(message, "𝚆𝚊𝚒𝚝 🔥🔥")
            try:
                messages = await get_messages(client, ids)
            except Exception as e:
                print(f"Error getting messages: {e}")
                return
            finally:
                try:
                    await temp_msg.delete()
                except:
                    pass
        except Exception as e:
            # If dynamic message fails, try simple message
            print(f"Error showing dynamic message: {e}")
            try:
                temp_msg = await message.reply("Please wait...")
                try:
                    messages = await get_messages(client, ids)
                except Exception as e:
                    print(f"Error getting messages: {e}")
                    return
                finally:
                    try:
                        await temp_msg.delete()
                    except:
                        pass
            except:
                # If even simple message fails, continue without message
                messages = await get_messages(client, ids)

        sent_msg = []  # Initialize sent_msg list
        for msg in messages:
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
                sent_msg.append(copied_msg)  # Use sent_msg consistently
            except Exception as e:
                print(f"Failed to send message: {e}")
                pass

        if FILE_AUTO_DELETE > 0:
            notification_msg = await message.reply(
                f"<b>This file will be deleted in {get_exp_time(FILE_AUTO_DELETE)}. Please save or forward it to your saved messages before it gets deleted.</b>"
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
                    [InlineKeyboardButton(
                        "🔄 Get File Again!", 
                        url=reload_url,
                        thumb_url=random.choice(PICS)  # Add random thumbnail from PICS
                    )]
                ]) if reload_url else None

                await notification_msg.edit(
                    "<b>ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!\n\nᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇</b>",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Error updating notification with 'Get File Again' button: {e}")
    else:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("for more", callback_data="more")],
            [
                InlineKeyboardButton("⚡️ ᴀʙᴏᴜᴛ", callback_data="about"),
                InlineKeyboardButton('🍁 sᴇʀɪᴇsғʟɪx', url='https://t.me/Team_Netflix/40')
            ]
        ])
        
        temp_msg = await message.reply_photo(
            photo=random.choice(PICS),
            caption="𝙻𝚘𝚊𝚍𝚒𝚗𝚐..."  # Initial caption
        )
        
        # Add typing effect to caption
        await send_dynamic_text(
            message,
            START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            # reply_markup=reply_markup#,
            #message_effect_id=5104841245755180586  # 🔥
            edit=temp_msg,
            delay=0.05  # Slightly faster for welcome message     
        )
        
        # Update with final markup after typing effect
        await temp_msg.edit_reply_markup(reply_markup)
        
        # Delete start message after 1 minute of inactivity
        asyncio.create_task(delete_message_after_delay(temp_msg, 60))  # Use temp_msg instead of start_msg

# Add helper function for message deletion
async def delete_message_after_delay(message, delay):
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")

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

    temp_msg = await message.reply_photo(
        photo=random.choice(PICS),
        caption="𝙲𝚑𝚎𝚌𝚔𝚒𝚗𝚐..."
    )
    
    force_msg = FORCE_MSG.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=None if not message.from_user.username else '@' + message.from_user.username,
        mention=message.from_user.mention,
        id=message.from_user.id
#     ),
#     reply_markup=InlineKeyboardMarkup(buttons)#,
#     #message_effect_id=5104841245755180586  # Add the effect ID here 😉 
# )
    )
    
    await send_dynamic_text(
        message,
        force_msg,
        edit=temp_msg,
        delay=0.05
    )
    
    await temp_msg.edit_reply_markup(InlineKeyboardMarkup(buttons))

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
async def send_text(client: Bot, message: Message):
    if not message.reply_to_message:
        msg = await send_dynamic_text(message, REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()
        return

    # Initialize broadcast stats
    stats = {
        'total': 0,
        'successful': 0,
        'blocked': 0,
        'deleted': 0,
        'unsuccessful': 0,
        'retries': 0
    }
    
    query = await full_userbase()
    broadcast_msg = message.reply_to_message
    failed_users = []  # Track failed deliveries
    
    pls_wait = await send_dynamic_text(message, "𝙱𝚛𝚘𝚊𝚍𝚌𝚊𝚜𝚝𝚒𝚗𝚐...")
    start_time = time.time()
    
    # Process users in chunks
    for i in range(0, len(query), BROADCAST_CHUNK_SIZE):
        user_chunk = query[i:i + BROADCAST_CHUNK_SIZE]
        chunk_results = await process_broadcast_chunk(broadcast_msg, user_chunk, stats)
        failed_users.extend(chunk_results)
        
        # Update status periodically
        if time.time() - start_time > 3:
            await update_broadcast_status(pls_wait, stats, len(query))
            start_time = time.time()

    # Log broadcast results
    await log_broadcast_results(message, stats, failed_users)
    
    # Check failure threshold and notify admin
    if stats['unsuccessful'] / stats['total'] > BROADCAST_FAILURE_THRESHOLD:
        await notify_broadcast_failure(message, stats, failed_users)

    final_status = f"""<b><u>Broadcast Completed</u>

Total Users: {stats['total']}
✅ Successful: {stats['successful']}
🚫 Blocked: {stats['blocked']}
❌ Deleted: {stats['deleted']}
📝 Failed: {stats['unsuccessful']}
🔄 Retries: {stats['retries']}</b>"""

    await pls_wait.edit(final_status)
    
    # Schedule cleanup of blocked/deleted users
    asyncio.create_task(cleanup_inactive_users(failed_users))

async def process_broadcast_chunk(broadcast_msg, user_chunk, stats):
    failed_users = []
    tasks = []
    
    for chat_id in user_chunk:
        tasks.append(broadcast_with_retry(broadcast_msg, chat_id, stats))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for chat_id, result in zip(user_chunk, results):
        stats['total'] += 1
        if isinstance(result, Exception):
            if isinstance(result, UserIsBlocked):
                stats['blocked'] += 1
                failed_users.append((chat_id, 'blocked'))
            elif isinstance(result, InputUserDeactivated):
                stats['deleted'] += 1
                failed_users.append((chat_id, 'deleted'))
            else:
                stats['unsuccessful'] += 1
                failed_users.append((chat_id, str(result)))
        else:
            stats['successful'] += 1
            
    return failed_users

async def broadcast_with_retry(broadcast_msg, chat_id, stats, retry_count=0):
    try:
        await broadcast_msg.copy(chat_id)
        await asyncio.sleep(0.1)  # Prevent flooding
        return True
    except FloodWait as e:
        if retry_count < MAX_RETRIES:
            stats['retries'] += 1
            await asyncio.sleep(e.x)
            return await broadcast_with_retry(broadcast_msg, chat_id, stats, retry_count + 1)
        raise
    except Exception as e:
        raise e

async def update_broadcast_status(status_msg, stats, total_users):
    try:
        status_text = f"""<b><u>Broadcast Status</u>

Progress: {stats['total']}/{total_users} users
✅ Successful: {stats['successful']}
🚫 Blocked: {stats['blocked']}
❌ Deleted: {stats['deleted']}
📝 Failed: {stats['unsuccessful']}
🔄 Retries: {stats['retries']}</b>"""
        await status_msg.edit(status_text)
    except Exception as e:
        logging.error(f"Failed to update broadcast status: {e}")

async def log_broadcast_results(message, stats, failed_users):
    log_text = f"""
Broadcast Summary
Time: {datetime.now()}
Initiated by: {message.from_user.id}
Total Users: {stats['total']}
Successful: {stats['successful']}
Failed: {stats['unsuccessful']}
Blocked: {stats['blocked']}
Deleted: {stats['deleted']}
Retries: {stats['retries']}

Failed Users:
"""
    for user_id, reason in failed_users:
        log_text += f"User {user_id}: {reason}\n"
    
    logging.info(log_text)
    
    # Save to file for reference
    with open("broadcast_logs.txt", "a") as f:
        f.write(f"{log_text}\n{'='*50}\n")

async def notify_broadcast_failure(message, stats, failed_users):
    failure_text = f"""⚠️ <b>High Broadcast Failure Rate</b>

Total Messages: {stats['total']}
Failed: {stats['unsuccessful']}
Failure Rate: {(stats['unsuccessful']/stats['total'])*100:.2f}%

Common failure reasons:
{get_common_failures(failed_users)}

Please check the broadcast_logs.txt for details."""

    for admin in ADMINS:
        try:
            await message._client.send_message(admin, failure_text)
        except Exception as e:
            logging.error(f"Failed to notify admin {admin}: {e}")

async def cleanup_inactive_users(failed_users):
    """Remove blocked and deleted users from database"""
    for user_id, reason in failed_users:
        if reason in ['blocked', 'deleted']:
            try:
                await del_user(user_id)
            except Exception as e:
                logging.error(f"Failed to remove user {user_id}: {e}")

def get_common_failures(failed_users):
    """Analyze and return most common failure reasons"""
    reasons = {}
    for _, reason in failed_users:
        reasons[reason] = reasons.get(reason, 0) + 1
    
    return "\n".join(f"- {reason}: {count} times" 
                    for reason, count in sorted(reasons.items(), 
                    key=lambda x: x[1], reverse=True)[:3])

# Add helper function for dynamic typing effect
async def send_dynamic_text(message: Message, text: str, edit: Union[Message, None] = None, delay: float = 0.07) -> Message:
    """
    Send or edit message with typing effect
    :param message: Original message to reply to or edit
    :param text: Text to type
    :param edit: Message to edit (if None, sends new message)
    :param delay: Delay between characters in seconds
    """
    current_text = ""
    if edit:
        msg = edit
    else:
        msg = await message.reply(current_text)
    
    for character in text:
        current_text += character
        try:
            await msg.edit(current_text)
            await asyncio.sleep(delay)
        except Exception as e:
            print(f"Error in dynamic typing: {e}")
            # If edit fails, just show full text
            await msg.edit(text)
            break
    
    return msg

async def check_subscription(client: Client, user_id: int) -> Dict[str, bool]:
    """Check user's subscription status for all required channels"""
    if user_id in ADMINS:
        return {"subscribed": True, "channels": []}
        
    channels_to_join = []
    try:
        for channel_id in [FORCE_SUB_CHANNEL1, FORCE_SUB_CHANNEL2, 
                          FORCE_SUB_CHANNEL3, FORCE_SUB_CHANNEL4]:
            if not channel_id or channel_id == 0:
                continue
            try:
                await client.get_chat_member(chat_id=channel_id, user_id=user_id)
            except UserNotParticipant:
                channels_to_join.append(channel_id)
            except Exception as e:
                print(f"Error checking channel {channel_id}: {e}")
                
        return {
            "subscribed": len(channels_to_join) == 0,
            "channels": channels_to_join
        }
    except Exception as e:
        print(f"Error in subscription check: {e}")
        return {"subscribed": False, "channels": []}

async def handle_not_subscribed(client: Client, message: Message, channels: List[int]):
    """Handle users who haven't subscribed to required channels"""
    buttons = []
    
    # Create buttons for channels that user hasn't joined
    for channel_id in channels:
        try:
            chat = await client.get_chat(channel_id)
            if chat.username:
                invite_link = f"https://t.me/{chat.username}"
            else:
                invite_link = await client.export_chat_invite_link(channel_id)
            buttons.append([
                InlineKeyboardButton(
                    text=f"• Join {chat.title} •",
                    url=invite_link
                )
            ])
        except Exception as e:
            print(f"Error creating button for channel {channel_id}: {e}")
            
    # Add reload button
    buttons.append([
        InlineKeyboardButton(
            text="🔄 Refresh",
            callback_data="check_subscription"
        )
    ])
    
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

@Bot.on_callback_query(filters.regex('^check_subscription$'))
async def check_sub_callback(client: Client, callback: CallbackQuery):
    try:
        sub_status = await check_subscription(client, callback.from_user.id)
        if sub_status["subscribed"]:
            await callback.message.delete()
            await start_command(client, callback.message)
        else:
            await callback.answer("❌ Please join all channels first!", show_alert=True)
    except Exception as e:
        print(f"Error in subscription callback: {e}")
        await callback.answer("An error occurred. Please try again.", show_alert=True)