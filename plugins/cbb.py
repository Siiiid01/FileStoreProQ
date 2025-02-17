import os
from pyrogram import Client
from bot import Bot
from config import *
import random
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    
    if data == "help":
        await query.message.edit_media(
            media=InputMediaPhoto(
                random.choice(PICS),  # New random image every time
                caption=HELP_TXT.format(first=query.from_user.first_name)
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʜᴏᴍᴇ", callback_data='start'),
                 InlineKeyboardButton("ᴄʟᴏꜱᴇ •", callback_data='close')]
            ])
        )

    elif data == "about":
        await query.message.edit_media(
            media=InputMediaPhoto(
                random.choice(PICS),  # New random image every time
                caption=ABOUT_TXT.format(first=query.from_user.first_name)
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʜᴏᴍᴇ •", callback_data='start'),
                 InlineKeyboardButton("ᴄʟᴏꜱᴇ •", callback_data='close')]
            ])
        )

    elif data == "start":
        await query.message.edit_media(
            media=InputMediaPhoto(
                random.choice(PICS),  # New random image every time
                caption=START_MSG.format(first=query.from_user.first_name)
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʜᴇʟᴘ •", callback_data='help'),
                 InlineKeyboardButton("• ᴀʙᴏᴜᴛ •", callback_data='about')]
            ])
        )

    elif data == "more":
        await query.message.edit_media(
            media=InputMediaPhoto(
                random.choice(PICS),  # New random image every time
                caption=MORE_TXT.format(first=query.from_user.first_name)
                # parse_mode="MarkdownV2"  # Ensure proper formatting
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʜᴇʟᴘ •", callback_data='help'),
                 InlineKeyboardButton("• ᴀʙᴏᴜᴛ •", callback_data='about')]
            ])
        )

    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass





# ////////////////////////////////////////////////////////////////////////////
# old code without random media
# *******************************************************************************
# from pyrogram import Client 
# from bot import Bot
# from config import *
# from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
# from database.database import add_user, del_user, full_userbase, present_user

# @Bot.on_callback_query()
# async def cb_handler(client: Bot, query: CallbackQuery):
#     data = query.data
#     if data == "help":
#         await query.message.edit_media()(
#             text=HELP_TXT.format(first=query.from_user.first_name),
#             disable_web_page_preview=True,
#             reply_markup=InlineKeyboardMarkup(
#                 [
                    
#                     [
#                         InlineKeyboardButton('• ʜᴏᴍᴇ', callback_data='start'),
#                         InlineKeyboardButton("ᴄʟᴏꜱᴇ •", callback_data='close')
#                     ]
#                 ]
#             )
#         )
#     elif data == "about":
#         await query.message.edit_media()(
#             text=ABOUT_TXT.format(first=query.from_user.first_name),
#             disable_web_page_preview=True,
#             reply_markup=InlineKeyboardMarkup(
#                 [
#                     [InlineKeyboardButton('• ʜᴏᴍᴇ •', callback_data='start'),
#                      InlineKeyboardButton('ᴄʟᴏꜱᴇ •', callback_data='close')]
#                 ]
#             )
#         )
#     elif data == "start":
#         await query.message.edit_media()(
#             text=START_MSG.format(first=query.from_user.first_name),
#             disable_web_page_preview=True,
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("• ʜᴇʟᴘ •", callback_data='help'),
#                  InlineKeyboardButton("• ᴀʙᴏᴜᴛ •", callback_data='about')]
#             ])
#         )
    
#     elif data == "close":
#         await query.message.delete()
#         try:
#             await query.message.reply_to_message.delete()
#         except:
#             pass
