import time

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {power_labels[n]}B"

def time_formatter(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"

async def progress(current, total, message, start, *args, **kwargs):  # Accept extra args
    now = time.time()
    diff = now - start
    if diff == 0:
        diff = 1e-6

    speed = current / diff
    eta = (total - current) / speed if speed > 0 else 0
    percentage = current * 100 / total
    bar_length = 10
    filled_length = int(bar_length * percentage / 100)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)

    text = (
        f"[{bar}] {percentage:.2f}%\n"
        f"{humanbytes(current)} of {humanbytes(total)}\n"
        f"Speed: {humanbytes(speed)}/s\n"
        f"ETA: {time_formatter(eta)}"
    )

    try:
        await message.edit_text(text)
    except:
        pass
