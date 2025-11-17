import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "https://api.itsvg.in/meta?url="


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔗 Send any link (YouTube • Instagram • Reels • Shorts • TikTok)\n"
        "I will download it for you 🔥"
    )


async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("❌ Please send a valid URL.")
        return

    await update.message.reply_text("⏳ Fetching media...")

    try:
        response = requests.get(API_URL + url, timeout=15)
        data = response.json()

        # API failed or no media found
        if "url" not in data or len(data["url"]) == 0:
            await update.message.reply_text("❌ Unable to fetch media. Try another link.")
            return

        media_url = data["url"][0]["url"]

        # Send video or image based on extension
        if media_url.endswith(".mp4"):
            await update.message.reply_video(media_url)
        else:
            await update.message.reply_photo(media_url)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN missing! Set it in Render Environment")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))

    print("⚡ Bot running on Render...")
    app.run_polling()


if __name__ == "__main__":
    main()
