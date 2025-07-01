import os
import time
import re
import subprocess

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatAction

# Utilities (from your main/utils.py)
from main.utils import progress, humanbytes, time_formatter

# Temporary user settings (use a database for persistent storage)
user_compression_settings = {}
DEFAULT_PERCENT = 75

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
@Client.on_message(filters.command("compress_settings"))
async def compress_settings(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔻 50%", callback_data="set_compress_50")],
        [InlineKeyboardButton("🔻 60%", callback_data="set_compress_60")],
        [InlineKeyboardButton("🔻 75%", callback_data="set_compress_75")],
        [InlineKeyboardButton("🔻 90%", callback_data="set_compress_90")]
    ])
    await message.reply("🔧 Choose your default compression percentage:", reply_markup=keyboard)

@Client.on_callback_query(filters.regex("set_compress_"))
async def set_compression_percentage(client, callback_query):
    percent = int(callback_query.data.split("_")[-1])
    user_id = callback_query.from_user.id
    user_compression_settings[user_id] = percent
    await callback_query.answer(f"✅ Set to {percent}% compression")
    await callback_query.message.edit("✅ Compression level updated.")

@Client.on_message(filters.command("compress") & filters.reply)
async def compress_video(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.video:
        return await message.reply("❌ Please reply to a video using `/compress` command.")

    video_msg = message.reply_to_message
    file_size = video_msg.video.file_size

    if file_size > MAX_FILE_SIZE:
        return await message.reply("❌ File exceeds Telegram’s 2GB limit.")

    user_id = message.from_user.id
    compress_percent = user_compression_settings.get(user_id, DEFAULT_PERCENT)
    reduction_ratio = compress_percent / 100.0

    start = time.time()
    downloading = await message.reply(f"⬇️ Downloading video for {compress_percent}% compression...")
    input_path = await video_msg.download(
        progress=progress,
        progress_args=(downloading, file_size, downloading, start)
    )
    await downloading.delete()

    if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
        return await message.reply("❌ Download failed or file is empty.")

    # Get duration
    try:
        duration_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", input_path
        ]
        total_duration = float(subprocess.check_output(duration_cmd).decode().strip())
    except Exception as e:
        return await message.reply(f"❌ Couldn't get duration: {e}")

    output_path = "compressed.mp4"
    processing_msg = await message.reply("⚙️ Compressing...")

    target_filesize = int(file_size * reduction_ratio) * 8
    audio_bitrate = 128_000
    video_bitrate = int((target_filesize / total_duration) - audio_bitrate)

    cmd = [
        "ffmpeg", "-i", input_path,
        "-b:v", str(video_bitrate),
        "-b:a", str(audio_bitrate),
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac", "-movflags", "+faststart",
        "-y", output_path
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time_pattern = re.compile(r'time=(\d+):(\d+):(\d+).(\d+)')
    last_percent = -1
    start_process = time.time()

    while True:
        line = process.stdout.readline()
        if line == "" and process.poll() is not None:
            break
        match = time_pattern.search(line)
        if match:
            h, m, s, ms = map(int, match.groups())
            current_time = h * 3600 + m * 60 + s + ms / 100
            percent = int((current_time / total_duration) * 100)
            if percent != last_percent and percent > 0:
                elapsed = time.time() - start_process
                eta = elapsed * (100 - percent) / percent if percent else 0
                await processing_msg.edit_text(f"⚙️ Compressing: {percent}%\nETA: {time_formatter(eta)}")
                last_percent = percent

    await processing_msg.delete()

    if process.poll() != 0:
        os.remove(input_path)
        return await message.reply("❌ FFmpeg failed.")

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        os.remove(input_path)
        return await message.reply("❌ Compressed file missing.")

    upload_msg = await message.reply("⬆️ Uploading...")
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

    await message.reply_video(
        video=output_path,
        caption=f"✅ Compressed to {compress_percent}% of original size.",
        progress=progress,
        progress_args=(upload_msg, os.path.getsize(output_path), upload_msg, time.time())
    )
    await upload_msg.delete()

    os.remove(input_path)
    os.remove(output_path)
