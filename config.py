#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import re
from os import environ
import os

id_pattern = re.compile(r'^.\d+$')


API_ID = os.environ.get("API_ID", "10811400")
API_HASH = os.environ.get("API_HASH", "191bf5ae7a6c39771e7b13cf4ffd1279")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7871689536:AAFFnu67hEP6ZXVWD4SMGMl9dekw_pzidOE")
ADMIN = int(os.environ.get("ADMIN", '6469754522'))
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
SUNRISES_PIC= "https://envs.sh/big.jpg" # Replace with your Telegraph link - Start Pic
INFO_PIC= "https://ibb.co/GQLJXQCP" # Replace with your Telegraph link - Information 
UPDATES_CHANNEL = os.getenv("UPDATES_CHANNEL", "https://t.me/Sunrises24BotUpdates") # Replace with your Updates link
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/Sunrises24BotSupport") # Replace with your Support link
WEBHOOK = bool(os.environ.get("WEBHOOK", True))
PORT = int(os.environ.get("PORT", "8080")) #for koyeb 8080 only
