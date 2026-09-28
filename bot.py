import os
import telebot
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# -------------------------
# بارگذاری ماژول‌ها
# -------------------------
from modules.concrete_roof import ROOF_TYPES, calc_roof_volume
from modules.rebar_core import calc_rebar
from modules.rebar_thermal import calc_thermal
from modules.rebar_tirche import calc_tirche
from modules.rebar_tirche_dobl import calc_tirche_dobl
from modules.rebar_column import calc_column_long
from modules.rebar_beam import calc_beam_long
from modules.rebar_strip import calc_strip_long
from modules.rebar_raft import calc_raft_mesh
from modules.rebar_wait import calc_wait
from modules.rebar_shenazh import calc_shenazh
from modules.summary import summarize

# -------------------------
# تنظیمات ربات
# -------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

user_state = {}
project_rebars = []

# -------------------------
# منوی اصلی
# -------------------------
def main_menu():
    m = InlineKeyboardMarkup()
    m.add(
        InlineKeyboardButton("🧱 بتن سقف", callback_data="menu_roof"),
        InlineKeyboardButton("🔩 برآورد میلگرد", callback_data="menu_rebar")
    )
    m.add(
        InlineKeyboardButton("📊 جمع‌بندی پروژه", callback_data="menu_summary")
    )
    return m

# -------------------------
# منوی سقف
# -------------------------
def menu_roof():
    m = InlineKeyboardMarkup()
    for key, (name, coeff) in ROOF_TYPES.items():
        m.add(InlineKeyboardButton(name, callback_data=f"roof_{key}"))
    m.add(InlineKeyboardButton("⬅️ بازگشت", callback_data="back_main"))
    return m

# -------------------------
# منوی میلگرد
# -------------------------
def menu_rebar():
    m = InlineKeyboardMarkup()
    m.add(
        InlineKeyboardButton("میلگرد حرارتی سقف", callback_data="rebar_thermal"),
        InlineKeyboardButton("تیرچه یونولیتی", callback_data="rebar_tirche"),
    )
    m.add(
        InlineKeyboardButton("تیرچه دوبل", callback_data="rebar_tirche_dobl"),
        InlineKeyboardButton("ستون بتنی", callback_data="rebar_column"),
    )
    m.add(
        InlineKeyboardButton("تیر بتنی", callback_data="rebar_beam"),
        InlineKeyboardButton("فونداسیون نواری", callback_data="rebar_strip"),
    )
    m.add(
        InlineKeyboardButton("فونداسیون رادیه", callback_data="rebar_raft"),
        InlineKeyboardButton("میلگرد انتظار ستون", callback_data="rebar_wait"),
    )
    m.add(
        InlineKeyboardButton("شناژ و کلاف", callback_data="rebar_shenazh")
    )
    m.add(InlineKeyboardButton("⬅️ بازگشت", callback_data="back_main"))
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
    chat_id = c.message.chat.id
    data = c.data

    # منوها
    if data == "menu_roof":
        bot.send_message(chat_id, "نوع سقف را انتخاب کن:", reply_markup=menu_roof())
        return

    if data == "menu_rebar":
        bot.send_message(chat_id, "نوع عضو را انتخاب کن:", reply_markup=menu_rebar())
        return

    if data == "back_main":
        bot.send_message(chat_id, "به منوی اصلی برگشتی:", reply_markup=main_menu())
        return

    if data == "menu_summary":
        send_summary(chat_id)
        return

    # -------------------------
    # انتخاب نوع سقف
    # -------------------------
    if data.startswith("roof_"):
        key = data.replace("roof_", "")
        name, coeff = ROOF_TYPES[key]

        user_state[chat_id] = {
            "mode": "roof",
            "roof_key": key,
            "roof_name": name,
            "coeff": coeff
        }

        bot.send_message(
            chat_id,
            f"🔳 {name}\nضریب بتن: {coeff}\n\n📏 طول سقف را وارد کن:"
        )
        return

    # -------------------------
    # میلگرد حرارتی سقف
    # -------------------------
    if data == "rebar_thermal":
        user_state[chat_id] = {"mode": "thermal"}
        bot.send_message(chat_id, "📏 طول سقف را وارد کن:")
        return

    # -------------------------
    # تیرچه یونولیتی
    # -------------------------
    if data == "rebar_tirche":
        user_state[chat_id] = {"mode": "tirche"}
        bot.send_message(chat_id, "🔩 قطر میلگرد را وارد کن:")
        return

    # -------------------------
    # تیرچه دوبل
    # -------------------------
    if data == "rebar_tirche_dobl":
        user_state[chat_id] = {"mode": "tirche_dobl", "step": 1}
        bot.send_message(chat_id, "🔩 قطر میلگرد تیرچه اول:")
        return

    # -------------------------
    # ستون
    # -------------------------
    if data == "rebar_column":
        user_state[chat_id] = {"mode": "column", "step": "dia"}
        bot.send_message(chat_id, "🔩 قطر میلگرد طولی ستون:")
        return

    # -------------------------
    # تیر
    # -------------------------
    if data == "rebar_beam":
        user_state[chat_id] = {"mode": "beam", "step": "dia"}
        bot.send_message(chat_id, "🔩 قطر میلگرد طولی تیر:")
        return

    # -------------------------
    # فونداسیون نواری
    # -------------------------
    if data == "rebar_strip":
        user_state[chat_id] = {"mode": "strip", "step": "dia"}
        bot.send_message(chat_id, "🔩 قطر میلگرد طولی فونداسیون نواری:")
        return

    # -------------------------
    # رادیه
    # -------------------------
    if data == "rebar_raft":
        user_state[chat_id] = {"mode": "raft", "step": "L"}
        bot.send_message(chat_id, "📏 طول رادیه:")
        return

    # -------------------------
    # میلگرد انتظار ستون
    # -------------------------
    if data == "rebar_wait":
        user_state[chat_id] = {"mode": "wait", "step": "dia"}
        bot.send_message(chat_id, "🔩 قطر میلگرد انتظار:")
        return

    # -------------------------
    # شناژ
    # -------------------------
    if data == "rebar_shenazh":
        user_state[chat_id] = {"mode": "shenazh", "step": "dia"}
        bot.send_message(chat_id, "🔩 قطر میلگرد شناژ:")
        return

# -------------------------
# ورودی‌های مرحله‌ای
# -------------------------
@bot.message_handler(func=lambda m: True)
def input_handler(msg):
    chat_id = msg.chat.id

    if chat_id not in user_state:
        return

    mode = user_state[chat_id]["mode"]

    # -------------------------
    # بتن سقف
    # -------------------------
    if mode == "roof":
        st = user_state[chat_id]

        if "length" not in st:
            st["length"] = float(msg.text)
            bot.send_message(chat_id, "📐 عرض سقف را وارد کن:")
            return

        st["width"] = float(msg.text)
        key = st["roof_key"]
        L = st["length"]
        W = st["width"]

        name, coeff, area, volume = calc_roof_volume(key, L, W)

        bot.send_message(chat_id, f"""
🔳 {name}
📏 طول: {L}
📐 عرض: {W}
📌 ضریب: {coeff}
📐 مساحت: {area:.2f}
⚖️ حجم بتن: {volume:.2f}
""", reply_markup=main_menu())

        del user_state[chat_id]
        return

    # -------------------------
    # میلگرد حرارتی سقف
    # -------------------------
    if mode == "thermal":
        st = user_state[chat_id]

        if "L" not in st:
            st["L"] = float(msg.text)
            bot.send_message(chat_id, "📐 عرض سقف:")
            return

        if "W" not in st:
            st["W"] = float(msg.text)
            bot.send_message(chat_id, "🔩 قطر میلگرد:")
            return

        if "dia" not in st:
            st["dia"] = int(msg.text)
            bot.send_message(chat_id, "📏 فاصله میلگردها:")
            return

        if "spacing" not in st:
            st["spacing"] = float(msg.text)
            bot.send_message(chat_id, "📌 درصد پرت:")
            return

        waste = float(msg.text)

        result = calc_thermal(
            st["L"], st["W"], st["dia"], st["spacing"], waste=waste
        )

        data = result["data"]

        bot.send_message(chat_id, f"""
میلگرد حرارتی سقف
تعداد جهت X: {result['nX']}
تعداد جهت Y: {result['nY']}
طول کل: {result['total_len']:.2f}

📌 خروجی:
قطر: Ø{data['dia']}
وزن کل: {data['total_weight']:.2f} kg
شاخه: {data['branches']}
""", reply_markup=main_menu())

        project_rebars.append(data)
        del user_state[chat_id]
        return

    # -------------------------
    # تیرچه یونولیتی
    # -------------------------
    if mode == "tirche":
        st = user_state[chat_id]

        if "dia" not in st:
            st["dia"] = int(msg.text)
            bot.send_message(chat_id, "🔢 تعداد میلگرد در هر تیرچه:")
            return

        if "count_per" not in st:
            st["count_per"] = int(msg.text)
            bot.send_message(chat_id, "🔢 تعداد تیرچه:")
            return

        if "tirche_count" not in st:
            st["tirche_count"] = int(msg.text)
            bot.send_message(chat_id, "📏 طول هر میلگرد:")
            return

        if "length_each" not in st:
            st["length_each"] = float(msg.text)
            bot.send_message(chat_id, "📌 درصد پرت:")
            return

        waste = float(msg.text)

        data = calc_tirche(
            member="تیرچه یونولیتی",
            dia=st["dia"],
            count_per_tirche=st["count_per"],
            tirche_count=st["tirche_count"],
            length_each=st["length_each"],
            waste=waste
        )

        bot.send_message(chat_id, f"""
تیرچه یونولیتی
قطر: Ø{data['dia']}
تعداد کل: {data['count']}
وزن کل: {data['total_weight']:.2f} kg
شاخه: {data['branches']}
""", reply_markup=main_menu())

        project_rebars.append(data)
        del user_state[chat_id]
        return

    # -------------------------
    # تیرچه دوبل
    # -------------------------
    if mode == "tirche_dobl":
        st = user_state[chat_id]

        if st["step"] == 1:
            st["dia1"] = int(msg.text)
            st["step"] = 2
            bot.send_message(chat_id, "🔢 تعداد میلگرد تیرچه اول:")
            return

        if st["step"] == 2:
            st["count1"] = int(msg.text)
            st["step"] = 3
            bot.send_message(chat_id, "📏 طول میلگرد تیرچه اول:")
            return

        if st["step"] == 3:
            st["len1"] = float(msg.text)
            st["step"] = 4
            bot.send_message(chat_id, "🔩 قطر میلگرد تیرچه دوم:")
            return

        if st["step"] == 4:
            st["dia2"] = int(msg.text)
            st["step"] = 5
            bot.send_message(chat_id, "🔢 تعداد میلگرد تیرچه دوم:")
            return

        if st["step"] == 5:
            st["count2"] = int(msg.text)
            st["step"] = 6
            bot.send_message(chat_id, "📏 طول میلگرد تیرچه دوم:")
            return

        if st["step"] == 6:
            st["len2"] = float(msg.text)
            st["step"] = 7
            bot.send_message(chat_id, "📌 درصد پرت:")
            return

        waste = float(msg.text)

        params1 = {
            "member": "تیرچه دوبل - تیرچه اول",
            "dia": st["dia1"],
            "count_per_tirche": st["count1"],
            "tirche_count": 1,
            "length_each": st["len1"],
            "waste": waste
        }

        params2 = {
            "member": "تیرچه دوبل - تیرچه دوم",
            "dia": st["dia2"],
            "count_per_tirche": st["count2"],
            "tirche_count": 1,
            "length_each": st["len2"],
            "waste": waste
        }

        r1, r2 = calc_tirche_dobl(params1, params2)

        bot.send_message(chat_id, f"""
تیرچه دوبل

تیرچه اول:
قطر: Ø{r1['dia']}
وزن کل: {r1['total_weight']:.2f} kg

تیرچه دوم:
قطر: Ø{r2['dia']}
وزن کل: {r2['total_weight']:.2f} kg
""", reply_markup=main_menu())

        project_rebars.append(r1)
        project_rebars.append(r2)
        del user_state[chat_id]
        return

    # -------------------------
    # ستون
    # -------------------------
    if mode == "column":
        st = user_state[chat_id]

        if st["step"] == "dia":
            st["dia"] = int(msg.text)
            st["step"] = "count"
            bot.send_message(chat_id, "🔢 تعداد میلگرد طولی:")
            return

        if st["step"] == "count":
            st["count"] = int(msg.text)
            st["step"] = "height"
            bot.send_message(chat_id, "📏 ارتفاع ستون:")
            return

        if st["step"] == "height":
            st["height"] = float(msg.text)
            st["step"] = "floors"
            bot.send_message(chat_id, "🔢 تعداد طبقات:")
            return

        if st["step"] == "floors":
            st["floors"] = int(msg.text)
            st["step"] = "waste"
            bot.send_message(chat_id, "📌 درصد پرت:")
            return

        waste = float(msg.text)

        data = calc_column_long(
            st["dia"], st["count"], st["height"], st["floors"], waste=waste
        )

        bot.send_message(chat_id, f"""
ستون بتنی - میلگرد طولی
قطر: Ø{data['dia']}
تعداد کل: {data['count']}
وزن کل: {data['total_weight']:.2f} kg
شاخه: {data['branches']}
""", reply_markup=main_menu())

        project_rebars.append(data)
        del user_state[chat_id]
        return

    # -------------------------
    # تیر
    # -------------------------
    if mode == "beam":
        st = user_state[chat_id]

        if st["step"] == "dia":
            st["dia"] = int(msg.text)
            st["step"] = "count"
            bot.send_message(chat_id, "🔢 تعداد میلگرد:")
            return

        if st["step"] == "count":
            st["count"] = int(msg.text)
            st["step"] = "length"
            bot.send_message(chat_id, "📏 طول تیر:")
            return

        if st["step"] == "length":
            st["length"] = float(msg.text)
            st["step"] = "waste"
            bot.send_message(chat_id, "📌 درصد پرت:")
            return

        waste = float(msg.text)

        data = calc_beam_long(
            "تیر بتنی - میلگرد طولی",
            st["dia"], st["count"], st["length"], waste=waste
        )

        bot.send_message(chat_id, f"""
تیر بتنی - میلگرد طولی
قطر: Ø{data['dia']}
تعداد کل: {data['count']}
وزن کل: {data['total_weight']:.2f} kg
شاخه: {data['branches']}
""", reply_markup=main_menu())

        project_rebars.append(data)
        del user_state[chat_id]
        return

    # -------------------------
    # فونداسیون نواری
    # -------------------------
    if mode == "strip":
        st = user_state[chat_id]

        if st["step"] == "dia":
            st["dia"] = int(msg.text)
            st["step"] = "count"
            bot.send_message(chat_id, "🔢 تعداد میلگرد:")
            return

        if st["step"] == "count":
            st["count"] = int(msg.text)
            st["step"] = "length"
            bot.send_message(chat_id, "📏 طول ف
