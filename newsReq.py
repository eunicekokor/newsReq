import os
import random

import requests
from flask import Flask, render_template, session
from elasticsearch import Elasticsearch, RequestsHttpConnection
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from requests_aws4auth import AWS4Auth
from flask_oauth import OAuth
from oauth import OAuthSignIn
from facebook_post import facebook_post
#import sns_receiver as sns


oauth = OAuth()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '386595135013015',
        'secret': 'b9c2f95ebfb42675e4986ef5f214f45b'
    },
    'twitter': {
        'id': '	SmxpntnfYOzbpIC2XFyctNGVT',
        'secret': 'Lxw1TgkQDAaj9eeuhZTXjptN30XaRSp1QitR8YCCvGJ8CotPWO'
    }
}

db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'index'

awsauth = AWS4Auth("AKIAJKFZK5I7DAXLROEQ", "KkUpDYrGL7maWIdo6MCTvWy1qSiEEnuqrxiCBCgE", "us-west-2", 'es')

host =  "search-newsreq-6xkhjq5amuh5hzynlndttavldi.us-west-2.es.amazonaws.com"

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

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    #articles = get_articles_from_elasticsearch(topics)
    if not current_user.is_anonymous:
        print("The user is " + current_user.nickname)
        result = es.search(index='user', doc_type="existing_users", body={
            "query": {
                "match": {
                    "username": str(current_user.nickname)
                }}
        })
        print(result['hits']['hits'][0]['_source']['favorite_topics'])
        favorite_topics = json.loads(result['hits']['hits'][0]['_source']['favorite_topics'])
        favorite_topics = [0,0,0,0,0]
        articles = get_articles_from_elasticsearch(favorite_topics)
    else:
        articles = []

    return render_template('index.html', articles=articles)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()



def get_posts_as_text(posts_json):
    posts = posts_json['data']
    for post in posts:
        try:
            new = facebook_post(post)
            #print(post)
            #print(post['message'])
        except:
            #can't view shared posts
            pass

def build_post_string(user_posts):
    giant_string = ""

    for post in user_posts:
        if post.article_text:
            temp_string = " ".join(str(x.encode("utf-8")) for x in post.article_text)
            giant_string += temp_string
            giant_string += " "

    return giant_string
def get_rand_indexes(max_index):
    value1 = random.randrange(1, max_index)
    value2 = random.randrange(1, max_index)
    return value1, value2

def get_articles_from_elasticsearch(topics):
    articles = []#each includes a title and a link
    print("getting articles")
    for topic in topics:
        res = es.search(size=50, index="test-index", doc_type="article", body={
            "query": {
                "match": {
                    "topicNo": str(topic)
                }
            }
        })
        results = res['hits']['hits']
        print(results)
        max_index = len(results)
        index1, index2 = get_rand_indexes(max_index)
        article_1 = (results[index1]['_source']['title'], results[index1]['_source']["urlToImage"], results[index1]['_source']["url"], results[index1]['_source']["description"])
        article_2 = (results[index2]['_source']['title'], results[index2]['_source']["urlToImage"], results[index2]['_source']["url"], results[index2]['_source']["description"])
        if article_1 not in articles:
            articles.append(article_1)
        if article_2 not in articles:
            articles.append(article_2)

    return articles

def user_exists(username):
    result = es.search(index='user', doc_type="existing_users", body={
        "query": {
            "match": {
                "username": str(username)
            }}
    })

    if len(result['hits']['hits']) > 0:
        return True
    else:
        return False

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, user_likes, posts = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    else:

        if not user_exists(username):

            user_posts = []
            for post in posts['data']:
                try:
                    user_posts.append(facebook_post(post))
                except:
                    pass
            post_string = build_post_string(user_posts)
            send_data = {'content': post_string}
            response = requests.post("http://c9b4dbd0.ngrok.io/getUserTopic", data=json.dumps(send_data), headers={'content-type': 'application/json'})

            response_dict = json.loads(response.text)

            user_topics = []
            user_topics.append(response_dict["topicNo1"])
            user_topics.append(response_dict["topicNo2"])
            user_topics.append(response_dict["topicNo3"])
            user_topics.append(response_dict["topicNo4"])
            user_topics.append(response_dict["topicNo5"])

            print(user_topics)

            try:
                es.index(index='user', doc_type='existing_users', body={
                    'username': username,
                    'favorite_topics': json.dumps(user_topics),
                })
            except:
                print('User already exists')

    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)


    return redirect(url_for('index'))

@app.route('/es')
def test_es():
    result = es.search(index='news',doc_type="article",body={
        "query": { "match_all": {} },
        "sort": { "publishedAt": { "order": "desc" }
        }
    })
    data = json.dumps(result['hits']['hits'])
    return data


if __name__ == '__main__':
    db.create_all()
    #app.debug = True
    app.run(host='0.0.0.0')
