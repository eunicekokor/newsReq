import requests
import json
import time

apiKey = "8f37248639844a2294dbe1af7c6f3b24"

sources = {
  "business": ["bloomberg", "business-insider","cnbc","financial-times","fortune"],
  "entertainment": ["buzzfeed","daily-mail","entertainment-weekly"],
  "gaming": ["ign", "polygon"],
  "general": ["the-guardian-uk", "the-washington-post", "the-telegraph", "time", "associated-press"],
  "music": ["mtv-news", "mtv-news-uk"],
  "sport": ["bbc-sport", "espn", "nfl-news", "fox-sports"],
  "science-and-nature": ["national-geographic", "new-scientist"],
  "technology": ["techcrunch","wired-de","ars-technica", "engadget", "hacker-news", "recode"]
}

# When we're building up our news db, our request will query each category
# and request articles from each source. Sort by latest, popular, and top
# Example API Request -->

for category in sources.keys():
  source_list = sources[category]
  for source in source_list:
    request_url = "https://newsapi.org/v1/articles?source={source}&apiKey={apiKey}".format(source=source, apiKey=apiKey)
    try:
      resp = requests.get(request_url)
    except:
      time.sleep(10)
      resp = requests.get(request_url)

    json_data = resp.json()
    if json_data.get('articles'):
      article_list = json_data['articles']
      print "Articles for {} in the category of {}".format(source, category)
      for article in article_list:
        article["category"] = str(category)
        article["source"] = str(source)
        print "{}\n\n".format(article)

        ## add indexing to ES

