from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
import os
import subprocess
import re
import time

API_ID = int(os.getenv("API_ID", "10811400"))     # Replace with your API_ID
API_HASH = os.getenv("API_HASH", "191bf5ae7a6c39771e7b13cf4ffd1279")  # Replace with your API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN", "7097361755:AAHJcqT4_YBvSq5hG7FwP5kDhugFBTwfRQE")  # Replace with your Bot Token
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "-1002067650699"))

app = Client("enhance_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

MAX_FILE_SIZE = 300 * 1024 * 1024  # 300MB

# Utility: Format seconds to HH:MM:SS string
def time_formatter(seconds: float) -> str:
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

# Utility: Human-readable bytes (optional, if used in progress)
def humanbytes(size):
    # Simple function to convert bytes to KB/MB/GB strings
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

# Progress callback for downloads/uploads (optional, from your utils)
async def progress(current, total, message: Message, start, *args):
    now = time.time()
    diff = now - start
    if round(diff % 5) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff if diff else 0
        eta = (total - current) / speed if speed else 0
        bar = "[" + "â–ˆ" * int(percentage / 10) + "â–‘" * (10 - int(percentage / 10)) + "]"
        try:
            await message.edit_text(
                f"{bar} {percentage:.2f}%\n"
                f"{humanbytes(current)} of {humanbytes(total)}\n"
                f"Speed: {humanbytes(speed)}/s\n"
                f"ETA: {time_formatter(eta)}"
            )
        except:
            pass  # ignore edit failures due to Telegram rate limits


@app.on_message(filters.command("enhance") & filters.reply)
async def enhance_video(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.video:
        return await message.reply("❌ Please reply to a video file with /enhance.")

    cmd = message.text.split(maxsplit=2)
    custom_name = "enhanced.mp4"
    if "-n" in cmd:
        name_index = cmd.index("-n") + 1
        if name_index < len(cmd):
            custom_name = cmd[name_index]
            if not custom_name.endswith(".mp4"):
                custom_name += ".mp4"

    user_id = message.from_user.id
    username = message.from_user.username or "NoUsername"
    video_msg = message.reply_to_message
    file_size = video_msg.video.file_size

    if file_size > MAX_FILE_SIZE:
        return await message.reply("❌ File is larger than 300MB. Please send a smaller video.")

    start = time.time()
    downloading = await message.reply("⏬ Downloading video...")
    input_path = await video_msg.download(
        progress=progress,
        progress_args=(downloading, video_msg.video.file_size, downloading, start)
    )
    await downloading.delete()

    if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
        return await message.reply("❌ Download failed or file is empty.")

    # Log initiation to log channel
    await client.send_message(
        chat_id=LOG_CHANNEL_ID,
        text=(
            f"**Enhancement Started**\n"
            f"👤 User: `{username}` (`{user_id}`)\n"
            f"📎 Filename: `{custom_name}`"
        )
    )

    # Get duration
    try:
        duration_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", input_path
        ]
        total_duration = float(subprocess.check_output(duration_cmd).decode().strip())
    except Exception as e:
        return await message.reply(f"❌ Couldn't get video duration: {e}")

    output_path = "enhanced.mp4"
    processing_msg = await message.reply("⚙️ Enhancing video...")

    # FFmpeg enhancement command
    cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", "scale=1920:1080:flags=lanczos,hqdn3d,"
               "unsharp=5:5:1.0:5:5:0.0,"
               "eq=contrast=1.2:brightness=0.05:saturation=1.2",
        "-map", "0", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-c:a", "copy", "-c:s", "mov_text",
        output_path
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time_pattern = re.compile(r'time=(\d+):(\d+):(\d+).(\d+)')
    last_percent = -1
    start_time = time.time()

    while True:
        line = process.stdout.readline()
        if line == "" and process.poll() is not None:
            break
        match = time_pattern.search(line)
        if match:
            h, m, s, ms = map(int, match.groups())
            current_seconds = h * 3600 + m * 60 + s + ms / 100
            percent = int((current_seconds / total_duration) * 100)
            if percent != last_percent and percent > 0:
                eta = time_formatter((time.time() - start_time) * (100 - percent) / percent)
                await processing_msg.edit_text(f"⚡ Enhancing video: {percent}%\nETA: {eta}")
                last_percent = percent

    await processing_msg.delete()

    retcode = process.poll()
    if retcode != 0:
        os.remove(input_path)
        return await message.reply(f"❌ FFmpeg failed with code {retcode}.")

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        os.remove(input_path)
        return await message.reply("❌ Enhanced file is empty or missing.")

    upload_msg = await message.reply("⬆️ Uploading enhanced video...")
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)

    await message.reply_document(
        document=output_path,
        file_name=custom_name,
        caption="✅ Enhanced Video (1080p) as Document",
        progress=progress,
        progress_args=(upload_msg, os.path.getsize(output_path), upload_msg, time.time())
    )

    await upload_msg.delete()
    os.remove(input_path)
    os.remove(output_path)

    # Log completion
    await client.send_message(
        chat_id=LOG_CHANNEL_ID,
        text=(
            f"**Enhancement Completed**\n"
            f"👤 User: `{username}` (`{user_id}`)\n"
            f"📎 Filename: `{custom_name}`"
        )
    )

if __name__ == "__main__":
    app.run()
