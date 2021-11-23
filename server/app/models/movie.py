"""This module includes functionality to work with Movies nodes."""

import logging

from neo4j import exceptions

from app import NEO4J_DRIVER
from app.exceptions import DatabaseError

CREATE_LIKED_RELATIONSHIP = """
    MERGE (user:User {external_id: $user_external_id})
    MERGE (movie:Movie {external_id: $movie_external_id})
    MERGE (user)-[liked_rel:LIKED]->(movie)
    ON CREATE SET liked_rel.at = timestamp()
    RETURN user.external_id as user_id, 
        liked_rel.at as liked_timestamp, 
        movie.external_id as movie_id
"""

DELETE_LIKED_RELATIONSHIP = """
    MATCH (user:User)-[liked_rel:LIKED]->(movie:Movie)
    WHERE user.external_id=$user_external_id AND movie.external_id=$movie_external_id
    DELETE liked_rel
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
                )
                return result.data()
        except exceptions.Neo4jError as err:
            LOGGER.error(
                "Failed to create liked relationship between user=%s and movie=%s. Error: %s",
                user_id, movie_id, err
            )
            raise DatabaseError("Failed to create liked relationship")

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
