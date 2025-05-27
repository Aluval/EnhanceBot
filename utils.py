from time import time
import math
from pyrogram.types import Message

# Progress function
async def progress(current, total, message, start, *args):
    percent = int(current * 100 / total)
    elapsed = time() - start
    speed = current / elapsed if elapsed > 0 else 0
    eta = (total - current) / speed if speed > 0 else 0
    try:
        await message.edit_text(
            f"⬇️ Progress: {percent}%\n"
            f"Speed: {speed / 1024:.2f} KB/s\nETA: {int(eta)}s"
        )
    except:
        pass
