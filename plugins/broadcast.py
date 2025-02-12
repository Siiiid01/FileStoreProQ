import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from bot import Bot
from config import ADMINS, PICS
from database.database import full_userbase, del_user
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
import random

# Constants
CHUNK_SIZE = 20  # Smaller chunks for better management
UPDATE_INTERVAL = 10  # Status update interval in seconds
AUTO_DELETE_TIME = 600  # 10 minutes
MAX_RETRIES = 3
MEDIA_DELAY = 2  # Delay between media messages in seconds

class BroadcastStatus:
    def __init__(self):
        self.total_users = 0
        self.current_chunk = 0
        self.total_chunks = 0
        self.successful = 0
        self.blocked = 0
        self.deleted = 0
        self.failed = 0
        self.start_time = time.time()
        self.current_chunk_progress = 0
        self.failed_users = []
        self.last_updated = 0

    async def initialize(self, client: Bot):
        """Initialize total users count"""
        users = await full_userbase()
        self.total_users = len(users)
        return users

    def get_progress_text(self, is_final=False):
        elapsed_time = int(time.time() - self.start_time)
        progress = (self.current_chunk / self.total_chunks * 100) if self.total_chunks else 0
        
        text = f"{'🏁 Final Broadcast Status' if is_final else '📊 Broadcast Status Update'}\n\n"
        text += f"⏳ Time Elapsed: {elapsed_time} seconds\n"
        text += f"👥 Total Users: {self.total_users}\n"
        text += f"📈 Progress: {progress:.1f}%\n"
        text += f"✅ Successful: {self.successful}\n"
        text += f"🚫 Blocked: {self.blocked}\n"
        text += f"❌ Deleted: {self.deleted}\n"
        text += f"💔 Failed: {self.failed}\n\n"
        
        if not is_final:
            text += f"🔄 Processing Chunk: {self.current_chunk}/{self.total_chunks}\n"
            text += f"📤 Current Chunk Progress: {self.current_chunk_progress}%"
        
        return text

async def process_chunk(client: Bot, message: Message, users: list, status: BroadcastStatus) -> None:
    """Process a chunk of users for broadcast"""
    chunk_size = len(users)
    for idx, user_id in enumerate(users, 1):
        try:
            await message.copy(user_id)
            status.successful += 1
            await asyncio.sleep(MEDIA_DELAY)  # Add delay between messages
        except FloodWait as e:
            await asyncio.sleep(e.x)
            try:
                await message.copy(user_id)
                status.successful += 1
            except:
                status.failed += 1
                status.failed_users.append(user_id)
        except UserIsBlocked:
            status.blocked += 1
            await del_user(user_id)
        except InputUserDeactivated:
            status.deleted += 1
            await del_user(user_id)
        except Exception:
            status.failed += 1
            status.failed_users.append(user_id)
        
        status.current_chunk_progress = (idx / chunk_size) * 100

async def update_status_message(status_msg: Message, status: BroadcastStatus):
    """Update the status message with current progress"""
    try:
        current_text = getattr(status_msg, 'caption', '')
        new_text = status.get_progress_text()
        
        if current_text != new_text:  # Only update if text has changed
            await status_msg.edit_media(
                media=InputMediaPhoto(
                    random.choice(PICS),
                    caption=new_text,
                    has_spoiler=True
                )
            )
    except Exception as e:
        print(f"Error updating status: {e}")

@Bot.on_message(filters.command('broadcast') & filters.private & filters.user(ADMINS))
async def broadcast_handler(client: Bot, message: Message):
    if not message.reply_to_message:
        await message.reply("Please reply to a message to broadcast!")
        return

    # Initialize broadcast status
    status = BroadcastStatus()
    
    # Send initial status message
    status_msg = await message.reply_photo(
        photo=random.choice(PICS),
        caption="🚀 Initializing broadcast...",
        has_spoiler=True
    )

    try:
        # Initialize total users
        all_users = await status.initialize(client)
        
        if status.total_users == 0:
            await status_msg.edit_caption("No users found in database!")
            return

        # Split users into smaller chunks
        chunks = [all_users[i:i + CHUNK_SIZE] for i in range(0, len(all_users), CHUNK_SIZE)]
        status.total_chunks = len(chunks)

        # Process chunks
        for chunk_idx, chunk in enumerate(chunks, 1):
            status.current_chunk = chunk_idx
            status.current_chunk_progress = 0
            
            # Process chunk with retries
            for retry in range(MAX_RETRIES):
                try:
                    await process_chunk(client, message.reply_to_message, chunk, status)
                    break
                except Exception as e:
                    if retry == MAX_RETRIES - 1:
                        print(f"Failed to process chunk {chunk_idx} after {MAX_RETRIES} retries: {e}")
                    await asyncio.sleep(5)

            # Update status message if enough time has passed
            current_time = time.time()
            if current_time - status.last_updated >= UPDATE_INTERVAL:
                await update_status_message(status_msg, status)
                status.last_updated = current_time

        # Send final status
        final_status = status.get_progress_text(is_final=True)
        await status_msg.edit_media(
            media=InputMediaPhoto(
                random.choice(PICS),
                caption=final_status,
                has_spoiler=True
            )
        )

        # Handle failed users
        if status.failed_users:
            with open('failed_broadcasts.txt', 'w') as f:
                f.write('\n'.join(map(str, status.failed_users)))
            await message.reply_document(
                'failed_broadcasts.txt',
                caption="📋 List of failed broadcast recipients"
            )

        # Schedule status message deletion
        await asyncio.sleep(AUTO_DELETE_TIME)
        await status_msg.delete()

    except Exception as e:
        error_text = f"❌ Broadcast Failed!\n\nError: {str(e)}"
        try:
            await status_msg.edit_media(
                media=InputMediaPhoto(
                    random.choice(PICS),
                    caption=error_text,
                    has_spoiler=True
                )
            )
        except:
            await message.reply(error_text) 