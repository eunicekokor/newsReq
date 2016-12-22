import json
import requests
import tweepy
import time
from flask import Flask, render_template, request
import certifi
from requests_aws4auth import AWS4Auth
import sys
from config import *


import sns_receiver as sns

application = Flask(__name__)


@application.route('/notification', methods=['GET','POST'])
def notification():
  print(request.method)
  if (request.method == "POST"):
    # print(key)

    print(request)
    # imd = request.form
    # print(dict(imd))
    # # print(request.data)
    # print("args",request.args.get())
    # # print(request.args.get('data', "clinton"))
    # #request.args.get('data', "clinton"))
    # # sns.notification(data)
    # print("POST notification")
    # data = request.args['data']
    # print(data)
    try:

      # data = request.args['data']
      # prinft(data)

      # r = requests.get(url)
      # print(r)
      sns.notification(request.data)
    except:
      print("Unexpected error:", sys.exc_info())
      pass
  return "HI"


if __name__ == "__main__":
    application.debug = True
    application.run(port=8000)