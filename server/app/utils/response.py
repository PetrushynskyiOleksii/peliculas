"""This module provides response utility."""

from flask import jsonify


def make_response(success, http_status, data=None, message=None):
    """Return formatted json response."""
    json_result = jsonify({"success": success, "message": message, "data": data})
    return json_result, http_status
