import os
import requests
import json
import time
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from config import *
import sys
import boto3


REGION = "us-west-2"

awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, REGION, 'sqs')
# awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, "us-east-1", 'es')

# host = os.environ['ES_URL']
# port = os.environ['ES_PORT']

# es = Elasticsearch(
#   hosts=[{
#     'host': host,
#     'port': int(port),
#   }],
#   http_auth=awsauth,
#   use_ssl=True,
#   verify_certs=True,
#   connection_class=RequestsHttpConnection
#   )

# # es.indices.delete(index='news', ignore=[400, 404])
# # time.sleep(10)

# # es.indices.create(index='news', ignore=400)
# print (es.info())

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
    print("Getting {}").format(category)
    source_list = sources[category]
    for source in source_list:
      print("Getting {}").format(source)
      request_url = "https://newsapi.org/v1/articles?source={source}&apiKey={apiKey}".format(source=source, apiKey=APIKEY)
      print request_url
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

          # print(article)
          ## add indexing to ES
          try:

            client = boto3.client(
              'sqs',
              aws_access_key_id=YOUR_ACCESS_KEY,
              aws_secret_access_key=YOUR_SECRET_KEY
            )

            queue_name='news-queue-main'
            # queue = client.create_queue(QueueName=queue_name, Attributes={'DelaySeconds': '5'})
            sqs = boto3.resource('sqs')
            queue = sqs.get_queue_by_name(QueueName=queue_name)

            print("this is the queue {}").format(queue)
            # queue.send_message(MessageBody="hoohoho")
            # res = queue.send_message(MessageBody=str(data["text"]), MessageAttributes={'tweet': 'yes'})
            res = queue.send_message(MessageBody=str(article["title"]).encode('ascii', 'ignore'), MessageAttributes={
              'Description': {
                'StringValue': '{}'.format(article["description"]),
                'DataType': 'String'
              },
              'Url': {
                'StringValue': '{}'.format(article["url"]),
                'DataType': 'String'
              },
              'PublishedAt': {
                'StringValue': '{}'.format(article["publishedAt"]),
                'DataType': 'String'
              },
              'Author': {
                'StringValue': '{}'.format(article["author"]),
                'DataType': 'String'
              },
              'Source': {
                'StringValue': '{}'.format(article["source"]),
                'DataType': 'String'
              },
              'Category': {
                'StringValue': '{}'.format(article["category"]),
                'DataType': 'String'
              },
              'UrlToImage': {
                'StringValue': '{}'.format(article["urlToImage"]),
                'DataType': 'String'
              }
            })
            print(res.get('MessageId'))

            # res = es.index(index="test", doc_type='tweet', body=str(data))
            print("Message sent")

            # dup = es.get(index="news", doc_type='article', id=article["title"])
            # print("Article ")
          except:
            print("Error adding to sqs", sys.exc_info()[1])
            # print("Article not in db, adding article", sys.exc_info()[0])
            # try:
            #   res = es.index(index="news", doc_type='article', id=article["title"], body=article)
            #   print ("{}\n\n".format(article))
            # except:
            #   print("Error adding to db", sys.exc_info()[1])
            #   pass

  print(count)

# fetchArticles(sources)


if __name__ == '__main__':

  while(1):
    fetchArticles(sources)
    # time.sleep(3600)   # EVERY 60 MINUTES


# URL
# Description
# Category
# Source
# Author
# ID

