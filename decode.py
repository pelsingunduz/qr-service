from pyzbar.pyzbar import decode
from PIL import Image


@app.route("/decode", methods=["POST"])
def decode_qr():
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

        decoded_data = decoded_objects[0].data.decode("utf-8")

        return jsonify({
            "message": "QR code decoded successfully",
            "data": decoded_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500 
