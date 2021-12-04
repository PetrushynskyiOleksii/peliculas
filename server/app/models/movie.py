"""This module includes functionality to work with Movies nodes."""

import logging

from neo4j import exceptions

from app import NEO4J_DRIVER
from app.exceptions import DatabaseError, DBNoResultFoundError


GET_SIMILAR_MOVIES = """
MATCH (movie:Movie {external_id: $movie_external_id})
    -[:ACTED_IN|WROTE|DIRECTED|PRODUCED|IN_GENRE|IN_COUNTRY]-(relationships)
    -[:ACTED_IN|WROTE|DIRECTED|PRODUCED|IN_GENRE|IN_COUNTRY]-(recommendations)
WITH recommendations, collect(relationships) AS relationships

RETURN recommendations.external_id as movie_external_id, REDUCE (
    score = 0,
    relationship IN relationships |
    score + CASE
                WHEN 'Country' in labels(relationship) THEN 1
                WHEN 'Actor' in labels(relationship) THEN 1.5
                WHEN 'Writer' in labels(relationship) THEN 2
                WHEN 'Director' in labels(relationship) THEN 2
                WHEN 'ProductionCompany' in labels(relationship) THEN 2
                WHEN 'Genre' in labels(relationship) THEN 3
            END
) as score
ORDER BY score DESC
LIMIT $limit
"""

CREATE_LIKED_RELATIONSHIP = """
    MATCH (movie:Movie {external_id: $movie_external_id})
    WITH movie
    MERGE (user:User {external_id: $user_external_id})
    MERGE (user)-[liked:LIKED]->(movie)
    ON CREATE SET liked.at = timestamp()
    RETURN user.external_id as user_id,
        liked.at as liked_timestamp,
        movie.external_id as movie_id
"""

DELETE_LIKED_RELATIONSHIP = """
    MATCH (user:User)-[liked:LIKED]->(movie:Movie)
    WHERE user.external_id=$user_external_id AND movie.external_id=$movie_external_id
    DELETE liked
"""
GET_COLLABORATIVE_RECOMMENDATIONS = """
    CALL {
        MATCH (user:User {external_id: $user_external_id})-[liked:LIKED]->(recent_liked:Movie)
        RETURN user, recent_liked ORDER BY liked.timestamp DESC LIMIT 10
    }
    MATCH (recent_liked)<-[:LIKED]-(similar_user:User)-[:LIKED]->(recommended_movies:Movie)
    WHERE NOT (user)-[:LIKED]->(recommended_movies)
    WITH SIZE(COLLECT(DISTINCT similar_user)) as similar_user_count, recommended_movies
    RETURN recommended_movies.external_id as movie_external_id
    ORDER BY similar_user_count DESC
    LIMIT $limit
"""


LOGGER = logging.getLogger(__name__)


class Movie:
    """This class includes functionality to work with Movies nodes."""

    driver = NEO4J_DRIVER

    @classmethod
    def create_liked_relationship(cls, user_id, movie_id):
        """Create liked relationship between user and movie."""
        try:
            with cls.driver.session() as session:
                result = session.run(
                    CREATE_LIKED_RELATIONSHIP,
                    user_external_id=user_id,
                    movie_external_id=movie_id
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
            with cls.driver.session() as session:
                session.run(
                    DELETE_LIKED_RELATIONSHIP,
                    user_external_id=user_id,
                    movie_external_id=movie_id
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
            with cls.driver.session() as session:
                result = session.run(
                    GET_COLLABORATIVE_RECOMMENDATIONS,
                    user_external_id=user_id,
                    limit=limit
                )
                recommended_movies = result.data()
                recommended_movies_ids = [movie["movie_external_id"] for movie in recommended_movies]
                return recommended_movies_ids
        except exceptions.Neo4jError as err:
            LOGGER.error(
                "Failed to get collaborative recommendations for user=%s. Error: %s",
                user_id, err
            )
            raise DatabaseError("Failed to get collaborative recommendations")

    @classmethod
    def get_similar_movies(cls, movie_id, limit):
        """Get similar movies to provided movie external id."""
        try:
            with cls.driver.session() as session:
                result = session.run(
                    GET_SIMILAR_MOVIES,
                    movie_external_id=movie_id,
                    limit=limit
                )
                similar_movies = result.data()
                similar_movies_ids = [movie["movie_external_id"] for movie in similar_movies]
                return similar_movies_ids
        except exceptions.Neo4jError as err:
            LOGGER.error(
                "Failed to get similar movies for external_id=%s. Error: %s",
                movie_id, err
            )
            raise DatabaseError("Failed to get similar movies")
