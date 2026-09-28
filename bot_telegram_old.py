import os
import telebot
import requests
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

API = "https://ai-metra-bot.onrender.com"

# -------------------------
# منوی اصلی (شیشه‌ای)
# -------------------------
def main_menu():
    menu = InlineKeyboardMarkup()
    menu.add(
        InlineKeyboardButton("🔍 تشخیص مصالح", callback_data="detect"),
        InlineKeyboardButton("📐 متره ساختمان", callback_data="metra")
    )
    menu.add(
        InlineKeyboardButton("ℹ️ راهنما", callback_data="help")
    )
    return menu

# -------------------------
# منوی دسته‌بندی متره
# -------------------------
def metra_menu():
    m = InlineKeyboardMarkup()
    m.add(
        InlineKeyboardButton("🏗 سازه‌ای", callback_data="sazeh"),
        InlineKeyboardButton("🧱 دیوارچینی", callback_data="divar")
    )
    m.add(
        InlineKeyboardButton("🪨 نازک‌کاری", callback_data="nazok"),
        InlineKeyboardButton("🧱 کف‌سازی", callback_data="kaf")
    )
    m.add(
        InlineKeyboardButton("🚰 تأسیسات", callback_data="tasisat")
    )
    m.add(InlineKeyboardButton("⬅️ بازگشت", callback_data="back_main"))
    return m

# -------------------------
# زیرمنوها
# -------------------------
def menu_sazeh():
    m = InlineKeyboardMarkup()
    m.add(
        InlineKeyboardButton("🧱 بتن", callback_data="beton"),
        InlineKeyboardButton("🔩 میلگرد", callback_data="mil"),
        InlineKeyboardButton("🛠 تیرآهن", callback_data="tir")
    )
    m.add(
        InlineKeyboardButton("🧱 ستون", callback_data="soton"),
        InlineKeyboardButton("🧱 فونداسیون", callback_data="fond"),
        InlineKeyboardButton("🧱 دیوار برشی", callback_data="divar_b")
    )
    m.add(InlineKeyboardButton("⬅️ بازگشت", callback_data="back_metra"))
    return m

def menu_divarchini():
    m = InlineKeyboardMarkup()
    m.add(
        InlineKeyboardButton("🧱 آجر", callback_data="ajer"),
        InlineKeyboardButton("🧱 بلوک", callback_data="blok"),
        InlineKeyboardButton("🧱 سفال", callback_data="sofal")
    )
    m.add(
        InlineKeyboardButton("🧱 یونولیت", callback_data="yuno")
    )
    m.add(InlineKeyboardButton("⬅️ بازگشت", callback_data="back_metra"))
    return m

def menu_nazok():
    m = InlineKeyboardMarkup()
    m.add(
        InlineKeyboardButton("🪨 سنگ", callback_data="sang"),
        InlineKeyboardButton("🧱 سرامیک", callback_data="saramik"),
        InlineKeyboardButton("🧱 گچ", callback_data="gach")
    )
    m.add(
        InlineKeyboardButton("🧱 کناف", callback_data="kanaf"),
        InlineKeyboardButton("🎨 رنگ", callback_data="rang")
    )
    m.add(InlineKeyboardButton("⬅️ بازگشت", callback_data="back_metra"))
    return m

def menu_kafsazi():
    m = InlineKeyboardMarkup()
    m.add(
        InlineKeyboardButton("🧱 بتن مگر", callback_data="magar"),
        InlineKeyboardButton("🧱 ماسه سیمان", callback_data="mases"),
        InlineKeyboardButton("🧱 کفپوش", callback_data="kafpush")
    )
    m.add(InlineKeyboardButton("⬅️ بازگشت", callback_data="back_metra"))
    return m

def menu_tasisat():
    m = InlineKeyboardMarkup()
    m.add(
        InlineKeyboardButton("🚰 لوله آب", callback_data="ab"),
        InlineKeyboardButton("🚽 فاضلاب", callback_data="faz"),
        InlineKeyboardButton("⚡ کابل برق", callback_data="bargh")
    )
    m.add(InlineKeyboardButton("⬅️ بازگشت", callback_data="back_metra"))
    return m

# -------------------------
# شروع
# -------------------------
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "سلام مهندس، خوش آمدی 🌟\nیکی از گزینه‌های زیر را انتخاب کن:",
        reply_markup=main_menu()
    )

# -------------------------
# هندل دکمه‌ها
# -------------------------
@bot.callback_query_handler(func=lambda c: True)
def callback(c):
    if c.data == "detect":
        bot.send_message(c.message.chat.id, "لطفاً عکس مصالح را ارسال کن.")
    elif c.data == "metra":
        bot.send_message(c.message.chat.id, "دسته موردنظر را انتخاب کن:", reply_markup=metra_menu())
    elif c.data == "help":
        bot.send_message(c.message.chat.id, "راهنما در حال ساخت است…")

    # زیرمنوها
    elif c.data == "sazeh":
        bot.send_message(c.message.chat.id, "نوع مصالح سازه‌ای:", reply_markup=menu_sazeh())
    elif c.data == "divar":
        bot.send_message(c.message.chat.id, "نوع مصالح دیوارچینی:", reply_markup=menu_divarchini())
    elif c.data == "nazok":
        bot.send_message(c.message.chat.id, "نوع مصالح نازک‌کاری:", reply_markup=menu_nazok())
    elif c.data == "kaf":
        bot.send_message(c.message.chat.id, "نوع مصالح کف‌سازی:", reply_markup=menu_kafsazi())
    elif c.data == "tasisat":
        bot.send_message(c.message.chat.id, "نوع مصالح تأسیسات:", reply_markup=menu_tasisat())

    # بازگشت
    elif c.data == "back_metra":
        bot.send_message(c.message.chat.id, "به منوی متره برگشتی:", reply_markup=metra_menu())
    elif c.data == "back_main":
        bot.send_message(c.message.chat.id, "به منوی اصلی برگشتی:", reply_markup=main_menu())

    # انتخاب مصالح → شروع دریافت ابعاد
    else:
        user_state[c.message.chat.id] = {"material": c.data}
        bot.send_message(c.message.chat.id, "🔹 لطفاً *طول* را وارد کن (متر):\n(این مقدار طول هست)", parse_mode="Markdown")

# -------------------------
# دریافت ابعاد مرحله‌به‌مرحله
# -------------------------
user_state = {}

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
