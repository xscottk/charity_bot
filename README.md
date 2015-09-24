# charity_bot
A bot for reddit which handles donations to charity via comments and the JustGiving.com API

# Usage
The bot is divided into 2 parts:

`monitor.py` - Which you should run every few minutes via a cron job. This script monitors reddit, post comments, etc.

`confirmation_server.py` - A small http daemon that you should keep running. This script monitors the callback URL that JustGiving uses, and records when someone sends a donation to JustGiving.

# Setup

From the root directory:

`pip -r requirements`
`touch private_settings.py`
`touch oauth.ini`

`private_settings.py` - should contain your JustGiving API/login info. You can obtain the below info by following the instructions at [https://api.justgiving.com/docs](https://api.justgiving.com/docs):

``` python
  JUSTGIVING_APP_ID  = 'xxxxxxxx'
  JUSTGIVING_USER    = 'example@email.com'
  JUSTGIVING_PASS    = 'password'
```

`oauth.ini` - Your PRAW OAuth2Util configuration. Use the "scope" specified below at a minimum. You likely don't need to touch the [server] section.
After running the `monitor.py` script a [token] section will be generated for you and added to the `oauth.ini` file. You can find out more info about OAuth2Util at [https://github.com/SmBe19/praw-OAuth2Util/blob/master/OAuth2Util/README.md](https://github.com/SmBe19/praw-OAuth2Util/blob/master/OAuth2Util/README.md)

``` ini
[app]
scope = identity,edit,flair,history,privatemessages,read,save,submit
refreshable = True
app_key = EXAMPLE_KEY
app_secret = EXAMPLE_SECRET

[server]
server_mode = False
url = 127.0.0.1
port = 65010
redirect_path = authorize_callback
link_path = oauth
```
