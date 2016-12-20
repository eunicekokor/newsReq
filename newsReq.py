import os
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
        print(user_posts[5].article_text)
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, "us-east-1", 'es')

host =  os.environ['ES_URL']
port =  os.environ['ES_PORT']

es = Elasticsearch(
  hosts=[{
    'host': host,
    'port': int(port),
  }],
  http_auth=awsauth,
  use_ssl=True,
  verify_certs=True,
  connection_class=RequestsHttpConnection
  )

@app.route('/')
def login():
    return "Hello"


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
