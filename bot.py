import os
from time import time
from subprocess import run
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import Message
from utils import progress

API_ID = int(os.getenv("API_ID", "10811400"))     # Replace with your API_ID
API_HASH = os.getenv("API_HASH", "191bf5ae7a6c39771e7b13cf4ffd1279")  # Replace with your API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")  # Replace with your Bot Token

app = Client("enhance_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("enhance") & filters.reply)
async def enhance_video(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.video:
        return await message.reply("Please reply to a video file with /enhance command.")

    video_msg = message.reply_to_message
    await message.reply("Downloading video...")
    input_path = await video_msg.download()

    output_path = "enhanced.mp4"
    await message.reply("Processing video enhancement...")

    cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", "scale=1920:1080:flags=lanczos,hqdn3d,unsharp=5:5:1.0:5:5:0.0,eq=contrast=1.2:brightness=0.05:saturation=1.2",
        "-c:v", "libx264", "-preset", "faster", "-crf", "28",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]

    run(cmd)

    await message.reply("Uploading enhanced video...")
    start = time()
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

    await message.reply_video(
        video=output_path,
        caption="Enhanced Video (1080p)",
        progress=progress,
        progress_args=(message, start)
    )

    os.remove(input_path)
    os.remove(output_path)


if __name__ == "__main__":
    app.run()
