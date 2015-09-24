# REMINDER: In production make sure we use a different email and maybe name for accepting donations.

# Example: r = requests.get('https://api-sandbox.justgiving.com/JUSTGIVING_APP_ID/v1/fundraising/pages', auth=HTTPBasicAuth('JUSTGIVING_USER', 'JUSTGIVING_PASS'), headers={'accept':'application/json'})

# import json
import OAuth2Util
import praw
import urllib
import uuid

from decimal import Decimal
TWO_PLACES = Decimal(10) ** -2

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from utils import *
from settings import *
from sql_tables import *

r = praw.Reddit(REDDIT_USER_AGENT)
o = OAuth2Util.OAuth2Util(r)

# Tracks comment triggers we've already processed.
# TODO: Replace with SQLite
mentions_file = open('processed_mentions', 'a+')

mentions_file.seek(0)
processed_mentions = mentions_file.read().splitlines()

engine = create_engine(SQLALCHEMY_ADDRESS)
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session   = DBSession() 

o.refresh()
all_mentions = r.get_mentions()

def validate_charity_id(mention):
  # Parse and validate donation message.
  # RETURN: Validated charity number, name, and website OR None if invalid charity number.

  # Call format: \u\Charity-Bot donate charityID
  # Default Charity if no charity specified: \u\Charity-Bot donate 2357 (Charity ID for Cancer Research UK)

  # Rules:
  # First argument must be the word 'donate'
  # Charity must be a valid charity number

  message = mention.body.split()

  donate  = message[1] == "donate"

  if not donate:
    return [None, None, None]

  try:
    charity_id = int(message[2])
  except (TypeError, ValueError):
    charity_id = DEFAULT_CHARITY_ID

  # QUESTION: Should I just be storing json responses for charity/donation details and then accessing them directly in functions?
  response            = justgiving_request_wrapper('v1/charity/' + str(charity_id),'GET')

  if response.status_code == 200:
    json_response       = response.json()
    charity_name        = json_response.get('name')
    charity_profile_url = json_response.get('profilePageUrl')

  else:
    charity_id = None
    charity_name = None
    charity_profile_url = None

  return [charity_id, charity_name, charity_profile_url]

def get_attribution_info(mention):
  donator         = mention.author.name
  donator_is_root = mention.is_root
  try:
    donator_post_id = mention.id
  except AttributeError:
    donator_post_id = None

  parent_post_id  = mention.parent_id

  try:
    if donator_is_root:
  # If root comment then assume donation is in the name of OP, otherwise assume donation is for the parent_commenter which the donator replied to.
      parent_commenter = mention.submission.author.name
    else:    
      parent_commenter = r.get_info(thing_id=parent_post_id).author.name
  except AttributeError:
    parent_commenter = None

  print(donator,"(id:",donator_post_id,"is_root",donator_is_root,") /", parent_commenter,"(",parent_post_id,")")
  
  # QUESTION: Is this the right way to do this? Or should I be using objects? Or something else?
  return [donator, donator_post_id, parent_commenter, parent_post_id, donator_is_root]

def get_donation_url(charity_id, user_id):
  # Get the donation link from justgiving. And add the GET variables we need to track the donation.
  # Example URL: https://v3-sandbox.justgiving.com/4w350m3/donation/direct/charity/2357/?exitUrl=http%3A%2F%2Fwww.dogstrust.org.uk%2F#MessageAndAmount

  if charity_id == None:
    return None

  # Pretty sure this is a sin...
  exit_url_info = 'http://' + HTTP_HOSTNAME + ":" + str(HTTP_PORT) + '/?donation_id=JUSTGIVING-DONATION-ID&user_id=' + str(user_id)
  exit_url_info = urllib.parse.quote(exit_url_info)

  donation_url = JUSTGIVING_BASE_WEBSITE_URL + '/4w350m3/donation/direct/charity/' + str(charity_id) + '/?exitUrl=' + exit_url_info

  return donation_url

def send_donation_url(donation_url, donator, parent_commenter):
  # Send the donation link to the donator. Return True if donation message sent, otherwise return False.
  if donation_url == None:
    return False

  message = "Here's your donation link. You're totally awesome! \n\n" + donation_url
  
  # If the parent_commenter deletes their post we need to let the donator know.
  if parent_commenter:
    subject = "Your donation link for /u/"+parent_commenter+"'s comment/post"
  else:
    subject = "Your donation link!"
    message += "\n\n Unfortunately the person who inspired your donation has deleted their post. I will be unable to notify them of your donation."

  if donator:
    # sent_message = r.send_message(recipient=donator, subject=subject, message=message)
    sent_message = handle_ratelimit(r.send_message, recipient=donator, subject=subject, message=message)  
  else:
    return False

  if not sent_message.get("errors"):
    return True
  else:
    return False

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

def post_confirmation(donator_is_root, donator, parent_commenter, parent_post_id, donation_amount, donation_currency, charity_name, charity_profile_url, donator_message=None):
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
    handle_ratelimit(submission.add_comment, reply)  
  else:
    handle_ratelimit(submission.reply, reply)

def check_mentions():

  # REMINDER: In production uncomment below line and delete other new_mentions
  # new_mentions = filter(lambda x: x.new, all_mentions)
  new_mentions = all_mentions

  for mention in new_mentions:
    if mention.id not in processed_mentions:

      user_id                   = str(uuid.uuid1())
      charity_id, charity_name,\
      charity_profile_url       = validate_charity_id(mention)

      # Skip processing the mention if charity_id is None
      if not charity_id:
        continue

      donator, donator_post_id,\
      parent_commenter, \
      parent_post_id, \
      donator_is_root           = get_attribution_info(mention)

      donation_url              = get_donation_url(charity_id, user_id)
      donation_url_sent         = send_donation_url(donation_url, donator, parent_commenter)

      new_donation = Donation(user_id=user_id, 
        charity_id=charity_id, 
        charity_name=charity_name, 
        charity_profile_url=charity_profile_url,
        donator=donator, 
        donator_post_id=donator_post_id, 
        donator_is_root=donator_is_root, 
        parent_commenter=parent_commenter, 
        parent_post_id=parent_post_id, 
        donation_url_sent=donation_url_sent, 
        donation_complete=False)
      session.add(new_donation)
      session.commit()

      print(mention.body,"=", charity_id, "Donation message sent:", donation_url_sent)


      # TODO: REMEMBER TO UNCOMMENT THIS IN PRODUCTION
      # TODO: Switch to sqlite for this at some point
      mention.mark_as_read() # Remotely prevents responding to the same message twice.
      mentions_file.write(mention.id + '\n') # Locally prevents responding to the same message twice.
      
      # post_confirmation()

  mentions_file.close()

def check_pending_donations():
  pending_donations = session.query(Donation).filter(
    and_(Donation.donation_url_sent == True, Donation.donation_id != None, Donation.donation_complete == False))

  for donation in pending_donations:
    donation_accepted, donation_amount, donation_currency, donation_message = get_donation_details(donation.donation_id)

    if donation_accepted and donation_amount and donation_currency:
      
      donation.donation_complete = True
      donation.donation_amount   = donation_amount
      donation.donation_currency = donation_currency

      session.commit()

      post_confirmation(
        donator_is_root=donation.donator_is_root,
        donator=donation.donator, 
        parent_commenter=donation.parent_commenter, 
        parent_post_id=donation.parent_post_id, 
        donation_amount=donation_amount, 
        donation_currency=donation_currency, 
        charity_name=donation.charity_name,
        charity_profile_url=donation.charity_profile_url, 
        donator_message=donation_message)

check_mentions()
check_pending_donations()