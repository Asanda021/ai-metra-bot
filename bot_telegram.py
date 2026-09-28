import os
import telebot
import requests
from flask import Flask
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

API = "https://ai-metra-bot.onrender.com"

# -------------------------
# منوی اصلی
# -------------------------
def main_menu():
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(
        KeyboardButton("🔍 تشخیص مصالح"),
        KeyboardButton("📐 محاسبه ابعاد")
    )
    menu.add(
        KeyboardButton("ℹ️ راهنما")
    )
    return menu

# -------------------------
# شروع
# -------------------------
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "سلام مهندس محمد 👷‍♂️\nاز منوی زیر انتخاب کن:",
        reply_markup=main_menu()
    )

# -------------------------
# تشخیص مصالح
# -------------------------
@bot.message_handler(func=lambda m: m.text == "🔍 تشخیص مصالح")
def ask_photo(msg):
    bot.send_message(msg.chat.id, "لطفاً عکس مصالح را ارسال کن.")

@bot.message_handler(content_types=['photo'])
def photo_handler(msg):
    file_id = msg.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)

    files = {"file": downloaded}
    r = requests.post(f"{API}/api/detect-material", files=files)
    result = r.json()

    material = result.get("detected_material", "unknown")

    bot.reply_to(msg,
        f"مصالح تشخیص داده شد:\n{material}\n\nبرای محاسبه ابعاد، گزینه «📐 محاسبه ابعاد» را بزن."
    )

# -------------------------
# محاسبه ابعاد
# -------------------------
@bot.message_handler(func=lambda m: m.text == "📐 محاسبه ابعاد")
def ask_dimensions(msg):
    bot.send_message(msg.chat.id, "ابعاد را وارد کن:\nمثال:\n4 3 0.2")

@bot.message_handler(func=lambda m: True)
def get_dimensions(msg):
    try:
        length, width, height = map(float, msg.text.split())
    except:
        return

    data = {
        "material": "stone",
        "length": length,
        "width": width,
        "height": height
    }

    r = requests.post(f"{API}/api/quantity", json=data)
    result = r.json()

    bot.reply_to(msg, f"""
🔹 مصالح: {result['material']}
🔹 مساحت: {result['area_m2']} متر مربع
🔹 حجم: {result['volume_m3']} متر مکعب
🔹 وزن: {result['weight_kg']} کیلوگرم
""")

# -------------------------
# اجرای همزمان ربات + Flask
# -------------------------
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: bot.infinity_polling()).start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
