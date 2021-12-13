"""This module provides search views."""

from http import HTTPStatus

from flask import Blueprint, request

from app.exceptions import DatabaseError
from app.models.movie import Movie
from app.utils.response import make_response


search_blueprint = Blueprint("pl-search", __name__)


@search_blueprint.route("/search/movies", methods=("GET", ))
def handle_movie_search():
    """Return results from elastic search by provided query."""
    limit = request.args.get("limit", type=int, default=10)
    query = request.args.get("query", type=str, default=None)

    if not query:
        return make_response(
            success=False,
            message="Required field query is not provided in the query params.",
            http_status=HTTPStatus.NOT_FOUND
        )

    try:
        movies = Movie.search_movies(query, limit=limit)
    except DatabaseError as err:
        return make_response(
            success=False,
            message=str(err),
            http_status=HTTPStatus.BAD_REQUEST
        )

    return make_response(success=True, data=movies, http_status=HTTPStatus.OK)

