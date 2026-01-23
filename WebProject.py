import streamlit as st
import requests
from PIL import Image
import io

# Flask Sunucusunun Adresi
API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="QR Arayüzü", page_icon="🔗")
st.title("🔗 Python QR İstemcisi")
st.markdown(f"**Bağlı Sunucu:**'{API_URL}'")

# Sekmeler
tab1, tab2 = st.tabs(["QR Oluştur", "QR Oku"])

with tab1:
    st.header("QR Kod Üret")
    user_input = st.text_input("QR İçeriği Girin")

    if st.button("Oluştur"):
        if user_input:
            try:
                # 1. Flask'a POST isteği atıyoruz.
                response = requests.post(f"{API_URL}/generate", json={"data": user_input})

                if response.status_code == 201:
                    data = response.json()
                    st.success("Başarılı! Sunucudan yanıt alındı.")

                    # 2. Resmi göstermek için Flask'tan geri yüklüyoruz (GET isteği)
                    download_link = data['download_url']
                    img_response = requests.get(f"{API_URL}{download_link}")

                    if img_response.status_code == 200:
                        image_bytes = img_response.content
                        st.image(image_bytes, caption="Sunucudan Gelen QR", width=250)

                        # İndirme Butonu
                        st.download_button(
                            label="📥 Dosyayı İndir",
                            data=image_bytes,
                            file_name="benim_qr_kodum.png",
                            mime="image/png"
                        )
                    else:
                        st.error(f"Hata: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Hata: Flask sunucusu (server.py) çalışmıyor olabilir!")
        else:
            st.warning("Lütfen veri girin.")

with tab2:
    st.header("QR Kod Çözümle")
    uploaded_file = st.file_uploader("QR resmini buraya bırakın", type=['png', 'jpg'])

    if uploaded_file is not None:
        # Resmi ekranda göster
        st.image(uploaded_file, width=200)

        if st.button("Sunucuya Gönder ve Çöz"):
            try:
                # Flask'a dosya gönderme (Multipart Upload)
                files = {'file': uploaded_file.getvalue()}
                response = requests.post(f"{API_URL}/decode", files=files)

                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        st.success("Sonuç Bulundu:")
                        for item in result['results']:
                            st.code(item)
                    else:
                        st.warning("QR Kod bulunamadı.")
                else:
                    st.error("Sunucu hatası.")

            except requests.exceptions.ConnectionError:
                st.error("Sunucuya bağlanılamadı.")
