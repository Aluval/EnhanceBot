import os
import time
import re
import subprocess

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction

from config import *
from main.utils import progress, humanbytes, time_formatter

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB


@Client.on_message(filters.command("compress") & filters.reply)
async def compress_video(client: Client, message: Message):

    reply = message.reply_to_message

    # ✅ SUPPORT VIDEO + DOCUMENT
    if reply.video:
        media = reply.video
        file_name = reply.video.file_name or "video.mp4"
    elif reply.document and reply.document.mime_type.startswith("video"):
        media = reply.document
        file_name = reply.document.file_name or "video.mkv"
    else:
        return await message.reply("❌ Reply to a video or video document with /compress")

    file_size = media.file_size

    # 🚫 SIZE CHECK
    if file_size > MAX_FILE_SIZE:
        return await message.reply(
            f"❌ File too large!\n\n"
            f"📦 Size: {humanbytes(file_size)}\n"
            f"🚫 Limit: 2GB"
        )

    # ❌ SKIP IF ALREADY COMPRESSED
    if "compressed" in file_name.lower():
        return await message.reply("⚠️ This file already looks compressed 😑")

    start = time.time()

    # ⬇️ DOWNLOAD
    downloading = await message.reply("⬇️ Downloading video...")
    input_path = await reply.download(
        progress=progress,
        progress_args=(downloading, file_size, downloading, start)
    )
    await downloading.delete()

    if not os.path.exists(input_path):
        return await message.reply("❌ Download failed")

    # 🎬 GET DURATION
    try:
        duration_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_path
        ]
        total_duration = float(subprocess.check_output(duration_cmd).decode().strip())
    except:
        total_duration = 0

    # 📁 OUTPUT NAME
    output_path = "compressed.mkv"

    processing_msg = await message.reply("⚡ Compressing video...")

    # 🔥 DANISH FFmpeg + METADATA
    cmd = [
        "ffmpeg", "-i", input_path,
        "-preset", "ultrafast",
        "-c:v", "libx265",
        "-crf", "27",

        # 🎬 METADATA
        "-metadata", "title=@Sunrises24BotUpdates",
        "-metadata:s:v", "title=@Sunrises24BotUpdates",
        "-metadata:s:a", "title=@Sunrises_24",

        "-map", "0:v",
        "-c:a", "aac",
        "-b:a", "128k",
        "-map", "0:a",
        "-c:s", "copy",
        "-map", "0:s?",

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
        if match and total_duration > 0:

            h, m, s, ms = map(int, match.groups())
            current_time = h * 3600 + m * 60 + s + ms / 100

            percent = int((current_time / total_duration) * 100)

            if percent != last_percent and percent > 0:
                elapsed = time.time() - start_time
                eta = elapsed * (100 - percent) / percent if percent else 0

                await processing_msg.edit_text(
                    f"⚡ Compressing: {percent}%\n"
                    f"⏳ ETA: {time_formatter(eta)}"
                )

                last_percent = percent

    await processing_msg.delete()

    if process.poll() != 0:
        os.remove(input_path)
        return await message.reply("❌ Compression failed")

    # 📊 RESULT
    original = os.path.getsize(input_path)
    compressed = os.path.getsize(output_path)
    reduction = 100 - ((compressed / original) * 100)

    # ⬆️ UPLOAD AS DOCUMENT
    upload_msg = await message.reply("⬆️ Uploading compressed file...")
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)

    await message.reply_document(
        document=output_path,
        file_name=f"{os.path.splitext(file_name)[0]}_compressed.mkv",
        caption=(
            f"✅ Compression Done\n\n"
            f"📦 Original: {humanbytes(original)}\n"
            f"📉 Compressed: {humanbytes(compressed)}\n"
            f"📊 Reduced: {reduction:.2f}%\n\n"
            f"🎬 Video: @Sunrises24BotUpdates\n"
            f"🔊 Audio: @Sunrises_24\n"
            f"⚡ PixelPulseBot"
        ),
        progress=progress,
        progress_args=(upload_msg, compressed, upload_msg, time.time())
    )

    await upload_msg.delete()

    # 🧹 CLEANUP
    os.remove(input_path)
    os.remove(output_path)


if __name__ == "__main__":
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
