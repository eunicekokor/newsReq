from flask import Flask, render_template
from elasticsearch import Elasticsearch, RequestsHttpConnection
import json
import pprint
import sys
from datetime import *
import time
import certifi
from requests_aws4auth import AWS4Auth

app = Flask(__name__)


YOUR_ACCESS_KEY = "AKIAIFXS6NMDG6DNTGNQ"
YOUR_SECRET_KEY = "lwVBol6OuS32W4DA+kasw5Qv8W5HfrKFCMC9g01W"
REGION = "us-west-2"

awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, REGION, 'es')

host = 'search-news-req-rdi65wkzrj6inpmxnjhftkl5fi.us-west-2.es.amazonaws.com'

es = Elasticsearch(
  hosts=[{
    'host': host,
    'port': 443,
  }],
  http_auth=awsauth,
  use_ssl=True,
  verify_certs=True,
  connection_class=RequestsHttpConnection
  )

# @app.route('/')
# def index():
#     return render_template('index.html')


@app.route('/')
def hello_world():
	result = es.search(index='news',doc_type="article",body={
		"query": { "match_all": {} },
		"sort": { "publishedAt": { "order": "desc" } 
		}
	})
	data = json.dumps(result['hits']['hits'])
	return data


if __name__ == '__main__':
    app.debug = True
    app.run(port=8000)
