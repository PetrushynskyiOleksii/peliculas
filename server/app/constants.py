"""THis module contains server app constants."""

import os

APP_NAME = "peliculas"

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(APP_DIR, os.pardir))
STATIC_DIR = os.path.join(ROOT_DIR, "static")
IMDB_DIR = os.path.join(ROOT_DIR, "imdb")

PRODUCTION_KEY = "production"
STAGING_KEY = "staging"
DEVELOP_KEY = "development"
TESTING_KEY = "testing"

DATE_FORMAT = "%Y.%m.%d"
DATETIME_FORMAT = "%Y.%m.%d %H:%M:%S"

# Database fields
EXTERNAL_ID_FIELD = "external_id"
DESCRIPTION_FIELD = "description"
ORIGINAL_TITLE_FIELD = "original_title"
TITLE_FIELD = "title"
