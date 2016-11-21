import boto3
import boto.sqs
import time
from requests_aws4auth import AWS4Auth
from boto.sqs.message import Message, RawMessage

# Let's use Amazon S3
sqs = boto3.resource('sqs')

YOUR_ACCESS_KEY = "AKIAIFXS6NMDG6DNTGNQ"
YOUR_SECRET_KEY = "lwVBol6OuS32W4DA+kasw5Qv8W5HfrKFCMC9g01W"
REGION = "us-west-2"
# Create the queue. This returns an SQS.Queue instance
# queue = sqs.create_queue(QueueName='test', Attributes={'DelaySeconds': '5'})
# awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, REGION, 'es')

conn = boto.sqs.connect_to_region(
     REGION,
     aws_access_key_id=YOUR_ACCESS_KEY,
     aws_secret_access_key=YOUR_SECRET_KEY)
# print conn.get_all_queues()
# q = conn.get_queue('newsyQueue') #non-fifo
q = conn.get_queue('newsQueue.fifo') #fifo

print (q)
m = Message()
m.set_body('Reader started at this point')
# m.set_group_id('lalala')
# q.set_attributes(
#   Attributes={
#   "ContentBasedDeduplication": True
#   })
resp = q.write(m)
print ("added message, got {}").format(resp)


while(True):
  for m in q.get_messages():
    print (m, m.get_body())
    q.delete_message(m)
  time.sleep(1)