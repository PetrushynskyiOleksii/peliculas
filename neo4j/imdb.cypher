// Create indexes
CREATE INDEX actor_name_index IF NOT EXISTS FOR (n:Actor) ON (n.name);
CREATE INDEX writer_name_index IF NOT EXISTS FOR (n:Writer) ON (n.name);
CREATE INDEX director_name_index IF NOT EXISTS FOR (n:Director) ON (n.name);
CREATE INDEX production_company_name_index IF NOT EXISTS FOR (n:ProductionCompany) ON (n.name);
CREATE INDEX genre_name_index IF NOT EXISTS FOR (n:Genre) ON (n.name);

// Load imdb data
USING PERIODIC COMMIT 100 LOAD CSV WITH HEADERS FROM "file:///imdb.csv" AS row
MERGE (movie:Movie {title: row.title, external_id: row.imdb_title_id})
FOREACH (genre_name IN split(row.genre, ", ") |
  MERGE (genre:Genre {name: genre_name})
  MERGE (movie)-[:IN_GENRE]->(genre))
FOREACH (country_name IN split(row.country, ", ") |
  MERGE (country:Country {name: country_name})
  MERGE (movie)-[:IN_COUNTRY]->(country))
FOREACH (actor_name IN split(row.actors, ", ") |
  MERGE (actor:Actor {name: actor_name})
  MERGE (actor)-[:ACTED_IN]->(movie))
FOREACH (director_name IN split(row.director, ", ") |
  MERGE (director:Director {name: director_name})
  MERGE (director)-[:DIRECTED]->(movie))
FOREACH (writer_name IN split(row.writer, ", ") |
  MERGE (writer:Writer {name: writer_name})
  MERGE (writer)-[:WROTE]->(movie))
FOREACH (production_company_name IN split(row.production_company, ", ") |
  MERGE (production_company:ProductionCompany {name: production_company_name})
  MERGE (production_company)-[:PRODUCED]->(movie));
