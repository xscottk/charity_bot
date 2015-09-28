import uuid
import urllib

from utils import *
from sql_tables import *

class TrackedDonation():

  def validate_charity_id(self, mention):
    # Parse and validate donation message.
    # RETURN: Validated charity number, name, and website OR None if invalid charity number.

    # Call format: \u\Charity-Bot donate charityID
    # Default Charity if no charity specified or invalid charityID: \u\Charity-Bot donate

    # Rules:
    # First argument must be the word 'donate'
    # Charity must be a valid number, and valid JustGiving charity number

    message = self.mention.body.split()

    donate  = message[1] == "donate"

    if not donate:
      self.charity_id          = None
      self.charity_name        = None
      self.charity_profile_url = None

    else:
      try:
        self.charity_id = int(message[2])
      except (TypeError, ValueError, IndexError):
        self.charity_id = DEFAULT_CHARITY_ID

      # QUESTION: Should I just be storing json responses for charity/donation details and then accessing them directly in functions?
      response            = justgiving_request_wrapper('v1/charity/' + str(self.charity_id),'GET')

      if response.status_code == 200:
        json_response            = response.json()
        self.charity_name        = json_response.get('name')
        self.charity_profile_url = json_response.get('profilePageUrl')

      else:
        self.charity_id          = None
        self.charity_name        = None
        self.charity_profile_url = None

  def set_attribution_info(self):
    mention         = self.mention
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
        parent_commenter = self.r.get_info(thing_id=parent_post_id).author.name
    except AttributeError:
      parent_commenter = None
    
    self.donator          = donator
    self.donator_post_id  = donator_post_id
    self.parent_commenter = parent_commenter
    self.parent_post_id   = parent_post_id
    self.donator_is_root  = donator_is_root
    # return [donator, donator_post_id, parent_commenter, parent_post_id, donator_is_root]

  def set_donation_url(self):
    # Get the donation link from justgiving. And add the GET variables we need to track the donation.
    charity_id = self.charity_id
    user_id    = self.user_id

    if charity_id == None:
      return None

    # Pretty sure this is a sin...
    exit_url_info = 'http://' + HTTP_HOSTNAME + ":" + str(HTTP_PORT) + '/?donation_id=JUSTGIVING-DONATION-ID&user_id=' + str(user_id)
    exit_url_info = urllib.parse.quote(exit_url_info)

    donation_url = JUSTGIVING_BASE_WEBSITE_URL + '/4w350m3/donation/direct/charity/' + str(charity_id) + '/?exitUrl=' + exit_url_info

    self.donation_url = donation_url

  def send_donation_url(self):
    # Send the donation link to the donator. Return True if donation message sent, otherwise return False.
    donation_url = self.donation_url
    donator = self.donator
    parent_commenter = self.parent_commenter

    if donation_url == None:
      self.donation_url_sent = False

    message = "Here's your donation link. You're totally awesome! \n\n" + donation_url
    
    # If the parent_commenter deletes their post we need to let the donator know.
    if parent_commenter:
      subject = "Your donation link for /u/"+parent_commenter+"'s comment/post"
    else:
      subject = "Your donation link!"
      message += "\n\n Unfortunately the person who inspired your donation has deleted their post. I will be unable to notify them of your donation."

    if donator:
      # sent_message = r.send_message(recipient=donator, subject=subject, message=message)
      sent_message = handle_ratelimit(self.r.send_message, recipient=donator, subject=subject, message=message)  
    else:
      self.donation_url_sent = False

    # TODO: return not sent_message.get("errors")..or maybe it's less clear
    if not sent_message.get("errors"):
      self.donation_url_sent = True
    else:
      self.donation_url_sent = False

  def save_to_database(self):

    new_donation = Donation(user_id=self.user_id, 
      charity_id=self.charity_id, 
      charity_name=self.charity_name, 
      charity_profile_url=self.charity_profile_url,
      donator=self.donator, 
      donator_post_id=self.donator_post_id, 
      donator_is_root=self.donator_is_root, 
      parent_commenter=self.parent_commenter, 
      parent_post_id=self.parent_post_id, 
      donation_url_sent=self.donation_url_sent, 
      donation_complete=False)
    self.session.add(new_donation)
    self.session.commit()
  
  def __init__(self, mention, r, session):
    self.r                   = r
    self.session             = session
    self.user_id             = str(uuid.uuid1())
    self.mention             = None
    self.is_valid            = False
    self.charity_id          = None
    self.charity_name        = None
    self.charity_profile_url = None

    self.donator             = None
    self.donator_post_id     = None
    self.parent_commenter    = None
    self.parent_post_id      = None
    self.donator_is_root     = None

    self.donation_url        = None
    self.donation_url_sent   = None

    self.mention = mention
    self.validate_charity_id(mention)
    
    if self.charity_id:

      self.set_attribution_info()
      self.set_donation_url()
      self.is_valid = True

    else:
      self.is_valid = False # TODO: Add a real validation function
      
