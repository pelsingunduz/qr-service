@app.route("/download/<filename>", methods=["GET"])
def download_qr(filename):
    filepath = os.path.join(QR_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(
            filepath,
            as_attachment=True,
            download_name="qr_code.png"  # İndirilen dosyanın adı bu olur
        )
    return "Dosya bulunamadı", 404
