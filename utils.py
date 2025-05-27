import math, time
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def humanbytes(size):
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    Dic_powerN = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s, ") if seconds else "") + \
          ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]


async def progress_message(current, total, ud_type, message, start):
    now = time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = humanbytes(current / diff) + "/s"
        elapsed_time_ms = round(diff * 1000)
        time_to_completion_ms = round((total - current) / (current / diff)) * 1000
        estimated_total_time_ms = elapsed_time_ms + time_to_completion_ms
        estimated_total_time = TimeFormatter(estimated_total_time_ms)
        progress = "{0}{1}".format(
            ''.join(["■" for _ in range(math.floor(percentage / 5))]),
            ''.join(["□" for _ in range(20 - math.floor(percentage / 5))])
        )
        try:
            await message.edit(
                f"{ud_type}\n\n{progress}\nProgress: {round(percentage, 2)}%\n"
                f"{humanbytes(current)} of {humanbytes(total)}\nSpeed: {speed}\nETA: {estimated_total_time}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🌟 Join Us 🌟", url="https://t.me/Sunrises24botupdates")]
                ])
            )
        except Exception as e:
            print(f"Error editing message: {e}")
