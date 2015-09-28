import praw
import requests
import time

from decimal import Decimal
TWO_PLACES = Decimal(10) ** -2
from requests.auth import HTTPBasicAuth

from settings import *

def justgiving_request_wrapper(resource, method, additional_headers=None, **kwargs):
  # Return either the requested resource (in JSON), POST confirmation, or None if something failed
  # QUESTION: Should I do subclassing instead here? Or overriding or something?
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

  else:
    return None

  return jg_request

def handle_ratelimit(func, *args, **kwargs):
  while True:
    try:
      return func(*args, **kwargs)
      break
    except praw.errors.RateLimitExceeded as error:
      sleep_time = error.sleep_time + 70 # Extra safety buffer
      print('Rate limit exceeded, sleeping for', sleep_time, 'seconds')
      time.sleep(sleep_time)

def get_donation_details(donation_id):
  # Get details for a donation_id from JustGiving
  if donation_id:
    try:
      response          = justgiving_request_wrapper('v1/donation/' + str(donation_id), 'GET')
      json_response     = response.json()
      donation_accepted = json_response.get('status') == 'Accepted'
      donation_amount   = str(json_response.get('donorLocalAmount'))
      donation_currency = str(json_response.get('donorLocalCurrencyCode'))
      donation_message  = str(json_response.get('message'))
      return [donation_accepted, donation_amount, donation_currency, donation_message]
    except (TypeError, ValueError):
      return [False, None, None, None]

  return [False, None, None, None]

def post_confirmation(r, donator_is_root, donator, parent_commenter, parent_post_id, donation_amount, donation_currency, charity_name, charity_profile_url, donator_message=None):
  # Post a confirmation comment back to the original parent_commenter...If parent_commenter is None (ie. missing), then reply to the donator comment, if that is missing (None), then do nothing. Remember to wrap both attempts in try/except for AttributeError here...
  

  donation_amount = str(Decimal(donation_amount).quantize(TWO_PLACES))

  intro = "Hey there " + parent_commenter + "!\n\n"
  body  = donator + " has donated " + donation_amount + " " + donation_currency + " to " + "[" + charity_name + "](" + charity_profile_url + ") because of your comment / submission. \n\n"
  if donator_message:
    footer = "They also included a message: \n\n" + donator_message
  else:
    footer = ""

  reply = intro + body + footer

  submission = r.get_info(thing_id=parent_post_id)

  if donator_is_root:
    comment = handle_ratelimit(submission.add_comment, reply)  
  else:
    comment = handle_ratelimit(submission.reply, reply)

  print("Sending confirmation of donation (", donation_amount, donation_currency,") for", charity_name, "to", parent_commenter)