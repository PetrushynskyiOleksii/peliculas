"""Base API configuration."""

import os


class BaseConfig:
    """Base configuration includes shared variables."""

    SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
    SERVER_PORT = os.getenv("SERVER_PORT", 5555)

    # Neo4j
    NEO4J_DATABASE_HOST = os.getenv("NEO4J_DATABASE_HOST", "localhost")
    NEO4J_DATABASE_PORT = os.getenv("NEO4J_DATABASE_PORT", "7687")
    NEO4J_DATABASE_USER = os.getenv("NEO4J_DATABASE_USER", "peliculas")
    NEO4J_DATABASE_PASSWORD = os.getenv("NEO4J_DATABASE_PASSWORD", "peliculas")
    NEO4J_DATABASE_URI = f"neo4j://{NEO4J_DATABASE_HOST}:{NEO4J_DATABASE_PORT}"
    NEO4j_DATABASE_SIZE = 100

    # ElasticSearch
    ES_DATABASE_MOVIE_INDEX = "movie-index"
    ES_DATABASE_HOST = os.getenv("ES_DATABASE_HOST", "localhost")
    ES_DATABASE_PORT = os.getenv("ES_DATABASE_PORT", 9200)
    ES_DATABASE_USER = os.getenv("ES_DATABASE_USER", "peliculas")
    ES_DATABASE_PASS = os.getenv("ES_DATABASE_PASS", "peliculas")
    ES_DATABASE_SIZE = 100

    # JWT
    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


class ProductionConfig(BaseConfig):
    """Production config includes variables for prod env."""

    # Neo4j
    NEO4j_DATABASE_SIZE = 100

    # ElasticSearch
    ES_DATABASE_SIZE = 100


class StagingConfig(BaseConfig):
    """Staging config includes variables for staging env."""

    # Neo4j
    NEO4j_DATABASE_SIZE = 25

    # ElasticSearch
    ES_DATABASE_SIZE = 25


class DevelopmentConfig(BaseConfig):
    """Develop config includes variables for develop env."""

    # Neo4j
    NEO4j_DATABASE_SIZE = 5

    # ElasticSearch
    ES_DATABASE_SIZE = 5


class TestingConfig(BaseConfig):
    """Testing config includes variables for testing env."""

    # Neo4j
    NEO4j_DATABASE_SIZE = 1

    # ElasticSearch
    ES_DATABASE_SIZE = 1
