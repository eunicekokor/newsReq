import os
from flask import Flask, render_template
from elasticsearch import Elasticsearch, RequestsHttpConnection
import json
from requests_aws4auth import AWS4Auth
YOUR_ACCESS_KEY = os.environ['CONSUMER_KEY']
YOUR_SECRET_KEY = os.environ['CONSUMER_SECRET']

app = Flask(__name__)

REGION = "us-west-2"

awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, "us-east-1", 'es')

host =  os.environ['ES_URL']
port =  os.environ['ES_PORT']

es = Elasticsearch(
  hosts=[{
    'host': host,
    'port': int(port),
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
