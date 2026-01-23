from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import qrcode
import uuid
import os

app = Flask(__name__)

QR_FOLDER = "static/qr"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB max file size


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            "error": "Invalid file type. Allowed types: " + ", ".join(ALLOWED_EXTENSIONS)
        }), 400
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    try:
        file.save(filepath)
        return jsonify({
            "message": "File uploaded successfully",
            "filename": unique_filename,
            "original_filename": original_filename,
            "file_url": f"/uploads/{unique_filename}",
            "file_size": os.path.getsize(filepath)
        }), 201
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500


@app.route("/uploads/<filename>", methods=["GET"])
def get_uploaded_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
