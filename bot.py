from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
import os
import subprocess
import re
from time import time

API_ID = int(os.getenv("API_ID", "10811400"))  # Replace with your API_ID
API_HASH = os.getenv("API_HASH", "191bf5ae7a6c39771e7b13cf4ffd1279")  # Replace with your API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN", "7097361755:AAHJcqT4_YBvSq5hG7FwP5kDhugFBTwfRQE")  # Replace with your Bot Token

app = Client("enhance_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

MAX_FILE_SIZE = 300 * 1024 * 1024  # 300MB

# Helper function to format bytes human-readable
def humanbytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0:'B', 1:'KB', 2:'MB', 3:'GB', 4:'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

# Helper function to format seconds into hh:mm:ss
def time_formatter(seconds):
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02}"

# Progress function to update message during upload/download
async def progress(current, total, message: Message, start):
    now = time()
    diff = now - start
    if diff == 0:
        diff = 0.1  # prevent division by zero
    percentage = current * 100 / total
    speed = current / diff
    eta = (total - current) / speed if speed != 0 else 0
    bar_length = 10
    filled_length = int(bar_length * current // total)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)

    # Update every ~5 seconds (rounded)
    if round(diff) % 5 == 0 or current == total:
        try:
            await message.edit_text(
                f"{bar} {percentage:.2f}%\n"
                f"{humanbytes(current)} of {humanbytes(total)}\n"
                f"Speed: {humanbytes(speed)}/s\n"
                f"ETA: {time_formatter(eta)}"
            )
        except Exception:
            pass  # Avoid crashing on edit errors (rate limit, deleted msg)

@app.on_message(filters.command("enhance") & filters.reply)
async def enhance_video(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.video:
        return await message.reply("❌ Please reply to a video file with /enhance.")

    video_msg = message.reply_to_message  
    file_size = video_msg.video.file_size  

    if file_size > MAX_FILE_SIZE:  
        return await message.reply("❌ File is larger than 300MB. Please send a smaller video.")  

    start = time()  
    downloading_msg = await message.reply("⬇️ Downloading video...")  
    input_path = await video_msg.download(
        progress=progress,
        progress_args=(downloading_msg, video_msg.video.file_size, start)
    )  

    if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:  
        return await message.reply("❌ Download failed or file is empty.")  

    # Get duration of video
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

    # FFmpeg command with filters for enhancement
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
            if percent != last_percent and percent <= 100:  
                try:
                    await processing_msg.edit_text(f"⚡ Enhancing video: {percent}%")
                except Exception:
                    pass
                last_percent = percent  

    retcode = process.poll()  
    if retcode != 0:  
        await message.reply(f"❌ FFmpeg failed with code {retcode}.")  
        os.remove(input_path)  
        return  

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:  
        await message.reply("❌ Enhanced file is empty or missing.")  
        os.remove(input_path)  
        return  

    uploading_msg = await message.reply("⬆️ Uploading enhanced video...")  
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)  

    await message.reply_video(  
        video=output_path,  
        caption="✅ Enhanced Video (1080p) with original audio and subtitles",  
        progress=progress,  
        progress_args=(uploading_msg, os.path.getsize(output_path), time())  
    )  

    os.remove(input_path)  
    os.remove(output_path)


if __name__ == "__main__":
    app.run()
