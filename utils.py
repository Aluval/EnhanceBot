import time
import math
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PROGRESS_BAR = """
{5}

Progress: {0}%
{1} of {2}
Speed: {3}
ETA: {4}
"""

async def progress(current, total, message: Message, start):
    now = time.time()
    diff = now - start
    if diff == 0:
        diff = 0.1
    percentage = current * 100 / total
    speed = humanbytes(current / diff) + "/s"
    elapsed_time_ms = round(diff * 1000)
    time_to_completion_ms = round((total - current) / (current / diff)) * 1000 if current > 0 else 0
    estimated_total_time_ms = elapsed_time_ms + time_to_completion_ms

    elapsed_time = TimeFormatter(elapsed_time_ms)
    estimated_total_time = TimeFormatter(estimated_total_time_ms)

    progress_str = "{0}{1}".format(
        ''.join(["■" for _ in range(math.floor(percentage / 5))]),
        ''.join(["□" for _ in range(20 - math.floor(percentage / 5))])
    )

    try:
        await message.edit(
            text=PROGRESS_BAR.format(
                round(percentage, 2),
                humanbytes(current),
                humanbytes(total),
                speed,
                estimated_total_time if estimated_total_time != '' else '0 s',
                progress_str
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🌟 Jᴏɪɴ Us 🌟", url="https://t.me/Sunrises24botupdates")]]
            )
        )
    except Exception as e:
        print(f"Error editing progress message: {e}")

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    result = ((str(days) + "d, ") if days else "") + \
             ((str(hours) + "h, ") if hours else "") + \
             ((str(minutes) + "m, ") if minutes else "") + \
             ((str(seconds) + "s, ") if seconds else "") 
    return result.rstrip(", ")

def humanbytes(size):
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    Dic_powerN = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {Dic_powerN[n]}"
