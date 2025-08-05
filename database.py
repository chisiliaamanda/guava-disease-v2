import sqlite3
from datetime import datetime
import hashlib

DB_PATH = "deteksi.db"

# Membuat tabel users dan riwayat jika belum ada
def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabel pengguna
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
            user_id INTEGER NOT NULL,
            image_name TEXT NOT NULL,
            hasil TEXT NOT NULL,
            waktu TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

# Hash password dengan SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Registrasi user baru
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

# Login user
def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

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

# Ambil riwayat berdasarkan user_id
def ambil_riwayat(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT image_name, hasil, waktu
        FROM riwayat
        WHERE user_id = ?
        ORDER BY waktu DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
