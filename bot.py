from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
import os
import subprocess
import re
import time

API_ID = int(os.getenv("API_ID", "10811400"))
API_HASH = os.getenv("API_HASH", "191bf5ae7a6c39771e7b13cf4ffd1279")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7097361755:AAHJcqT4_YBvSq5hG7FwP5kDhugFBTwfRQE")

app = Client("enhance_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
MAX_FILE_SIZE = 300 * 1024 * 1024

def time_formatter(seconds: float) -> str:
    seconds = int(seconds)
    return f"{seconds//3600:02d}:{(seconds%3600)//60:02d}:{seconds%60:02d}"

def humanbytes(size):
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

async def progress(current, total, message: Message, start, *args):
    now = time.time()
    diff = now - start
    if round(diff % 5) == 0 or current == total:
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
            pass

@app.on_message(filters.command("enhance") & filters.reply)
async def enhance_video(client: Client, message: Message):
    args = message.text.split()
    filename = "enhanced.mp4"
    upload_as_document = False

    for arg in args:
        if arg.endswith((".mp4", ".mkv", ".mov")) and "-n" in args:
            filename = arg
        if "-d" in args:
            upload_as_document = True

    if not message.reply_to_message or not message.reply_to_message.video:
        return await message.reply("❌ Please reply to a video with `/enhance` command.")

    video_msg = message.reply_to_message
    file_size = video_msg.video.file_size

    if file_size > MAX_FILE_SIZE:
        return await message.reply("❌ File too large. Max size is 300MB.")

    start = time.time()
    downloading = await message.reply("⬇️ Downloading...")
    input_path = await video_msg.download(
        progress=progress,
        progress_args=(downloading, file_size, downloading, start)
    )
    await downloading.delete()

    if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
        return await message.reply("❌ Download failed or file is empty.")

    try:
        duration_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", input_path
        ]
        total_duration = float(subprocess.check_output(duration_cmd).decode().strip())
    except Exception as e:
        return await message.reply(f"❌ Failed to get duration: {e}")

    processing_msg = await message.reply("⚙️ Enhancing...")

    cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", "scale=1920:1080:flags=lanczos,hqdn3d,unsharp=5:5:1.0:5:5:0.0,"
               "eq=contrast=1.2:brightness=0.05:saturation=1.2",
        "-map", "0",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-c:a", "copy",
        "-c:s", "mov_text",
        filename
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
                eta = time.time() - start_time
                remaining = eta * (100 - percent) / percent
                await processing_msg.edit_text(f"⚡ Enhancing video: {percent}%\nETA: {time_formatter(remaining)}")
                last_percent = percent

    await processing_msg.delete()
    retcode = process.poll()

    if retcode != 0 or not os.path.exists(filename) or os.path.getsize(filename) == 0:
        os.remove(input_path)
        return await message.reply("❌ FFmpeg processing failed or file missing.")

    upload_msg = await message.reply("⬆️ Uploading enhanced file...")
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT if upload_as_document else ChatAction.UPLOAD_VIDEO)

    try:
        if upload_as_document:
            await message.reply_document(
                document=filename,
                file_name=filename,
                caption=f"✅ Enhanced File: `{filename}`",
                progress=progress,
                progress_args=(upload_msg, os.path.getsize(filename), upload_msg, time.time())
            )
        else:
            await message.reply_video(
                video=filename,
                caption=f"✅ Enhanced Video: `{filename}`",
                supports_streaming=True,
                progress=progress,
                progress_args=(upload_msg, os.path.getsize(filename), upload_msg, time.time())
            )
    except Exception as e:
        await message.reply(f"❌ Upload failed: {e}")

    await upload_msg.delete()
    os.remove(input_path)
    os.remove(filename)

if __name__ == "__main__":
    app.run()
