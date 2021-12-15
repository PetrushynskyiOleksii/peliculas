"""This module includes cypher queries."""

GET_MOVIE = """
    MATCH (movie:Movie {external_id: $movie_external_id})
    MATCH (movie)<-[:ACTED_IN]-(actors)
    MATCH (movie)<-[:WROTE]-(writers)
    MATCH (movie)<-[:DIRECTED]-(directors)
    MATCH (movie)<-[:PRODUCED]-(production_companies)
    MATCH (movie)-[:IN_GENRE]->(genres)
    MATCH (movie)-[:IN_COUNTRY]->(countries)

    RETURN 
        movie.external_id as external_id, 
        movie.title as title, 
        collect(distinct actors.name) as actors,
        collect(distinct writers.name) as writers,
        collect(distinct directors.name) as directors,
        collect(distinct production_companies.name) as production_companies,
        collect(distinct genres.name) as genres,
        collect(distinct countries.name) as countries
"""

GET_USER_LIKED_MOVIES = """
    MATCH (:User {external_id: "user-5"})-[:LIKED]->(movie:Movie) 
    RETURN movie.external_id as external_id, movie.title as title
"""

GET_SIMILAR_MOVIES = """
    MATCH (movie:Movie {external_id: $movie_external_id})
        -[:ACTED_IN|WROTE|DIRECTED|PRODUCED|IN_GENRE|IN_COUNTRY]-(relationships)
        -[:ACTED_IN|WROTE|DIRECTED|PRODUCED|IN_GENRE|IN_COUNTRY]-(recommendations)
    WITH recommendations, collect(relationships) AS relationships

    RETURN 
        recommendations.external_id as external_id, 
        recommendations.title as title,
        REDUCE (
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

GET_CONTENT_BASED_RECOMMENDATIONS = """
    CALL {
        MATCH (user:User {external_id: $user_external_id})-[liked:LIKED]->(recent_liked:Movie)
        RETURN user, recent_liked ORDER BY liked.timestamp DESC LIMIT 10
    }
    MATCH (recent_liked)
        -[:ACTED_IN|WROTE|DIRECTED|PRODUCED|IN_GENRE|IN_COUNTRY]-(relationships)
        -[:ACTED_IN|WROTE|DIRECTED|PRODUCED|IN_GENRE|IN_COUNTRY]-(recommendations)
    WHERE NOT (user)-[:LIKED]->(recommendations)
    WITH recommendations, collect(relationships) AS relationships

    RETURN 
        recommendations.external_id as external_id, 
        recommendations.title as title, 
        REDUCE (
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
    RETURN liked.at as liked_timestamp,
        movie.external_id as external_id
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
    RETURN 
        recommended_movies.external_id as external_id,
        recommended_movies.title as title
    ORDER BY similar_user_count DESC
    LIMIT $limit
"""
