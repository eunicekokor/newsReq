import requests
import json
import time
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
import sys

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

# es.indices.delete(index='news', ignore=[400, 404])
# time.sleep(10)

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
count = 0
for category in sources.keys():
  source_list = sources[category]

  # For each source, query News API for articles
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
      print("Number of Articles", len(article_list), "total", count)
      count += len(article_list)
      print "Articles for {} in the category of {}".format(source, category)
      for article in article_list:

        # Remove unreadable characters in article fields and add category, src
        for v in article.keys():
          if article[v]:
            article[v] = article[v].encode('ascii', 'ignore')
        article["category"] = str(category)
        article["source"] = str(source)

        ## add indexing to ES
        try:
          dup = es.get(index="news", doc_type='article', id=article["title"])
          print("Article "
        except:
          print("Article not in db, adding article", sys.exc_info()[0])
          try:
            res = es.index(index="news", doc_type='article', id=article["title"], body=article)
            print "{}\n\n".format(article)
          except:
            print("Error adding to db", sys.exc_info()[0])
            pass


print(count)

