import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
import json
from config import *
import sys
import pprint
import ast
from requests_aws4auth import AWS4Auth

REGION="us-west-2"

# es = Elasticsearch(
#   hosts=[{
#     'host': host,
#     'port': 443,
#   }],
#   http_auth=awsauth,
#   use_ssl=True,
#   connection_class=RequestsHttpConnection
#   )
# es.indices.create(index='tweet-sqs', ignore=400)

# print (es.info())

# req = {
#   'Type' : 'Notification',
#   'Message' : {
#     'text' : "tweet here about clinton or whatever",
#     'coordinates' : (-30.0, 45.9),
#     'sentiment' : 'positive'
#   }
# }
# YOUR_ACCESS_KEY="AKIAJ7GFBSYVCRWBQ72A"
# YOUR_SECRET_KEY="regiCxIQefPYZrUd3ZJXUD52IlZzYydOHQkWNrnQ"

awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, REGION, 'es')
host = "search-tweet-trends-euni-bv5nxkgvthtwhgtrq6grokr4oi.us-west-2.es.amazonaws.com"
# host = "search-tweet-trends-24sebrx4nnqqvhbh3c737rotcq.us-west-2.es.amazonaws.com"
global es
es = Elasticsearch(
  hosts=[{
    'host': host,
    'port': 443,
  }],
  http_auth=awsauth,
  use_ssl=True,
  connection_class=RequestsHttpConnection
  )
es.indices.create(index='test-index', ignore=400)

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
      print("Notification message: {}\n".format(msg))

      tweet = {}

      tweet['text'] = msg['text']
      tweet['name'] = msg['name']
      tweet['coordinates'] = msg['coordinates']
      tweet['sentiment'] = msg['sentiment']

      res = es.index(index="test-index", doc_type='tweet', body=tweet)

      print("INDEXED:")
      print(res)
    else:
      print "PASSING OVER: {}".format(req)
      pass