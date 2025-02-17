from pyrogram import Client, filters
import random
import asyncio

# Constants
DELETE_TIMEOUT = 120  # 1 minute in seconds
ANIMATION_TIME = 2  # Time to wait for dice animation
RESULT_DISPLAY_TIME = 5  # Time to show result before deleting

# Convert text to aesthetic style (light and cool font)
def aesthetify(string):
    light_font_offset = 0x1D5D4 - 0x41  # Uppercase A in the light font
    result = []
    for c in string:
        if "A" <= c <= "Z":  # Uppercase letters
            result.append(chr(ord(c) + light_font_offset))
        elif "a" <= c <= "z":  # Lowercase letters
            result.append(chr(ord(c) + (light_font_offset + 6)))
        elif c == " ":
            result.append(" ")
        else:
            result.append(c)
    return "".join(result)

# Restrict bot to private chats only
private_filter = filters.private & ~filters.channel & ~filters.group

@Client.on_message(filters.command("ae") & private_filter)
async def aesthetic(client, message):
    text = " ".join(message.command[1:])
    if not text:
        temp_msg = await message.reply_text("• ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ꜱᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴄᴏɴᴠᴇʀᴛ. •")
        await asyncio.sleep(DELETE_TIMEOUT)
        await temp_msg.delete()
        return
    
    aesthetic_text = aesthetify(text)
    result_msg = await message.reply_text(aesthetic_text)
    await asyncio.sleep(DELETE_TIMEOUT)
    await result_msg.delete()
    try:
        await message.delete()
    except:
        pass

# Emoji Constants for games
GAMES = {
    "dart": "🎯",
    "dice": "🎲",
    "luck": "🎰",
    "goal": "⚽",
    "basketball": "🏀",
    "bowling": "🎳"
}

@Client.on_message(filters.command(list(GAMES.keys())) & private_filter)
async def play_game(client, message):
    game = message.command[0]  # Get the command name
    emoji = GAMES.get(game)

    # Delete the user's command message for a clean UI
    try:
        await message.delete()
    except:
        pass  # Ignore if the bot doesn't have delete permissions

    # Send a status message indicating the game is starting
    status_message = await message.reply_text(f"🎮 Pʟᴀʏɪɴɢ {game.capitalize()}...")

    # Send dice with the respective emoji
    dice_msg = await client.send_dice(
        chat_id=message.chat.id,
        emoji=emoji,
        disable_notification=True
    )

    # Wait for the dice animation to complete
    await asyncio.sleep(ANIMATION_TIME)

    # Edit the status message to indicate the game result
    result_msg = await status_message.edit(f"🎮 {game.capitalize()} Oᴠᴇʀ! yᴏᴜʀ ʀᴇsᴜʟᴛ: {dice_msg.dice.value} 🎲")

    # Wait for specified time before deleting messages
    await asyncio.sleep(DELETE_TIMEOUT)
    try:
        await status_message.delete()
        await dice_msg.delete()
    except Exception as e:
        print(f"Error deleting game messages: {e}")

# Random funny responses
RUN_STRINGS = [
    "ᴀ ʙʀᴏᴋᴇɴ ꜱᴏᴜʟ ꜰɪʟʟᴇᴅ ᴡɪᴛʜ ᴅᴀʀᴋɴᴇꜱꜱ... ᴡʜʏ ʜᴀᴠᴇ ʏᴏᴜ ᴄᴏᴍᴇ ᴛᴏ ʀᴇᴍɪɴᴅ ɪᴛ?",
    "ᴡᴇ ʜᴀᴠᴇ ʙᴇᴄᴏᴍᴇ ᴛʜᴇ ʟᴏꜱᴛ ꜱᴏᴜʟꜱ ᴏꜰ ᴛʜᴇ ᴜɴᴅᴇʀᴡᴀᴛᴇʀ ᴡᴏʀʟᴅ...",
    "ʏᴏᴜ ᴡᴀɴᴛ ᴛʜᴇ ʙᴀᴅ ᴄᴀʟʟ ... ʙᴜᴛ ʏᴏᴜ ɴᴇᴇᴅ ɢᴏᴏᴅ ᴛʜᴜɴᴅᴇʀ ....",
    "ᴏʜ ʙʟᴏᴏᴅʏ ɢʀᴀᴍᴀ ᴠɪʀᴛᴜᴇꜱ!",
    "ꜱᴇᴀ ᴍᴜɢɢɪᴇ ɪ ᴀᴍ ɢᴏɪɴɢ ᴛᴏ ᴘᴀʏ ᴛʜᴇ ʙɪʟʟ.",
    "ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ᴍᴀʟᴇ ᴄʜᴀꜰꜰ!!",
    "ᴋɪɴᴅɪ ... ᴋɪɴᴅɪ ...!",
    "ᴄʜɪʟᴅʀᴇɴ..",
    "ʏᴏᴜʀ ꜰᴀᴛʜᴇʀ ᴛᴏ ᴘᴀᴜʟ...",
    "ʙᴇꜰᴏʀᴇ ꜰᴀʟʟɪɴɢ ɪɴ ᴛʜᴇ 4ᴛʜ ᴘᴇɢɢɪɴɢ, ɪ ᴡɪʟʟ ᴀʀʀɪᴠᴇ ᴛʜᴇʀᴇ.",
    "ᴛᴏ ᴛᴇʟʟ ᴍᴇ ɪ ʟᴏᴠᴇ ʏᴏ...."
]

@Client.on_message(filters.command("runs") & private_filter)
async def runs(_, message):
    """ Send a random funny string """
    try:
        await message.delete()
    except:
        pass
        
    status_message = await message.reply_text("• ʀᴜɴɴɪɴɢ...")
    await asyncio.sleep(1)
    
    effective_string = random.choice(RUN_STRINGS)
    await status_message.edit(effective_string)

    await asyncio.sleep(DELETE_TIMEOUT)
    try:
        await status_message.delete()
    except Exception as e:
        print(f"Error deleting run message: {e}")





# from pyrogram import Client, filters
# import random
# import asyncio

# # Convert text to aesthetic style (light and cool font)
# def aesthetify(string):
#     light_font_offset = 0x1D5D4 - 0x41  # Uppercase A in the light font
#     result = []
#     for c in string:
#         if "A" <= c <= "Z":  # Uppercase letters
#             result.append(chr(ord(c) + light_font_offset))
#         elif "a" <= c <= "z":  # Lowercase letters
#             result.append(chr(ord(c) + (light_font_offset + 6)))
#         elif c == " ":
#             result.append(" ")
#         else:
#             result.append(c)
#     return "".join(result)

# # Restrict bot to private chats only
# private_filter = filters.private & ~filters.channel & ~filters.group

# @Client.on_message(filters.command("ae") & private_filter)
# async def aesthetic(client, message):
#     text = " ".join(message.command[1:])
#     if not text:
#         await message.reply_text("⚠ Please provide some text to convert.")
#         return
    
#     aesthetic_text = aesthetify(text)
#     await message.edit(aesthetic_text)

# # Emoji Constants for games
# GAMES = {
#     "dart": "🎯",
#     "dice": "🎲",
#     "luck": "🎰",
#     "goal": "⚽",
#     "basketball": "🏀",
#     "bowling": "🎳"
# }

# @Client.on_message(filters.command(list(GAMES.keys())) & private_filter)
# async def play_game(client, message):
#     game = message.command[0]  # Get the command name
#     emoji = GAMES.get(game)
    
#     # Delete the user's command message for a clean UI
#     await message.delete()

#     # Send a status message indicating the game is starting
#     status_message = await message.reply_text(f"🎮 Playing {game.capitalize()}...")

#     # Send dice with the respective emoji
#     await client.send_dice(
#         chat_id=message.chat.id,
#         emoji=emoji,
#         disable_notification=True,
#         reply_to_message_id=status_message.message_id
#     )

#     # Once dice is sent, edit the status message to indicate game has been played
#     await asyncio.sleep(2)  # Wait for the dice animation to complete
#     await status_message.edit(f"{game.capitalize()} finished! 🎲")

#     # Optionally delete the status message after some time
#     await asyncio.sleep(5)
#     await status_message.delete()

# # Random funny responses
# RUN_STRINGS = [
#     "A broken soul filled with darkness... Why have you come to remind it?",
#     "We have become the lost souls of the underwater world...",
#     "You want the bad call ... but you need good thunder ....",
#     "Oh Bloody Grama Virtues!",
#     "Sea MUGGie I Am Going to Pay The Bill.",
#     "You are not a male chaff!!",
#     "Kindi ... Kindi ...!",
#     "Children..",
#     "Your father to Paul...",
#     "Before falling in the 4th pegging, I will arrive there.",
#     "To tell me I love Yo....",
# ]

# @Client.on_message(filters.command("runs") & private_filter)
# async def runs(_, message):
#     """ Send a random funny string """
#     status_message = await message.reply_text("🏃 Running...")
#     await asyncio.sleep(1)
    
#     effective_string = random.choice(RUN_STRINGS)
#     await status_message.edit(effective_string)
    
    # Delete after timeout

