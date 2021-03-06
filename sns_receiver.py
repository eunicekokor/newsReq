import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
import json
import sys
import pprint
import ast
from requests_aws4auth import AWS4Auth

REGION="us-west-2"
awsauth = AWS4Auth("qcAuLjDQ6MkwobK2ThEvWjiY8", "qcAuLjDQ6MkwobK2ThEvWjiY8", "us-west-2", 'es')
# host = "search-tweet-trends-euni-bv5nxkgvthtwhgtrq6grokr4oi.us-west-2.es.amazonaws.com"
# host = "search-tweet-trends-24sebrx4nnqqvhbh3c737rotcq.us-west-2.es.amazonaws.com"
global es
es = Elasticsearch(
  hosts=[{
    'host': "search-newsreq-6xkhjq5amuh5hzynlndttavldi.us-west-2.es.amazonaws.com",
    'port': 443,
  }],
  http_auth=awsauth,
  use_ssl=True,
  connection_class=RequestsHttpConnection
  )
es.indices.create(index='article-index', ignore=400)

print (es.info())

def notification(req):
  global client
  client = boto3.client('sns')
  # conn = sns.SNSConnection(aws_access_key_id=YOUR_ACCESS_KEY, aws_secret_access_key =YOUR_SECRET_KEY)

  req = req.decode("utf-8")
  # req = ast.literal_eval(req)
  req = json.loads(req)
  print("NOTIFICATION", req)
  if (req["Type"] == 'SubscriptionConfirmation'):
    confirmation = client.confirm_subscription(TopicArn=req["TopicArn"], Token=req["Token"])

    print("Confirmation: {}\n".format(confirmation))

  else:
    if (req["Type"] == 'Notification'):
      msg = json.loads(req['Message'])
      print("\nNotification message: {}\n".format(msg))

      article = {}

      article['url'] = msg['url']
      article['title'] = msg['title']
      article['description'] = msg['description']
      article['urlToImage'] = msg['urlToImage']
      article['author'] = msg['author']
      article['publishedAt'] = msg['publishedAt']
      article['source'] = msg['source']
      article['category'] = msg['category']

      try:
        dup = es.get(index="test-index", doc_type='article', id=article["title"])
        print("DUPLICATE, SKIPPED ")
      except:
        try:
          print("Article not in db, adding article")
          res = es.index(index="test-index", doc_type='article', body=msg)
        except:
              print("Error adding to elasticsearch", sys.exc_info()[1])
              pass

      print("INDEXED:")
      print(res)
    else:
      print "PASSING OVER: {}".format(req)
      pass