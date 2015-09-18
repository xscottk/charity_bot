import praw
import OAuth2Util
from private_settings import *
from settings import *

user_agent = "web:charity:v0.0.1 (by /u/pyskell)"
username   = "Charity-Bot"
trigger    = "/u/Charity-Bot"

r = praw.Reddit(user_agent)
o = OAuth2Util.OAuth2Util(r)

mentions_file = open('processed_mentions', 'a+')

mentions_file.seek(0)
processed_mentions = mentions_file.read().splitlines()

o.refresh()
mentions = r.get_mentions()

for mention in mentions:
  if mention.id not in processed_mentions:
    print(mention)
  else:
    mentions_file.write(mention.id + '\n')
