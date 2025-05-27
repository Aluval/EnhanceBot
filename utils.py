from time import time

def humanbytes(size: int) -> str:
    """Convert bytes to human-readable format."""
    if size < 0:
        return "0B"
    power = 2 ** 10
    n = 0
    units = ["B", "KB", "MB", "GB", "TB"]
    while size > power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}"

def time_formatter(seconds: int) -> str:
    """Format seconds to hh:mm:ss string."""
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

async def progress(current, total, message, start, *args):
    now = time()
    diff = now - start
    if diff == 0:
        diff = 0.1  # Avoid division by zero

    percentage = current * 100 / total
    speed = current / diff
    eta = (total - current) / speed if speed > 0 else 0
    bar_length = 10
    filled_length = int(bar_length * percentage // 100)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)

    try:
        await message.edit_text(
            f"{bar} {percentage:.2f}%\n"
            f"{humanbytes(current)} of {humanbytes(total)}\n"
            f"Speed: {humanbytes(speed)}/s\n"
            f"ETA: {time_formatter(eta)}"
        )
    except:
        pass  # Ignore errors like FloodWait or message deleted
