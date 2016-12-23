import json
import time
from flask import Flask, render_template, request
import certifi
from requests_aws4auth import AWS4Auth
import sys
print sys.path
from config import *
import sns_receiver as sns

app = Flask(__name__)

# NOTE I moved this to getNews.py, so if you run getNews.py it should work for SNS
@app.route('/notification', methods=['GET','POST'])
def notification():
  print(request.method)
  if (request.method == "POST"):
    print(request)
    try:
      sns.notification(request.data)
    except:
      print("Unexpected error:", sys.exc_info())
      pass
  return "HI"


if __name__ == "__main__":
    app.debug = True
    app.run(port=8000)
