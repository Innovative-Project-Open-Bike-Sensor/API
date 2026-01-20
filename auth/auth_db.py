from database import create_connection
from .auth_utils import hash_password, verify_password

def add_user(id: str, password: str) -> bool:
    password_hash, salt = hash_password(password)
    conn = create_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (id, password_hash, salt) VALUES (?, ?, ?)",
            (id, password_hash, salt)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur ajout utilisateur: {e}")
        return False
    finally:
        conn.close()

def check_user(id: str, password: str) -> bool:
    conn = create_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password_hash, salt FROM users WHERE id = ?",
            (id,)
        )
        result = cursor.fetchone()
        if not result:
            return False
        stored_hash, stored_salt = result
        return verify_password(stored_hash, stored_salt, password)
    except sqlite3.Error as e:
        print(f"Erreur vérification utilisateur: {e}")
        return False
    finally:
        conn.close()
