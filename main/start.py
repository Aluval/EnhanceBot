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

logging.info('Bot started successfully!')

START_TIME = datetime.datetime.now()


# 🚀 START
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
            "🔹 Enhance videos under **300MB**\n"
            "🔹 Compress videos up to **2GB**\n\n"
            "⚡ Commands:\n"
            "• `/enhance` → 1080p upscale + filters\n"
            "• `/compress` → reduce size (fast x265)\n\n"
            "📦 Output sent as **file (no Telegram compression)**\n"
            "🏷 Metadata added automatically\n\n"
            "Click below to explore more 👇"
        ),
        reply_markup=buttons
    )


# 🛠 HELP
@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply_text(
        "**🛠 PixelPulseBot Help**\n\n"
        "`/start` - Start bot\n"
        "`/help` - Show help\n"
        "`/enhance` - Reply to video to enhance\n"
        "`/compress` - Reply to video to compress\n"
        "`/ping` - Check speed\n"
        "`/stats` - Server stats\n"
        "`/logs` - Admin only\n\n"
        "**📌 Limits:**\n"
        "• Enhance → 300MB\n"
        "• Compress → 2GB\n\n"
        "**⚡ Features:**\n"
        "✔ Live progress + ETA\n"
        "✔ Fast FFmpeg processing\n"
        "✔ Output as document\n"
        "✔ Metadata auto added"
    )


# 🔘 CALLBACKS
@Client.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data

    if data == "about":
        await callback_query.message.edit_text(
            "**🎩 About PixelPulseBot**\n\n"
            "PixelPulseBot is a high-performance Telegram bot powered by FFmpeg.\n\n"
            "**🚀 Features:**\n"
            "🔹 1080p video enhancement\n"
            "🔹 Denoise & sharpening\n"
            "🔹 Color correction\n"
            "🔹 Fast compression (x265)\n"
            "🔹 Output as file (no quality loss)\n"
            "🔹 Metadata tagging\n\n"
            "🧑‍💻 Dev: @Sunrises_24\n"
            "⚡ Powered by Pyrogram + FFmpeg",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )

    elif data == "help":
        await callback_query.message.edit_text(
            "**🛠 PixelPulseBot Help**\n\n"
            "`/enhance` → Improve quality\n"
            "`/compress` → Reduce size\n\n"
            "**📌 Limits:**\n"
            "Enhance: 300MB\n"
            "Compress: 2GB\n\n"
            "⚡ Fast + Stable + Clean Output",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )

    elif data == "start":
        await start_command(client, callback_query.message)


# 📘 ABOUT COMMAND
@Client.on_message(filters.command("about"))
async def about_command(client: Client, message: Message):
    await message.reply_text(
        "**🎩 About PixelPulseBot**\n\n"
        "A minimal, high-performance Telegram bot for video processing.\n\n"
        "**✨ Features:**\n"
        "✔ 1080p enhancement\n"
        "✔ Fast compression (x265)\n"
        "✔ Metadata tagging\n"
        "✔ No Telegram recompression\n\n"
        "🧑‍💻 Dev: @Sunrises_24\n"
        "📢 Updates: @Sunrises24BotUpdates\n"
        "💬 Support: @Sunrises24BotSupport"
    )


# 🏓 PING
@Client.on_message(filters.command("ping"))
async def ping(bot, msg: Message):
    start = time.time()
    response = await msg.reply_text("🔍 Pinging...")
    end = time.time()
    duration = (end - start) * 1000

    await response.edit_text(
        f"🏓 **Pong!**\n"
        f"📶 `{duration:.2f} ms`\n\n"
        "⚡ PixelPulseBot"
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
        await m.reply(f"❌ Error: {str(e)}")


if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
