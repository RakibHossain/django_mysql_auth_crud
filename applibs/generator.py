import hashlib
from mysite.settings import PASS_SALT


def password_encrypt(password):
    salt = PASS_SALT
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest()


def create_verification_token(uuid):
    salt = PASS_SALT
    return hashlib.sha384(salt.encode() + str(uuid).encode()).hexdigest()
