"""This module includes script for populating database with imdb data."""

import csv
import logging

from neo4j import GraphDatabase

from app import constants, APP_CONFIG


LOGGER = logging.getLogger(__name__)
NEO4J_DRIVER = GraphDatabase.driver(
    APP_CONFIG.DATABASE_URI,
    auth=(APP_CONFIG.DATABASE_USER, APP_CONFIG.DATABASE_PASSWORD)
)

IMDB_FILEPATH = f"{constants.IMDB_DIR}/imdb.csv"
IMDB_TITLE_ID_FIELD = "imdb_title_id"
IMDB_TITLE_FIELD = "title"
IMDB_GENRE_FIELD = "genre"
IMDB_COUNTRY_FIELD = "country"
IMDB_DIRECTOR_FIELD = "director"
IMDB_WRITER_FIELD = "writer"
IMDB_PRODUCTION_COMPANY_FIELD = "production_company"
IMDB_ACTORS_FIELD = "actors"

CREATE_MOVIE = "MERGE (:Movie {title: $movie_title, external_id: $movie_external_id})"
CREATE_MOVIE_GENRE = """
    MATCH (movie:Movie {external_id: $movie_external_id})
    MERGE (genre:Genre {name: $genre_name})
    MERGE (movie)-[:IN_GENRE]->(genre)
"""
CREATE_MOVIE_COUNTRY = """
    MATCH (movie:Movie {external_id: $movie_external_id})
    MERGE (country:Country {name: $country_name})
    MERGE (movie)-[:IN_COUNTRY]->(country)
"""
CREATE_MOVIE_DIRECTOR = """
    MATCH (movie:Movie {external_id: $movie_external_id})
    MERGE (director:Director {name: $director_name})
    MERGE (director)-[:DIRECTED]->(movie)
"""
CREATE_MOVIE_WRITER = """
    MATCH (movie:Movie {external_id: $movie_external_id})
    MERGE (writer:Writer {name: $writer_name})
    MERGE (writer)-[:WROTE]->(movie)
"""
CREATE_MOVIE_PRODUCTION_COMPANY = """
    MATCH (movie:Movie {external_id: $movie_external_id})
    MERGE (production_company:ProductionCompany {name: $production_company_name})
    MERGE (production_company)-[:PRODUCED]->(movie)
"""
CREATE_MOVIE_ACTOR = """
    MATCH (movie:Movie {external_id: $movie_external_id})
    MERGE (actor:Actor {name: $actor_name})
    MERGE (actor)-[:ACTED_IN]->(movie)
"""


def insert_imdb():
    """Create nodes for each entity in imdb csv file."""
    counter = 0
    with open(IMDB_FILEPATH) as imdb_file:
        imdb_csv = csv.DictReader(imdb_file)
        for row in imdb_csv:
            with NEO4J_DRIVER.session() as session:
                title_id = row[IMDB_TITLE_ID_FIELD]
                title = row[IMDB_TITLE_FIELD]
                session.run(CREATE_MOVIE, movie_external_id=title_id, movie_title=title)

                genres = row[IMDB_GENRE_FIELD].strip()
                if genres:
                    for genre in genres.split(", "):
                        session.run(CREATE_MOVIE_GENRE, movie_external_id=title_id, genre_name=genre)

                countries = row[IMDB_COUNTRY_FIELD].strip()
                if countries:
                    for country in countries.split(", "):
                        session.run(CREATE_MOVIE_COUNTRY,  movie_external_id=title_id, country_name=country)

                directors = row[IMDB_DIRECTOR_FIELD].strip()
                if directors:
                    for director in directors.split(", "):
                        session.run(CREATE_MOVIE_DIRECTOR, movie_external_id=title_id, director_name=director)

                writers = row[IMDB_WRITER_FIELD].strip()
                if writers:
                    for writer in writers.split(", "):
                        session.run(CREATE_MOVIE_WRITER, movie_external_id=title_id, writer_name=writer)

                production_companies = row[IMDB_PRODUCTION_COMPANY_FIELD].strip()
                if production_companies:
                    for production_company in production_companies.split(", "):
                        session.run(
                            CREATE_MOVIE_PRODUCTION_COMPANY,
                            movie_external_id=title_id,
                            production_company_name=production_company
                        )

                actors = row[IMDB_ACTORS_FIELD].strip()
                if actors:
                    for actor in actors.split(", "):
                        session.run(CREATE_MOVIE_ACTOR, movie_external_id=title_id, actor_name=actor)

                counter += 1
                print(f"Processed {counter}", end="\r")


if __name__ == '__main__':
    try:
        insert_imdb()
    except Exception as exc:
        LOGGER.exception("Unhandled error during inserting imbd. Error: ")
