"""
Event Bot Server
"""

import passlib.context

from eventbot.config import passlib as config


crypt_context = passlib.context.CryptContext(schemes=config.SCHEMES)


def hash(raw: str) -> str:
    """Hash the password with a randomly generated salt."""
    return crypt_context.hash(raw)


def verify(raw: str, crypted: str) -> bool:
    """Match a raw and crypted password."""
    try:
        return crypt_context.verify(raw, crypted)
    except ValueError:
        return False


def identify(crypted: str):
    """Identify which algorithm the hash belongs to."""
    return crypt_context.identify(crypted)
