import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.constantes import AES_KEY, pwd_context


def hash_email(email: str) -> str:
    return hashlib.sha256(email.strip().lower().encode()).hexdigest()


def encrypt_email(email: str) -> bytes:
    aesgcm = AESGCM(AES_KEY)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, email.encode(), None)
    return nonce + ct


def decrypt_email(data: bytes) -> str:
    aesgcm = AESGCM(AES_KEY)
    nonce, ct = data[:12], data[12:]
    return aesgcm.decrypt(nonce, ct, None).decode()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)
