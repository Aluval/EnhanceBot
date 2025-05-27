import os
import re
import subprocess
from time import time
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import Message
from utils import progress_message, humanbytes, TimeFormatter



API_ID = int(os.getenv("API_ID", "10811400"))
API_HASH = os.getenv("API_HASH", "191bf5ae7a6c39771e7b13cf4ffd1279")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7097361755:AAHJcqT4_YBvSq5hG7FwP5kDhugFBTwfRQE")
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1002067650699"))

app = Client("enhance_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
MAX_FILE_SIZE = 300 * 1024 * 1024



@app.on_message(filters.command("enhance") & filters.private)
async def enhance_command(client: Client, message: Message):
    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.document):
        return await message.reply("❌ Please reply to a **video or document** with `/enhance`.")

    video_msg = message.reply_to_message
    file_size = video_msg.video.file_size if video_msg.video else video_msg.document.file_size
    if file_size > MAX_FILE_SIZE:
        return await message.reply("❌ File is larger than 300MB. Please send a smaller video.")

    filename = video_msg.document.file_name if video_msg.document else video_msg.video.file_name
    args = message.text.split(maxsplit=2)
    output_filename = "enhanced.mp4"

    if "-n" in args:
        try:
            output_filename = args[args.index("-n") + 1]
        except IndexError:
            return await message.reply("❌ You used `-n` but didn't provide a filename.")

    user_name = message.from_user.first_name
    await client.send_message(LOG_CHANNEL, f"⚙️ Enhancement initiated by {user_name}\nFile: `{filename}`")

    start = time()
    downloading = await message.reply("⬇️ Downloading video...")

    input_path = await video_msg.download(
        progress=progress_message,
        progress_args=("⬇️ Downloading", file_size, downloading, start)
    )

    if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
        return await message.reply("❌ Download failed or file is empty.")

    try:
        total_duration = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", input_path
        ]).decode().strip())
    except Exception as e:
        os.remove(input_path)
        return await message.reply(f"❌ Couldn't get video duration: {e}")

    processing_msg = await message.reply("⚙️ Enhancing video...")
    cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", "scale=1920:1080:flags=lanczos,hqdn3d,unsharp=5:5:1.0:5:5:0.0,eq=contrast=1.2:brightness=0.05:saturation=1.2",
        "-map", "0", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-c:a", "copy", "-c:s", "mov_text", output_filename
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time_pattern = re.compile(r'time=(\d+):(\d+):(\d+).(\d+)')
    start_time = time()
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
            eta = TimeFormatter(int((total_duration - current_seconds) * 1000))
            if percent != last_percent:
                try:
                    await processing_msg.edit_text(
                        f"⚡ Enhancing Video: {percent}%\nEstimated Time Left: {eta}"
                    )
                except:
                    pass
                last_percent = percent

    if process.poll() != 0 or not os.path.exists(output_filename) or os.path.getsize(output_filename) == 0:
        os.remove(input_path)
        return await message.reply("❌ FFmpeg failed or file is empty.")

    await processing_msg.edit_text("⬆️ Uploading enhanced video...")
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

    output_size = os.path.getsize(output_filename)
    caption = f"✅ Enhanced Video by Multi ARM 24 BOT"

    try:
        if output_filename.endswith(".mp4"):
            await message.reply_video(
                video=output_filename,
                caption=caption,
                progress=progress_message,
                progress_args=("⬆️ Uploading", output_size, message, time())
            )
        else:
            await message.reply_document(
                document=output_filename,
                caption=caption,
                progress=progress_message,
                progress_args=("⬆️ Uploading", output_size, message, time())
            )
    except Exception as e:
        await message.reply(f"❌ Upload failed: {e}")

    await client.send_message(LOG_CHANNEL, f"✅ Enhancement completed for {user_name}\nFile: `{output_filename}`")
    os.remove(input_path)
    os.remove(output_filename)


if __name__ == "__main__":
    app.run()
