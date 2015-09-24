# charity_bot
A bot for reddit which handles donations to charity via comments and the JustGiving.com API

# Usage
The bot is called via reddit comments with one of the two call formats below:

`/u/Charity-Bot donate` - Will send the user a donation link to the default charity (currently Cancer Research UK)

`/u/Charity-Bot donate ID` - ID is an integer for the charity the donator wants to donate to. 

To get a charity ID, go to its charity page on JustGiving ([https://www.justgiving.com/rmcc/](example)), click the "Donate" button, and find the number after `/charity/` in your URL bar.

I'm working on compiling an easier to use list over the next few days so this annoying process is only temporary.

If an ID is invalid, either doesn't exist, or is not an integer, the default charity (Cancer Research UK) will be used.

The bot assumes that the parent commenter or OP of the donator's comment is who the donation is for.

# Running
The bot is divided into 2 parts:

`monitor.py` - Which you should run every few minutes via a cron job. This script monitors reddit, post comments, etc.

`confirmation_server.py` - A small http daemon that you should keep running. This script monitors the callback URL that JustGiving uses, and records when someone sends a donation to JustGiving.

# Setup

From the root directory:

`pip -r requirements`

`touch private_settings.py`

`touch oauth.ini`

`private_settings.py` - Contains your JustGiving API/login info. You can obtain the below info by following the instructions at [https://api.justgiving.com/docs](https://api.justgiving.com/docs):

``` python
  JUSTGIVING_APP_ID  = 'xxxxxxxx'
  JUSTGIVING_USER    = 'example@email.com'
  JUSTGIVING_PASS    = 'password'
```

`oauth.ini` - Your PRAW OAuth2Util configuration. 
Use the `scope` specified below at a minimum. You likely only need to edit app_key and app_secret which you can find out more about at [https://github.com/reddit/reddit/wiki/OAuth2](https://github.com/reddit/reddit/wiki/OAuth2)

After running the `monitor.py` script a `[token]` section will be generated for you and added to the `oauth.ini` file.

You can find out more info about OAuth2Util at [https://github.com/SmBe19/praw-OAuth2Util/blob/master/OAuth2Util/README.md](https://github.com/SmBe19/praw-OAuth2Util/blob/master/OAuth2Util/README.md)


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

# Workflow

1. The donator calls the bot as specified in the Usage section.

2. `monitor.py` then sends a donation link to the donator.

3. The donator makes their donation, after the donation is made they're sent to an exitURL.

4. `confirmation_server.py` catches this exitURL and records that the donation_id and user_id

5. `monitor.py` checks for any sent donation_urls that have a donation_id.
  * If they exist, and are accepted donations then it notifies the parent commenter (via comments).