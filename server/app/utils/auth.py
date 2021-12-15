"""This module provides decorators for server application."""

from functools import wraps
from http import HTTPStatus

from flask import request, g

from app.exceptions import TokenError
from app.utils.response import make_response
from app.utils.jwt import decode_token


def auth_required(view):
    """Check if authorization token in headers is correct."""

    @wraps(view)
    def decorated_function(*args, **kwargs):
        """Returns UNAUTHORIZED if authorization token is not correct or empty."""
        token = request.headers.get("Authorization")
        if not token:
            return make_response(
                success=False,
                message="You aren't authorized. Please provide authorization token.",
                http_status=HTTPStatus.UNAUTHORIZED,
            )

        token = token.split("Bearer ")[-1]
        try:
            payload = decode_token(token)
        except TokenError as err:
            return make_response(
                success=False,
                message=f"Wrong credentials. {str(err)}",
                http_status=HTTPStatus.UNAUTHORIZED,
            )

        g.user_id = payload["user_id"]
        return view(*args, **kwargs)

    return decorated_function
