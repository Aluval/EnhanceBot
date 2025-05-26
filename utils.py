import asyncio
from time import time
from pyrogram.types import Message

async def progress(current, total, message: Message, start):
    now = time()
    speed = current / (now - start + 0.001)
    percent = (current / total) * 100
    eta = (total - current) / speed if speed else 0
    text = (
        f"Uploading: {percent:.2f}%\n"
        f"Speed: {speed / 1024:.2f} KB/s\n"
        f"ETA: {eta:.2f} seconds"
    )
    try:
        await message.edit(text)
    except Exception:
        pass
