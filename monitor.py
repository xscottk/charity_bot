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

        td = TrackedDonation(mention, r, session)
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
        r=r,
        donator_is_root=donation.donator_is_root,
        donator=donation.donator, 
        parent_commenter=donation.parent_commenter, 
        parent_post_id=donation.parent_post_id, 
        donation_amount=donation_amount, 
        donation_currency=donation_currency, 
        charity_name=donation.charity_name,
        charity_profile_url=donation.charity_profile_url, 
        donator_message=donation_message)

# def init():
#   while True:
#     o.refresh()
#     check_mentions()
#     check_pending_donations()
#     time.sleep(CHECKING_INTERVAL)

# print("Starting daemonized")

# with daemon.DaemonContext():
#  init()
o.refresh()
check_mentions()
check_pending_donations()