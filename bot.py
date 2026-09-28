from flask import Flask, request

app = Flask(__name__)

@app.get("/")
def home():
    return "AI Metra Bot Backend is running ✔️"

@app.post("/api/quantity")
def quantity():
    data = request.json

    length = float(data.get("length", 0))
    width = float(data.get("width", 0))
    height = float(data.get("height", 0))

    volume = length * width * height

    return {
        "length": length,
        "width": width,
        "height": height,
        "volume": volume,
        "message": "محاسبه حجم با موفقیت انجام شد ✔️"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
