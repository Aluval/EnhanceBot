from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from time import time
import os
import subprocess
from utils import progress

API_ID = int(os.getenv("API_ID", "10811400"))     # Replace with your API_ID
API_HASH = os.getenv("API_HASH", "191bf5ae7a6c39771e7b13cf4ffd1279")  # Replace with your API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN", "7097361755:AAHJcqT4_YBvSq5hG7FwP5kDhugFBTwfRQE")  # Replace with your Bot Token

app = Client("enhance_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

import os 
import json 
import uuid 
import subprocess 
from time import time
from pyrogram import Client, filters 
from pyrogram.types import Message 

JOBS_DIR = "jobs" os.makedirs(JOBS_DIR, exist_ok=True)


def save_job(job_id, data): 
    with open(f"{JOBS_DIR}/{job_id}.json", "w") as f: 
        json.dump(data, f)

def load_jobs(): 
    jobs = [] 
    for file in os.listdir(JOBS_DIR): 
        if file.endswith(".json"): 
           with open(f"{JOBS_DIR}/{file}") as f:
               jobs.append(json.load(f)) 
        return jobs

@app.on_message(filters.command("enhance") & filters.reply) 
async def enhance_video(client: Client, message: Message): 
    if not message.reply_to_message or not message.reply_to_message.video: 
        return await message.reply("Please reply to a video file with /enhance command.")

video_msg = message.reply_to_message
start_time = time()
downloading = await message.reply("Downloading video...")

input_path = await video_msg.download(progress=progress, progress_args=(downloading, start_time))
if not os.path.getsize(input_path):
    return await message.reply("Downloaded file is empty. Please try again.")

# Generate unique job ID and save job metadata
job_id = str(uuid.uuid4())
job_data = {
    "job_id": job_id,
    "user_id": message.from_user.id,
    "chat_id": message.chat.id,
    "input_path": input_path,
    "status": "downloaded"
}
save_job(job_id, job_data)

await process_enhancement(client, job_data)

async def process_enhancement(client: Client, job): 
    input_path = job["input_path"] output_path = f"enhanced_{job['job_id']}.mp4"

# Get video duration
try:
    duration_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", input_path
    ]
    duration = subprocess.check_output(duration_cmd).decode().strip()
    await client.send_message(job["chat_id"], f"Video Duration: {float(duration):.2f} seconds")
except Exception as e:
    await client.send_message(job["chat_id"], f"Failed to get duration: {e}")

processing_msg = await client.send_message(job["chat_id"], "Enhancing video...")
job["status"] = "processing"
save_job(job["job_id"], job)

cmd = [
    "ffmpeg", "-i", input_path,
    "-vf", "scale=1920:1080:flags=lanczos,hqdn3d,unsharp=5:5:1.0:5:5:0.0,eq=contrast=1.2:brightness=0.05:saturation=1.2",
    "-map", "0", "-c:v", "libx264", "-preset", "faster", "-crf", "28",
    "-c:a", "copy", "-c:s", "copy",
    output_path
]

process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
while True:
    line = process.stdout.readline()
    if line == "" and process.poll() is not None:
        break
    if "time=" in line:
        await processing_msg.edit_text(f"Enhancing video...\n{line.strip()}")

if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
    return await client.send_message(job["chat_id"], "Enhancement failed or file size is 0.")

await client.send_message(job["chat_id"], "Uploading enhanced video...")
await client.send_video(
    chat_id=job["chat_id"],
    video=output_path,
    caption="Enhanced Video (1080p) with original audio and subtitles",
    progress=progress,
    progress_args=(processing_msg, time())
)

job["status"] = "done"
save_job(job["job_id"], job)

os.remove(input_path)
os.remove(output_path)
os.remove(f"{JOBS_DIR}/{job['job_id']}.json")

@app.on_message(filters.command("resume_jobs")) 
async def resume_jobs(client: Client, message: Message): 
    jobs = load_jobs() 
    for job in jobs: 
        if job["status"] in ["downloaded", "processing"]: 
            await process_enhancement(client, job)



@app.on_message(filters.command("start")) 
async def on_start(client: Client, message: Message): 
    await resume_jobs(client, message)



if __name__ == "__main__":
    app.run()
