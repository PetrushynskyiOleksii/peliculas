"""This module includes functionality to work with Movies nodes."""

import logging

from neo4j import exceptions
from elasticsearch import ElasticsearchException

from app import NEO4J_DRIVER, APP_CONFIG
from app.es import ElasticSearchDriver
from app.exceptions import DatabaseError, DBNoResultFoundError
from app.utils.cypher_queries import (
    GET_MOVIE,
    GET_SIMILAR_MOVIES,
    GET_USER_LIKED_MOVIES,
    GET_CONTENT_BASED_RECOMMENDATIONS,
    GET_COLLABORATIVE_RECOMMENDATIONS,
    CREATE_LIKED_RELATIONSHIP,
    DELETE_LIKED_RELATIONSHIP,
)
from app.constants import (
    DESCRIPTION_FIELD,
    TITLE_FIELD,
    ORIGINAL_TITLE_FIELD,
    EXTERNAL_ID_FIELD,
)

LOGGER = logging.getLogger(__name__)


class Movie:
    """This class includes functionality to work with Movies nodes."""

    neo4j_driver = NEO4J_DRIVER
    es_driver = ElasticSearchDriver

    @classmethod
    def create_liked_relationship(cls, user_id, movie_id):
        """Create liked relationship between user and movie."""
        try:
            with cls.neo4j_driver.session() as session:
                result = session.run(
                    CREATE_LIKED_RELATIONSHIP,
                    user_external_id=user_id,
                    movie_external_id=movie_id,
                ).data()
        except exceptions.Neo4jError as err:
            LOGGER.error(
                "Failed to create liked relationship between user=%s and movie=%s. Error: %s",
                user_id, movie_id, err
            )
            raise DatabaseError("Failed to create liked relationship")

        if not result:
            raise DBNoResultFoundError(f"The movie does not exist: external_id={movie_id}")

        return result

    @classmethod
    def delete_liked_relationship(cls, user_id, movie_id):
        """Delete liked relationship between user and movie."""
        try:
            with cls.neo4j_driver.session() as session:
                session.run(
                    DELETE_LIKED_RELATIONSHIP,
                    user_external_id=user_id,
                    movie_external_id=movie_id,
                )
        except exceptions.Neo4jError as err:
            LOGGER.error(
                "Failed to delete liked relationship between user=%s and movie=%s. Error: %s",
                user_id, movie_id, err
            )
            raise DatabaseError("Failed to delete liked relationship")

    @classmethod
    def get_collaborative_recommendations(cls, user_id, limit):
        """Get movies recommendations based on collaborative filtering."""
        try:
            with cls.neo4j_driver.session() as session:
                return session.run(
                    GET_COLLABORATIVE_RECOMMENDATIONS,
                    user_external_id=user_id,
                    limit=limit,
                ).data()
        except exceptions.Neo4jError as err:
            LOGGER.error(
                "Failed to get collaborative recommendations for user=%s. Error: %s",
                user_id, err
            )
            raise DatabaseError("Failed to get collaborative recommendations")

    @classmethod
    def get_content_based_recommendations(cls, user_id, limit):
        """Get content-based movies recommendations."""
        try:
            with cls.neo4j_driver.session() as session:
                return session.run(
                    GET_CONTENT_BASED_RECOMMENDATIONS,
                    user_external_id=user_id,
                    limit=limit,
                ).data()
        except exceptions.Neo4jError as err:
            LOGGER.error(
                "Failed to get content-based recommendations for user=%s. Error: %s",
                user_id, err
            )
            raise DatabaseError("Failed to get content-based recommendations")

    @classmethod
    def get_similar_movies(cls, movie_id, limit):
        """Get similar movies to provided movie external id."""
        try:
            with cls.neo4j_driver.session() as session:
                return session.run(
                    GET_SIMILAR_MOVIES,
                    movie_external_id=movie_id,
                    limit=limit
                ).data()
        except exceptions.Neo4jError as err:
            LOGGER.error(
                "Failed to get similar movies for external_id=%s. Error: %s",
                movie_id, err
            )
            raise DatabaseError("Failed to get similar movies")

    @classmethod
    def get_movie(cls, movie_id):
        """Return movie by provided movie external id."""
        try:
            with cls.neo4j_driver.session() as session:
                movie = session.run(
                    GET_MOVIE,
                    movie_external_id=movie_id,
                ).single().data()

                return movie
        except exceptions.Neo4jError as err:
            LOGGER.error(
                "Failed to get movie by external_id=%s. Error: %s",
                movie_id, err
            )
            raise DatabaseError("Failed to get movie by external id")

    @classmethod
    def get_user_liked_movies(cls, user_id):
        """Get liked movies for provided user."""
        try:
            with cls.neo4j_driver.session() as session:
                return session.run(
                    GET_USER_LIKED_MOVIES,
                    user_external_id=user_id,
                ).data()
        except exceptions.Neo4jError as err:
            LOGGER.error(
                "Failed to get liked movies for user=%s. Error: %s",
                user_id, err
            )
            raise DatabaseError("Failed to get user liked movies")

    @classmethod
    def search_movies(cls, query, limit):
        """Get movies from elastic search by provided query."""
        try:
            query = cls.es_driver.format_multi_match_query(
                query=query,
                fields=(TITLE_FIELD, DESCRIPTION_FIELD),
                projection=(EXTERNAL_ID_FIELD, ORIGINAL_TITLE_FIELD),
            )
            movies = cls.es_driver.search(
                query=query,
                index=APP_CONFIG.ES_DATABASE_MOVIE_INDEX,
                limit=limit
            )
        except ElasticsearchException as err:
            LOGGER.error(
                "Failed to search movies by query=%s from es. Error: %s",
                query, err
            )
            raise DatabaseError("Failed to search movies by query")

        return movies
