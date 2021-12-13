"""This module contains base initializers required for server."""

import os

from neo4j import GraphDatabase
from elasticsearch import Elasticsearch

from app import constants, default_settings


APP_MODE = os.environ.get("APP_MODE", constants.DEVELOP_KEY)
APP_CONFIG_NAME = "{}Config".format(APP_MODE.capitalize())
APP_CONFIG = getattr(default_settings, APP_CONFIG_NAME)

NEO4J_DRIVER = GraphDatabase.driver(
    APP_CONFIG.DATABASE_URI,
    auth=(APP_CONFIG.DATABASE_USER, APP_CONFIG.DATABASE_PASSWORD)
)
ES_DRIVER = Elasticsearch(
    [APP_CONFIG.ES_DATABASE_HOST],
    http_auth=(APP_CONFIG.ES_DATABASE_USER, APP_CONFIG.ES_DATABASE_PASS),
    port=APP_CONFIG.ES_DATABASE_PORT,
)
