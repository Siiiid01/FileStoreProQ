import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from bot import Bot
from config import ADMINS, PICS
from database.database import full_userbase, del_user
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
import random
import math

# Dynamic Constants
MIN_CHUNK_SIZE = 20
MAX_CHUNK_SIZE = 200
BASE_DELAY = 1.5  # Base delay between messages
MAX_CONCURRENT_CHUNKS = 3  # Number of chunks to process simultaneously
STATUS_UPDATE_INTERVAL = 5  # Status update interval in seconds
AUTO_DELETE_TIME = 600  # 10 minutes

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
        self.processing_chunks = set()
        self.completed_chunks = set()

    async def initialize(self, client: Bot):
        """Initialize total users count and calculate optimal chunk size"""
        users = await full_userbase()
        self.total_users = len(users)
        
        # Dynamic chunk size based on total users
        chunk_size = min(
            max(
                MIN_CHUNK_SIZE,
                math.ceil(self.total_users / 50)  # Aim for ~50 chunks
            ),
            MAX_CHUNK_SIZE
        )
        
        # Split users into chunks
        chunks = [users[i:i + chunk_size] for i in range(0, len(users), chunk_size)]
        self.total_chunks = len(chunks)
        
        return chunks

    def get_progress_text(self, is_final=False):
        elapsed_time = int(time.time() - self.start_time)
        progress = (len(self.completed_chunks) / self.total_chunks * 100) if self.total_chunks else 0
        
        # Calculate speed and ETA
        speed = self.successful / elapsed_time if elapsed_time > 0 else 0
        remaining_users = self.total_users - (self.successful + self.blocked + self.deleted + self.failed)
        eta = int(remaining_users / speed) if speed > 0 else 0
        
        text = f"{'🏁 Final Broadcast Status' if is_final else '📊 Broadcast Status'}\n\n"
        text += f"⏳ Time Elapsed: {format_time(elapsed_time)}\n"
        text += f"⏰ ETA: {format_time(eta)}\n"
        text += f"📊 Progress: {progress:.1f}%\n"
        text += f"👥 Total Users: {self.total_users}\n"
        text += f"✅ Successful: {self.successful}\n"
        text += f"🚫 Blocked: {self.blocked}\n"
        text += f"❌ Deleted: {self.deleted}\n"
        text += f"💔 Failed: {self.failed}\n"
        text += f"⚡️ Speed: {speed:.1f} messages/sec\n\n"
        
        if not is_final:
            text += f"🔄 Active Chunks: {len(self.processing_chunks)}/{self.total_chunks}\n"
            text += f"✨ Completed Chunks: {len(self.completed_chunks)}/{self.total_chunks}"
        
        return text

async def process_chunk(client: Bot, message: Message, users: list, status: BroadcastStatus, chunk_id: int) -> None:
    """Process a chunk of users for broadcast with adaptive delays"""
    status.processing_chunks.add(chunk_id)
    chunk_size = len(users)
    
    for idx, user_id in enumerate(users, 1):
        try:
            await message.copy(user_id)
            status.successful += 1
            
            # Adaptive delay based on success rate
            success_rate = status.successful / (status.successful + status.failed)
            delay = BASE_DELAY * (2 - success_rate)  # Adjust delay based on success rate
            await asyncio.sleep(delay)
            
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
        except Exception as e:
            print(f"Error broadcasting to {user_id}: {str(e)}")
            status.failed += 1
            status.failed_users.append(user_id)
    
    status.processing_chunks.remove(chunk_id)
    status.completed_chunks.add(chunk_id)

async def update_status_message(status_msg: Message, status: BroadcastStatus):
    """Update the status message with current progress"""
    try:
        current_text = getattr(status_msg, 'caption', '')
        new_text = status.get_progress_text()
        
        if current_text != new_text:
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
        caption="🚀 Initializing broadcast...\n\nCalculating optimal settings based on user count...",
        has_spoiler=True
    )

    try:
        # Initialize and get chunks
        chunks = await status.initialize(client)
        
        if status.total_users == 0:
            await status_msg.edit_caption("No users found in database!")
            return

        # Process chunks concurrently with semaphore
        sem = asyncio.Semaphore(MAX_CONCURRENT_CHUNKS)
        status_update_task = asyncio.create_task(periodic_status_update(status_msg, status))
        
        async def process_chunk_with_semaphore(chunk, chunk_id):
            async with sem:
                await process_chunk(client, message.reply_to_message, chunk, status, chunk_id)

        # Create tasks for all chunks
        chunk_tasks = [
            asyncio.create_task(process_chunk_with_semaphore(chunk, i))
            for i, chunk in enumerate(chunks)
        ]

        # Wait for all chunks to complete
        await asyncio.gather(*chunk_tasks)
        status_update_task.cancel()

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

async def periodic_status_update(status_msg: Message, status: BroadcastStatus):
    """Periodically update status message"""
    while True:
        await asyncio.sleep(STATUS_UPDATE_INTERVAL)
        await update_status_message(status_msg, status)

def format_time(seconds: int) -> str:
    """Format seconds into readable time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes}m {seconds}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds %= 60
        return f"{hours}h {minutes}m {seconds}s" 