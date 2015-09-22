# REMINDER: In production make sure we use a different email and maybe name for accepting donations.

# Example: r = requests.get('https://api-sandbox.justgiving.com/JUSTGIVING_APP_ID/v1/fundraising/pages', auth=HTTPBasicAuth('JUSTGIVING_USER', 'JUSTGIVING_PASS'), headers={'accept':'application/json'})

import OAuth2Util
import praw
import urllib
import uuid

from utils import *
from settings import *

r = praw.Reddit(REDDIT_USER_AGENT)
o = OAuth2Util.OAuth2Util(r)

mentions_file = open('processed_mentions', 'a+')

mentions_file.seek(0)
processed_mentions = mentions_file.read().splitlines()

o.refresh()
all_mentions = r.get_mentions()

def validate_charity_id(mention):
  # Parse and validate donation message.
  # RETURN: Validated charity number OR None if invalid charity number.

  # Call format: \u\Charity-Bot donate charityID
  # Default Charity if no charity specified: \u\Charity-Bot donate 2357 (Charity ID for Cancer Research UK)

  # Rules:
  # First argument must be the word 'donate'
  # Charity must be a valid charity number

  message = mention.body.split()

  donate  = message[1] == "donate"

  if not donate:
    return None

  # TODO: Try to shorten once Python 3.6 w/ PEP 0505 comes out
  try:
    charity_id = int(message[2])
  except ValueError:
    charity_id = DEFAULT_CHARITY_ID

  jg = justgiving_request_wrapper('v1/charity/' + str(charity_id),'GET')

  if jg.status_code != 200:
    return DEFAULT_CHARITY_ID

  return charity_id

def get_attribution_info(mention):
  donator = mention.author.name

  # If root comment then assume donation is in the name of the submitter, otherwise assume donation is for the parent_commenter which the donator replied to.
  if mention.is_root:
    parent_commenter = mention.submission.author.name
  else:    
    parent_commenter = r.get_info(thing_id=mention.parent_id).author.name

  print(donator,"/", parent_commenter)
  return [donator, parent_commenter]

def get_donation_url(charity_id, user_id):
  # Get the donation link from justgiving. And add the GET variables we need to track the donation.
  # Example URL: https://v3-sandbox.justgiving.com/4w350m3/donation/direct/charity/2357/?exitUrl=http%3A%2F%2Fwww.dogstrust.org.uk%2F#MessageAndAmount

  if charity_id == None:
    return None

  # Pretty sure this is a sin...
  exit_url_info = 'http://' + HTTP_HOSTNAME + ":" + HTTP_PORT + '/?donation_id=JUSTGIVING-DONATION-ID&uuid=' + user_id
  exit_url_info = urllib.parse.quote(exit_url_info)

  donation_url = JUSTGIVING_BASE_WEBSITE_URL + '/4w350m3/donation/direct/charity/' + str(charity_id) + '/?exitUrl=' + exit_url_info

  return donation_url

def send_donation_message(donation_url, donator, parent_commenter):
  # Send the donation link to the donator. Return True if donation message sent, otherwise return False.
  if donation_url == None:
    return False

  subject = "Your donation link for /u/"+parent_commenter+"'s comment/post"
  message = "Here's your donation link. You're totally awesome! \n\n" + donation_url
  sent_message = r.send_message(recipient=donator, subject=subject, message=message)

  if not sent_message.get("errors"):
    return True
  else:
    return False

def confirm_accepted_donation(donation_id):
  # Confirm that the donation was accepted by JustGiving.
  if donation_id:
    response         = justgiving_request_wrapper('v1/donation/' + donation_id, 'GET')
    decoded_response = json.loads(response)
    status           = decoded_response.get('status')

    if status == "Accepted":
      return True

def post_confirmation():
  # Post a confirmation comment back to the original message id.
  pass

def init():

  # REMINDER: In production uncomment below line and delete other new_mentions
  # new_mentions = filter(lambda x: x.new, all_mentions)
  new_mentions = all_mentions

  for mention in new_mentions:
    if mention.id not in processed_mentions:

      charity_id                = validate_charity_id(mention)
      donator, parent_commenter = get_attribution_info(mention)
      user_id                   = str(uuid.uuid1())
      donation_url              = get_donation_url(charity_id, user_id)
      donation_message_sent     = send_donation_message(donation_url, donator, parent_commenter)
      print(mention.body,"=", charity_id, "Donation message sent:", donation_message_sent)

      # TODO: REMEMBER TO UNCOMMENT THIS IN PRODUCTION
      mention.mark_as_read() # Remotely prevents responding to the same message twice.
      # TODO: Switch to sqlite at some point
      mentions_file.write(mention.id + '\n') # Locally prevents responding to the same message twice.
      
      # confirm_donation() # Will need a way to repeatedly check this...may be better calling and then queuing up a checking system after sending the donation message
      # post_confirmation()

  mentions_file.close()

init()