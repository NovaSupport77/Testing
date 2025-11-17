import os
import sys
import types
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ❌ imghdr ko fake module bana diya (Render Python 3.13 FIX)
fake_imghdr = types.ModuleType("imghdr")
sys.modules["imghdr"] = fake_imghdr

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(BOT_TOKEN)

app = Flask(__name__)

# SONG DOWNLOAD (yt-dlp)
import yt_dlp

async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Send like: /song track name")
        return

    await update.message.reply_text("⏳ Searching...")

    ydl_opts = {
        "format": "mp3/bestaudio",
        "outtmpl": "/tmp/song.%(ext)s",
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            file_path = ydl.prepare_filename(info["entries"][0])
            mp3_path = file_path.rsplit(".", 1)[0] + ".mp3"
        
        await update.message.reply_audio(audio=open(mp3_path, "rb"))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /song <name> to download MP3.")

# TELEGRAM UPDATE HANDLER
async def handle_update(update_json):
    update = Update.de_json(update_json, bot)
    await application.process_update(update)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update_json = request.get_json(force=True)
    bot.loop.create_task(handle_update(update_json))
    return "OK"

@app.route("/")
def home():
    return "Bot is running!"

# TELEGRAM APPLICATION
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("song", song))

# START FLASK
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
