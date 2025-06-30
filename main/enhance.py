import os
import time
import re
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message, ChatAction
from main.utils import progress, humanbytes

MAX_FILE_SIZE = 300 * 1024 * 1024  # 300MB


@app.on_message(filters.command("enhance") & filters.reply)
async def enhance_video(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.video:
        return await message.reply("❌ Please reply to a video file with /enhance.")

    video_msg = message.reply_to_message
    file_size = video_msg.video.file_size

    if file_size > MAX_FILE_SIZE:
        return await message.reply("❌ File is larger than 300MB. Please send a smaller video.")

    start = time.time()
    downloading = await message.reply("⬇️ Downloading video...")
    input_path = await video_msg.download(
        progress=progress,
        progress_args=(downloading, video_msg.video.file_size, downloading, start)
    )
    # Delete the download progress message after download finishes
    await downloading.delete()

    if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
        return await message.reply("❌ Download failed or file is empty.")

    # Get video duration with ffprobe
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
                elapsed = time.time() - start_time
                eta = elapsed * (100 - percent) / percent if percent else 0
                eta_formatted = time_formatter(eta)
                await processing_msg.edit_text(f"⚡ Enhancing video: {percent}%\nETA: {eta_formatted}")
                last_percent = percent

    # Delete enhancement progress message after finishing
    await processing_msg.delete()

    retcode = process.poll()
    if retcode != 0:
        await message.reply(f"❌ FFmpeg failed with code {retcode}.")
        os.remove(input_path)
        return

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        await message.reply("❌ Enhanced file is empty or missing.")
        os.remove(input_path)
        return

    upload_msg = await message.reply("⬆️ Uploading enhanced video...")
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

    await message.reply_video(
        video=output_path,
        caption="✅ Enhanced Video (1080p) with original audio and subtitles",
        progress=progress,
        progress_args=(upload_msg, os.path.getsize(output_path), upload_msg, time.time())
    )
    # Delete upload progress message after upload finishes
    await upload_msg.delete()

    # Cleanup
    os.remove(input_path)
    os.remove(output_path)
