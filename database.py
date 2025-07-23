import sqlite3
from datetime import datetime
import hashlib

DB_PATH = "guava.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabel users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Tabel riwayat deteksi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS riwayat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_name TEXT,
            hasil TEXT,
            waktu TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

# Fungsi hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fungsi registrasi
def register_user(username, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        hashed = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# Fungsi login
def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed))
    user = cursor.fetchone()
    conn.close()
    if user:
        return user[0]  # user_id
    return None

# Simpan riwayat deteksi
def simpan_riwayat(user_id, image_name, hasil):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO riwayat (user_id, image_name, hasil, waktu)
        VALUES (?, ?, ?, ?)
    """, (user_id, image_name, hasil, waktu))
    conn.commit()
    conn.close()

# Ambil riwayat berdasarkan user
def ambil_riwayat(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT image_name, hasil, waktu
        FROM riwayat
        WHERE user_id = ?
        ORDER BY waktu DESC
    """, (user_id,))
    hasil = cursor.fetchall()
    conn.close()
    return hasil
