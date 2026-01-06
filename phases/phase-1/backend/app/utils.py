import secrets


def generate_token(length: int = 32) -> str:
    return secrets.token_hex(length)
# Placeholder utilities for Phase II
