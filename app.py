import streamlit as st
from PIL import Image
from ultralytics import YOLO
import database
import os

# Setup database dan folder penyimpanan gambar
database.create_tables()
RIWAYAT_FOLDER = "riwayat_images"
os.makedirs(RIWAYAT_FOLDER, exist_ok=True)

# Load model
MODEL_PATH = "weights/best.pt"  # Pastikan model kamu ada di path ini
model = YOLO(MODEL_PATH)

# Gaya tampilan
def custom_style():
    st.markdown("""
    <style>
    .block-container {
        background: linear-gradient(to bottom right, #fce4ec, #f8bbd0);
        border-radius: 10px;
        padding: 20px;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #f48fb1, #f06292);
    }
    </style>
    """, unsafe_allow_html=True)

# Login dan Registrasi
def login_page():
    st.title("🔐 Login Pengguna")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_id = database.login_user(username, password)
        if user_id:
            st.session_state['user_id'] = user_id
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Username atau password salah!")

    st.markdown("Belum punya akun? Daftar di bawah:")
    new_user = st.text_input("Username Baru")
    new_pass = st.text_input("Password Baru", type="password")
    if st.button("Daftar"):
        if database.register_user(new_user, new_pass):
            st.success("Registrasi berhasil. Silakan login.")
        else:
            st.warning("Username sudah terpakai.")

# Halaman Deteksi
def detection_page():
    st.title("🍈 Deteksi Penyakit Buah Jambu Biji")

    confidence = st.slider("Confidence", 10, 100, 30) / 100
    uploaded_file = st.file_uploader("Unggah gambar jambu biji...", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar Input", use_container_width=True)

        if st.button("🔍 Jalankan Deteksi"):
            result = model.predict(image, conf=confidence)
            hasil = result[0].plot()[:, :, ::-1]
            st.image(hasil, caption="Hasil Deteksi", use_container_width=True)

            boxes = result[0].boxes
            labels = []
            for box in boxes:
                cls_id = int(box.cls[0].item())
                label = model.model.names.get(cls_id, "Unknown")
                labels.append(label)

            hasil_label = ", ".join(set(labels))
            st.success(f"Hasil Deteksi: {hasil_label}")

            save_path = os.path.join(RIWAYAT_FOLDER, uploaded_file.name)
            image.save(save_path)

            if 'user_id' in st.session_state:
                database.simpan_riwayat(st.session_state['user_id'], uploaded_file.name, hasil_label)
                st.info("Riwayat disimpan!")

# Halaman Riwayat
def history_page():
    st.title("📜 Riwayat Deteksi")
    if 'user_id' not in st.session_state:
        st.warning("Login terlebih dahulu untuk melihat riwayat.")
        return

    riwayat = database.ambil_riwayat(st.session_state['user_id'])
    if not riwayat:
        st.info("Belum ada riwayat.")
    else:
        for i, (img_name, hasil, waktu) in enumerate(riwayat, 1):
            st.markdown(f"### Riwayat #{i}")
            img_path = os.path.join(RIWAYAT_FOLDER, img_name)
            if os.path.exists(img_path):
                st.image(img_path, caption=img_name, use_container_width=True)
            st.write(f"Hasil: {hasil}")
            st.write(f"Waktu: {waktu}")
            st.write("---")

# Halaman Utama
def main():
    custom_style()
    st.sidebar.title("🧪 Menu Aplikasi")
    if 'user_id' not in st.session_state:
        login_page()
        return

    if st.sidebar.button("🔓 Logout"):
        del st.session_state['user_id']
        st.rerun()

    halaman = st.sidebar.radio("Pilih Halaman", ["Deteksi", "Riwayat"])
    if halaman == "Deteksi":
        detection_page()
    elif halaman == "Riwayat":
        history_page()

if __name__ == "__main__":
    main()
