import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "https://api.itsvg.in/meta?url="

bot = Bot(BOT_TOKEN)
app = Flask(__name__)

dispatcher = Dispatcher(bot, None, workers=0)


def start(update, context):
    update.message.reply_text("Send any link to download 🔥")


def downloader(update, context):
    url = update.message.text.strip()

    if not url.startswith("http"):
        update.message.reply_text("❌ Valid link do.")
        return

    update.message.reply_text("⏳ Downloading...")

    try:
        r = requests.get(API_URL + url)
        data = r.json()

        if "url" not in data or len(data["url"]) == 0:
            update.message.reply_text("❌ Media nahi mila.")
            return

        media_url = data["url"][0]["url"]

        if media_url.endswith(".mp4"):
            bot.send_video(chat_id=update.effective_chat.id, video=media_url)
        else:
            bot.send_photo(chat_id=update.effective_chat.id, photo=media_url)

    except Exception as e:
        update.message.reply_text(f"❌ Error: {e}")


dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))


@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.json, bot)
    dispatcher.process_update(update)
    return "ok", 200


@app.route("/")
def home():
    return "Bot is running!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
