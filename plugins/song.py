from pyrogram import Client, filters
from pyrogram.types import Message
import os, requests
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

CHANNEL_LINK = "https://t.me/Moviess_Ok"  # Replace with your actual channel

@Client.on_message(filters.command("song") & filters.private)
async def song(client, message: Message):
    query = " ".join(message.command[1:])
    
    if not query:
        return await message.reply("**Usage:** `/song [song name]`")
    
    m = await message.reply(f"🎵 **Searching for:** `{query}`")
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        video_url = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        duration = results[0]["duration"]
        thumbnail_url = results[0]["thumbnails"][0]
        
        thumb_name = f'thumb_{title}.jpg'
        thumb = requests.get(thumbnail_url, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)
    except Exception as e:
        return await m.edit("⚠ **Song not found!** Try a different name.")
    
    await m.edit("📥 **Downloading your song...**")
    
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)

        # Convert duration to seconds
        duration_parts = list(map(int, duration.split(':')))
        duration_secs = sum(duration_parts[i] * 60 ** (len(duration_parts)-i-1) for i in range(len(duration_parts)))

        await message.reply_audio(
            audio_file,
            caption=f"🎧 **Downloaded Song**\n[🔗 Join Channel]({CHANNEL_LINK})",
            title=title,
            duration=duration_secs,
            performer="MusicBot",
            thumb=thumb_name
        )            
        await m.delete()
    except Exception as e:
        await m.edit("🚫 **Error Downloading Song!**")
    
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except:
        pass
