from private_settings import *

CONTENT_TYPE = 'application/json'

# I graciously request that if you run this bot, please leave the "by /u/pyskell" portion in the USER_AGENT string. 
# Please also add yourself as a contributor to the "by" list if you've made changes.
REDDIT_USER_AGENT   = "web:charity:v0.0.2 (by /u/pyskell)"

REDDIT_REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

# Testing environment variables. COMMENT OUT IN PRODUCTION.
JUSTGIVING_BASE_API_URL = 'https://api-sandbox.justgiving.com'
JUSTGIVING_BASE_WEBSITE_URL = 'https://v3-sandbox.justgiving.com'

# Production environment variables. COMMENT OUT IN TESTING.
# JUSTGIVING_BASE_API_URL = 'https://api.justgiving.com'
# JUSTGIVING_BASE_WEBSITE_URL = 'https://justgiving.com'

# QUESTION: Is there a better way to assemble a URL?
JUSTGIVING_API_URL = JUSTGIVING_BASE_API_URL + '/' + JUSTGIVING_APP_ID + '/'

# The charity ID to use if a user does not specify a charity
DEFAULT_CHARITY_ID = 2357 # This is the ID for Cancer Research UK

SQLALCHEMY_ADDRESS = 'sqlite:///charity_database.db'

CHECKING_INTERVAL = 20 # Time to wait inbetween checking for new mentions/complete donations