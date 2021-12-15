"""This module provides basic server endpoints."""

import logging
from http import HTTPStatus

from flask import Blueprint, request

from app.utils.response import make_response


internal_blueprint = Blueprint("ct-internal", __name__)


LOGGER = logging.getLogger(__name__)
SAFE_REQUEST_METHODS = ("GET", "HEAD", "OPTIONS")


@internal_blueprint.route("/health", methods=["GET"])
def health():
    """Return health OK http status."""
    return make_response(
        success=True,
        message=f"OK. URL: {str(request.url)}",
        http_status=HTTPStatus.OK
    )


def validate_body():
    """Validate request json body for all request, except GET."""
    if request.method not in SAFE_REQUEST_METHODS and request.json is None:
        return make_response(
            success=False,
            message="Wrong input. Couldn't found json body.",
            http_status=HTTPStatus.BAD_REQUEST,
        )


def handle_404(error):
    """Return custom response for 404 http status code."""
    return make_response(
        success=False,
        message=f"The endpoint ({request.path}) you are trying to access could not be found on the server.",
        http_status=HTTPStatus.NOT_FOUND,
    )


def handle_405(error):
    """Return custom response for 405 http status code."""
    return make_response(
        success=False,
        message=f"The method ({request.method}) you are trying to use for this URL is not supported.",
        http_status=HTTPStatus.METHOD_NOT_ALLOWED,
    )


def handle_500(error):
    """Return custom response for 500 http status code."""
    LOGGER.error("Unhandled 500x error: %s", error)

    return make_response(
        success=False,
        message=f"Something has gone wrong on the server side (URL - {str(request.url)}). Please, try again later.",
        http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )
