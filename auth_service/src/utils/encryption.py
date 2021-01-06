import random
import string

from Cryptodome.Cipher import AES

from src.models.data_models import EncryptedToken
from src.settings import AUTH_PRIVATE_KEY


def encrypt_token(data: str) -> EncryptedToken:
    cipher_aes = AES.new(AUTH_PRIVATE_KEY.encode("utf-8"), AES.MODE_EAX)
    ciphertext, digest = cipher_aes.encrypt_and_digest(data.encode())

    return EncryptedToken(
        nonce=cipher_aes.nonce,
        digest=digest,
        token=ciphertext
    )


def decrypt_token(encrypted: EncryptedToken) -> str:
    cipher_aes = AES.new(AUTH_PRIVATE_KEY.encode("utf-8"), AES.MODE_EAX, encrypted.nonce)
    data = cipher_aes.decrypt_and_verify(encrypted.token, encrypted.digest)
    return data.decode()


def get_random_string(length: int) -> str:
    return ''.join(random.choice(string.printable) for _ in range(length))
