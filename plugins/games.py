from pyrogram import Client, filters
import random
import asyncio

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
        await message.reply_text("⚠ Please provide some text to convert.")
        return
    
    aesthetic_text = aesthetify(text)
    await message.edit(aesthetic_text)

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
    status_message = await message.reply_text(f"🎮 Playing {game.capitalize()}...")

    # Send dice with the respective emoji
    dice_msg = await client.send_dice(
        chat_id=message.chat.id,
        emoji=emoji,
        disable_notification=True,
        reply_to_message_id=status_message.id
    )

    # Wait for the dice animation to complete
    await asyncio.sleep(2)

    # Edit the status message to indicate the game result
    await status_message.edit(f"🎮 {game.capitalize()} Over! Your result: {dice_msg.dice.value} 🎲")

    # Wait for 10 seconds before deleting both messages
    await asyncio.sleep(10)
    try:
        await status_message.delete()
        await dice_msg.delete()
    except Exception as e:
        print(f"Error deleting game messages: {e}")
        pass

# Random funny responses
RUN_STRINGS = [
    "A broken soul filled with darkness... Why have you come to remind it?",
    "We have become the lost souls of the underwater world...",
    "You want the bad call ... but you need good thunder ....",
    "Oh Bloody Grama Virtues!",
    "Sea MUGGie I Am Going to Pay The Bill.",
    "You are not a male chaff!!",
    "Kindi ... Kindi ...!",
    "Children..",
    "Your father to Paul...",
    "Before falling in the 4th pegging, I will arrive there.",
    "To tell me I love Yo....",
]

@Client.on_message(filters.command("runs") & private_filter)
async def runs(_, message):
    """ Send a random funny string """
    status_message = await message.reply_text("🏃 Running...")
    await asyncio.sleep(1)
    
    effective_string = random.choice(RUN_STRINGS)
    await status_message.edit(effective_string)







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
