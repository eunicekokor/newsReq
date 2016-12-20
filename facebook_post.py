from urlparse import urlparse
from goose import Goose
from requests import get
import requests
import re

non_news_sites = ["instagram", "youtube", "twitter"]

class facebook_post:

    def display_post(self):
        print('User: {}\nContent: {}\nArticle: {}'.format(
            self.user_id, self.message, self.article))
        print("\n\n")

    def is_news(self, url):
        for site in non_news_sites:
            temp_url = str(site + ".com")
            if(temp_url in url):
                return False
        return True

    def extract_url(self,url):
        long_url = requests.head(url, allow_redirects=True).url
        parsed_url = urlparse(long_url)
        return parsed_url.netloc

    def get_article_text(self):
        if(self.article_url and self.is_news(self.article_url)):
            response = get(self.article_url)
            extractor = Goose()
            article = extractor.extract(raw_html=response.content)
            article_text = article.cleaned_text
            l = article_text.split(' ')
            return l

        return None

    def check_for_article(self):
        url = re.search("(?P<url>https?://[^\s]+)", self.message).group("url")
        if url:
            return url
        else:
            return None

    def __init__(self, post):

        self.user_id = post['id']
        self.created_time = post['created_time']
        self.message = post['message']
        # Search for article
        self.article_url = self.check_for_article()
        self.article_text = self.get_article_text()
