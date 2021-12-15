"""This module provides movies views."""

from http import HTTPStatus

from flask import Blueprint, request, g

from app.exceptions import DatabaseError, DBNoResultFoundError
from app.models.movie import Movie
from app.utils.auth import auth_required
from app.utils.response import make_response


movies_blueprint = Blueprint("pl-movies", __name__)


@movies_blueprint.route("user/movies", methods=("GET",))
@auth_required
def handle_user_liked_movies():
    """Return movies liked by user."""
    try:
        liked_movies = Movie.get_user_liked_movies(g.user_id)
    except DatabaseError as err:
        return make_response(
            success=False,
            message=str(err),
            http_status=HTTPStatus.BAD_REQUEST
        )

    return make_response(success=True, data=liked_movies, http_status=HTTPStatus.OK)


@movies_blueprint.route("/movies", methods=("GET",))
def handle_movies_search():
    """Return results from elastic search by provided query."""
    limit = request.args.get("limit", type=int, default=10)
    query = request.args.get("query", type=str, default=None)

    if not query:
        return make_response(
            success=False,
            message="Required field query is not provided in the query params.",
            http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
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


@movies_blueprint.route("/movies/<movie_id>", methods=("GET",))
def handle_get_movie(movie_id):
    """Return movie data by provided movie external id."""
    try:
        movie = Movie.get_movie(movie_id)
    except DatabaseError as err:
        return make_response(
            success=False,
            message=str(err),
            http_status=HTTPStatus.BAD_REQUEST
        )

    return make_response(success=True, data=movie, http_status=HTTPStatus.OK)


@movies_blueprint.route("/movies/<movie_id>/like", methods=("POST",))
@auth_required
def handle_movie_like(movie_id):
    """Create like for provided movie and user."""
    try:
        result = Movie.create_liked_relationship(g.user_id, movie_id)
    except (DatabaseError, DBNoResultFoundError) as err:
        return make_response(
            success=False,
            message=str(err),
            http_status=HTTPStatus.BAD_REQUEST
        )

    return make_response(success=True, data=result, http_status=HTTPStatus.CREATED)


@movies_blueprint.route("/movies/<movie_id>/like", methods=("DELETE",))
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


@movies_blueprint.route("/movies/<movie_id>/similar", methods=("GET",))
def handle_movie_similar(movie_id):
    """Return list of similar movies to provided movie_id."""
    limit = request.args.get("limit", type=int, default=10)

    try:
        movies = Movie.get_similar_movies(movie_id, limit=limit)
    except DatabaseError as err:
        return make_response(
            success=False,
            message=str(err),
            http_status=HTTPStatus.BAD_REQUEST
        )

    return make_response(success=True, data=movies, http_status=HTTPStatus.OK)


@movies_blueprint.route("movies/recommendations/collaborative", methods=("GET",))
@auth_required
def handle_collaborative_recommendations():
    """Return collaborative recommendations for provided user."""
    limit = request.args.get("limit", type=int, default=10)

    try:
        movies = Movie.get_collaborative_recommendations(g.user_id, limit=limit)
    except DatabaseError as err:
        return make_response(
            success=False,
            message=str(err),
            http_status=HTTPStatus.BAD_REQUEST
        )

    return make_response(success=True, data=movies, http_status=HTTPStatus.OK)


@movies_blueprint.route("/movies/recommendations/content-based", methods=("GET",))
@auth_required
def handle_content_based_recommendations():
    """Return content-based recommendations for provided user."""
    limit = request.args.get("limit", type=int, default=10)

    try:
        movies = Movie.get_content_based_recommendations(g.user_id, limit=limit)
    except DatabaseError as err:
        return make_response(
            success=False,
            message=str(err),
            http_status=HTTPStatus.BAD_REQUEST
        )

    return make_response(success=True, data=movies, http_status=HTTPStatus.OK)
