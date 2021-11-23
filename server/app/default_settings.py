"""Base API configuration."""

import os


class BaseConfig:
    """Base configuration includes shared variables."""
    SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
    SERVER_PORT = os.getenv("SERVER_PORT", 5555)

    # Database
    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT", "7687")
    DATABASE_USER = os.getenv("DATABASE_USER", "peliculas")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "peliculas")
    DATABASE_URI = f"neo4j://{DATABASE_HOST}:{DATABASE_PORT}"

    # JWT
    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


class ProductionConfig(BaseConfig):
    """Production config includes variables for prod env."""
    pass


class StagingConfig(BaseConfig):
    """Staging config includes variables for staging env."""
    pass


class DevelopmentConfig(BaseConfig):
    """Develop config includes variables for develop env."""
    pass


class TestingConfig(BaseConfig):
    """Testing config includes variables for testing env."""
    pass
