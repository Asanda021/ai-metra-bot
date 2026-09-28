from flask import Flask, request

app = Flask(__name__)

@app.get("/")
def home():
    return "AI Metra Bot Backend is running ✔️"

@app.post("/api/quantity")
def quantity():
    data = request.json

    material = data.get("material", "").lower()

    # ابعاد ورودی
    length = float(data.get("length", 0))       # متر
    width = float(data.get("width", 0))         # متر
    height = float(data.get("height", 0))       # متر
    thickness = float(data.get("thickness", 0)) # متر (برای سنگ، سرامیک، کاشی، کناف)

    count = int(data.get("count", 0))           # مصالح دونه‌ای
    bags = int(data.get("bags", 0))             # مصالح کیسه‌ای

    # محاسبه مساحت
    area = length * width                       # متر مربع

    # محاسبه حجم
    volume = length * width * height            # متر مکعب

    # چگالی‌ها (kg/m³)
    densities = {
        "concrete": 2400,
        "steel": 7850,
        "brick": 1800,
        "block": 1200,
        "gypsum": 850,
        "cement": 1500,
        "stone": 2600,
        "ceramic": 2000,
        "tile": 2000,
        "knauf": 800,
        "wood": 600,
        "sand": 1600,
        "soil": 1200,
        "gravel": 1700,
        "plaster": 900,
        "paint": 1200
    }

    density = densities.get(material, 0)

    # وزن
    weight = volume * density
