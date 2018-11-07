#!/usr/bin/python3

from mastodon import Mastodon
import os
import re
from datetime import datetime
import http.client
import urllib
import json
from dotenv import load_dotenv
load_dotenv()

CHUNK_SIZE = 200
TRANSLATION_API_BASE_URI = "www.louchebem.fr"
TRANSLATION_API_ENDPOINT = "/api/use.php?"

# read config from file
with open('config.json') as json_data_file:
    config = json.load(json_data_file)

# get token from env variable (from .env)
token = os.getenv('MASTODON_BEARER_TOKEN')

# get API client
mastodon = Mastodon(access_token = token, api_base_url = config['base_url'])

# random answers
def get_translation(normal_text):
  # available answers
  params = {'methode': 'url', 'texte': remove_mention(normal_text)}
  encoded = urllib.parse.urlencode(params)
  response = do_request(encoded)
  return parse_html(response)

# execute request to API
def do_request(encoded_params):
    url = TRANSLATION_API_BASE_URI + TRANSLATION_API_ENDPOINT + encoded_params
    print(url)

    conn = http.client.HTTPConnection(TRANSLATION_API_BASE_URI)
    conn.request("GET", TRANSLATION_API_ENDPOINT + encoded_params)
    response = conn.getresponse()
    data = response.read().decode("latin-1")
    conn.close()
    return data

# parse response body
def parse_html(html_data):
    no_html = re.sub('<[^<]+?>', '', html_data)
    trimmed = no_html.strip()
    return trimmed

def remove_mention(status):
    return re.sub('@.+\\s', '', status)

# get all mentions of the bot (@-ed)
notifications = mastodon.notifications()
mentions = list(filter(lambda n: n['type'] == 'mention', notifications))
print("{0}: {1} 🔔".format(datetime.now(), len(mentions)))

# answer to all mentions
for mention in mentions:
    html_text = mention['status']['content']
    text = parse_html(html_text)

    # get translation for given text
    translation = get_translation(text)

    # posting in reply to mention
    print("{0}: 👤 {1}".format(datetime.now(), mention['account']['username']))
    print("{0}: 📯 {1}".format(datetime.now(), translation))
    mastodon.status_reply(to_status=mention['status'], status=translation, visibility='public')
    print("{0}: 👍".format(datetime.now()))

    # dismiss this notification, so it doesn't appear
    # when fetching notifications later
    mastodon.notifications_dismiss(mention)

print("{0}: 👍 😴".format(datetime.now()))
