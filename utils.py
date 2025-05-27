from time import time
import math
from pyrogram.types import Message

async def progress(current, total, message: Message, start):
    now = time()
    diff = now - start

    if round(diff % 5) == 0:
        percentage = current * 100 / total
        speed = current / diff
        eta = (total - current) / speed if speed != 0 else 0
        bar = "[" + "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10)) + "]"

        await message.edit_text(
            f"{bar} {percentage:.2f}%\n"
            f"{humanbytes(current)} of {humanbytes(total)}\n"
            f"Speed: {humanbytes(speed)}/s\n"
            f"ETA: {time_formatter(eta)}"
        )

def humanbytes(size):
    if not size:
        return "0 B"
    power = 1024
    n = 0
    Dic_powerN = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {Dic_powerN[n]}"

def time_formatter(seconds):
    seconds = int(seconds)
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return (f"{days}d " if days else "") + \
           (f"{hours}h " if hours else "") + \
           (f"{minutes}m " if minutes else "") + \
           (f"{sec}s" if sec else "")
