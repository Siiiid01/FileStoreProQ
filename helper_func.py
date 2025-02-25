import base64
import re
import asyncio
import time
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import *
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait
from shortzy import Shortzy
from database.database import *
from datetime import datetime
from database.database import db_check_ban, get_ban_status
from config import ADMINS



async def is_subscribed1(filter, client, update):
    if not FORCE_SUB_CHANNEL1:
        return True
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id = FORCE_SUB_CHANNEL1, user_id = user_id)
    except UserNotParticipant:
        return False

    if not member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return False
    else:
        return True

async def is_subscribed2(filter, client, update):
    if not FORCE_SUB_CHANNEL2:
        return True
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id = FORCE_SUB_CHANNEL2, user_id = user_id)
    except UserNotParticipant:
        return False

    if not member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return False
    else:
        return True

async def is_subscribed3(filter, client, update):
    if not FORCE_SUB_CHANNEL3:
        return True
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id = FORCE_SUB_CHANNEL3, user_id = user_id)
    except UserNotParticipant:
        return False

    if not member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return False
    else:
        return True

async def is_subscribed4(filter, client, update):
    if not FORCE_SUB_CHANNEL4:
        return True
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id = FORCE_SUB_CHANNEL4, user_id = user_id)
    except UserNotParticipant:
        return False

    if not member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return False
    else:
        return True


async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

async def decode(base64_string):
    """Decode base64 string with better error handling"""
    try:
        # Add padding if needed
        base64_string = base64_string.strip("=")  # Remove any existing padding
        padding = len(base64_string) % 4
        if padding:
            base64_string += "=" * (4 - padding)

        # Decode with padding
        string_bytes = base64.urlsafe_b64decode(base64_string)
        try:
            return string_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return string_bytes.decode('ascii', errors='ignore')
    except Exception as e:
        from plugins.logs import log_error
        log_error(f"Base64 decode error: {str(e)} for string: {base64_string}")
        return None

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        else:
            return 0
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern,message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id
    else:
        return 0


def get_readable_time(seconds: int) -> str:
    """Convert seconds to readable time format"""
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d '
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h '
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m '
    seconds = int(seconds)
    result += f'{seconds}s'
    return result

async def get_verify_status(user_id):
    verify = await db_verify_status(user_id)
    return verify

async def update_verify_status(user_id, verify_token="", is_verified=False, verified_time=0, link=""):
    current = await db_verify_status(user_id)
    current['verify_token'] = verify_token
    current['is_verified'] = is_verified
    current['verified_time'] = verified_time
    current['link'] = link
    await db_update_verify_status(user_id, current)


async def get_shortlink(url, api, link):
    shortzy = Shortzy(api_key=api, base_site=url)
    link = await shortzy.convert(link)
    return link

def get_exp_time(seconds):
    periods = [('days', 86400), ('hours', 3600), ('mins', 60), ('secs', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)} {period_name}'
    return result


subscribed1 = filters.create(is_subscribed1)
subscribed2 = filters.create(is_subscribed2)
subscribed3 = filters.create(is_subscribed3)
subscribed4 = filters.create(is_subscribed4)

async def send_telegraph_log(client, user_id, file_name, file_type, telegraph_url):
    """Send Telegraph upload log to channel"""
    try:
        user = await client.get_users(user_id)
        user_mention = user.mention
    except:
        user_mention = f"User {user_id}"
    
    log_text = (
        "**New Telegraph Upload**\n\n"
        f"**User:** {user_mention}\n"
        f"**User ID:** `{user_id}`\n"
        f"**File Name:** `{file_name}`\n"
        f"**File Type:** {file_type}\n"
        f"**Telegraph URL:** {telegraph_url}\n"
        f"**Upload Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    try:
        await client.send_message(TELEGRAPH_LOG_CHANNEL, log_text)
    except Exception as e:
        print(f"Failed to send Telegraph log: {e}")

async def send_ban_log(client, user_id, admin_id, reason=None, action="banned"):
    """Send ban/unban log to channel"""
    try:
        user = await client.get_users(user_id)
        admin = await client.get_users(admin_id)
        user_mention = user.mention
        admin_mention = admin.mention
    except:
        user_mention = f"User {user_id}"
        admin_mention = f"Admin {admin_id}"
    
    log_text = (
        f"**User {action.title()}**\n\n"
        f"**User:** {user_mention}\n"
        f"**User ID:** `{user_id}`\n"
        f"**{action.title()} By:** {admin_mention}\n"
        f"**Admin ID:** `{admin_id}`\n"
    )

    if reason and action == "banned":
        log_text += f"**Reason:** {reason}\n"
    
    log_text += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    try:
        await client.send_message(BAN_LOG_CHANNEL, log_text)
    except Exception as e:
        print(f"Failed to send ban log: {e}")

async def send_new_user_notification(client, user):
    """Send notification when new user starts the bot"""
    try:
        # Get user details
        user_mention = user.mention
        join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create notification message
        log_text = (
            "**👤 New User Started Bot**\n\n"
            f"**User:** {user_mention}\n"
            f"**ID:** `{user.id}`\n"
            f"**Username:** @{user.username if user.username else 'None'}\n"
            f"**First Name:** {user.first_name}\n"
            f"**Last Name:** {user.last_name if user.last_name else 'None'}\n"
            f"**Language:** {user.language_code if user.language_code else 'None'}\n"
            f"**Joined On:** {join_date}"
        )
        
        # Send with user's profile photo if available
        try:
            profile_photos = await client.get_profile_photos(user.id, limit=1)
            if profile_photos and profile_photos.total_count > 0:
                await client.send_photo(
                    chat_id=NEW_USER_LOG_CHANNEL,
                    photo=profile_photos[0].file_id,
                    caption=log_text
                )
                return
        except:
            pass
        
        # If no profile photo or error getting it, send text only
        await client.send_message(
            chat_id=NEW_USER_LOG_CHANNEL,
            text=log_text
        )
        
    except Exception as e:
        print(f"Failed to send new user notification: {e}")

def check_user_ban(func):
    async def wrapper(client, message):
        try:
            user_id = message.from_user.id
            
            # Skip ban check for admins
            if user_id in ADMINS:
                return await func(client, message)
                
            # Check if user is banned
            is_banned = await db_check_ban(user_id)
            if is_banned:
                # Send ban message and stop all further processing
                ban_info = await get_ban_status(user_id)
                ban_reason = ban_info.get('ban_reason', 'No reason provided')
                ban_msg = f"<b>⚠️ You are banned from using this bot</b>\n\n<b>Reason:</b> {ban_reason}"
                try:
                    await message.reply_text(ban_msg)
                except:
                    pass
                # Important: Return None to stop command execution
                return
            
            # User not banned, add small delay and continue
            await asyncio.sleep(0.3)
            return await func(client, message)
            
        except Exception as e:
            print(f"Error in ban check: {e}")
            # On any error, block access
            return
            
    return wrapper
