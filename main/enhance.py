import os
import time
import re
import subprocess

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction

from main.utils import progress, humanbytes, time_formatter
from config import *

MAX_FILE_SIZE = 300 * 1024 * 1024  # 300MB


# 🌟 PixelPulseBot Enhance (Video + Document Support)
@Client.on_message(filters.command("enhance") & filters.reply)
async def enhance_video(client: Client, message: Message):

    reply = message.reply_to_message

    # ✅ SUPPORT VIDEO + DOCUMENT
    if reply.video:
        media = reply.video
    elif reply.document and reply.document.mime_type.startswith("video"):
        media = reply.document
    else:
        return await message.reply("❌ Reply to a video or video document with /enhance")

    file_size = media.file_size

    # 🚫 SIZE CHECK
    if file_size > MAX_FILE_SIZE:
        return await message.reply(
            f"❌ File too large!\n\n"
            f"📦 Size: {humanbytes(file_size)}\n"
            f"🚫 Limit: 300MB"
        )

    start = time.time()

    # ⬇️ DOWNLOAD (LIVE)
    downloading = await message.reply("⬇️ Downloading video...")

    input_path = await reply.download(
        progress=progress,
        progress_args=(downloading, file_size, downloading, start)
    )

    await downloading.delete()

    if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
        return await message.reply("❌ Download failed or file is empty")

    # 🎬 GET DURATION
    try:
        duration_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_path
        ]
        total_duration = float(subprocess.check_output(duration_cmd).decode().strip())
    except Exception as e:
        return await message.reply(f"❌ Couldn't get duration: {e}")

    output_path = "enhanced.mp4"

    processing_msg = await message.reply("⚡ Enhancing video...")

    # 🔥 ENHANCE FILTERS
    cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", "scale=1920:1080:flags=lanczos,hqdn3d,"
               "unsharp=5:5:1.0:5:5:0.0,"
               "eq=contrast=1.2:brightness=0.05:saturation=1.2",
        "-map", "0",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-c:a", "copy",
        "-c:s", "mov_text",
        "-y", output_path
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # 🔥 LIVE PROGRESS
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
            current = h * 3600 + m * 60 + s + ms / 100

            percent = int((current / total_duration) * 100)

            if percent != last_percent and percent > 0:
                elapsed = time.time() - start_time
                eta = elapsed * (100 - percent) / percent if percent else 0

                await processing_msg.edit_text(
                    f"⚡ Enhancing: {percent}%\n"
                    f"⏳ ETA: {time_formatter(eta)}"
                )

                last_percent = percent

    await processing_msg.delete()

    if process.poll() != 0:
        os.remove(input_path)
        return await message.reply("❌ Enhancement failed")

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        os.remove(input_path)
        return await message.reply("❌ Output file missing")

    # ⬆️ UPLOAD (LIVE)
    upload_msg = await message.reply("⬆️ Uploading enhanced video...")
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

    await message.reply_video(
        video=output_path,
        caption="✅ Enhanced Video (1080p)\n⚡ PixelPulseBot",
        progress=progress,
        progress_args=(upload_msg, os.path.getsize(output_path), upload_msg, time.time())
    )

    await upload_msg.delete()

    # 🧹 CLEANUP
    os.remove(input_path)
    os.remove(output_path)


if __name__ == "__main__":
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
