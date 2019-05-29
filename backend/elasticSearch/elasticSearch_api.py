from ontologyAPI.ontology_api import get_all_persons
from elasticsearch import Elasticsearch

import json


def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Connected to Elasticsearch')
    else:
        print('Awww it could not connect!')
    return _es


def create_person_index():
    settings = {
        # "settings": {
        #     "number_of_shards": 1,
        #     "number_of_replicas": 0,
        #     "analysis": {
        #         "filter": {
        #             "edge_ngram_filter": {
        #                 "type": "edge_ngram",
        #                 "min_gram": 1,
        #                 "max_gram": 10
        #             }
        #         },
        #         "analyzer": {
        #             "edge_ngram_analyzer": {
        #                 "type": "custom",
        #                 "tokenizer": "standard",
        #                 "filter": [
        #                     "lowercase",
        #                     "edge_ngram_filter"
        #                 ]
        #             }
        #         }
        #     }
        # },
        "settings": {
            "analysis": {
                "analyzer": {
                    "autocomplete": {
                        "tokenizer": "autocomplete",
                        "filter": [
                            "lowercase"
                        ]
                        },
                        "autocomplete_search": {
                            "tokenizer": "lowercase"
                        }
                },
                "tokenizer": {
                    "autocomplete": {
                        "type": "edge_ngram",
                        "min_gram": 1,
                        "max_gram": 10,
                        "token_chars": [
                            "letter"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "person": {
                "dynamic": "strict",
                "properties": {
                    "uri": {
                        "type": "text"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "autocomplete",
                        "search_analyzer": "autocomplete_search"
                        # "index_analyzer": "edge_ngram_analyzer",
                        # "search_analyzer": "standard"
                    }
                }
            }
        }
    }
    # Ignore 400 means to ignore "Index Already Exist" error.
    es.indices.create(index='artontology', ignore=400, body=settings)

def store_all_persons():
    print('Storing all persons in Elasticsearch index ...')
    all_persons = get_all_persons()
    for person in all_persons:
        uri, name = person
        doc = {'uri': uri, 'name': name}
        es.index(index='artontology', doc_type='person', body=doc)
    print("Finished Elasticsearch storing")


def search_persons(name):
    query = { "query": { "match": { "name": { "query": name, "fuzziness": 2, "operator": "and" }}}}
    # regexp = {'_source': ['uri', 'name'], 'query': { 'regexp': { 'name': '*?('+name+').*' }}}
    # fuzzy = {'_source': ['uri', 'name'], 'query': { 'fuzzy': { 'name': { "value": name }}}}
    res = es.search(index='artontology', body=query)
    return res


def clean_index():
    es.indices.delete(index='*')
    create_person_index()
    store_all_persons()

es = connect_elasticsearch()
# clean_index()