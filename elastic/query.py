from elasticsearch import Elasticsearch

def indexquery(query_json,index='autosuggest', size=10):
    '''
    backend implementation of esquery for autosuggest
    query_json: elastic search json.
    '''
    es = Elasticsearch(["localhost:9200"], timeout=60, retry_on_timeout=True)
    query_string_query = query_json
    result = es.search(index=index, body=query_string_query,size=size)
    return result

def elasticquery(query,index):
    # default query
    query_json = \
    {'query': {
        "bool": {
            "should": [
                # fuzzy match
                {
                "match": {
                    "NAME": {
                        "query": query,
                        "fuzziness": "AUTO:0,3",
                        "prefix_length" : 0,
                        "max_expansions": 50,
                        "boost": 1,
                        "operator": "or",
                        }
                    }
                },
                # exact match boost for general name query
                {
                "match": {
                    "NAME": {
                        "query": query,
                        "fuzziness": 0,
                        "boost": 2,
                    }
                    }
                },
                # exact match boost for exact phrase query match
                {
                "match_phrase": {
                    "NAMEEXACT": {
                        "query": query,
                        "boost": 3,
                    }
                    }
                },
        ]
        }
    },
        "sort": {"_score": {"order": "desc"}}
    }

    result = {'result': indexquery(query_json,index=index,size=500)['hits']['hits']} # list of results line by line in "_source"

    return result


if __name__ == "__main__":
    print(elasticquery("Abdominal","sample"))
