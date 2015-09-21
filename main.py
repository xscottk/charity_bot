# REMINDER: In production make sure we use a different email and maybe name for accepting donations.

# Example: r = requests.get('https://api-sandbox.justgiving.com/JUSTGIVING_APP_ID/v1/fundraising/pages', auth=HTTPBasicAuth('JUSTGIVING_USER', 'JUSTGIVING_PASS'), headers={'accept':'application/json'})

import OAuth2Util
import praw
import requests
from requests.auth import HTTPBasicAuth

from settings import *

r = praw.Reddit(REDDIT_USER_AGENT)
o = OAuth2Util.OAuth2Util(r)

mentions_file = open('processed_mentions', 'a+')

mentions_file.seek(0)
processed_mentions = mentions_file.read().splitlines()

o.refresh()
mentions = r.get_mentions()

def justgiving_request_wrapper(resource, method, additional_headers=None, **kwargs):
  # Return either the requested resource (in JSON), POST confirmation, or None if something failed
  # QUESTION: Should I do subclassing instead here?
  # TODO: Figure out how to merge default headers and optional additional headers passed to justgiving_request_wrapper

  default_headers = {'accept':'application/json'}

  if additional_headers == None:
    all_headers = default_headers
  else:
    all_headers = default_headers.copy()
    all_headers.update(additional_headers)

# TODO: I don't like this, but I don't know how else to do it...
  if method == 'GET':
    jg_request = requests.get(JUSTGIVING_API_URL + resource, auth=HTTPBasicAuth(JUSTGIVING_USER, JUSTGIVING_PASS), headers=all_headers, **kwargs)

  elif method == 'POST':
    jg_request = requests.post(JUSTGIVING_API_URL + resource, auth=HTTPBasicAuth(JUSTGIVING_USER, JUSTGIVING_PASS), headers=all_headers, **kwargs)

  # elif method == 'PUT':
  #   jg_request = requests.put(JUSTGIVING_API_URL + resource, auth=HTTPBasicAuth(JUSTGIVING_USER, JUSTGIVING_PASS), headers=all_headers, **kwargs)    

  else:
    return None

  return jg_request

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

def get_donation_url(charity_id):
  # Get the donation link from justgiving.
  # Example URL: https://v3-sandbox.justgiving.com/4w350m3/donation/direct/charity/2357/?exitUrl=http%3A%2F%2Fwww.dogstrust.org.uk%2F#MessageAndAmount

  if charity_id == None:
    return None

  donation_url = JUSTGIVING_BASE_URL + '/4w350m3/donation/direct/charity/' + str(charity_id)

  return donation_url

def send_donation_message(donation_url, donator, parent_commenter):
  # Send the donation link to the donator. Return True if donation message sent, otherwise return False.
  if donation_url == None:
    return False

  subject = "Your donation link for /u/"+parent_commenter+"'s comment/post"
  message = "Here's your donation link. You're totally awesome! \n" + donation_url
  sent_message = r.send_message(recipient=donator, subject=subject, message=message)

  if sent_message.status_code == 200:
    return True
  else:
    return False

def confirm_donation():
  # Confirm that the donation was made through the link.
  pass

def post_confirmation():
  # Post a confirmation comment back to the original message id.
  pass

def init():
  for mention in mentions:
    if mention.id not in processed_mentions:
      # print(mention)
      # import pdb; pdb.set_trace()
      # from IPython.core.debugger import Tracer; Tracer()()
      charity_id                = validate_charity_id(mention)
      donator, parent_commenter = get_attribution_info(mention)
      donation_url              = get_donation_url(charity_id)
      donation_message_sent     = send_donation_message(donation_url, donator, parent_commenter)
      print(mention.body,"=", charity_id, "Donation message sent:", donation_message_sent)
      # confirm_donation() # Will need a way to repeatedly check this...may be better calling and then queuing up a checking system after sending the donation message
      # post_confirmation()

      # TODO: Switch to sqlite at some point
      # TODO: REMEMBER TO UNCOMMENT THIS IN PRODUCTION
      # mentions_file.write(mention.id + '\n')

  mentions_file.close()

init()