import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "https://api.itsvg.in/meta?url="

WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")  # auto webhook


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send link to download 🔥")


async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("❌ Valid link do.")
        return

    await update.message.reply_text("⏳ Downloading...")

    try:
        r = requests.get(API_URL + url)
        data = r.json()

        if "url" not in data or len(data["url"]) == 0:
            await update.message.reply_text("❌ Media nahi mila.")
            return

        media_url = data["url"][0]["url"]

        if media_url.endswith(".mp4"):
            await update.message.reply_video(media_url)
        else:
            await update.message.reply_photo(media_url)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloader))

    # Webhook mode — NO UPDATER — NO ERROR EVER
    await app.initialize()
    await app.start()
    await app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path="webhook",
    )

    print("🚀 Webhook bot running on Render...")

    await app.updater.idle()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
