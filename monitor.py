import daemon
import OAuth2Util
import praw
import time
import urllib

from decimal import Decimal
TWO_PLACES = Decimal(10) ** -2

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from objects import *
from utils import *
from settings import *
from sql_tables import *

r = praw.Reddit(REDDIT_USER_AGENT)
o = OAuth2Util.OAuth2Util(r)

engine = create_engine(SQLALCHEMY_ADDRESS)
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session   = DBSession()

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
    comment = handle_ratelimit(submission.add_comment, reply)  
  else:
    comment = handle_ratelimit(submission.reply, reply)

  print("Sending confirmation of donation (", donation_amount, donation_currency,") for", charity_name, "to", parent_commenter)

def check_mentions():
  # Remote mentions tracking
  all_mentions = r.get_mentions()
  new_mentions = filter(lambda x: x.new, all_mentions)

  # Local mentions tracking
  with open('processed_mentions', 'a+') as mentions_file:
    mentions_file.seek(0)
    processed_mentions = mentions_file.read().splitlines()

    for mention in new_mentions:
      if mention.id not in processed_mentions:

        td = TrackedDonation(mention, r)
        td.send_donation_url()

        td.save_to_database()

        print(mention.body,"=", td.charity_id, "Donation message sent:", td.donation_url_sent)
        print(td.donator,"(id:",td.donator_post_id,"is_root",td.donator_is_root,") /", td.parent_commenter,"(",td.parent_post_id,")")

        mention.mark_as_read() # Remotely prevents responding to the same message twice.
        mentions_file.write(mention.id + '\n') # Locally prevents responding to the same message twice.

def check_pending_donations():
  pending_donations = session.query(Donation).filter(
    and_(Donation.donation_url_sent == True, 
         Donation.donation_id != None, 
         Donation.donation_complete == False))

  for donation in pending_donations:
    donation_accepted,\
    donation_amount,\
    donation_currency,\
    donation_message = get_donation_details(donation.donation_id)

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

def init():
  while True:
    o.refresh()
    print("Checking mentions...")
    check_mentions()
    print("Checking pending donations...")
    check_pending_donations()
    print("Sleeping for %s seconds..." % CHECKING_INTERVAL)
    time.sleep(CHECKING_INTERVAL)

# print("Starting daemonized")

# with daemon.DaemonContext():
#  init()
# o.refresh()
# check_mentions()
# check_pending_donations()
init()