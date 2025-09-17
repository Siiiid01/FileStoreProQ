from bot import Bot
import pyrogram.utils
from database.database import set_maintenance_mode  # Add this import

pyrogram.utils.MIN_CHANNEL_ID = -1002008657265

async def init_maintenance():
    """Initialize maintenance mode to False on bot start"""
    try:
        await set_maintenance_mode(False)
    except Exception as e:
        print(f"Error initializing maintenance mode: {e}")

if __name__ == "__main__":
    Bot().run()
