import sqlite3
import hashlib

# Buat tabel users dan detection_history jika belum ada
def create_tables():
    conn = sqlite3.connect('deteksi.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_name TEXT,
            detection_result TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


# Hash password menggunakan SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Registrasi user baru
def register_user(username, password):
    conn = sqlite3.connect('deteksi.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                       (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username sudah ada
    finally:
        conn.close()


# Login user, return user_id jika berhasil
def login_user(username, password):
    conn = sqlite3.connect('deteksi.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?',
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None


# Simpan riwayat deteksi
def simpan_riwayat(user_id, image_name, hasil_deteksi):
    conn = sqlite3.connect('deteksi.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO detection_history (user_id, image_name, detection_result)
        VALUES (?, ?, ?)
    ''', (user_id, image_name, hasil_deteksi))
    conn.commit()
    conn.close()


# Ambil riwayat deteksi berdasarkan user_id
def ambil_riwayat(user_id):
    conn = sqlite3.connect('deteksi.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT image_name, detection_result, detected_at
        FROM detection_history
        WHERE user_id = ?
        ORDER BY detected_at DESC
    ''', (user_id,))
    hasil = cursor.fetchall()
    conn.close()
    return hasil


# Jalankan hanya sekali untuk membuat tabel di awal
if __name__ == "__main__":
    create_tables()
    print("Database dan tabel berhasil dibuat.")

