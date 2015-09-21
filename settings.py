from private_settings import *

CONTENT_TYPE = 'application/json'

REDDIT_USER_AGENT   = "web:charity:v0.0.1 (by /u/pyskell)"
REDDIT_USERNAME     = "Charity-Bot"
REDDIT_TRIGGER      = "/u/Charity-Bot"

REDDIT_REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

JUSTGIVING_BASE_API_URL = 'https://api-sandbox.justgiving.com'
JUSTGIVING_BASE_WEBSITE_URL = 'https://v3-sandbox.justgiving.com'


# QUESTION: Is there a better way to assemble a URL?
JUSTGIVING_API_URL = JUSTGIVING_BASE_API_URL + '/' + JUSTGIVING_APP_ID + '/'

# The charity ID to use if a user does not specify a charity
DEFAULT_CHARITY_ID = 2357