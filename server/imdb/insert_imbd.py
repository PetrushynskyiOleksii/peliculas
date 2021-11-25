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

CREATE_RECORDS = """
    CREATE (movie:Movie {title: $movie_title, external_id: $movie_external_id})
    WITH movie
    
    UNWIND split($genres, ", ") as genre_name
    MERGE (genre:Genre {name: genre_name})
    MERGE (movie)-[:IN_GENRE]->(genre)
    WITH movie
    
    UNWIND split($countries, ", ") as country_name
    MERGE (country:Country {name: country_name})
    MERGE (movie)-[:IN_COUNTRY]->(country)
    WITH movie
    
    UNWIND split($directors, ", ") as director_name
    MERGE (director:Director {name: director_name})
    MERGE (director)-[:DIRECTED]->(movie)
    WITH movie
    
    UNWIND split($writers, ", ") as writer_name
    MERGE (writer:Writer {name: writer_name})
    MERGE (writer)-[:WROTE]->(movie)
    WITH movie
    
    UNWIND split($production_companies, ", ") as production_company_name
    MERGE (production_company:ProductionCompany {name: production_company_name})
    MERGE (production_company)-[:PRODUCED]->(movie)
    WITH movie
    
    UNWIND split($actors, ", ") as actor_name
    MERGE (actor:Actor {name: actor_name})
    MERGE (actor)-[:ACTED_IN]->(movie)
"""


def insert_imdb():
    """Create nodes for each entity in imdb csv file."""
    counter = 0
    with open(IMDB_FILEPATH) as imdb_file, NEO4J_DRIVER.session() as session:
        imdb_csv = csv.DictReader(imdb_file)
        for row in imdb_csv:
            title_id = row[IMDB_TITLE_ID_FIELD]
            title = row[IMDB_TITLE_FIELD]
            genres = row[IMDB_GENRE_FIELD].strip() or None
            countries = row[IMDB_COUNTRY_FIELD].strip() or None
            directors = row[IMDB_DIRECTOR_FIELD].strip() or None
            writers = row[IMDB_WRITER_FIELD].strip() or None
            production_companies = row[IMDB_PRODUCTION_COMPANY_FIELD].strip() or None
            actors = row[IMDB_ACTORS_FIELD].strip() or None

            session.run(
                CREATE_RECORDS,
                movie_title=title,
                movie_external_id=title_id,
                genres=genres,
                countries=countries,
                directors=directors,
                writers=writers,
                production_companies=production_companies,
                actors=actors
            )

            counter += 1
            print(f"Processed {counter}", end="\r")


if __name__ == '__main__':
    try:
        insert_imdb()
    except Exception as exc:
        LOGGER.exception("Unhandled error during inserting imbd. Error: ")
