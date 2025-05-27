from time import time
import math
from pyrogram.types import Message

# Progress function
async def progress(current, total, message: Message, start, *args):
    now = time()
    diff = now - start

    if round(diff % 5) == 0:
        percentage = current * 100 / total
        speed = current / diff if diff else 0
        eta = (total - current) / speed if speed else 0
        bar = "[" + "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10)) + "]"

        try:
            await message.edit_text(
                f"{bar} {percentage:.2f}%\n"
                f"{humanbytes(current)} of {humanbytes(total)}\n"
                f"Speed: {humanbytes(speed)}/s\n"
                f"ETA: {time_formatter(eta)}"
            )
        except:
            pass  # Avoid crash if Telegram rate-limitsa
