import math
from time import time
from pyrogram.types import Message

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: '', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {Dic_powerN[n]}B"

def time_formatter(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s") if seconds else "")
    return tmp.strip(", ")

async def progress(current, total, message: Message, start, *args):
    now = time()
    diff = now - start
    if diff == 0:
        diff = 1
    percentage = current * 100 / total
    speed = current / diff
    eta = (total - current) / speed if speed else 0
    bar = "[" + "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10)) + "]"

    if int(percentage) % 5 == 0:
        try:
            await message.edit_text(
                f"{bar} {percentage:.2f}%\n"
                f"{humanbytes(current)} of {humanbytes(total)}\n"
                f"Speed: {humanbytes(speed)}/s\n"
                f"ETA: {time_formatter(eta)}"
            )
        except:
            pass  # ignore rate limit or race conditions
