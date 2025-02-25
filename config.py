import os
import random 
from os import environ,getenv
import logging
from logging.handlers import RotatingFileHandler


#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "123654782:")
#Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", ""))
#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")
#Your db channel Id
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002008657265"))
# NAMA OWNER
OWNER = os.environ.get("OWNER", "Anime106_Request_bot")
#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "2090517919"))
#Port
PORT = os.environ.get("PORT", "8080")
#Database
DB_URI = os.environ.get("DATABASE_URL", "")
DB_NAME = os.environ.get("DATABASE_NAME", "Cluster99")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "zoro")

#Time in seconds for message delete, put 0 to never delete
TIME = int(os.environ.get("TIME", "120"))


#force sub channel id, if you want enable force sub
FORCE_SUB_CHANNEL1 = int(os.environ.get("FORCE_SUB_CHANNEL1", "-1001712434868"))
#put 0 to disable
FORCE_SUB_CHANNEL2 = int(os.environ.get("FORCE_SUB_CHANNEL2", "0"))#put 0 to disable
FORCE_SUB_CHANNEL3 = int(os.environ.get("FORCE_SUB_CHANNEL3", "0"))#put 0 to disable
FORCE_SUB_CHANNEL4 = int(os.environ.get("FORCE_SUB_CHANNEL4", "0"))#put 0 to disable


# Log channels
TELEGRAPH_LOG_CHANNEL = os.environ.get("TELEGRAPH_LOG_CHANNEL", "-1002023266715")
BAN_LOG_CHANNEL = os.environ.get("BAN_LOG_CHANNEL", "-1002023266715")
NEW_USER_LOG_CHANNEL = os.environ.get("NEW_USER_LOG_CHANNEL", "-1002023266715") 


TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

#random pics seprated by space
PICS = os.environ.get("PICS", "https://i.ibb.co/XxbHQ9Gk/9a45465f2734f8605fed7f4af74327d7.jpg https://i.ibb.co/tT3zN48J/11de456850aa9f6658b261e32f251adc.jpg https://i.ibb.co/bjv2mPqm/13c8721971be20487907d888f9499b86.jpg https://i.ibb.co/mrRxhmWZ/015a4efb55c3afcf8ba14f2a3bcfd3fe.jpg https://i.ibb.co/T3N3r9d/26f7a1b317fe45c561e16801a5ca1dac.jpg https://i.ibb.co/h1xBWZ7t/37f6e062f2102ee3f24ef951a31f1187.jpg https://i.ibb.co/VcMwPbv5/286b8c1c0c82369d9dd2de76e376965d.jpg https://i.ibb.co/DfSJcnDy/451eddc019cbfd5771d8eea67cd3a2f1.jpg https://i.ibb.co/C59WqYfx/416846b57cac2dea82ec64e6b5d25143.jpg https://i.ibb.co/ymrgyFYr/651587a924c109a8044c1a644b0eb02d.jpg https://i.ibb.co/35YXNj90/791117c8699dbe3ec06a5b05181140ba.jpg https://i.ibb.co/ZRCNWBYG/4051986ff3e8189ad0b632a5afa4ef55.jpg https://i.ibb.co/VctbyT45/a71cda7519b6bef1a12da8aadc58a226.jpg https://i.ibb.co/Q7Jy0Xt9/a4851b8177e7543e14f50014308bbc6d.jpg https://i.ibb.co/RRQ12vP/b1cfdaaeb073b478b6b55a3082c6e39f.jpg https://i.ibb.co/cKgWD7K5/b8695471815592db698416feb2bea3b8.jpg https://i.ibb.co/4nXjyzNK/bb904bb66452e4cec045da5483a8ded9.jpg https://i.ibb.co/TMRB0Rvr/cacecd9472deaf6950a33bb2abec9658.jpg https://i.ibb.co/sJqXhk69/cb6a673c58e205907a31c86fdd0cf258.jpg https://i.ibb.co/tMtF2bVV/de14c54e3fe99a3f576bd9396517962e.jpg https://i.ibb.co/SDzP8V7t/e414da7e55508a6e6674060b0db53c4f.jpg https://i.ibb.co/4gsQC7WD/e3130de1bd5d7cb390db553b80085c31.jpg https://i.ibb.co/5gQzK63P/ec1780d148293d41ba0785281200decd.jpg https://i.ibb.co/ccWQ3p79/ef8f1b0850464b31162382955ee93c18.jpg https://i.ibb.co/kg0XW9pJ/f1476eccd899f6db25f6696f599a4ca3.jpg").split()
START_PIC = random.choice(PICS)


# Turn this feature on or off using True or False put value inside  ""
# TRUE for yes FALSE if no 
TOKEN = True if os.environ.get('TOKEN', "False") == "True" else False 
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "publicearn.com")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 600)) # Add time in seconds
IS_VERIFY = os.environ.get("IS_VERIFY", "True")
TUT_VID = os.environ.get("TUT_VID","https://t.me/Moviess_Ok/43")


HELP_TXT = '''<b>╭──〔 📂 ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ 〕──╮</b>  
<blockquote>• ᴡᴏʀᴋɪɴɢ ғᴏʀ <b>@Moviess_Ok</b> 🚀  </blockquote>  

<b>• ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅꜱ:</b>  
<blockquote expandable><b>• ᴜꜱᴇʀꜱ ᴄᴏᴍᴍᴀɴᴅꜱ:</b>  
📌 /alive – ᴄʜᴇᴄᴋ ʙᴏᴛ ꜱᴛᴀᴛᴜꜱ  
📌 /start – ꜱᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ  
📌 /id – ɢᴇᴛ ʏᴏᴜʀ ᴜꜱᴇʀ ɪᴅ  
📌 /telegraph – ᴜᴘʟᴏᴀᴅ ᴍᴇᴅɪᴀ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴘʜ  
📌 /feedback – ꜱᴇɴᴅ ꜰᴇᴇᴅʙᴀᴄᴋ ᴛᴏ ᴀᴅᴍɪɴ  
📌 /ping – ᴛᴇꜱᴛ ʙᴏᴛ ʀᴇꜱᴘᴏɴꜱᴇ ᴛɪᴍᴇ  
📌 /stickerid – ɢᴇᴛ ꜱᴛɪᴄᴋᴇʀ ɪᴅ </blockquote>  


<blockquote>• <i>ᴏᴡɴᴇʀ:</i> <a href="https://t.me/Anime106_Request_bot">QuirkySiiiiiid</a></blockquote>'''


ABOUT_TXT = '''<b><blockquote expandable>◈ ᴄʀᴇᴀᴛᴏʀ: <a href=https://t.me/Anime106_Request_Bot>QuirkySiiiiiid</a>
◈ ꜰᴏᴜɴᴅᴇʀ ᴏꜰ : <a href=https://t.me/Moviess_Ok>ᴍᴏᴠɪᴇꜱ ᴏᴋ</a>
◈ ᴀɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ : <a href=https://t.me/AnnimeMoviessok>ᴀɴɪᴍᴇ'ꜱ ᴏᴋ</a>
◈ ᴏɴᴇ ᴘɪᴇᴄᴇ ᴄʜᴀɴɴᴇʟ : <a href=https://t.me/Moviess_Ok>ᴏɴᴇ ᴘɪᴇᴄᴇ</a>
◈ ᴀᴅᴜʟᴛ ᴍᴀɴʜᴡᴀ : <a href=https://t.me/H_Anime_and_popular_videos>ᴀᴅ*ʟᴛ</a>
◈ ᴍᴀɴɢᴀ/ᴍᴀɴʜᴡᴀ ᴄʜᴀɴɴᴇʟ: <a href=https://telegram.me/+KA9OYVhJXptiYzll>ᴇᴛᴇʀɴᴀʟᴍᴀɴɢᴀ</a>
♏︎ ᴅᴇᴠᴇʟᴏᴘᴇʀ : <a href=https://t.me/Anime106_Request_Bot>QuirkySiiiiiid</a></blockquote></b>'''


MORE_TXT = '''<b><blockquote expandable>ᴛʜɪs ɪs ᴀɴ ғɪʟᴇ ᴛᴏ ʟɪɴᴋ ʙᴏᴛ ᴡᴏʀᴋ ғᴏʀ @Moviess_Ok </blockquote></b>'''
# MORE_TXT = '''**> ᴛʜɪs ɪs ᴀɴ ғɪʟᴇ ᴛᴏ ʟɪɴᴋ ʙᴏᴛ ᴡᴏʀᴋ ғᴏʀ @Moviess_Ok [🎬](tg://emoji?id=5780464752744468119)**'''



START_MSG = os.environ.get("START_MESSAGE", '''<b>╭─▸ ʙᴀᴋᴋᴀᴀᴀ!! {mention} ⚡🔥 ◂─╮</b>  
<blockquote expandable>╔════════════════════════════╗  
  🚀 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴜʟᴛɪᴍᴀᴛᴇ ғɪʟᴇ ʙᴏᴛ!</b>  
  🛡️ <i>ᴘʀɪᴠᴀᴛᴇ & sᴇᴄᴜʀᴇ ғɪʟᴇ sᴛᴏʀᴀɢᴇ.</i>  
  🎮 <b>ᴍɪɴɪ-ɢᴀᴍᴇs ᴍᴏᴅᴇ:</b> <i>ғᴜɴ ᴀᴡᴀɪᴛs!</i>  
  🔗 <b>ɢᴇɴᴇʀᴀᴛᴇ ᴜɴɪǫᴜᴇ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋs!</b>  
  ⚡ <i>ʙʟᴀᴢɪɴɢ ғᴀsᴛ ғɪʟᴇ ʀᴇᴛʀɪᴇᴠᴀʟ.</i>  
  🕹️ <b>ʀᴇᴛʀᴏ-ɢᴀᴍɪɴɢ ᴠɪʙᴇs ᴜɴʟᴏᴄᴋᴇᴅ!</b>  
  💠 <i>ᴜɴʙʀᴇᴀᴋᴀʙʟᴇ, ᴜʟᴛʀᴀ-ᴇʟɪᴛᴇ, ᴄʟᴀssɪᴄ.</i>  
╚════════════════════════════╝</blockquote>''')
try:
    ADMINS=[2090517919]
    for x in (os.environ.get("ADMINS", "2090517919").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")

#Force sub message 
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", """<blockquote>⋟⋟ ʜᴇʟʟᴏ, <b>{first}</b>! </blockquote>  

<blockquote><b><i>🔹 ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟꜱ, ᴛʜᴇɴ ᴛᴀᴘ ᴛʜᴇ <u>ʀᴇʟᴏᴀᴅ</u> ʙᴜᴛᴛᴏɴ  
ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ꜰɪʟᴇ! 🔹</i></b></blockquote>""")

#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "<<blockquote><i><b>• ʙʏ @Moviess_Ok</b></i></blockquote>")

#set True if you want to prevent users from forwarding files from bot
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False

# Message effect IDs
REACTIONS = ["❤️", "🔥", "🎉" ]

#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'

BOT_STATS_TEXT = """
<b>📊 Bot Statistics</b>

⏱ Uptime: {uptime}
"""



USER_REPLY_TEXT = "ʙᴀᴋᴋᴀ ! ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍʏ ꜱᴇɴᴘᴀɪ!!"

ADMINS.append(OWNER_ID)
ADMINS.append(2090517919)

LOG_FILE_NAME = "QuirkySiiiiiidFileShare.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
   