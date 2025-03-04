from pyrogram import Client, filters, enums
from pyrogram.types import Message
import random
from config import ADMINS
from bot import Bot
import asyncio
import traceback
from datetime import datetime

# Define reactions
REACTIONS = [
    "❤️", "🔥", "👍", "👏", "🎉", "🤩", "💯", "💪", "👌", "💫",
    "🌟", "✨", "💥", "💫", "🎯", "💝", "💖", "💕", "💗", "💓"
]

async def send_error_message(client: Bot, message: Message, error: Exception, context: str):
    """Helper function to send detailed error messages"""
    error_traceback = traceback.format_exc()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Detailed error message for chat
    error_message = f"""
<b>⚠️ Debug Error Report</b>

<b>• Context:</b> <code>{context}</code>
<b>• Timestamp:</b> <code>{timestamp}</code>
<b>• Error Type:</b> <code>{type(error).__name__}</code>
<b>• Error Message:</b> <code>{str(error)}</code>

<b>• User Info:</b>
- ID: <code>{message.from_user.id}</code>
- Name: {message.from_user.mention}
- Username: @{message.from_user.username or 'None'}

<b>• Command Used:</b> <code>{message.text or 'None'}</code>

<i>This error has been logged for debugging purposes.</i>
"""
    
    # Log error to console
    print(f"\n{'='*50}\nError in Reaction Module\n{'='*50}")
    print(f"Context: {context}")
    print(f"Timestamp: {timestamp}")
    print(f"User: {message.from_user.id} (@{message.from_user.username})")
    print(f"Command: {message.text}")
    print(f"\nTraceback:\n{error_traceback}")
    print(f"{'='*50}\n")
    
    # Send error message to chat
    try:
        await message.reply_text(error_message, parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        print(f"Failed to send error message: {e}")

async def get_message_from_link(client: Bot, link: str) -> Message:
    try:
        # Extract chat_id and message_id from link
        parts = link.split('/')
        if len(parts) < 5:
            return None
        
        chat_id = parts[4]
        message_id = int(parts[5])
        
        # Handle private chat links
        if chat_id.startswith('-100'):
            chat_id = int(chat_id)
        else:
            # For public chats, get chat_id from username
            chat = await client.get_chat(chat_id)
            chat_id = chat.id
            
        return await client.get_messages(chat_id, message_id)
    except Exception as e:
        print(f"Error getting message from link: {e}")
        return None

@Bot.on_message(filters.command("react") & filters.private & filters.user(ADMINS))
async def start_react(client: Bot, message: Message):
    try:
        # Add reaction to command
        try:
            await message.react(emoji=random.choice(REACTIONS), big=True)
        except Exception as e:
            await send_error_message(client, message, e, "Failed to add reaction to command")

        await message.reply_text("""
<b>Welcome to Reaction Bot!</b>

Please send me:
1. A forwarded message, or
2. A message link (e.g., https://t.me/...)

I'll add 3-5 random reactions to the message.
    """, parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await send_error_message(client, message, e, "Error in start_react handler")

@Bot.on_message(filters.command("react_now") & filters.private & filters.user(ADMINS))
async def react_command(client: Bot, message: Message):
    try:
        target_message = None
        
        # Check if it's a forwarded message
        if message.reply_to_message:
            target_message = message.reply_to_message
        # Check if it's a message link
        elif message.text and "t.me" in message.text:
            link = message.text.split()[1] if len(message.text.split()) > 1 else None
            if link:
                target_message = await get_message_from_link(client, link)
                if not target_message:
                    raise ValueError("Failed to get message from link. Please check if the link is valid.")
        
        if not target_message:
            await message.reply_text("""
<b>❌ No valid message found!</b>

Please either:
1. Reply to a message with /react, or
2. Send /react followed by a message link
            """, parse_mode=enums.ParseMode.HTML)
            return

        # Generate random number of reactions (3-5)
        num_reactions = random.randint(3, 5)
        selected_reactions = random.sample(REACTIONS, num_reactions)
        
        # Send reactions
        status_message = await message.reply_text("`Adding reactions...`")
        
        reaction_status = []
        for reaction in selected_reactions:
            try:
                await client.send_reaction(
                    chat_id=target_message.chat.id,
                    message_id=target_message.id,
                    emoji=reaction
                )
                reaction_status.append(f"✅ {reaction}")
                await asyncio.sleep(0.5)  # Small delay between reactions
            except Exception as e:
                reaction_status.append(f"❌ {reaction} (Failed: {str(e)})")
                await send_error_message(client, message, e, f"Failed to add reaction {reaction}")
                continue
        
        # Prepare detailed status message
        status_text = f"""
<b>✅ Reaction Status Report</b>

<b>• Target Message:</b>
- ID: <code>{target_message.id}</code>
- Chat: <code>{target_message.chat.title or 'Private Chat'}</code>

<b>• Reactions Applied:</b>
{chr(10).join(reaction_status)}

<b>• Success Rate:</b> {len([s for s in reaction_status if '✅' in s])}/{len(selected_reactions)}
        """
        
        await status_message.edit(status_text, parse_mode=enums.ParseMode.HTML)
        
    except Exception as e:
        await send_error_message(client, message, e, "Error in react_command handler") 