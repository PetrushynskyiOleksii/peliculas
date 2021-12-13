"""This module includes functionality to work with ES."""


from app import ES_DRIVER


QUERY_FIELD = "query"
MULTI_MATCH_FIELD = "multi_match"
FIELDS_FIELD = "fields"
SOURCE_FIELD = "_source"
HITS_FIELD = "hits"


class ElasticSearchDriver:
    """Clas to work with elastic search."""

    driver = ES_DRIVER

    @staticmethod
    def format_response(result):
        """Return formatted response"""
        return [movie[SOURCE_FIELD] for movie in result[HITS_FIELD][HITS_FIELD]]

    @staticmethod
    def format_multi_match_query(query, fields, projection=None):
        """Return formatted multi match query."""
        query = {
            QUERY_FIELD: {
                MULTI_MATCH_FIELD: {
                    QUERY_FIELD: query,
                    FIELDS_FIELD: fields,
                }
            }
        }

        if projection:
            query[SOURCE_FIELD] = projection

        return query

    @classmethod
    def search(cls, query, index, limit):
        """Get search results and format response."""
        result = cls.driver.search(body=query, index=index, size=limit)
        return cls.format_response(result)
