from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
import os
import subprocess
from time import time
import re
from utils import progress, humanbytes, Time_formatter

API_ID = int(os.getenv("API_ID", "10811400"))     # Replace with your API_ID
API_HASH = os.getenv("API_HASH", "191bf5ae7a6c39771e7b13cf4ffd1279")  # Replace with your API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN", "7097361755:AAHJcqT4_YBvSq5hG7FwP5kDhugFBTwfRQE")  # Replace with your Bot Token
app = Client("enhance_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

MAX_FILE_SIZE = 300 * 1024 * 1024  # 300MB

@app.on_message(filters.command("enhance") & filters.private)
async def enhance_video(client: Client, message: Message):
    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.document):
        return await message.reply("❌ Please reply to a **video** or **document** with `/enhance`.")

    media = message.reply_to_message.video or message.reply_to_message.document
    file_size = media.file_size

    if file_size > MAX_FILE_SIZE:
        return await message.reply("❌ File size exceeds 300MB limit.")

    custom_name = None
    if "-n" in message.text:
        parts = message.text.split("-n", 1)
        if len(parts) > 1:
            name = parts[1].strip()
            if name.lower().endswith((".mp4", ".mkv", ".mov")):
                custom_name = name

    start = time()
    downloading = await message.reply("⬇️ Downloading...")
    input_path = await media.download(
        progress=progress,
        progress_args=(downloading, file_size, downloading, start)
    )

    if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
        return await message.reply("❌ Download failed or empty file.")

    try:
        duration = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path
        ]).decode().strip())
    except Exception as e:
        return await message.reply(f"❌ Error getting duration: {e}")

    output_path = "enhanced.mp4"
    processing = await message.reply("⚙️ Enhancing...")

    cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", "scale=1920:1080:flags=lanczos,hqdn3d,"
               "unsharp=5:5:1.0:5:5:0.0,"
               "eq=contrast=1.2:brightness=0.05:saturation=1.2",
        "-map", "0", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-c:a", "copy", "-c:s", "mov_text", output_path
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    regex = re.compile(r'time=(\d+):(\d+):(\d+).(\d+)')
    last_percent = -1

    while True:
        line = proc.stdout.readline()
        if line == "" and proc.poll() is not None:
            break
        match = regex.search(line)
        if match:
            h, m, s, ms = map(int, match.groups())
            current = h * 3600 + m * 60 + s + ms / 100
            percent = int((current / duration) * 100)
            if percent != last_percent:
                await processing.edit_text(f"⚡ Enhancing: {percent}%\n⏳ ETA: {time_formatter(duration - current)}")
                last_percent = percent

    if proc.poll() != 0 or not os.path.exists(output_path):
        os.remove(input_path)
        return await message.reply("❌ Enhancement failed.")

    upload_msg = await message.reply("⬆️ Uploading enhanced video...")
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

    try:
        await message.reply_video(
            video=output_path,
            caption=f"✅ Enhanced Video (1080p)\n`{custom_name or 'enhanced.mp4'}`",
            file_name=custom_name or "enhanced.mp4",
            progress=progress,
            progress_args=(upload_msg, os.path.getsize(output_path), upload_msg, time())
        )
    except:
        await message.reply_document(
            document=output_path,
            caption=f"✅ Enhanced Video\n`{custom_name or 'enhanced.mp4'}`",
            file_name=custom_name or "enhanced.mp4",
            progress=progress,
            progress_args=(upload_msg, os.path.getsize(output_path), upload_msg, time())
        )

    os.remove(input_path)
    os.remove(output_path)

if __name__ == "__main__":
    app.run()
