"""This module provides user views."""

from datetime import datetime, timedelta
from http import HTTPStatus

from flask import Blueprint, request, g

from app import constants
from app.exceptions import DatabaseError
from app.models.movie import Movie
from app.utils.auth import auth_required
from app.utils.response import make_response


movie_blueprint = Blueprint('pl-movie', __name__)


@movie_blueprint.route("/movie/<movie_id>/like",  methods=("POST", ))
@auth_required
def handle_movie_like(movie_id):
    """Create like for provided movie and user."""
    try:
        result = Movie.create_liked_relationship(g.user_id, movie_id)
    except DatabaseError as err:
        return make_response(
            success=False,
            message=str(err),
            http_status=HTTPStatus.BAD_REQUEST
        )

    return make_response(success=True, data=result, http_status=HTTPStatus.CREATED)


@movie_blueprint.route("/movie/<movie_id>/like", methods=("DELETE", ))
@auth_required
def handle_movie_dislike(movie_id):
    """Delete like for provided movie and user."""
    try:
        Movie.delete_liked_relationship(g.user_id, movie_id)
    except DatabaseError as err:
        return make_response(
            success=False,
            message=str(err),
            http_status=HTTPStatus.BAD_REQUEST
        )

    return make_response(success=True, http_status=HTTPStatus.NO_CONTENT)


@movie_blueprint.route("/movie/<movie_id>/similar", methods=("GET", ))
def handle_movie_similar(movie_id):
    """Return list of similar movies to provided movie_id."""


@movie_blueprint.route("/movies/most_rated", methods=("GET", ))
def handle_movie_most_rated(movie_id):
    """Create like for provided movie and user."""