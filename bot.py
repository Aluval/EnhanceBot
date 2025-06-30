from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
import os
import subprocess
import re
import time
import datetime
from datetime import timedelta
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
API_ID = int(os.getenv("API_ID", "10811400"))     # Replace with your API_ID
API_HASH = os.getenv("API_HASH", "191bf5ae7a6c39771e7b13cf4ffd1279")  # Replace with your API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN", "7097361755:AAHJcqT4_YBvSq5hG7FwP5kDhugFBTwfRQE")  # Replace with your Bot Token
ADMIN = int(os.environ.get("ADMIN", '6469754522'))
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
SUNRISES_PIC= "https://graph.org/file/bd91761f6e938e2e6d23a.jpg"  # Replace with your Telegraph link

app = Client("enhance_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

MAX_FILE_SIZE = 300 * 1024 * 1024  # 300MB
# Define Start Time for Uptime Calculation
START_TIME = datetime.datetime.now()

# Utility: Format seconds to HH:MM:SS string
def time_formatter(seconds: float) -> str:
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

# Utility: Human-readable bytes (optional, if used in progress)
def humanbytes(size):
    # Simple function to convert bytes to KB/MB/GB strings
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

# Progress callback for downloads/uploads (optional, from your utils)
async def progress(current, total, message: Message, start, *args):
    now = time.time()
    diff = now - start
    if round(diff % 5) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff if diff else 0
        eta = (total - current) / speed if speed else 0
        bar = "[" + "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10)) + "]"
        try:
            await message.edit_text(
                f"{bar} {percentage:.2f}%\n"
                f"{humanbytes(current)} of {humanbytes(total)}\n"
                f"Speed: {humanbytes(speed)}/s\n"
                f"ETA: {time_formatter(eta)}"
            )
        except:
            pass  # ignore edit failures due to Telegram rate limits

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


@app.on_message(filters.command("about"))
async def about_command(client: Client, message: Message):
    await message.reply_text(
        "**📽️ About EnhanceBot**\n\n"
        "EnhanceBot is a Telegram bot built using Python and FFmpeg. It improves video quality using filters like:\n"
        "- ✅ Upscale to 1080p\n"
        "- 🎞️ Noise reduction\n"
        - "🔧 Sharpening & color correction\n"
        "- 🔊 Keeps original audio & subtitles\n\n"
        "⚙️ Powered by: Pyrogram + FFmpeg\n"
        "💡 Developer: @Aluval or [GitHub](https://github.com/Aluval)\n"
        "📦 Max file size: 300MB\n\n"
        "Use `/enhance` by replying to a video under 300MB to start!"
    )

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
            InlineKeyboardButton("🛠 Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("📢 Updates", url=UPDATES_CHANNEL),
            InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)
        ]
    ])
    
    await message.reply_photo(
        photo=SUNRISES_PIC,  
        caption=(
            "**👋 Welcome to EnhanceBot!**\n\n"
            "🔹 Send any video under **300MB**\n"
            "🔹 Reply with `/enhance` to improve sharpness, color, and quality.\n\n"
            "Click the buttons below to know more!"
        ),
        reply_markup=buttons
    )

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply_text(
       "**🛠 EnhanceBot Help**\n\n"
            "`/start` - Welcome message\n"
            "`/help` - Show this help\n"
            "`/enhance` - Reply to a video to enhance it\n"
            "`/ping` - Check bot speed\n"
            "`/stats` - stats\n"
            "`/logs` - (Admins only) Bot logs\n\n"
            "**Note:** File size must be under 300MB."
    )

@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    if data == "about":
        await callback_query.message.edit_text(
            "**📽️ About EnhanceBot**\n\n"
            "EnhanceBot uses **FFmpeg** to:\n"
            "🔹 Upscale videos to 1080p\n"
            "🔹 Denoise and sharpen\n"
            "🔹 Boost brightness and saturation\n"
            "🔹 Keep audio and subtitles intact\n\n"
            "Built by: @Aluval\nPowered by: Pyrogram + FFmpeg",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )
    elif data == "help":
        await callback_query.message.edit_text(
            "**🛠 EnhanceBot Help**\n\n"
            "`/start` - Welcome message\n"
            "`/help` - Show this help\n"
            "`/enhance` - Reply to a video to enhance it\n"
            "`/ping` - Check bot speed\n"
            "`/stats` - stats\n"
            "`/logs` - (Admins only) Bot logs\n\n"
            "**Note:** File size must be under 300MB.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )
    elif data == "start":
        await start_command(client, callback_query.message)


@app.on_message(filters.command("ping"))
async def ping(bot, msg: Message):
    start = time.time()
    response = await msg.reply_text("🔍 Pinging...")
    end = time.time()
    duration = (end - start) * 1000  # ms
    await response.edit_text(
        f"🏓 **Pong!**\n"
        f"📶 **Response Time:** `{duration:.2f} ms`\n\n"
        "✨ Powered by EnhanceBot\n"
        "👤 Credits: @Sunrises_24"
    )

@Client.on_callback_query(filters.regex("^refresh_stats$"))
async def refresh_stats_callback(_, query):
    uptime = datetime.datetime.now() - START_TIME
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

    total_space = psutil.disk_usage('/').total / (1024 ** 3)
    used_space = psutil.disk_usage('/').used / (1024 ** 3)
    free_space = psutil.disk_usage('/').free / (1024 ** 3)

    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent

    stats_text = (
        "🖥️ **EnhanceBot Server Status**\n\n"
        f"⏱️ **Uptime:** `{uptime_str}`\n"
        f"💾 **Disk:** `{used_space:.2f} GB / {total_space:.2f} GB`"
        f" ({used_space / total_space * 100:.1f}%)\n"
        f"⚙️ **CPU Usage:** `{cpu_usage:.1f}%`\n"
        f"🧠 **RAM Usage:** `{ram_usage:.1f}%`\n"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")],
        [InlineKeyboardButton("📢 UPDATES", url=UPDATES_CHANNEL)],
        [InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)]
    ])

    await msg.reply_photo(
        photo=SUNRISES_PIC,
        caption=stats_text,
        reply_markup=keyboard
    )

# 🔒 Admin-only /logs Command
@Client.on_message(filters.command('logs') & filters.user(ADMIN))
async def log_file(_, m: Message):
    try:
        await m.reply_document("SunrisesBot.txt", caption="📄 Bot Logs File")
    except Exception as e:
        await m.reply(f"❌ Error: `{str(e)}`")

if __name__ == "__main__":
    app.run()
