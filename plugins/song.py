from pyrogram import Client, filters
from pyrogram.types import Message
import os, requests, yt_dlp, asyncio
from youtube_search import YoutubeSearch

CHANNEL_LINK = "https://t.me/Moviess_Ok"

@Client.on_message(filters.command("song") & filters.private)
async def song(client, message: Message):
    # React to the command with music emoji
    try:
        await message.react("👻", big=True)
    except:
        pass

    query = " ".join(message.command[1:])
    
    if not query:
        error_msg = await message.reply("**Usage:** `/song [song name]`")
        # Delete command and error message after 10 minutes
        await asyncio.sleep(600)
        try:
            await message.delete()
            await error_msg.delete()
        except:
            pass
        return
    
    m = await message.reply(f"🎵 **Searching for:** `{query}`")
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        duration = results[0]["duration"]
        thumbnail = results[0]["thumbnails"][0]
        
        # Download thumbnail
        thumb_name = f'thumb_{message.id}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)
        
    except Exception as e:
        error_msg = await m.edit("⚠ **Song not found!** Try a different name.")
        # Delete messages after 10 minutes
        await asyncio.sleep(600)
        try:
            await message.delete()
            await error_msg.delete()
        except:
            pass
        return

    await m.edit("📥 **Downloading your song...**")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'format_limitations': False,
        'extractaudio': True,
        'preferredcodec': 'mp3',
        'preferredquality': '192',
        'noplaylist': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'cookiefile': None,  # Don't use cookies
        'nocheckcertificate': True,  # Skip HTTPS certificate validation
        'outtmpl': '%(title)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            audio_url = info['url']
            title = info['title']
            
            # Download audio directly using requests
            audio_name = f"{title}.mp3"
            response = requests.get(audio_url, allow_redirects=True)
            with open(audio_name, 'wb') as f:
                f.write(response.content)

        # Convert duration to seconds
        duration_parts = duration.split(':')
        duration_sec = sum(x * int(t) for x, t in zip([1, 60, 3600][::-1], duration_parts[::-1]))

        # Send audio
        sent_audio = await message.reply_audio(
            audio_name,
            caption=f"🎧 **{title}**\n[🔗 Join Channel]({CHANNEL_LINK})",
            thumb=thumb_name,
            duration=duration_sec,
            performer="@Moviess_Ok"
        )
        
        # Send auto-delete notification
        notification = await message.reply(
            "⚠️ **This song will be auto-deleted in 10 minutes!**\n"
            "**Save it to your saved messages or channel before it's deleted.**"
        )
        
        await m.delete()

        # Wait for 10 minutes then delete everything
        await asyncio.sleep(600)
        try:
            await message.delete()  # Delete original command
            await sent_audio.delete()
            await notification.delete()
        except Exception as e:
            print(f"Error deleting messages: {e}")

    except Exception as e:
        error_msg = await m.edit(f"🚫 **Download Error!**\nTry another song or contact support.")
        print(e)  # For debugging
        # Delete messages after 10 minutes even if download failed
        await asyncio.sleep(600)
        try:
            await message.delete()
            await error_msg.delete()
        except:
            pass

    finally:
        # Clean up files
        try:
            os.remove(audio_name)
            os.remove(thumb_name)
        except:
            pass
