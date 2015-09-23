from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Donation(Base):
  __tablename__ = 'donation'

  id                = Column(Integer, primary_key=True)
  user_id           = Column(String(50), nullable=False) # A UUID that we generate to link donation confirmations to donation_id. Looks like: f6decf46-613f-11e5-be5c-3c970e4cfa1a
  charity_id        = Column(Integer, nullable=False) # The charity being donated to
  donation_id       = Column(Integer, nullable=True) # The donation ID that just giving gives back to us. We query this to find out the donation status. Looks like: 35533643
  
  # Donator and parent_commenter usernames and post ids
  donator           = Column(String(30), nullable=False)
  donator_post_id   = Column(String(30), nullable=False) # The reddit comment ID that triggered Charity-Bot
  parent_commenter  = Column(String(30), nullable=False)
  parent_post_id    = Column(String(30), nullable=False)

  
  donator_is_root   = Column(Boolean, nullable=False)
  donation_url_sent = Column(Boolean, nullable=False) # Donation url sent via pm
  donation_complete = Column(Boolean, nullable=False)




