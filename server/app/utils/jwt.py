"""This module provides helper functionality with JWT."""


import jwt

from app import APP_CONFIG
from app.exceptions import TokenError


def decode_token(token):
    """Return decoded payload from json web token."""
    try:
        return jwt.decode(token, APP_CONFIG.JWT_SECRET_KEY, algorithms=APP_CONFIG.JWT_ALGORITHM)
    except jwt.DecodeError:
        raise TokenError("The token is invalid.")
    except jwt.ExpiredSignatureError:
        raise TokenError("The token has expired.")
