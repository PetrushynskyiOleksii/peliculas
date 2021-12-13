"""This module is entrypoint of app."""

from http import HTTPStatus

from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from app import APP_CONFIG
from app.api.movie import movies_blueprint
from app.api.index import (
    internal_blueprint,
    handle_404,
    handle_405,
    handle_500,
    validate_body,
)


def create_app():
    """Create the flask application and initialize it."""
    app = Flask(__name__)
    CORS(app)

    swagger_blueprint = get_swaggerui_blueprint("/api/v1/docs", "/static/swagger.yaml")
    app.register_blueprint(swagger_blueprint, url_prefix="/api/v1/docs")

    app.register_blueprint(internal_blueprint, url_prefix="/api/v1")
    app.register_blueprint(movies_blueprint, url_prefix="/api/v1")

    app.register_error_handler(HTTPStatus.NOT_FOUND, handle_404)
    app.register_error_handler(HTTPStatus.METHOD_NOT_ALLOWED, handle_405)
    app.register_error_handler(HTTPStatus.INTERNAL_SERVER_ERROR, handle_500)

    app.config.from_object(APP_CONFIG)

    app.before_request(validate_body)

    return app


if __name__ == '__main__':
    server = create_app()
    server.run(host=APP_CONFIG.SERVER_HOST, port=APP_CONFIG.SERVER_PORT)
