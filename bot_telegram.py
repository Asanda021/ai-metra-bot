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
        KeyboardButton("📐 متره ساختمان")
    )
    menu.add(KeyboardButton("ℹ️ راهنما"))
    return menu

# -------------------------
# منوی دسته‌بندی متره
# -------------------------
def metra_menu():
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(
        KeyboardButton("🧱 دیوارچینی"),
        KeyboardButton("🪨 نازک‌کاری")
    )
    menu.add(
        KeyboardButton("🏗 سازه‌ای"),
        KeyboardButton("🚰 تأسیسات")
    )
    menu.add(KeyboardButton("⬅️ بازگشت"))
    return menu

# -------------------------
# زیرمنوها
# -------------------------
def menu_sazeh():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(
        KeyboardButton("🧱 بتن"),
        KeyboardButton("🔩 میلگرد"),
        KeyboardButton("🛠 تیرآهن")
    )
    m.add(KeyboardButton("⬅️ بازگشت"))
    return m

def menu_divarchini():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(
        KeyboardButton("🧱 آجر"),
        KeyboardButton("🧱 بلوک"),
        KeyboardButton("🧱 یونولیت")
    )
    m.add(KeyboardButton("⬅️ بازگشت"))
    return m

def menu_nazok():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(
        KeyboardButton("🪨 سنگ"),
        KeyboardButton("🧱 سرامیک"),
        KeyboardButton("🧱 گچ"),
        KeyboardButton("🧱 کناف")
    )
    m.add(KeyboardButton("⬅️ بازگشت"))
    return m

def menu_tasisat():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(
        KeyboardButton("🚰 لوله آب"),
        KeyboardButton("🚽 فاضلاب"),
        KeyboardButton("⚡ کابل برق")
    )
    m.add(KeyboardButton("⬅️ بازگشت"))
    return m

# -------------------------
# شروع
# -------------------------
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "سلام مهندس محمد 👷‍♂️\nاز منوی زیر انتخاب کن:", reply_markup=main_menu())

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

    bot.reply_to(msg, f"مصالح تشخیص داده شد:\n{material}")

# -------------------------
# انتخاب دسته متره
# -------------------------
@bot.message_handler(func=lambda m: m.text == "📐 متره ساختمان")
def metra(msg):
    bot.send_message(msg.chat.id, "دسته موردنظر را انتخاب کن:", reply_markup=metra_menu())

# -------------------------
# انتخاب زیر دسته‌ها
# -------------------------
@bot.message_handler(func=lambda m: m.text == "🏗 سازه‌ای")
def saz(msg):
    bot.send_message(msg.chat.id, "نوع مصالح سازه‌ای:", reply_markup=menu_sazeh())

@bot.message_handler(func=lambda m: m.text == "🧱 دیوارچینی")
def divar(msg):
    bot.send_message(msg.chat.id, "نوع مصالح دیوارچینی:", reply_markup=menu_divarchini())

@bot.message_handler(func=lambda m: m.text == "🪨 نازک‌کاری")
def nazok(msg):
    bot.send_message(msg.chat.id, "نوع مصالح نازک‌کاری:", reply_markup=menu_nazok())

@bot.message_handler(func=lambda m: m.text == "🚰 تأسیسات")
def tasisat(msg):
    bot.send_message(msg.chat.id, "نوع مصالح تأسیسات:", reply_markup=menu_tasisat())

# -------------------------
# دریافت ابعاد مرحله‌به‌مرحله
# -------------------------
user_state = {}

@bot.message_handler(func=lambda m: m.text in [
    "🧱 بتن","🔩 میلگرد","🛠 تیرآهن",
    "🧱 آجر","🧱 بلوک","🧱 یونولیت",
    "🪨 سنگ","🧱 سرامیک","🧱 گچ","🧱 کناف",
    "🚰 لوله آب","🚽 فاضلاب","⚡ کابل برق"
])
def ask_length(msg):
    user_state[msg.chat.id] = {"material": msg.text}
    bot.send_message(msg.chat.id, "🔹 لطفاً *طول* را وارد کن (متر):\n(این مقدار طول هست)", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.chat.id in user_state and "length" not in user_state[m.chat.id])
def get_length(msg):
    try:
        user_state[msg.chat.id]["length"] = float(msg.text)
        bot.send_message(msg.chat.id, "🔹 لطفاً *عرض* را وارد کن (متر):\n(این مقدار عرض هست)", parse_mode="Markdown")
    except:
        bot.send_message(msg.chat.id, "❗ مقدار طول اشتباهه. دوباره وارد کن.")

@bot.message_handler(func=lambda m: m.chat.id in user_state and "width" not in user_state[m.chat.id])
def get_width(msg):
    try:
        user_state[msg.chat.id]["width"] = float(msg.text)
        bot.send_message(msg.chat.id, "🔹 لطفاً *ارتفاع* را وارد کن (متر):\n(این مقدار ارتفاع هست)", parse_mode="Markdown")
    except:
        bot.send_message(msg.chat.id, "❗ مقدار عرض اشتباهه. دوباره وارد کن.")

@bot.message_handler(func=lambda m: m.chat.id in user_state and "height" not in user_state[m.chat.id])
def get_height(msg):
    try:
        user_state[msg.chat.id]["height"] = float(msg.text)
    except:
        bot.send_message(msg.chat.id, "❗ مقدار ارتفاع اشتباهه. دوباره وارد کن.")
        return

    data = {
        "material": user_state[msg.chat.id]["material"],
        "length": user_state[msg.chat.id]["length"],
        "width": user_state[msg.chat.id]["width"],
        "height": user_state[msg.chat.id]["height"]
    }

    r = requests.post(f"{API}/api/quantity", json=data)
    result = r.json()

    bot.send_message(msg.chat.id, f"""
🔹 مصالح: {result['material']}
🔹 مساحت: {result['area_m2']} متر مربع
🔹 حجم: {result['volume_m3']} متر مکعب
🔹 وزن: {result['weight_kg']} کیلوگرم
""", reply_markup=main_menu())

    del user_state[msg.chat.id]

# -------------------------
# اجرای همزمان ربات + Flask
# -------------------------
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: bot.infinity_polling()).start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
