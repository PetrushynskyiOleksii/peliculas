"""This module includes functionally for populating elasticsearch database."""

import csv
import logging

from elasticsearch.helpers import bulk

from app import ES_DRIVER

LOGGER = logging.getLogger(__name__)


IMDB_TITLE_ID_FIELD = "imdb_title_id"
IMDB_TITLE_FIELD = "title"
IMDB_ORIGINAL_TITLE_FIELD = "original_title"
IMDB_DESCRIPTION_FIELD = "description"
IMDB_DIRECTOR_FIELD = "director"
IMDB_WRITER_FIELD = "writer"
IMDB_ACTORS_FIELD = "actors"
IMDB_PRODUCTION_COMPANY_FIELD = "production_company"

ES_EXTERNAL_ID_FIELD = "external_id"
ES_TITLE_FIELD = "title"
ES_ORIGINAL_TITLE_FIELD = "original_title"
ES_DESCRIPTION_FIELD = "description"

MOVIE_INDEX_NAME = "movie-index"

ES_MAX_INSERT_COUNT = 1000


def es_create_movie_index():
    """Create movie index in elasticsearch."""
    index_configs = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "description_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "stemmer", "stop"],
                        "stopwords": "_english_",
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "description": {"type": "text", "analyzer": "description_analyzer"},
                "stuff": {"type": "text"},
            }
        },
    }
    ES_DRIVER.indices.create(index="movie_index", ignore=400, body=index_configs)


def es_create_stuff_index():
    """Create movie index in elasticsearch."""
    index_configs = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "description_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "stemmer", "stop"],
                        "stopwords": "_english_",
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "external_id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "simple"},
                "original_title": {"type": "keyword"},
                "description": {"type": "text", "analyzer": "description_analyzer"},
            }
        },
    }
    ES_DRIVER.indices.create(index=MOVIE_INDEX_NAME, ignore=400, body=index_configs)


def es_insert_movies():
    """Insert imdb records into elasticsearch."""
    es_docs_count = 0
    es_docs = []
    with open("imdb.csv") as file:
        csv_reader = csv.DictReader(file)
        for line in csv_reader:
            external_id = line[IMDB_TITLE_ID_FIELD]
            title = line[IMDB_TITLE_FIELD]
            description = line[IMDB_DESCRIPTION_FIELD]

            stuff = set()
            directors = line[IMDB_DIRECTOR_FIELD].strip()
            if directors:
                stuff.update(directors.split(", "))

            writer = line[IMDB_WRITER_FIELD]
            if writer:
                stuff.update(writer.split(", "))

            actors = line[IMDB_ACTORS_FIELD]
            if actors:
                stuff.update(actors.split(", "))

            production_company = line[IMDB_PRODUCTION_COMPANY_FIELD]
            if production_company:
                stuff.update(production_company.split(", "))

            es_docs.append({
                ES_EXTERNAL_ID_FIELD: external_id,
                ES_TITLE_FIELD: title,
                ES_DESCRIPTION_FIELD: description,
                ES_ORIGINAL_TITLE_FIELD: title,
            })
            es_docs_count += 1

            if es_docs_count > ES_MAX_INSERT_COUNT:
                bulk(ES_DRIVER, es_docs, index=MOVIE_INDEX_NAME)
                es_docs = []
                es_docs_count = 0

        bulk(ES_DRIVER, es_docs, index=MOVIE_INDEX_NAME)


if __name__ == "__main__":
    try:
        es_create_movie_index()
        es_insert_movies()
    except Exception as exc:
        LOGGER.exception("Failed to insert records to es: ")
    else:
        LOGGER.info("ES was successfully populated.")
