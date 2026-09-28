from flask import Flask, request

app = Flask(__name__)

@app.get("/")
def home():
    return "AI Metra Bot Backend is running ✔️"

@app.post("/api/quantity")
def quantity():
    data = request.json

    material = data.get("material", "concrete")
    length = float(data.get("length", 0))
    width = float(data.get("width", 0))
    height = float(data.get("height", 0))

    volume = length * width * height

    densities = {
        "concrete": 2400,
        "brick": 1800,
        "block": 1200,
        "steel": 7850
    }

    prices = {
        "concrete": 2500000,   # قیمت هر مترمکعب
        "brick": 1200000,
        "block": 900000,
        "steel": 45000         # قیمت هر کیلوگرم
    }

    density = densities.get(material, 2400)
    price = prices.get(material, 2500000)

    weight = volume * density

    if material == "steel":
        total_price = weight * price
    else:
        total_price = volume * price

    return {
        "material": material,
        "length": length,
        "width": width,
        "height": height,
        "volume_m3": volume,
        "weight_kg": weight,
        "price_per_unit": price,
        "total_price": total_price,
        "message": "محاسبه حجم، وزن و قیمت با موفقیت انجام شد ✔️"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
