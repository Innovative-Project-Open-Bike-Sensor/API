import hashlib
import os

def hash_password(password: str) -> tuple[str, str]:
    salt = os.urandom(16).hex()
    password_salted = password + salt
    password_hash = hashlib.sha256(password_salted.encode()).hexdigest()
    return password_hash, salt

def verify_password(stored_hash: str, stored_salt: str, input_password: str) -> bool:
    input_salted = input_password + stored_salt
    input_hash = hashlib.sha256(input_salted.encode()).hexdigest()
    return input_hash == stored_hash
