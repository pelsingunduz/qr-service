from flask import Flask, request, jsonify, send_file, render_template
import qrcode
import uuid
import os
from PIL import Image

# Optional dependency for decoding
try:
    from pyzbar.pyzbar import decode
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False

app = Flask(__name__)

# Folders
QR_FOLDER = "static/qr"
UPLOAD_FOLDER = "static/uploads"

os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed upload extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
     return render_template("index.html")

# ----------------------------
# POST /generate
# ----------------------------
@app.route("/generate", methods=["POST"])
def generate_qr():
    if not request.is_json:
        return jsonify({"error": "JSON body required"}), 400

    data = request.json.get("data")
    color = request.json.get("color", "black")
    bg_color = request.json.get("bgColor", "white")
    size = int(request.json.get("size", 200))
    error_level = request.json.get("errorCorrection", "M").upper()

    if not data:
        return jsonify({"error": "data field is required"}), 400

    # Hata düzeltme seviyesi
    error_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H
    }
    ec_level = error_map.get(error_level, qrcode.constants.ERROR_CORRECT_M)

    filename = f"{uuid.uuid4()}.png"
    filepath = os.path.join(QR_FOLDER, filename)

    qr = qrcode.QRCode(
        version=1,
        error_correction=ec_level,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=color, back_color=bg_color)
    img = img.resize((size, size))
    img.save(filepath)

    return jsonify({
        "message": "QR code generated",
        "filename": filename,
        "download_url": f"/download/{filename}"
    }), 201

# ----------------------------
# POST /upload
# ----------------------------
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "file field is required"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": "Invalid file type. Allowed: png, jpg, jpeg"
        }), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    return jsonify({
        "message": "File uploaded successfully",
        "filename": filename,
        "file_path": f"/static/uploads/{filename}"
    }), 201

# ----------------------------
# POST /decode
# ----------------------------
@app.route("/decode", methods=["POST"])
def decode_qr():
    if not PYZBAR_AVAILABLE:
        return jsonify({
            "error": "QR decode dependency not available on this environment"
        }), 501

    if "file" not in request.files:
        return jsonify({"error": "QR image file is required"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        img = Image.open(file)
        decoded_objects = decode(img)

        if not decoded_objects:
            return jsonify({"error": "QR code could not be decoded"}), 400

        return jsonify({
            "message": "QR code decoded successfully",
            "data": decoded_objects[0].data.decode("utf-8")
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# GET /download
# ----------------------------
@app.route("/download/<filename>", methods=["GET"])
def download_qr(filename):
    filepath = os.path.join(QR_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    return send_file(
        filepath,
        as_attachment=True,
        download_name="qr_code.png"
    )

if __name__ == "__main__":
    app.run(debug=True)
