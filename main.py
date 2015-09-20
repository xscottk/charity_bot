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

def request_wrapper(resource, method, additional_headers=None, **kwargs):
  # Return either the requested resource (in JSON), POST confirmation, or None if something failed
  # QUESTION: Should I do subclassing instead here?
  # TODO: Figure out how to merge default headers and optional additional headers passed to request_wrapper

  default_headers = {'accept':'application/json'}

  if additional_headers == None:
    all_headers = default_headers
  else:
    all_headers = default_headers.copy()
    all_headers.update(additional_headers)

  if method == 'GET':
    request = requests.get(JUSTGIVING_API_URL + resource, auth=HTTPBasicAuth(JUSTGIVING_USER, JUSTGIVING_PASS), headers=all_headers, **kwargs)

  elif method == 'POST':
    request = requests.post(JUSTGIVING_API_URL + resource, auth=HTTPBasicAuth(JUSTGIVING_USER, JUSTGIVING_PASS), headers=all_headers, **kwargs)

  else:
    return None

  return request

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
  except:
    charity_id = DEFAULT_CHARITY_ID

  r = request_wrapper('v1/charity/' + str(charity_id),'GET')

  if r.status_code != 200:
    return DEFAULT_CHARITY_ID


  return charity_id
    

def get_donation(donation_amount, charity):
  # Get the donation link from justgiving.
  pass

def send_donation_message():
  # Send the donation link to the comment author.
  pass

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
      donation_details = validate_charity_id(mention)
      print(mention.body,"=", donation_details)
      # get_donation()
      # send_donation_message()
      # confirm_donation() # Will need a way to repeatedly check this...may be better calling and then queuing up a checking system after sending the donation message
      # post_confirmation()

      # TODO: Switch to sqlite at some point
      # TODO: REMEMBER TO UNCOMMENT THIS IN PRODUCTION
      # mentions_file.write(mention.id + '\n')

  mentions_file.close()

init()