import os
import time
import subprocess

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction

# Your config
from config import *

# Your utility functions
from main.utils import progress, humanbytes, time_formatter

# Mediainfo function (IMPORTANT)
from main.utils import info

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB in bytes


#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24

@Client.on_message(filters.command("compress") & filters.reply)
async def compress_video(client: Client, message: Message):

    if not message.reply_to_message or not message.reply_to_message.video:
        return await message.reply("❌ Reply to a video with /compress")

    video_msg = message.reply_to_message
    file_size = video_msg.video.file_size

    if file_size > MAX_FILE_SIZE:
        return await message.reply("❌ File exceeds 2GB limit")

    start = time.time()
    downloading = await message.reply("⬇️ Downloading...")

    input_path = await video_msg.download(
        progress=progress,
        progress_args=(downloading, file_size, downloading, start)
    )
    await downloading.delete()

    if not os.path.exists(input_path):
        return await message.reply("❌ Download failed")

    output_path = "compressed.mkv"

    processing_msg = await message.reply("⚡ Fast Compressing...")

    cmd = [
        "ffmpeg", "-i", input_path,
        "-preset", "ultrafast",
        "-c:v", "libx265",
        "-crf", "27",
        "-map", "0:v",
        "-c:a", "aac",
        "-b:a", "128k",
        "-map", "0:a",
        "-c:s", "copy",
        "-map", "0:s?",
        "-y", output_path
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    while True:
        line = process.stdout.readline()
        if line == "" and process.poll() is not None:
            break

    await processing_msg.delete()

    if process.poll() != 0:
        os.remove(input_path)
        return await message.reply("❌ Compression failed")

    # 📊 SIZE INFO
    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)

    reduction = 100 - ((compressed_size / original_size) * 100)
    reduction_text = f"{reduction:.2f}%"

    # 📄 MEDIAINFO
    before_info = await info(input_path, message)
    after_info = await info(output_path, message)

    upload_msg = await message.reply("⬆️ Uploading...")
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

    await message.reply_video(
        video=output_path,
        caption=(
            f"✅ Compression Done\n\n"
            f"📦 Original: {humanbytes(original_size)}\n"
            f"📉 Compressed: {humanbytes(compressed_size)}\n"
            f"📊 Reduced: {reduction_text}\n\n"
            f"📄 [Before]({before_info}) | [After]({after_info})"
        ),
        progress=progress,
        progress_args=(upload_msg, compressed_size, upload_msg, time.time())
    )

    await upload_msg.delete()

    os.remove(input_path)
    os.remove(output_path)


if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
