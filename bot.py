import os
import glob
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ارسل رابط فيديو من يوتيوب أو تيك توك أو تويتر/X ✅"
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("ارسل رابط صحيح")
        return

    msg = await update.message.reply_text("جاري التحميل...")

    try:
        for f in glob.glob(f"{DOWNLOAD_DIR}/*"):
            os.remove(f)

        ydl_opts = {
            "outtmpl": f"{DOWNLOAD_DIR}/video.%(ext)s",
            "format": "best[ext=mp4]/best",
            "noplaylist": True,
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        files = glob.glob(f"{DOWNLOAD_DIR}/*")

        if not files:
            await msg.edit_text("فشل التحميل")
            return

        file_path = files[0]

        await msg.edit_text("تم التحميل، جاري الإرسال...")

        with open(file_path, "rb") as video:
            await update.message.reply_video(video)

        os.remove(file_path)

    except Exception as e:
        await msg.edit_text("حدث خطأ أثناء التحميل")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

app.run_polling(drop_pending_updates=True)
