import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import configs

AES_KEY = base64.urlsafe_b64decode(configs.IP_ENCRYPTION_KEY)


def encrypt_ip(ip: str) -> str:
    """Encrypt IP address into a single base64 string."""
    aesgcm = AESGCM(AES_KEY)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, ip.encode(), None)
    return base64.urlsafe_b64encode(nonce + ciphertext).decode()


def decrypt_ip(encrypted_str: str) -> str:
    """Decrypt IP address from single base64 string."""
    data = base64.urlsafe_b64decode(encrypted_str)
    nonce, ciphertext = data[:12], data[12:]
    aesgcm = AESGCM(AES_KEY)
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
