import math
from time import time
from pyrogram.types import Message

def humanbytes(size):
    # Returns human-readable file size
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {Dic_powerN[n]}B"

def time_formatter(seconds):
    seconds = int(seconds)
    result = ""
    if seconds >= 3600:
        hours = seconds // 3600
        result += f"{hours}h "
        seconds %= 3600
    if seconds >= 60:
        minutes = seconds // 60
        result += f"{minutes}m "
        seconds %= 60
    result += f"{seconds}s"
    return result.strip()

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
        except: pass
