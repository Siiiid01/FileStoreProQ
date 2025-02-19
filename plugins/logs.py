import os
import sys
import traceback
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from config import ADMINS

# Initialize error log file
ERROR_LOG_FILE = "bot_errors.log"

def log_error(error_message: str):
    """Log errors to file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ERROR_LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {error_message}\n")

def get_error_logs():
    """Read and return error logs"""
    try:
        if os.path.exists(ERROR_LOG_FILE):
            with open(ERROR_LOG_FILE, "r") as f:
                logs = f.read().strip()
            return logs if logs else "No errors logged."
        return "No error log file exists."
    except Exception as e:
        return f"Error reading logs: {str(e)}"

# Command to view errors
@Bot.on_message(filters.command("errors") & filters.private & filters.user(ADMINS))
async def view_errors(client: Bot, message: Message):
    try:
        logs = get_error_logs()
        if len(logs) > 4000:
            # If logs are too long, send as file
            with open("error_logs.txt", "w") as f:
                f.write(logs)
            await message.reply_document(
                "error_logs.txt",
                caption="Bot Error Logs",
                quote=True
            )
            os.remove("error_logs.txt")  # Clean up
        else:
            # Send logs as message
            await message.reply_text(f"**Bot Error Logs:**\n\n```{logs}```", quote=True)
    except Exception as e:
        await message.reply_text(f"Error retrieving logs: {str(e)}", quote=True)

# Function to handle uncaught exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    """Log uncaught exceptions"""
    error_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    log_error(f"Uncaught exception:\n{error_details}")
    sys.__excepthook__(exc_type, exc_value, exc_traceback)  # Call original exception handler

# Set up exception handler
sys.excepthook = handle_exception 