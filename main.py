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

def get_valid_currencies():
  # Get the list of valid currencies from justgiving

  # TODO: For now we just return a list manually...may be nice to periodically check for new currencies in the future.
  return [('GBP','£') , ('USD','$') , ('HKD','HK$') , ('SGD','SG$') , ('CAD','CA$') , ('AED','د.إ') , ('AUD','AU$') , ('ZAR','R') , ('EUR','€')]

def parse_message(mention):
  # Parse and validate donation message.

  # Call format: \u\Charity-Bot $X Y ($5 123)
  # Currency can be $ or pound or OTHERS?
  # Default Charity: \u\Charity-Bot $X 2357 (Charity ID for Cancer Research UK)

  # Rules:
  # Currency sign must be valid
  # Donation amount must be >0
  # Charity must be a valid charity number
  message = mention.body.split()
  
  # Make sure we get the right number of arguments (3): /u/Charity-Bot Amount Charity
  if len(message) != 3:
    return None

  donation_amount = message[1]
  charity_id      = message[2]

  donation = [donation_amount, charity_id]

  return donation

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
      donation_details = parse_message(mention)
      print(donation_details)
      get_donation()
      send_donation_message()
      confirm_donation() # Will need a way to repeatedly check this...may be better calling and then queuing up a checking system after sending the donation message
      post_confirmation()

      # TODO: Switch to sqlite at some point
      # TODO: REMEMBER TO UNCOMMENT THIS IN PRODUCTION
      # mentions_file.write(mention.id + '\n')

  mentions_file.close()

init()