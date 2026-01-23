from flask import Flask, request, jsonify, send_file
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
    return "QR Service is running!"


# ----------------------------
# POST /generate
# ----------------------------
@app.route("/generate", methods=["POST"])
def generate_qr():
    if not request.is_json:
        return jsonify({"error": "JSON body required"}), 400

    data = request.json.get("data")
    if not data:
        return jsonify({"error": "data field is required"}), 400

    filename = f"{uuid.uuid4()}.png"
    filepath = os.path.join(QR_FOLDER, filename)

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
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
