import praw
from private_settings import *
from settings import *

user_agent = "web:charity:v0.0.1 (by /u/pyskell)"
username   = "Charity-Bot"
trigger    = "/u/Charity-Bot"

r = praw.Reddit(user_agent)
r.set_oauth_app_info(client_id=private_id,
                     client_secret=private_secret,
                     redirect_uri = redirect_uri)
r.refresh_access_information(refresh_token)
r.login(username, password)

# Uncomment to test connection
# authenticated_user = r.get_me()
# print(authenticated_user.name)

mentions = r.request_json('https://www.reddit.com/message/mentions/')

for mention in mentions:
  print(mention)

# TODO: Get fed-up and put this in another script...

# Uncomment to get new access_code
# url = r.get_authorize_url('uniqueKey', 'identity edit flair history privatemessages read save submit', True)
# import webbrowser
# webbrowser.open(url)

# Uncomment to get new refresh_token after getting new access_code
# access_information = r.get_access_information(access_code)
# r.set_access_credentials(**access_information)
# print(authenticated_user.name, access_information['refresh_token'])


# r.send_message('pyskell', 'test', 'this is a test')