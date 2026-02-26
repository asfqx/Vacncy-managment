from elasticsearch import Elasticsearch
from app.core import settings

elastic_search = Elasticsearch(settings.elastic_url)
