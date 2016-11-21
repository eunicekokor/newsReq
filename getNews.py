import requests
import json
import time
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection

apiKey = "8f37248639844a2294dbe1af7c6f3b24"

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

es.indices.create(index='news', ignore=400)
print (es.info())

sources = {
  "business": ["bloomberg", "business-insider","cnbc","financial-times","fortune"],
  "entertainment": ["buzzfeed","daily-mail","entertainment-weekly"],
  "gaming": ["ign", "polygon"],
  "general": ["the-guardian-uk", "the-washington-post", "the-telegraph", "time", "associated-press"],
  "music": ["mtv-news", "mtv-news-uk"],
  "sport": ["bbc-sport", "espn", "nfl-news", "fox-sports"],
  "science-and-nature": ["national-geographic", "new-scientist"],
  "technology": ["techcrunch","wired-de","ars-technica", "engadget", "hacker-news", "recode"]
}

# When we're building up our news db, our request will query each category
# and request articles from each source. Sort by latest, popular, and top
# Example API Request -->

for category in sources.keys():
  source_list = sources[category]
  for source in source_list:
    request_url = "https://newsapi.org/v1/articles?source={source}&apiKey={apiKey}".format(source=source, apiKey=apiKey)
    try:
      resp = requests.get(request_url)
    except:
      time.sleep(10)
      resp = requests.get(request_url)

    json_data = resp.json()
    if json_data.get('articles'):
      article_list = json_data['articles']
      print "Articles for {} in the category of {}".format(source, category)
      for article in article_list:
        article["category"] = str(category)
        article["source"] = str(source)
        #print "{}\n\n".format(article)

        ## add indexing to ES
        try:
          in_db_result = es.search(index='news',doc_type="article",body={
            "query": {
              "match": {
                "title": article['title']
              }
            }
          })
          duplicate = json.dumps(in_db_result['hits']['hits'])
          print("Duplicate", duplicate)
          if(len(duplicate) == 0):
            res = es.index(index="news", doc_type='article', body=article)
            print("Adding to db")
            print "{}\n\n".format(article)
          else:
            print("Skipped adding to db")
        except:
          print("Error adding to db")
          pass


