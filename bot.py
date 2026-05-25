import os
import re
import glob
import shutil
import telebot
import yt_dlp

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

BASE_DIR = "downloads"
os.makedirs(BASE_DIR, exist_ok=True)

MAX_SIZE_MB = 48
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024


def is_url(text):
    return text.startswith("http://") or text.startswith("https://")


def clean_url(url):
    url = url.strip()

    # تنظيف روابط يوتيوب المختصرة من si
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"

    # تنظيف روابط YouTube Shorts
    if "youtube.com/shorts/" in url:
        video_id = url.split("/shorts/")[1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"

    return url


def safe_name(text):
    return re.sub(r"[^a-zA-Z0-9_-]", "_", str(text))


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "أرسل رابط فيديو من YouTube / Shorts / TikTok / Twitter/X وسأحاول تحميله لك ✅"
    )


@bot.message_handler(commands=["help"])
def help_cmd(message):
    bot.reply_to(
        message,
        "طريقة الاستخدام:\n"
        "أرسل رابط الفيديو فقط.\n\n"
        "ملاحظة: إذا كان الفيديو كبير جدًا قد لا يرسله تليجرام."
    )


@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text.strip()

    if not is_url(url):
        bot.reply_to(message, "أرسل رابط صحيح يبدأ بـ http أو https")
        return

    url = clean_url(url)

    chat_id = message.chat.id
    user_dir = os.path.join(BASE_DIR, safe_name(chat_id))
    os.makedirs(user_dir, exist_ok=True)

    wait_msg = bot.reply_to(message, "⏳ جاري تجهيز الرابط والتحميل...")

    try:
        # تنظيف مجلد المستخدم
        for f in glob.glob(os.path.join(user_dir, "*")):
            os.remove(f)

        ydl_opts = {
            "outtmpl": os.path.join(user_dir, "video.%(ext)s"),
            "format": (
                "best[ext=mp4][filesize<48M]/"
                "best[ext=mp4][filesize_approx<48M]/"
                "worst[ext=mp4]/"
                "best"
            ),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "max_filesize": MAX_SIZE_BYTES,
            "merge_output_format": "mp4",
            "socket_timeout": 30,
            "retries": 3,
            "fragment_retries": 3,
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                    "Mobile/15E148 Safari/604.1"
                )
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        files = glob.glob(os.path.join(user_dir, "*"))

        if not files:
            bot.edit_message_text(
                "❌ لم أستطع تحميل الفيديو.",
                chat_id,
                wait_msg.message_id
            )
            return

        file_path = files[0]
        file_size = os.path.getsize(file_path)

        if file_size > MAX_SIZE_BYTES:
            bot.edit_message_text(
                "❌ الفيديو كبير جدًا ولا يمكن إرساله عبر البوت.\n"
                "جرّب فيديو أقصر أو رابط آخر.",
                chat_id,
                wait_msg.message_id
            )
            return

        title = info.get("title", "video")

        bot.edit_message_text(
            "✅ تم التحميل، جاري إرسال الفيديو...",
            chat_id,
            wait_msg.message_id
        )

        try:
            with open(file_path, "rb") as video:
                bot.send_video(
                    chat_id,
                    video,
                    caption=f"✅ تم التحميل\n{title}"
                )
        except Exception:
            with open(file_path, "rb") as doc:
                bot.send_document(
                    chat_id,
                    doc,
                    caption=f"✅ تم التحميل\n{title}"
                )

        bot.delete_message(chat_id, wait_msg.message_id)

    except yt_dlp.utils.DownloadError:
        bot.edit_message_text(
            "❌ فشل التحميل.\n"
            "قد يكون الرابط خاص، محمي، أو يحتاج جودة أقل.",
            chat_id,
            wait_msg.message_id
        )

    except Exception as e:
        bot.edit_message_text(
            "❌ حدث خطأ غير متوقع أثناء التحميل.",
            chat_id,
            wait_msg.message_id
        )

    finally:
        try:
            shutil.rmtree(user_dir)
        except Exception:
            pass


print("Bot is running...")
bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
