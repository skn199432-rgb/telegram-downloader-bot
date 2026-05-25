import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ارسل رابط فيديو من يوتيوب أو تيك توك أو تويتر/X وسأحاول تحميله لك."
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("ارسل رابط صحيح")
        return

    msg = await update.message.reply_text("جاري التحميل...")

    try:
        ydl_opts = {
            "outtmpl": f"{DOWNLOAD_DIR}/%(title).50s.%(ext)s",
            "format": "mp4/best",
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await msg.edit_text("تم التحميل، جاري الإرسال...")

        with open(file_path, "rb") as video:
            await update.message.reply_video(video=video)

        os.remove(file_path)

    except Exception as e:
        await msg.edit_text("حدث خطأ أثناء التحميل")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    app.run_polling()

if __name__ == "__main__":
    main()
