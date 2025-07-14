import streamlit as st
from PIL import Image
from ultralytics import YOLO
import numpy as np
import database
import os

# Setup database
database.create_tables()

# Load model YOLO
MODEL_PATH = 'weights/best.pt'
model = YOLO(MODEL_PATH)

# Buat folder penyimpanan gambar riwayat
RIWAYAT_FOLDER = 'riwayat_images'
os.makedirs(RIWAYAT_FOLDER, exist_ok=True)

# UI Styles
def girly_style():
    st.markdown("""
    <style>
    .block-container {
      background: linear-gradient(135deg, #ffe4e6, #f8bbd0) !important;
      border-radius: 15px;
      padding: 2rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #ff80ab, #f48fb1);
    }
    </style>
    """, unsafe_allow_html=True)

# Login dan Registrasi
def login_page():
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_id = database.login_user(username, password)
        if user_id:
            st.session_state['user_id'] = user_id
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Username atau password salah.")

    st.markdown("Belum punya akun? Registrasi di bawah:")
    reg_user = st.text_input("Username Baru")
    reg_pass = st.text_input("Password Baru", type="password")
    if st.button("Register"):
        if database.register_user(reg_user, reg_pass):
            st.success("Registrasi berhasil! Silakan login.")
        else:
            st.error("Username sudah digunakan.")

# Sidebar Header
def sidebar_header():
    st.sidebar.markdown("### Selamat datang 👋")
    st.sidebar.markdown("---")
    st.sidebar.caption("👩‍💻 Oleh Chisilia Amanda Wahyudi | Skripsi Deteksi Penyakit Jambu 🍈")

# Halaman Home
def home_page():
    st.title("🍈 Guava Disease Detection with YOLOv11")
    st.markdown("""
    Deteksi penyakit jambu biji secara otomatis menggunakan model YOLOv11.

    **Jenis penyakit:**
    1. Phytophthora → busuk akar & batang  
    2. Scab → bercak kasar di kulit  
    3. Styler and Root → gangguan bunga & akar
    """)
    st.image("images/jambu1.jpg", caption="Contoh Jambu Biji", use_container_width=True)

# Halaman Deteksi
def detection_page():
    st.title("🔍 Deteksi Penyakit Jambu")
    confidence = st.sidebar.slider("Confidence", 10, 100, 25) / 100

    uploaded = st.sidebar.file_uploader("Unggah Gambar", type=["jpg", "jpeg", "png"])

    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="Gambar Input", use_column_width=True)

        if st.button("🔎 Deteksi Sekarang"):
            result = model.predict(img, conf=confidence)
            boxes = result[0].boxes
            hasil = result[0].plot()[:, :, ::-1]
            st.image(hasil, caption="Hasil Deteksi", use_container_width=True)

            detected_labels = []
            for box in boxes:
                cls_id = int(box.cls[0].item())
                label = model.model.names.get(cls_id, "Unknown")
                detected_labels.append(label)

            st.markdown("**Deteksi:**")
            st.write(", ".join(set(detected_labels)))

            # Simpan gambar asli ke folder riwayat_images
            save_path = os.path.join(RIWAYAT_FOLDER, uploaded.name)
            img.save(save_path)

            if 'user_id' in st.session_state:
                database.simpan_riwayat(
                    st.session_state['user_id'],
                    uploaded.name,
                    ", ".join(set(detected_labels))
                )
                st.success("Riwayat deteksi berhasil disimpan.")

# Halaman Riwayat
def history_page():
    st.title("📜 Riwayat Deteksi")
    if 'user_id' not in st.session_state:
        st.warning("Silakan login untuk melihat riwayat.")
        return

    riwayat = database.ambil_riwayat(st.session_state['user_id'])
    if not riwayat:
        st.info("Belum ada riwayat deteksi.")
    else:
        for i, (img_name, result, waktu) in enumerate(riwayat, 1):
            st.subheader(f"Riwayat #{i}")

            img_path = os.path.join(RIWAYAT_FOLDER, img_name)
            if os.path.exists(img_path):
                st.image(img_path, caption=img_name, use_column_width=True)
            else:
                st.warning(f"Gambar {img_name} tidak ditemukan.")

            st.write(f"**Hasil Deteksi:** {result}")
            st.write(f"**Waktu:** {waktu}")
            st.write("---")

# Aplikasi Utama
def main():
    girly_style()
    sidebar_header()

    if 'user_id' not in st.session_state:
        login_page()
        return

    if st.sidebar.button("🔓 Logout"):
        del st.session_state['user_id']
        st.rerun()

    menu = st.sidebar.radio("📌 Menu", ["Home", "Detection", "History"])
    if menu == "Home":
        home_page()
    elif menu == "Detection":
        detection_page()
    elif menu == "History":
        history_page()

if __name__ == "__main__":
    main()
