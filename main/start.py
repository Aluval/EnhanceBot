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

# Define Start Time for Uptime Calculation
START_TIME = datetime.datetime.now()

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
            "**👋 Welcome to PixelPulseBot!**\n\n"
            "🔹 Send any video under **300MB**\n"
            "🔹 Reply with `/enhance` to improve sharpness, color, and quality.\n\n"
            "Click the buttons below to know more!"
        ),
        reply_markup=buttons
    )

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply_text(
       "**🛠 PixelPulseBot[EnhanceBot] Help**\n\n"
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
            "**📽️ About PixelPulseBot[EnhanceBot]**\n\n"
            "EnhanceBot uses **FFmpeg** to:\n"
            "🔹 Upscale videos to 1080p\n"
            "🔹 Denoise and sharpen\n"
            "🔹 Boost brightness and saturation\n"
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
# 🟢 /stats Command
@app.on_message(filters.command("stats"))
async def stats_command(_, msg: Message):
    uptime = datetime.datetime.now() - START_TIME
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

    total_space = psutil.disk_usage('/').total / (1024 ** 3)
    used_space = psutil.disk_usage('/').used / (1024 ** 3)
    free_space = psutil.disk_usage('/').free / (1024 ** 3)

    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent

    stats_text = (
        "🖥️ **PixelPulseBot[EnhanceBot] Server Status**\n\n"
        f"⏱️ **Uptime:** `{uptime_str}`\n"
        f"💾 **Disk:** `{used_space:.2f} GB / {total_space:.2f} GB` "
        f"({used_space / total_space * 100:.1f}%)\n"
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


# 🔁 /stats Refresh Handler
@app.on_callback_query(filters.regex("^refresh_stats$"))
async def refresh_stats_callback(_, query: CallbackQuery):
    uptime = datetime.datetime.now() - START_TIME
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

    total_space = psutil.disk_usage('/').total / (1024 ** 3)
    used_space = psutil.disk_usage('/').used / (1024 ** 3)
    free_space = psutil.disk_usage('/').free / (1024 ** 3)

    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent

    stats_text = (
        "🖥️ **PixelPulseBot[EnhanceBot] Server Status**\n\n"
        f"⏱️ **Uptime:** `{uptime_str}`\n"
        f"💾 **Disk:** `{used_space:.2f} GB / {total_space:.2f} GB` "
        f"({used_space / total_space * 100:.1f}%)\n"
        f"⚙️ **CPU Usage:** `{cpu_usage:.1f}%`\n"
        f"🧠 **RAM Usage:** `{ram_usage:.1f}%`\n"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")],
        [InlineKeyboardButton("📢 UPDATES", url=UPDATES_CHANNEL)],
        [InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)]
    ])

    await query.message.edit_caption(
        caption=stats_text,
        reply_markup=keyboard
    )


# 🔒 Admin-only /logs Command
@app.on_message(filters.command('logs') & filters.user(ADMIN))
async def log_file(_, m: Message):
    try:
        await m.reply_document("PixelPulseBot.txt", caption="📄 Bot Logs File")
    except Exception as e:
        await m.reply(f"❌ Error: `{str(e)}`")
      
if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
