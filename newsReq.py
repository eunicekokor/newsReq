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

YOUR_ACCESS_KEY = os.environ['CONSUMER_KEY']
YOUR_SECRET_KEY = os.environ['CONSUMER_SECRET']

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

awsauth = AWS4Auth("AKIAJKFZK5I7DAXLROEQ", "KkUpDYrGL7maWIdo6MCTvWy1qSiEEnuqrxiCBCgE", "us-east-1", 'es')

host =  "search-news-c4aykocrhzke4pf6yvrzdu5zbe.us-east-1.es.amazonaws.com"
port =  os.environ['ES_PORT']

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
    return render_template('index.html')


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
        res = es.search(size=50, index="news", doc_type="article", body={
            "query": {
                "match": {
                    "topicNo": str(topic)
                }
            }
        })
        results = res['hits']['hits']
        max_index = len(results)
        index1, index2 = get_rand_indexes(max_index)
        articles.append(("title", results[index1]['_source']['text']))
        articles.append(("title", results[index2]['_source']['text']))
    return articles

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
        user_posts = []
        for post in posts['data']:
            try:
                user_posts.append(facebook_post(post))
            except:
                pass
        post_string = build_post_string(user_posts)
        send_data = {'content': post_string}
        response = requests.post("https://newsreqfinal.herokuapp.com/getUserTopic", data=json.dumps(send_data), headers={'content-type': 'application/json'})
        print(response)
        #topics = retrieve them from response somehow
        topics = [4,6,7,8,5]

        articles = get_articles_from_elasticsearch(topics)

    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return render_template('index.html', articles=articles)

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
    app.debug = True
    app.run(port=8000)
