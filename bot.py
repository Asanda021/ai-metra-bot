from flask import Flask, request

app = Flask(__name__)

@app.get("/")
def home():
    return "AI Metra Bot Backend is running ✔️"

@app.post("/api/quantity")
def quantity():
    data = request.json

    material = data.get("material", "").lower()
    length = float(data.get("length", 0))
    width = float(data.get("width", 0))
    height = float(data.get("height", 0))
    thickness = float(data.get("thickness", 0))   # برای سنگ، سرامیک، کاشی، کناف
    count = int(data.get("count", 0))             # مصالح دونه‌ای
    bags = int(data.get("bags", 0))               # مصالح کیسه‌ای

    # محاسبه مساحت
    area = length * width  # m²

    # محاسبه حجم
    volume = length * width * height  # m³

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
        "knauf": 800
    }

    density = densities.get(material, 0)

    # وزن
    weight = volume * density

    return {
        "material": material,
        "length_m": length,
        "width_m": width,
        "height_m": height,
        "thickness_m": thickness,
        "area_m2": area,
        "volume_m3": volume,
        "weight_kg": weight,
        "count": count,
        "bags": bags,
        "message": "محاسبه واحدهای مهندسی انجام شد ✔️"
    }

@app.post("/api/detect-material")
def detect_material():
    return {
        "message": "این API آماده دریافت عکس است ✔️",
        "status": "waiting_for_image"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
