import os
import requests
import json
import time
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
import sys

REGION = "us-west-2"

YOUR_ACCESS_KEY = os.environ['CONSUMER_KEY']
YOUR_SECRET_KEY = os.environ['CONSUMER_SECRET']

awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, "us-east-1", 'es')

host = os.environ['ES_URL']
port = os.environ['ES_PORT']

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

# es.indices.delete(index='news', ignore=[400, 404])
# time.sleep(10)

# es.indices.create(index='news', ignore=400)
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

def fetchArticles(sources):
  count = 0
  for category in sources.keys():
    source_list = sources[category]
    for source in source_list:
      request_url = "https://newsapi.org/v1/articles?source={source}&apiKey={apiKey}".format(source=source, apiKey=APIKEY)
      try:
        resp = requests.get(request_url)
      except:
        time.sleep(10)
        resp = requests.get(request_url)

      json_data = resp.json()
      if json_data.get('articles'):
        article_list = json_data['articles']
        no_articles = len(article_list)
        print("Number of Articles", no_articles, "total", count)
        count += no_articles
        print ("Articles for {} in the category of {}".format(source, category))
        for article in article_list:
          for v in article.keys():
            if article[v]:
              article[v] = article[v].encode('ascii', 'ignore')
          article["category"] = str(category)
          article["source"] = str(source)

          ## add indexing to ES
          try:
            dup = es.get(index="news", doc_type='article', id=article["title"])
            print("Article ")
          except:
            print("Article not in db, adding article", sys.exc_info()[0])
            try:
              res = es.index(index="news", doc_type='article', id=article["title"], body=article)
              print ("{}\n\n".format(article))
            except:
              print("Error adding to db", sys.exc_info()[1])
              pass

  print(count)

fetchArticles(sources)
