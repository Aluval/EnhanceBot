from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
import os
import subprocess
from time import time
import re
from utils import progress, humanbytes, time_formatter

API_ID = int(os.getenv("API_ID", "10811400"))
API_HASH = os.getenv("API_HASH", "191bf5ae7a6c39771e7b13cf4ffd1279")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7097361755:AAHJcqT4_YBvSq5hG7FwP5kDhugFBTwfRQE")

app = Client("enhance_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

MAX_FILE_SIZE = 300 * 1024 * 1024  # 300MB

def format_eta(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s" if minutes else f"{secs}s"

@app.on_message(filters.command("enhance") & filters.reply)
async def enhance_video(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.video:
        return await message.reply("❌ Please reply to a video with `/enhance`.")

    video_msg = message.reply_to_message
    file_size = video_msg.video.file_size

    if file_size > MAX_FILE_SIZE:
        return await message.reply("❌ File is larger than 300MB.")

    custom_name = None
    if "-n" in message.text:
        parts = message.text.split("-n", 1)
        if len(parts) > 1:
            name = parts[1].strip()
            if name and name.lower().endswith((".mp4", ".mkv", ".mov")):
                custom_name = name

    start = time()
    downloading = await message.reply("⬇️ Downloading video...")
    input_path = await video_msg.download(
        progress=progress,
        progress_args=(downloading, file_size, downloading, start)
    )

    if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
        return await message.reply("❌ Download failed or file is empty.")

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

    cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", "scale=1920:1080:flags=lanczos,hqdn3d,"
               "unsharp=5:5:1.0:5:5:0.0,"
               "eq=contrast=1.2:brightness=0.05:saturation=1.2",
        "-map", "0",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-c:a", "copy",
        "-c:s", "mov_text",
        output_path
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time_pattern = re.compile(r'time=(\d+):(\d+):(\d+).(\d+)')
    last_percent = -1

    while True:
        line = process.stdout.readline()
        if line == "" and process.poll() is not None:
            break
        match = time_pattern.search(line)
        if match:
            h, m, s, ms = map(int, match.groups())
            current_seconds = h * 3600 + m * 60 + s + ms / 100
            percent = int((current_seconds / total_duration) * 100)
            eta = format_eta(total_duration - current_seconds)
            if percent != last_percent:
                await processing_msg.edit_text(f"⚡ Enhancing video: {percent}%\n⏳ ETA: {eta}")
                last_percent = percent

    if process.poll() != 0:
        os.remove(input_path)
        return await message.reply("❌ FFmpeg enhancement failed.")

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        os.remove(input_path)
        return await message.reply("❌ Enhanced file missing or empty.")

    await processing_msg.edit_text("⬆️ Uploading enhanced video...")
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

    final_name = custom_name if custom_name else "enhanced.mp4"
    try:
        await message.reply_video(
            video=output_path,
            caption=f"✅ Enhanced Video (1080p)\nName: `{final_name}`",
            file_name=final_name,
            progress=progress,
            progress_args=(message, os.path.getsize(output_path), message, time())
        )
    except Exception:
        await message.reply_document(
            document=output_path,
            caption=f"✅ Enhanced Video (1080p)\nName: `{final_name}`",
            file_name=final_name,
            progress=progress,
            progress_args=(message, os.path.getsize(output_path), message, time())
        )

    os.remove(input_path)
    os.remove(output_path)

if __name__ == "__main__":
    app.run()
