import os
import glob
import telebot
import yt_dlp

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "ارسل رابط فيديو من يوتيوب أو تيك توك أو تويتر/X ✅")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text.strip()

    if not url.startswith("http"):
        bot.reply_to(message, "ارسل رابط صحيح يبدأ بـ http")
        return

    wait = bot.reply_to(message, "جاري التحميل...")

    try:
        for f in glob.glob(f"{DOWNLOAD_DIR}/*"):
            os.remove(f)

        opts = {
            "outtmpl": f"{DOWNLOAD_DIR}/video.%(ext)s",
            "format": "best[ext=mp4]/best",
            "noplaylist": True,
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        files = glob.glob(f"{DOWNLOAD_DIR}/*")
        if not files:
            bot.edit_message_text("فشل التحميل.", message.chat.id, wait.message_id)
            return

        file_path = files[0]

        bot.edit_message_text("تم التحميل، جاري الإرسال...", message.chat.id, wait.message_id)

        with open(file_path, "rb") as video:
            bot.send_video(message.chat.id, video)

        os.remove(file_path)

    except Exception:
        bot.edit_message_text("فشل التحميل. الرابط قد يكون خاص أو الفيديو كبير.", message.chat.id, wait.message_id)

print("Bot is running...")
bot.infinity_polling(skip_pending=True)
