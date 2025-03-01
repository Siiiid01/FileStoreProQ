
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id, check_user_ban

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
@check_user_ban
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(text = "•ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ ꜰɪʀꜱᴛ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ (ᴡɪᴛʜ ǫᴜᴏᴛᴇꜱ).. \n\n• ᴏʀ ꜱᴇɴᴅ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴘᴏꜱᴛ ʟɪɴᴋ\n <blockquote> Bᴀᴛᴄʜ ғɪʀsᴛ </blockquote>", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("<blockquote><b><i>⚠︎ ᴇʀʀᴏʀ</i></b></blockquote>\n\n<b><i>• ᴛʜɪꜱ ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴘᴏꜱᴛ ᴏʀ ʟɪɴᴋ  ɪꜱ ɴᴏᴛ ꜰʀᴏᴍ ᴍʏ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ... </i></b>", quote = True)
            continue

    while True:
        try:
            second_message = await client.ask(text = "• ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ ʟᴀꜱᴛ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ (ᴡɪᴛʜ ǫᴜᴏᴛᴇꜱ).. \n\n• ᴏʀ ꜱᴇɴᴅ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴘᴏꜱᴛ ʟɪɴᴋ\n<blockquote> Bᴀᴛᴄʜ Lᴀsᴛ </blockquote>​", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("<blockquote><b><i>⚠︎ ᴇʀʀᴏʀ</i></b></blockquote>\n\n<b><i>• ᴛʜɪꜱ ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴘᴏꜱᴛ ᴏʀ ʟɪɴᴋ  ɪꜱ ɴᴏᴛ ꜰʀᴏᴍ ᴍʏ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ... </i></b>", quote = True)
            continue


    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("✾ Sʜᴀʀᴇ URL ✾", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(f"<blockquote><b>• ʜᴇʀᴇ ɪꜱ ʏᴏᴜʀ ʙᴀᴛᴄʜ ʟɪɴᴋ •</b></blockquote>\n\n{link}", quote=True, reply_markup=reply_markup)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
@check_user_ban
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(text = "•ꜰᴏʀᴡᴀʀᴅ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ (ᴡɪᴛʜ ǫᴜᴏᴛᴇꜱ).. \n\n• ᴏʀ ꜱᴇɴᴅ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴘᴏꜱᴛ ʟɪɴᴋ​", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("<blockquote><b><i>⚠︎ ᴇʀʀᴏʀ</i></b></blockquote>\n\n<b><i>• ᴛʜɪꜱ ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴘᴏꜱᴛ ᴏʀ ʟɪɴᴋ  ɪꜱ ɴᴏᴛ ꜰʀᴏᴍ ᴍʏ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ... </i></b>", quote = True)
            continue

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("◈ Sʜᴀʀᴇ Uʀʟ ◈", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<blockquote><b>• ʜᴇʀᴇ ɪꜱ ʏᴏᴜʀ ʟɪɴᴋ •</b></blockquote>\n\n{link}", quote=True, reply_markup=reply_markup)
