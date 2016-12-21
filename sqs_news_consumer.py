from elasticsearch import Elasticsearch, RequestsHttpConnection
import json
import pprint
import boto3
import re
import sys


# Get the service resource
sqs = boto3.resource('sqs')

# Get the queue
queue = sqs.get_queue_by_name(QueueName='news-queue-main')


def sns_connect():
    global client
    global topicarn
    client = boto3.client('sns')
    #return client
    response = client.create_topic(
        Name='news_articles'
    )

    #print(tweet_message)
    topicarn = response['TopicArn']
    #print(response)
    subscriber = client.subscribe(
        TopicArn=topicarn,
        Protocol='http' ,
        #Endpoint='http://127.0.0.1:5000/notification' 108.6.175.225
        Endpoint='http://c725a958.ngrok.io'
        # Endpoint = 'flask-env.5gi2k9npmn.us-west-2.elasticbeanstalk.com/notification'
    )
    print(("Subscriber: {}\n").format(subscriber))

sns_connect()

while(1):

  # Process messages by printing out body and optional author name
  for message in queue.receive_messages(MessageAttributeNames=['All']):
      if message.message_attributes is not None:

        title = message.body
        description = message.message_attributes.get('Description').get('StringValue')
        author = message.message_attributes.get('Author').get('StringValue')
        url = message.message_attributes.get('Url').get('StringValue')
        urlToImage = message.message_attributes.get('UrlToImage').get('StringValue')
        publishedAt = message.message_attributes.get('PublishedAt').get('StringValue')
        source = message.message_attributes.get('Source').get('StringValue')
        category = message.message_attributes.get('Category').get('StringValue')

        # tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",message.body).split())
        print ("trying")
        # options={'language':'english'}
        try:

          print("HEYO ", title, description, url, category)

          article = {
            'title' : title,
            'description' : description,
            'author' : author,
            'url' : url,
            'urlToImage' : urlToImage,
            'publishedAt' : publishedAt,
            'source' : source,
            'category' : category
          }

          print ("Final Data: {}\n").format(article)

          published_message = client.publish(
              TopicArn=topicarn,
              Message=json.dumps(article, ensure_ascii=False),
              MessageStructure='string'
          )
          print("We published something!")
          # client.confirm_subsciption(str(req["TopicArn"]), str(req["Token"]))
          # res = es.index(index="tweet-sqs", doc_type='tweet', body=data)

          # print(res)
        except:
          print (sys.exc_info())
          pass
        # Let the queue know that the message is processed
      message.delete()

