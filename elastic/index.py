from elasticsearch import Elasticsearch
from elasticsearch import helpers
from csv import DictReader as DR

# initialize Elasticsearch object to running docker container
es = Elasticsearch(["localhost:9200"], timeout=60, retry_on_timeout=True)
# add stopwords for filtering
stopwords=["a","an","and","are","as","at","be","but","by","for","if","in","into","is","it","no","not","of","on","or","such","that","the","their","then","there","these","they","this","to","was","will","with","syndrome","syndromes","disorder","disorders","disease","diseases"]
# necessary settings for search and filtering for lucene indexing, see Elasticsearch documentation for explanation
es_settings={
            "analysis": {
                "filter": { 
                    "english_poss_stemmer": {
                        "type": "stemmer",
                        "name": "possessive_english"
                        },
                        "ngramfilter": {
                        "type": "edge_ngram",
                        "min_gram": 3,
                        "max_gram": 20,
                        "token_chars": ["letter","digit", "whitespace"]
                        }
                    },
                "analyzer": {
                    "ngram_analyzer": {
                        "filter": ["lowercase","english_poss_stemmer","ngramfilter"],
                        "tokenizer": "standard"
                        },
                    "stop_analyzer": {
                        "type": "stop",
                        "stopwords": stopwords,
                        "filter": ["lowercase","ngramfilter"],
                        "tokenizer": "standard"
                        },
                    "normal_analyzer": {
                        "filter": ["lowercase","ngramfilter"],
                        "tokenizer": "standard"
                        }
                    }
                }
            }
search_settings={
                    "type": "text",
                    "analyzer": "ngram_analyzer",
                    "search_analyzer": "stop_analyzer"
}
exact_settings={
                    "type": "text",
                    "analyzer": "normal_analyzer",
                    "search_analyzer": "normal_analyzer"
}
# sets up the index function for parsing the sampledb file and adding to elasticsearch index
def index_sample(INDEX_NAME='sample',path_to_db='sampledb.txt'):
    request_body = {
        "settings": es_settings,
        "mappings": {
            "properties": {
                "ID": {
                    "type": "text"
                },
                "NAME": search_settings, # mesh term name/string
                "NAMEEXACT": exact_settings # mesh term name/string
            }
        }
    }
    if es is not None:
            es.indices.delete(index=INDEX_NAME, ignore=404)
            es.indices.create(index=INDEX_NAME, body=request_body)
            es_data = []
            with open(path_to_db, "r") as ftxt:
                dictfile = DR(ftxt, dialect='excel-tab')
                """
                DescriptorUI    DescriptorName
                """
                for row in dictfile:
                    data = {}
                    data['ID'] = row['DescriptorUI']
                    data['NAME'] = row['DescriptorName']
                    data['NAMEEXACT'] = row['DescriptorName']
                    action = {"_index": INDEX_NAME, '_source': data}
                    es_data.append(action)
                    if len(es_data) > 1000:
                        helpers.bulk(es, es_data, stats_only=False)
                        es_data = []
                if len(es_data) > 0:
                    helpers.bulk(es, es_data, stats_only=False)

if __name__ == "__main__":
    index_sample()
