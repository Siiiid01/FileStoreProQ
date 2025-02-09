from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import random 
import os
from bot import Bot
from config import *  # Using existing (PICS)

NO_PROFILE_PHOTO = "https://i.ibb.co/Mx2JYfrV/Shawn-Levy.jpg"  # Add this default photo URL

@Bot.on_message(filters.command("id") & filters.private)
async def showid(client, message: Message):
    # Delete the command message
    try:
        await message.delete()
    except:
        pass  # Ignore errors if the bot cannot delete the message

    user = message.from_user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name or "N/A"
    username = f"@{user.username}" if user.username else "N/A"
    language = user.language_code if user.language_code else "N/A"

    # Generate response text
    response_text = (
        f"<blockquote>🔥 **User Info:**\n</blockquote>"
        f"<blockquote>🆔 **User ID:** `{user_id}`\n</blockquote>"
        f"<blockquote>📛 **First Name:** `{first_name}`\n</blockquote>"
        f"<blockquote>📝 **Last Name:** `{last_name}`\n</blockquote>"
        f"<blockquote>🔗 **Username:** `{username}`\n</blockquote>"
        f"<blockquote>🌍 **Language:** `{language}`</blockquote>"
    )

    # More Info and Close buttons
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("• More Info •", callback_data=f"more_info_{user_id}")],
        [InlineKeyboardButton("• Close •", callback_data="close")]
    ])


    # Send response and add reaction
    bot_msg = await message.reply_photo(
        photo=random.choice(PICS),
        caption=response_text,
        reply_markup=buttons
    )
    
    # Add reaction to bot's message
    await bot_msg.react("🔥")


@Bot.on_callback_query(filters.regex(r"^more_info_(\d+)"))
async def more_info(client, callback_query):
    user_id = int(callback_query.data.split("_")[1])
    user = await client.get_users(user_id)  # Fetch full user info

    # Fetch user details
    about = user.bio or "N/A"
    try:
        profile_pics = await client.get_chat_photos(user_id)
        first_photo = await profile_pics.next()
        profile_pic = first_photo.file_id
    except StopAsyncIteration:
        profile_pic = NO_PROFILE_PHOTO  # Use the default photo if no profile picture

    join_date = user.status.date.strftime("%Y-%m-%d") if user.status else "Unknown"
    bot_lang_code = callback_query.message.chat.language_code or "N/A"

    # Update response text
    response_text = (
        f"<blockquote>🔥 User Info:\n"
        f"🆔 User ID:`{user_id}`\n"
        f"📛 First Name: `{user.first_name}`\n"
        f"📝 Last Name: `{user.last_name or 'N/A'}`\n"
        f"🔗 Username: `{user.username or 'N/A'}`\n"
        f"🌍 Language: `{callback_query.message.chat.language_code}`</blockquote>\n\n"
        
        f"<blockquote>🔹 More Info:\n"
        f"📷 Profile Picture: Sent above 👆\n"
        f"📝 Bio: `{about}`\n"
        f"📅 Joined Telegram: `{join_date}`\n"
        f"🤖 Bot Language Code: `{bot_lang_code}`\n\n"
        f"👑 Bot Owner: @Anime106_Request_Bot </blockquote>"
    )

    # Close button
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("• Close •", callback_data="close")
    ]])


    # Edit the existing message with updated info & new image
    await callback_query.message.edit_media(
        media=dict(
            type="photo",
            media=profile_pic,
            caption=response_text
        ),
        reply_markup=buttons
    )


@Bot.on_callback_query(filters.regex("^close"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()



    # Edit the existing message with updated info & new image
    await callback_query.message.edit_media(
        media=profile_pic,
        caption=response_text
    )






# """Get id of the replied user
# Syntax: /id"""

# from pyrogram import filters, enums
# from pyrogram.types import Message

# from bot import Bot


# @Bot.on_message(filters.command("id") & filters.private)
# async def showid(client, message):
#     chat_type = message.chat.type

#     if chat_type == enums.ChatType.PRIVATE:
#         user_id = message.chat.id
#         await message.reply_text(
#             f"<b>ʏᴏᴜʀ ᴜsᴇʀ ɪᴅ ɪs:</b> <code>{user_id}</code>", quote=True
#         )


# ---------------------------------------------------------------------------------
#==================================================================================

# from pyrogram import filters, enums
# from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
# import os
# import random 
# from bot import Bot
# from config import *  # Using existing (PICS)

# NO_PROFILE_PHOTO = "https://i.ibb.co/Mx2JYfrV/Shawn-Levy.jpg"  # Add this default photo URL

# @Bot.on_message(filters.command("id") & filters.private)
# async def showid(client, message: Message):
#     # Delete the command message
#     await message.delete()
    
#     user = message.from_user
#     user_id = user.id
#     first_name = user.first_name
#     last_name = user.last_name or "N/A"
#     username = f"@{user.username}" if user.username else "N/A"
#     language = user.language_code if user.language_code else "N/A"

#     # Generate response text
#     response_text = (
#         f"<blockquote>🔥 **User Info:**\n</blockquote>"
#         f"<blockquote>🆔 **User ID:** `{user_id}`\n</blockquote>"
#         f"<blockquote>📛 **First Name:** `{first_name}`\n</blockquote>"
#         f"<blockquote>📝 **Last Name:** `{last_name}`\n</blockquote>"
#         f"<blockquote>🔗 **Username:** `{username}`\n</blockquote>"
#         f"<blockquote>🌍 **Language:** `{language}`</blockquote>"
#     )

#     # More Info and Close buttons
#     buttons = InlineKeyboardMarkup([
#         [InlineKeyboardButton("• More Info •", callback_data=f"more_info_{user_id}")],
#         [InlineKeyboardButton("• Close •", callback_data="close")]
#     ])


#     # Send response and add reaction
#     bot_msg = await message.reply_photo(
#         photo=random.choice(PICS),
#         caption=response_text,
#         reply_markup=buttons
#     )
    
#     # Add reaction to bot's message
#     await bot_msg.react("🔥")


# @Bot.on_callback_query(filters.regex(r"more_info_(\d+)"))
# async def more_info(client, callback_query):
#     user_id = int(callback_query.data.split("_")[2])
#     user = await client.get_users(user_id)  # Fetch full user info

#     # Fetch user details
#     about = user.bio or "N/A"
#     try:
#         profile_pics = await client.get_chat_photos(user_id)
#         first_photo = await profile_pics.next()
#         profile_pic = first_photo.file_id
#     except StopAsyncIteration:
#         profile_pic = NO_PROFILE_PHOTO  # Use the default photo if no profile picture

#     join_date = user.status.date.strftime("%Y-%m-%d") if user.status else "Unknown"
#     bot_lang_code = callback_query.message.chat.language_code or "N/A"

#     # Update response text
#     response_text = (
#         f"<blockquote>🔥 **User Info:**\n</blockquote>"
#         f"<blockquote>🆔 **User ID:** `{user_id}`\n</blockquote>"
#         f"<blockquote>📛 **First Name:** `{user.first_name}`\n</blockquote>"
#         f"<blockquote>📝 **Last Name:** `{user.last_name or 'N/A'}`\n</blockquote>"
#         f"<blockquote>🔗 **Username:** `{user.username or 'N/A'}`\n</blockquote>"
#         f"<blockquote>🌍 **Language:** `{callback_query.message.chat.language_code}`</blockquote>\n\n"
        
#         f"<blockquote>🔹 **More Info:**\n</blockquote>"
#         f"<blockquote>📷 **Profile Picture:** Sent above 👆\n</blockquote>"
#         f"<blockquote>📝 **Bio:** `{about}`\n</blockquote>"
#         f"<blockquote>📅 **Joined Telegram:** `{join_date}`\n</blockquote>"
#         f"<blockquote>🤖 **Bot Language Code:** `{bot_lang_code}`</blockquote>\n\n"
#         f"<blockquote>👑 **Bot Owner:** @Anime106_Request_Bot </blockquote>"
#     )

#     # Close button
#     buttons = InlineKeyboardMarkup([[
#         InlineKeyboardButton("• Close •", callback_data="close")
#     ]])


#     # Edit the existing message with updated info & new image
#     await callback_query.message.edit_media(
#         media=dict(
#             type="photo",
#             media=profile_pic,
#             caption=response_text
#         ),
#         reply_markup=buttons
#     )


# @Bot.on_callback_query(filters.regex("^close"))
# async def close_callback(client, callback_query):
#     await callback_query.message.delete()



#     # Edit the existing message with updated info & new image
#     await callback_query.message.edit_media(
#         media=profile_pic,
#         caption=response_text
#     )


# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

# """Get id of the replied user
# Syntax: /id"""

# from pyrogram import filters, enums
# from pyrogram.types import Message

# from bot import Bot


# @Bot.on_message(filters.command("id") & filters.private)
# async def showid(client, message):
#     chat_type = message.chat.type

#     if chat_type == enums.ChatType.PRIVATE:
#         user_id = message.chat.id
#         await message.reply_text(
#             f"<b>ʏᴏᴜʀ ᴜsᴇʀ ɪᴅ ɪs:</b> <code>{user_id}</code>", quote=True
#         )
