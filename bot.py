from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from time import time
import os
import subprocess
from utils import progress

API_ID = int(os.getenv("API_ID", "10811400"))     # Replace with your API_ID
API_HASH = os.getenv("API_HASH", "191bf5ae7a6c39771e7b13cf4ffd1279")  # Replace with your API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN", "7097361755:AAE_zegGSo1OsWQWsy7G8eit4pDXFxOj7I8")  # Replace with your Bot Token

app = Client("enhance_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


MAX_FILE_SIZE = 300 * 1024 * 1024  # 300MB

@app.on_message(filters.command("enhance") & filters.reply)
async def enhance_video(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.video:
        return await message.reply("Please reply to a video file with /enhance command.")

    video_msg = message.reply_to_message
    file_size = video_msg.video.file_size

    if file_size > MAX_FILE_SIZE:
        return await message.reply("❌ File is larger than 300MB. Please send a smaller video.")

    start = time()
    downloading = await message.reply("⬇️ Downloading video...")
    input_path = await video_msg.download(
        progress=progress,
        progress_args=(downloading, start)
    )

    # Get duration
    try:
        duration_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", input_path
        ]
        duration = subprocess.check_output(duration_cmd).decode().strip()
        await message.reply(f"⏱️ Video Duration: {float(duration):.2f} seconds")
    except Exception as e:
        await message.reply(f"⚠️ Failed to get video duration: {e}")

    output_path = "enhanced.mp4"
    processing_msg = await message.reply("⚙️ Enhancing video...")

    cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", "scale=1920:1080:flags=lanczos,hqdn3d,unsharp=5:5:1.0:5:5:0.0,"
               "eq=contrast=1.2:brightness=0.05:saturation=1.2",
        "-map", "0",
        "-c:v", "libx264", "-preset", "faster", "-crf", "28",
        "-c:a", "copy",
        "-c:s", "mov_text",  # safer subtitle codec
        output_path
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    while True:
        line = process.stdout.readline()
        if line == "" and process.poll() is not None:
            break
        if "time=" in line:
            await processing_msg.edit_text(f"⚙️ Enhancing video...\n`{line.strip()}`")

    # FFmpeg exit check
    retcode = process.poll()
    if retcode != 0:
        await message.reply(f"❌ FFmpeg failed with code {retcode}.")
        os.remove(input_path)
        return

    # Validate output file
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        await message.reply("❌ Enhanced file is empty or missing.")
        os.remove(input_path)
        return

    await message.reply("⬆️ Uploading enhanced video...")
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

    await message.reply_video(
        video=output_path,
        caption="✅ Enhanced Video (1080p) with original audio and subtitles",
        progress=progress,
        progress_args=(message, time())
    )

    os.remove(input_path)
    os.remove(output_path)

if __name__ == "__main__":
    app.run()
