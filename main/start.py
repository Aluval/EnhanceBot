import time
import datetime
from datetime import timedelta
from config import *
import psutil
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
import logging

logging.basicConfig(
    filename='PixelPulseBot.txt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24

# Example of logging a message
logging.info('Bot started successfully!')
# Define Start Time for Uptime Calculation
START_TIME = datetime.datetime.now()

@Client.on_message(filters.command("start"))
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
            "**👋 Welcome to PixelPulseBot!**\n\n"
            "🔹 Send any video under **300MB** for enhance\n"
            "🔹 Send any video under **2GB** for compress\n"
            "🔹 Reply with `/enhance` to improve sharpness, color, and quality.\n"
            "🔹 Reply with `/compress` to reduce file size (choose quality via `/compress_settings`).\n\n"
            "Click the buttons below to know more!"
        ),
        reply_markup=buttons
    )

@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply_text(
       "**🛠 PixelPulseBot[EnhanceBot] Help**\n\n"
        "`/start` - Welcome message\n"
        "`/help` - Show this help\n"
        "`/enhance` - Reply to a video to enhance it\n"
        "`/compress` - Reply to a video to compress it\n"
        "`/compress_settings` - Set compression % (50/60/75/90)\n"
        "`/ping` - Check bot speed\n"
        "`/stats` - Server usage stats\n"
        "`/logs` - (Admins only) Bot logs\n\n"
        "**Note:** File size must be under 300MB for enhance."
        "**Note:** File size must be under 2GB for compression."
    )

@Client.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    if data == "about":
        await callback_query.message.edit_text(
            "**🎩 About PixelPulseBot[EnhanceBot]**\n\n"
            "EnhanceBot uses **FFmpeg** to:\n"
            "🔹 Upscale videos to 1080p\n"
            "🔹 Denoise and sharpen\n"
            "🔹 Boost brightness and saturation\n"
            "🔹 Compress video by selected size\n"
            "🔹 Keep audio and subtitles intact\n\n"
            "Built by: @Sunrises_24\nPowered by: Pyrogram + FFmpeg",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )
    elif data == "help":
        await callback_query.message.edit_text(
            "**🛠 PixelPulseBot[EnhanceBot] Help**\n\n"
            "`/start` - Welcome message\n"
            "`/help` - Show this help\n"
            "`/enhance` - Reply to a video to enhance it\n"
            "`/compress` - Reply to a video to compress it\n"
            "`/compress_settings` - Set compression % (50/60/75/90)\n"
            "`/ping` - Check bot speed\n"
            "`/stats` - Server usage stats\n"
            "`/logs` - (Admins only) Bot logs\n\n"
            "**Note:** File size must be under 300MB for enhance.
            "**Note:** File size must be under 2GB for compression.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )
    elif data == "start":
        await start_command(client, callback_query.message)

@Client.on_message(filters.command("about"))
async def about_command(client: Client, message: Message):
    await message.reply_text(
        "**🎩 About PixelPulseBot**\n\n"
        "PixelPulseBot is a Telegram bot that enhances and compresses videos using advanced FFmpeg filters.\n\n"
        "**Key Features:**\n"
        "✅ Upscale videos to 1080p\n"
        "🎞️ Noise reduction & sharpening\n"
        "🎨 Color enhancement\n"
        "📉 File compression based on user-selected %\n"
        "🔊 Retains original audio & subtitles\n\n"
        "🔧 Powered by FFmpeg & Pyrogram\n"
        "🧑‍💻 Developed by: @Sunrises_24\n"
        "📢 Updates: @Sunrises24BotUpdates\n"
        "💬 Support: @Sunrises24BotSupport"
    )

@Client.on_message(filters.command("ping"))
async def ping(bot, msg: Message):
    start = time.time()
    response = await msg.reply_text("🔍 Pinging...")
    end = time.time()
    duration = (end - start) * 1000
    await response.edit_text(
        f"🏓 **Pong!**\n"
        f"📶 **Response Time:** `{duration:.2f} ms`\n\n"
        "✨ Powered by PixelPulseBot\n"
        "👤 Credits: @Sunrises_24"
    )

# 🟢 /stats Command
@Client.on_message(filters.command("stats"))
async def stats_command(_, msg: Message):
    uptime = datetime.datetime.now() - START_TIME
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

    total_space = psutil.disk_usage('/').total / (1024 ** 3)
    used_space = psutil.disk_usage('/').used / (1024 ** 3)
    free_space = psutil.disk_usage('/').free / (1024 ** 3)

    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent

    stats_message = (
        f"📊 **Server Stats** 📊\n\n"
        f"⏳ **Uptime:** `{uptime_str}`\n"
        f"💾 **Total Space:** `{total_space:.2f} GB`\n"
        f"📂 **Used Space:** `{used_space:.2f} GB` ({used_space / total_space * 100:.1f}%)\n"
        f"📁 **Free Space:** `{free_space:.2f} GB`\n"
        f"⚙️ **CPU Usage:** `{cpu_usage:.1f}%`\n"
        f"💻 **RAM Usage:** `{ram_usage:.1f}%`\n"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")],
        [
            InlineKeyboardButton("📢 Updates", url=UPDATES_CHANNEL),
            InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)
        ]
    ])

    await msg.reply_photo(
        photo=INFO_PIC,
        caption=stats_message,
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex("^refresh_stats$"))
async def refresh_stats_callback(_, callback_query: CallbackQuery):
    uptime = datetime.datetime.now() - START_TIME
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

    total_space = psutil.disk_usage('/').total / (1024 ** 3)
    used_space = psutil.disk_usage('/').used / (1024 ** 3)
    free_space = psutil.disk_usage('/').free / (1024 ** 3)

    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent

    stats_message = (
        f"📊 **Server Stats** 📊\n\n"
        f"⏳ **Uptime:** `{uptime_str}`\n"
        f"💾 **Total Space:** `{total_space:.2f} GB`\n"
        f"📂 **Used Space:** `{used_space:.2f} GB` ({used_space / total_space * 100:.1f}%)\n"
        f"📁 **Free Space:** `{free_space:.2f} GB`\n"
        f"⚙️ **CPU Usage:** `{cpu_usage:.1f}%`\n"
        f"💻 **RAM Usage:** `{ram_usage:.1f}%`\n"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")],
        [
            InlineKeyboardButton("📢 Updates", url=UPDATES_CHANNEL),
            InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)
        ]
    ])

    try:
        await callback_query.message.edit_caption(
            caption=stats_message,
            reply_markup=keyboard
        )
        await callback_query.answer("✅ Stats refreshed!")
    except Exception as e:
        await callback_query.answer("⚠️ Could not refresh.", show_alert=True)
        print(f"Error refreshing stats: {e}")




# 🔒 Admin-only /logs Command
@Client.on_message(filters.command('logs') & filters.user(ADMIN))
async def log_file(_, m: Message):
    try:
        await m.reply_document("PixelPulseBot.txt", caption="📄 Bot Logs File")
    except Exception as e:
        await m.reply(f"❌ Error: `{str(e)}`")
      
if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
