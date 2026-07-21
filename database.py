import sqlite3
import os
from flask_login import UserMixin
from config import Config
from cryptography.fernet import Fernet


class User(UserMixin):
    def __init__(self, id, username, email, password_hash, api_key=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.api_key = api_key
        self.created_at = created_at


def get_db_connection():
    connection = sqlite3.connect(Config.DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    connection = get_db_connection()
    with open(os.path.join(os.path.dirname(__file__), "schema.sql"), "r") as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()


def query_db(query, args=(), one=False):
    connection = get_db_connection()
    cursor = connection.execute(query, args)
    rows = cursor.fetchall()
    connection.commit()
    connection.close()
    return (rows[0] if rows else None) if one else rows


def execute_db(query, args=()):
    connection = get_db_connection()
    cursor = connection.execute(query, args)
    connection.commit()
    last_id = cursor.lastrowid
    connection.close()
    return last_id


def get_user_by_id(user_id):
    row = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    if row:
        return User(
            row["id"],
            row["username"],
            row["email"],
            row["password_hash"],
            row["api_key"],
            row["created_at"]
        )
    return None


def get_user_by_username(username):
    row = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)
    if row:
        return User(
            row["id"],
            row["username"],
            row["email"],
            row["password_hash"],
            row["api_key"],
            row["created_at"]
        )
    return None


def get_user_by_email(email):
    row = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)
    if row:
        return User(
            row["id"],
            row["username"],
            row["email"],
            row["password_hash"],
            row["api_key"],
            row["created_at"]
        )
    return None


def get_crypt_handler():
    try:
        return Fernet(Config.ENCRYPTION_KEY.encode())
    except Exception:
        key = Fernet.generate_key()
        return Fernet(key)


def encrypt_key(plain_key):
    if not plain_key:
        return None
    cipher = get_crypt_handler()
    return cipher.encrypt(plain_key.encode()).decode()


def decrypt_key(encrypted_key):
    if not encrypted_key:
        return None
    cipher = get_crypt_handler()
    try:
        return cipher.decrypt(encrypted_key.encode()).decode()
    except Exception:
        return None
