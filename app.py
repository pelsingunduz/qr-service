from flask import Flask, request, jsonify, send_file
import qrcode
import uuid
import os

app = Flask(__name__)

QR_FOLDER = "static/qr"
os.makedirs(QR_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return "QR Service is running (Python 3.13)!"


@app.route("/generate", methods=["POST"])
def generate_qr():
    data = request.json.get("data")

    if not data:
        return jsonify({"error": "data field is required"}), 400

    filename = f"{uuid.uuid4()}.png"
    filepath = os.path.join(QR_FOLDER, filename)

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filepath)

    return jsonify({
        "message": "QR code generated",
        "download_url": f"/download/{filename}"
    }), 201


@app.route("/download/<filename>", methods=["GET"])
def download_qr(filename):
    filepath = os.path.join(QR_FOLDER, filename)
    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
