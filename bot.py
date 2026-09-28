from flask import Flask, request

app = Flask(__name__)

@app.get("/")
def home():
    return "AI Metra Bot Backend is running ✔️"

@app.post("/api/quantity")
def quantity():
    data = request.json

    material = data.get("material", "concrete")  # نوع مصالح
    length = float(data.get("length", 0))
    width = float(data.get("width", 0))
    height = float(data.get("height", 0))

    volume = length * width * height

    # چگالی‌ها (بعداً کامل‌ترش می‌کنیم)
    densities = {
        "concrete": 2400,   # بتن
        "brick": 1800,      # آجر
        "block": 1200,      # بلوک سیمانی
        "steel": 7850       # میلگرد
    }

    density = densities.get(material, 2400)
    weight = volume * density

    return {
        "material": material,
        "length": length,
        "width": width,
        "height": height,
        "volume_m3": volume,
        "weight_kg": weight,
        "message": "محاسبه حجم و وزن با موفقیت انجام شد ✔️"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
